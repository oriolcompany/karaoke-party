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

_VOCAL_TAG = "(vocals)"
_INSTRUMENTAL_TAG = "(instrumental)"

_separator = None
_separator_model: str | None = None
_separator_lock = threading.Lock()
# Separate from model load: align + stem workers must not share stems-work.
_stems_run_lock = threading.Lock()

# Stable basenames so we never depend on the source MP3's filename (spaces,
# unicode, or audio-separator returning cwd-relative paths only).
_OUTPUT_NAMES = {
    "Vocals": "kp_vocals",
    "Instrumental": "kp_instrumental",
    "Drums": "kp_drums",
    "Bass": "kp_bass",
    "Other": "kp_other",
    "Guitar": "kp_guitar",
    "Piano": "kp_piano",
}


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
    from .track_cache import instrumental_path as _path

    return _path(cache_dir, key)


def vocals_path(cache_dir: Path, key: str) -> Path:
    from .track_cache import vocals_path as _path

    return _path(cache_dir, key)


def has_instrumental(cache_dir: Path, key: str) -> bool:
    path = instrumental_path(cache_dir, key)
    return path.is_file() and path.stat().st_size > 0


def has_vocals(cache_dir: Path, key: str) -> bool:
    path = vocals_path(cache_dir, key)
    return path.is_file() and path.stat().st_size > 0


def clear_stems(cache_dir: Path, key: str) -> int:
    from .track_cache import clear_track_files

    return clear_track_files(cache_dir, key, {"stems"})["stems"]


def work_dir() -> Path:
    """Scratch space for raw stems, shared by every separation."""
    from .track_cache import stems_work_dir

    return stems_work_dir()


def _clear_work_dir() -> None:
    scratch = work_dir()
    if not scratch.is_dir():
        return
    for path in scratch.iterdir():
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
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
    missing = [str(source) for source in sources if not source.is_file()]
    if missing:
        raise SeparationError(
            "ffmpeg no troba les pistes temporals: " + "; ".join(missing[:4])
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for source in sources:
        command += ["-i", str(source.resolve())]
    if len(sources) > 1:
        # normalize=0 keeps a plain sum, so the stems recombine at original level.
        command += ["-filter_complex", f"amix=inputs={len(sources)}:normalize=0"]
    command += ["-c:a", "libmp3lame", "-b:a", OUTPUT_BITRATE, str(target.resolve())]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0 or not target.is_file() or target.stat().st_size <= 0:
        detail = (result.stderr or result.stdout or "").strip()[:300]
        inputs = ", ".join(source.name for source in sources)
        raise SeparationError(f"ffmpeg ha fallat ({inputs}): {detail or 'sense detall'}")


def _classify(paths: list[Path]) -> tuple[list[Path], list[Path], list[Path]]:
    vocals: list[Path] = []
    instrumental: list[Path] = []
    others: list[Path] = []
    for path in paths:
        name = path.name.lower()
        if _VOCAL_TAG in name or name.startswith("kp_vocals"):
            vocals.append(path)
        elif _INSTRUMENTAL_TAG in name or name.startswith("kp_instrumental"):
            instrumental.append(path)
        else:
            others.append(path)
    return vocals, instrumental, others


def _resolve_outputs(produced: list | None, scratch: Path) -> list[Path]:
    """Map `separate()` return values to real files under the stems work dir.

    audio-separator's Demucs path returns *basename only* (no output_dir), while
    the bytes were written inside ``scratch``. Prefer scratch; never trust a
    same-named leftover in the process cwd.
    """
    scratch = scratch.resolve()
    outputs: list[Path] = []
    seen: set[Path] = set()

    def _take(candidate: Path) -> bool:
        try:
            resolved = candidate.resolve()
        except OSError:
            return False
        if not resolved.is_file() or resolved.stat().st_size <= 0:
            return False
        if resolved in seen:
            return True
        # Only accept files inside scratch (or an explicit absolute path that exists
        # under scratch). CWD-relative ghosts caused ffmpeg "No such file".
        try:
            resolved.relative_to(scratch)
        except ValueError:
            return False
        outputs.append(resolved)
        seen.add(resolved)
        return True

    for item in produced or []:
        raw = Path(str(item))
        if raw.is_absolute():
            if _take(raw):
                continue
            if _take(scratch / raw.name):
                continue
        else:
            if _take(scratch / raw.name):
                continue
            if _take(scratch / raw):
                continue

    if outputs:
        return outputs
    if not scratch.is_dir():
        return []
    return sorted(
        path.resolve()
        for path in scratch.iterdir()
        if path.is_file()
        and path.stat().st_size > 0
        and not path.name.startswith("kp-input")
    )


def _stage_outputs(outputs: list[Path], staging: Path) -> list[Path]:
    """Copy separator output into a private folder before encoding/clearing."""
    if staging.exists():
        shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True, exist_ok=True)
    staged: list[Path] = []
    for source in outputs:
        destination = staging / source.name
        shutil.copy2(source, destination)
        staged.append(destination)
    return staged


def _reset_separator() -> None:
    """Drop the cached Separator after a corrupt/partial Demucs run."""
    global _separator, _separator_model
    with _separator_lock:
        _separator = None
        _separator_model = None


def _safe_input_copy(audio_path: Path, scratch: Path) -> Path:
    """Copy the song to a plain ASCII name inside stems-work.

    Demucs/audio-separator choke on long Windows paths with accents, brackets
    (YouTube ids) and nested album folders — and a failed run can leave the
    shared DemucsSeparator without ``demucs_model_instance``.
    """
    suffix = audio_path.suffix.lower() if audio_path.suffix else ".mp3"
    if suffix not in {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".opus"}:
        suffix = ".mp3"
    target = scratch / f"kp-input{suffix}"
    if target.exists():
        try:
            target.unlink()
        except OSError:
            pass
    shutil.copy2(audio_path, target)
    return target


def _run_separator(audio_path: Path) -> list:
    """Run audio-separator; reset + retry when Demucs leaves an empty result.

    ``Separator.separate`` catches architecture crashes (including
    ``demucs_model_instance`` AttributeError), logs them, and returns ``[]``.
    The shared DemucsSeparator is then stuck until we drop the cached Separator.
    """
    def _once() -> list:
        separator = _get_separator()
        try:
            return list(separator.separate(str(audio_path), dict(_OUTPUT_NAMES)) or [])
        except Exception as exc:  # noqa: BLE001 — some versions re-raise
            _reset_separator()
            raise SeparationError(f"Separació fallida: {exc}") from exc

    produced = _once()
    if produced:
        return produced
    _reset_separator()
    produced = _once()
    if produced:
        return produced
    raise SeparationError(
        "El separador no ha generat cap pista "
        "(Demucs ha fallat; mira l’error a la consola i torna-ho a provar)"
    )


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
    # Both stems are required: Whisper needs the vocal track, karaoke needs the
    # instrumental. A lone instrumental (e.g. vocals encode failed once) must
    # not short-circuit a later separation.
    if (
        target_instrumental.is_file()
        and target_instrumental.stat().st_size > 0
        and target_vocals.is_file()
        and target_vocals.stat().st_size > 0
    ):
        return target_instrumental, target_vocals
    if target_instrumental.is_file() and not (
        target_vocals.is_file() and target_vocals.stat().st_size > 0
    ):
        try:
            target_instrumental.unlink()
        except OSError:
            pass

    def report(ratio: float, phase: str) -> None:
        if on_progress is None:
            return
        try:
            on_progress(ratio, phase)
        except Exception:  # noqa: BLE001 — progress must never abort separation
            pass

    from .track_cache import ensure_track_dir

    track_folder = ensure_track_dir(cache_dir, key)
    staging = track_folder / "stems-raw"
    # Serialize: align worker and stem worker share one stems-work + Demucs instance.
    with _stems_run_lock:
        scratch = work_dir()
        try:
            report(0.05, "model")
            _clear_work_dir()
            safe_input = _safe_input_copy(Path(audio_path).resolve(), scratch)

            report(0.15, "separant")
            produced = _run_separator(safe_input)
            outputs = _resolve_outputs(produced, scratch)
            if not outputs:
                raise SeparationError(
                    "El separador no ha generat cap pista "
                    "(possible error d’exportació FLAC/ffmpeg intern)"
                )

            staged = _stage_outputs(outputs, staging)
            # Scratch can be cleared as soon as we have private copies.
            _clear_work_dir()

            report(0.85, "codificant")
            vocals, instrumental, others = _classify(staged)
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
            if staging.exists():
                shutil.rmtree(staging, ignore_errors=True)

    report(1.0, "fet")
    return target_instrumental, (target_vocals if target_vocals and target_vocals.is_file() else None)


def ensure_vocals(
    audio_path: Path,
    key: str,
    cache_dir: Path,
    on_progress: Callable[[float, str], None] | None = None,
) -> Path:
    """Return the vocal stem, running separation first when it is not cached yet.

    This is the single entry point Whisper alignment must use so every path in
    the project isolates vocals before transcription.
    """
    if has_vocals(cache_dir, key):
        return vocals_path(cache_dir, key)
    if not separation_available():
        raise SeparationError(
            'Cal la separació de pistes abans de Whisper · pip install -e ".[stems]"'
        )
    _, vocals = separate_track(audio_path, key, cache_dir, on_progress=on_progress)
    if vocals is None or not vocals.is_file():
        raise SeparationError("No s’ha pogut generar la pista de veu per a Whisper")
    return vocals
