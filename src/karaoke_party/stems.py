"""Vocal/instrumental separation so a song can be sung karaoke style.

Separation is done with `audio-separator`, which wraps the UVR model zoo
(Demucs, MDX-Net, Mel-Band/BS-RoFormer) behind one API and downloads weights on
first use. The model is configurable because the quality/speed trade-off depends
a lot on the machine: Demucs is the fast default, RoFormer is slower but cleaner.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import threading
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path

# Demucs by default: good separation and fast on GPU. Any filename from
# `audio-separator --list_models` works, e.g. a RoFormer .ckpt for best quality.
DEFAULT_MODEL = (os.environ.get("KARAOKE_STEMS_MODEL") or "").strip() or "htdemucs.yaml"
OUTPUT_BITRATE = (os.environ.get("KARAOKE_STEMS_BITRATE") or "").strip() or "192k"
USE_AUTOCAST = (os.environ.get("KARAOKE_STEMS_AUTOCAST") or "").strip() not in {"", "0", "false"}

INSTRUMENTAL_SUFFIX = ".instrumental.mp3"
VOCALS_SUFFIX = ".vocals.mp3"

_VOCAL_TAG = "(vocals)"
_INSTRUMENTAL_TAG = "(instrumental)"

_separator = None
_separator_model: str | None = None
_separator_lock = threading.Lock()


class SeparationError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _separator_installed() -> bool:
    # find_spec instead of import: importing audio_separator pulls in torch,
    # which costs seconds and would stall the library endpoint.
    return importlib.util.find_spec("audio_separator") is not None


def separation_available() -> bool:
    return _separator_installed() and ffmpeg_available()


@lru_cache(maxsize=1)
def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def model_name() -> str:
    return DEFAULT_MODEL


def instrumental_path(cache_dir: Path, key: str) -> Path:
    return cache_dir / f"{key}{INSTRUMENTAL_SUFFIX}"


def vocals_path(cache_dir: Path, key: str) -> Path:
    return cache_dir / f"{key}{VOCALS_SUFFIX}"


def has_instrumental(cache_dir: Path, key: str) -> bool:
    path = instrumental_path(cache_dir, key)
    return path.is_file() and path.stat().st_size > 0


def has_vocals(cache_dir: Path, key: str) -> bool:
    path = vocals_path(cache_dir, key)
    return path.is_file() and path.stat().st_size > 0


def clear_stems(cache_dir: Path, key: str) -> int:
    removed = 0
    for path in (instrumental_path(cache_dir, key), vocals_path(cache_dir, key)):
        try:
            path.unlink()
            removed += 1
        except OSError:
            continue
    return removed


def work_dir() -> Path:
    """Scratch space for raw stems, shared by every separation."""
    from .config import stems_cache_dir

    path = stems_cache_dir() / "work"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _clear_work_dir() -> None:
    for path in work_dir().iterdir():
        if path.is_file():
            try:
                path.unlink()
            except OSError:
                continue


def _get_separator():
    """One Separator per process: loading model weights is the slow part.

    The output directory is fixed for the separator's whole life. The loaded model
    keeps its own copy of it and recreates it when missing, so pointing the
    separator at a fresh directory per track would silently write the stems to the
    previous one.
    """
    global _separator, _separator_model
    from audio_separator.separator import Separator

    from .config import stem_models_dir

    with _separator_lock:
        if _separator is None or _separator_model != DEFAULT_MODEL:
            separator = Separator(
                log_level=40,  # logging.ERROR
                output_dir=str(work_dir()),
                output_format="FLAC",  # lossless here; a single MP3 encode happens later
                model_file_dir=str(stem_models_dir()),
                use_autocast=USE_AUTOCAST,
            )
            separator.load_model(model_filename=DEFAULT_MODEL)
            _separator = separator
            _separator_model = DEFAULT_MODEL
        return _separator


def _encode_mp3(sources: list[Path], target: Path) -> None:
    """Encode one stem, or sum several stems, into a single MP3."""
    if not sources:
        raise SeparationError("No hi ha cap pista per codificar")
    command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for source in sources:
        command += ["-i", str(source)]
    if len(sources) > 1:
        # normalize=0 keeps a plain sum, so the stems recombine at original level.
        command += ["-filter_complex", f"amix=inputs={len(sources)}:normalize=0"]
    command += ["-c:a", "libmp3lame", "-b:a", OUTPUT_BITRATE, str(target)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0 or not target.is_file():
        raise SeparationError(f"ffmpeg ha fallat: {(result.stderr or '').strip()[:300]}")


def _classify(paths: list[Path]) -> tuple[list[Path], list[Path], list[Path]]:
    vocals: list[Path] = []
    instrumental: list[Path] = []
    others: list[Path] = []
    for path in paths:
        name = path.name.lower()
        if _VOCAL_TAG in name:
            vocals.append(path)
        elif _INSTRUMENTAL_TAG in name:
            instrumental.append(path)
        else:
            others.append(path)
    return vocals, instrumental, others


def _resolve_outputs(produced: list | None, scratch: Path) -> list[Path]:
    """Turn whatever `separate()` returned into real files inside the work dir."""
    outputs: list[Path] = []
    for item in produced or []:
        path = Path(str(item))
        for candidate in (path, scratch / path.name):
            if candidate.is_file():
                outputs.append(candidate)
                break
    if outputs:
        return outputs
    return sorted(path for path in scratch.iterdir() if path.is_file())


def separate_track(
    audio_path: Path,
    key: str,
    cache_dir: Path,
    on_progress: Callable[[float, str], None] | None = None,
) -> tuple[Path, Path | None]:
    """Write cached instrumental (and vocals) for one track. Returns their paths."""
    if not audio_path.is_file():
        raise FileNotFoundError(str(audio_path))
    if not ffmpeg_available():
        raise SeparationError("Cal ffmpeg per generar la pista instrumental")

    target_instrumental = instrumental_path(cache_dir, key)
    target_vocals = vocals_path(cache_dir, key)
    if target_instrumental.is_file() and target_instrumental.stat().st_size > 0:
        return target_instrumental, (target_vocals if target_vocals.is_file() else None)

    def report(ratio: float, phase: str) -> None:
        if on_progress is None:
            return
        try:
            on_progress(ratio, phase)
        except Exception:  # noqa: BLE001 — progress must never abort separation
            pass

    cache_dir.mkdir(parents=True, exist_ok=True)
    scratch = work_dir()
    try:
        report(0.05, "model")
        _clear_work_dir()
        separator = _get_separator()

        report(0.15, "separant")
        produced = separator.separate(str(audio_path))
        outputs = _resolve_outputs(produced, scratch)
        if not outputs:
            raise SeparationError("El separador no ha generat cap pista")

        report(0.85, "codificant")
        vocals, instrumental, others = _classify(outputs)
        # Two-stem models hand us the instrumental directly; four-stem models
        # (Demucs) give drums/bass/other, which we sum back together.
        sources = instrumental or others
        if not sources:
            raise SeparationError("No s’ha pogut aïllar la pista instrumental")
        _encode_mp3(sources, target_instrumental)

        if vocals:
            try:
                _encode_mp3(vocals, target_vocals)
            except SeparationError:
                target_vocals = None
        else:
            target_vocals = None
    finally:
        _clear_work_dir()

    report(1.0, "fet")
    return target_instrumental, (target_vocals if target_vocals and target_vocals.is_file() else None)
