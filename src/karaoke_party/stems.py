"""Vocal/instrumental separation so a song can be sung karaoke style.

Separation is done with `audio-separator`, which wraps the UVR model zoo
(Demucs, MDX-Net, Mel-Band/BS-RoFormer) behind one API and downloads weights on
first use. The model is configurable because the quality/speed trade-off depends
a lot on the machine: Demucs is the fast default, RoFormer is slower but cleaner.
"""

from __future__ import annotations

import importlib.util
import inspect
import os
import shutil
import subprocess
import threading
import time
import uuid
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

# Demucs by default: good separation and fast on GPU. Any filename from
# `audio-separator --list_models` works, e.g. a RoFormer .ckpt for best quality.
DEFAULT_MODEL = (os.environ.get("KARAOKE_STEMS_MODEL") or "").strip() or "htdemucs.yaml"
OUTPUT_BITRATE = (os.environ.get("KARAOKE_STEMS_BITRATE") or "").strip() or "192k"
USE_AUTOCAST = (os.environ.get("KARAOKE_STEMS_AUTOCAST") or "").strip() not in {"", "0", "false"}

_VOCAL_TAG = "(vocals)"
_INSTRUMENTAL_TAG = "(instrumental)"

# ASCII-only stem basenames. audio-separator otherwise embeds the song title
# (accents, brackets, …) into every FLAC name; on Windows that regularly
# breaks the later ffmpeg encode with "No such file or directory".
_SAFE_STEM_NAMES = {
    "Vocals": "stem_vocals",
    "Instrumental": "stem_instrumental",
    "Bass": "stem_bass",
    "Drums": "stem_drums",
    "Other": "stem_other",
}

# Progress band the model pass gets; encoding takes over from there.
_SEPARATE_FROM = 0.15
_SEPARATE_TO = 0.80
# Scratch folders survive a crash, so they are only dropped once no live run
# could still own them.
_STALE_RUN_SECONDS = 6 * 60 * 60

_OUTPUT_FORMAT = "WAV"

_separator = None
_separator_model: str | None = None
_separator_format: str | None = None
_separator_lock = threading.Lock()
_separation_lock = threading.Lock()


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
    """Root of the scratch space; every separation gets a folder inside it."""
    from .track_cache import stems_work_dir

    return stems_work_dir()


def _new_run_dir() -> Path:
    """Private scratch for a single separation.

    Raw stems used to land in one shared folder that was wiped at the start and
    end of every run, so a second separation (another worker, or a second copy
    of the app) deleted the FLACs ffmpeg was about to read. A folder per run
    removes that class of failure entirely.
    """
    path = work_dir() / f"run-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _prune_stale_runs() -> None:
    """Drop scratch left behind by a crash, plus files from the old layout."""
    now = time.time()
    for path in work_dir().iterdir():
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir() and now - path.stat().st_mtime > _STALE_RUN_SECONDS:
                shutil.rmtree(path, ignore_errors=True)
        except OSError:
            continue


def clear_work_dir(timeout: float = 5.0) -> int:
    """Empty the scratch space. Returns how many files were removed.

    Skips the whole thing while a separation holds the lock: wiping a live run
    is exactly the bug this layout is meant to prevent.
    """
    if not _separation_lock.acquire(timeout=timeout):
        return 0
    removed = 0
    try:
        for path in work_dir().iterdir():
            try:
                if path.is_file():
                    path.unlink()
                    removed += 1
                elif path.is_dir():
                    removed += sum(1 for item in path.rglob("*") if item.is_file())
                    shutil.rmtree(path, ignore_errors=True)
            except OSError:
                continue
    finally:
        _separation_lock.release()
    return removed


def _use_output_dir(separator, folder: Path) -> None:
    """Send this run's stems to ``folder``.

    The loaded model keeps its own copy of the output directory, so setting it
    on the Separator alone would still write into the previous run's folder.
    """
    separator.output_dir = str(folder)
    model = getattr(separator, "model_instance", None)
    if model is not None:
        model.output_dir = str(folder)


@contextmanager
def _demucs_progress(report: Callable[[float, str], None]) -> Iterator[None]:
    """Forward Demucs' per-chunk progress; a no-op if its API ever changes.

    audio-separator hardcodes ``set_progress_bar=None``, which left the UI
    frozen at the start of the longest phase of the whole pipeline.
    """
    try:
        from audio_separator.separator.architectures import demucs_separator

        original = demucs_separator.apply_model
        supported = "set_progress_bar" in inspect.signature(original).parameters
    except Exception:  # noqa: BLE001 — progress must never block separation
        yield
        return
    if not supported:
        yield
        return

    def on_chunk(_base: float, value: float) -> None:
        # Demucs counts its chunks up to 0.8, whatever the track length.
        done = min(1.0, max(0.0, float(value) / 0.8))
        report(_SEPARATE_FROM + done * (_SEPARATE_TO - _SEPARATE_FROM), "separant")

    def with_progress(*args, **kwargs):
        if kwargs.get("set_progress_bar") is None:
            kwargs["set_progress_bar"] = on_chunk
        return original(*args, **kwargs)

    demucs_separator.apply_model = with_progress
    try:
        yield
    finally:
        demucs_separator.apply_model = original


def _get_separator():
    """One Separator per process: loading model weights is the slow part."""
    global _separator, _separator_model, _separator_format
    from audio_separator.separator import Separator

    from .config import stem_models_dir

    with _separator_lock:
        if (
            _separator is None
            or _separator_model != DEFAULT_MODEL
            or _separator_format != _OUTPUT_FORMAT
        ):
            separator = Separator(
                log_level=40,  # logging.ERROR
                output_dir=str(work_dir()),
                # WAV avoids a second ffmpeg round-trip inside pydub's FLAC
                # exporter, which on Windows sometimes reported success to us
                # while leaving stem_*.flac missing for the later encode.
                output_format=_OUTPUT_FORMAT,
                model_file_dir=str(stem_models_dir()),
                use_autocast=USE_AUTOCAST,
            )
            separator.load_model(model_filename=DEFAULT_MODEL)
            _separator = separator
            _separator_model = DEFAULT_MODEL
            _separator_format = _OUTPUT_FORMAT
        return _separator


def _encode_mp3(sources: list[Path], target: Path) -> None:
    """Encode one stem, or sum several stems, into a single MP3."""
    if not sources:
        raise SeparationError("No hi ha cap pista per codificar")
    missing = [
        str(source)
        for source in sources
        if not (source.is_file() and source.stat().st_size > 0)
    ]
    if missing:
        raise SeparationError(f"Falten pistes separades: {', '.join(Path(m).name for m in missing)}")
    target.parent.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for source in sources:
        command += ["-i", str(source.resolve())]
    if len(sources) > 1:
        # normalize=0 keeps a plain sum, so the stems recombine at original level.
        command += ["-filter_complex", f"amix=inputs={len(sources)}:normalize=0"]
    command += ["-c:a", "libmp3lame", "-b:a", OUTPUT_BITRATE, str(target.resolve())]
    # ffmpeg reports in UTF-8; the console codepage would mangle accented paths.
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0 or not target.is_file() or target.stat().st_size <= 0:
        detail = (result.stderr or "").strip()[:300] or "sortida buida"
        raise SeparationError(f"ffmpeg ha fallat: {detail}")


def _classify(paths: list[Path]) -> tuple[list[Path], list[Path], list[Path]]:
    vocals: list[Path] = []
    instrumental: list[Path] = []
    others: list[Path] = []
    for path in paths:
        name = path.name.lower()
        stem = path.stem.lower()
        if stem == "stem_vocals" or _VOCAL_TAG in name:
            vocals.append(path)
        elif stem == "stem_instrumental" or _INSTRUMENTAL_TAG in name:
            instrumental.append(path)
        else:
            others.append(path)
    return vocals, instrumental, others


def _resolve_outputs(produced: list | None, scratch: Path) -> list[Path]:
    """Collect real stem files from the scratch folder.

    ``audio-separator`` always appends a name to its return list even when the
    write silently no-ops (near-silent stem / pydub export error). Trust the
    directory listing first; only use ``produced`` as a hint for ordering.
    """
    on_disk = {
        path.name.lower(): path
        for path in scratch.iterdir()
        if path.is_file() and path.stat().st_size > 0 and path.stem.lower() != "input"
    }
    outputs: list[Path] = []
    seen: set[str] = set()
    for item in produced or []:
        name = Path(str(item)).name.lower()
        path = on_disk.get(name)
        if path is not None and name not in seen:
            outputs.append(path)
            seen.add(name)
    for name, path in sorted(on_disk.items()):
        if name not in seen:
            outputs.append(path)
            seen.add(name)
    return outputs


def _stage_stems(sources: list[Path], folder: Path, prefix: str) -> list[Path]:
    """Copy stems next to the final MP3 before calling ffmpeg.

    Encoding from the ephemeral ``run-*`` folder raced with cleanup and with
    audio-separator's own temp handling; staging under ``tracks/<key>/`` keeps
    the inputs stable until the MP3 is written.
    """
    folder.mkdir(parents=True, exist_ok=True)
    staged: list[Path] = []
    for index, source in enumerate(sources):
        if not source.is_file() or source.stat().st_size <= 0:
            continue
        dest = folder / f"{prefix}_{index}{source.suffix.lower() or '.wav'}"
        shutil.copy2(source, dest)
        staged.append(dest)
    return staged


def _cleanup_staged(folder: Path, prefix: str) -> None:
    if not folder.is_dir():
        return
    for path in folder.glob(f"{prefix}_*"):
        try:
            path.unlink()
        except OSError:
            continue


def _stage_input(audio_path: Path, run_dir: Path) -> Path:
    """Copy the song into the run folder under an ASCII name.

    Demucs/ffmpeg reading a Desktop path full of accents and brackets is a
    common source of silent write failures; a short local copy sidesteps that.
    """
    suffix = audio_path.suffix.lower() or ".mp3"
    if suffix not in {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".opus"}:
        suffix = ".mp3"
    staged = run_dir / f"input{suffix}"
    shutil.copy2(audio_path, staged)
    return staged


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

    # One separation at a time: the Separator and its loaded model are shared
    # mutable state, and two Demucs passes would only fight over the same GPU.
    with _separation_lock:
        # Both stems are required: Whisper needs the vocal track, karaoke needs
        # the instrumental. A lone instrumental (e.g. vocals encode failed once)
        # must not short-circuit a later separation.
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
        _prune_stale_runs()
        run_dir = _new_run_dir()
        encode_ok = False
        try:
            report(0.05, "model")
            separator = _get_separator()
            _use_output_dir(separator, run_dir)

            report(_SEPARATE_FROM, "separant")
            staged_input = _stage_input(Path(audio_path), run_dir)
            with _demucs_progress(report):
                produced = separator.separate(
                    str(staged_input),
                    custom_output_names=dict(_SAFE_STEM_NAMES),
                )
            outputs = _resolve_outputs(produced, run_dir)
            if not outputs:
                listing = ", ".join(path.name for path in run_dir.iterdir()) or "(buit)"
                raise SeparationError(
                    f"El separador no ha generat cap pista · contingut: {listing}"
                )

            report(0.85, "codificant")
            vocals, instrumental, others = _classify(outputs)
            # Two-stem models hand us the instrumental directly; four-stem models
            # (Demucs) give drums/bass/other, which we sum back together.
            sources = instrumental or others
            if not sources:
                raise SeparationError("No s’ha pogut aïllar la pista instrumental")

            staged_inst = _stage_stems(sources, track_folder, "tmp_inst")
            staged_vocals = _stage_stems(vocals, track_folder, "tmp_vocals")
            try:
                if not staged_inst:
                    raise SeparationError("No s’han pogut preparar les pistes instrumentals")
                _encode_mp3(staged_inst, target_instrumental)

                if staged_vocals:
                    try:
                        _encode_mp3(staged_vocals, target_vocals)
                    except SeparationError:
                        target_vocals = None
                else:
                    target_vocals = None
                encode_ok = True
            finally:
                _cleanup_staged(track_folder, "tmp_inst")
                _cleanup_staged(track_folder, "tmp_vocals")
        finally:
            # Keep the scratch on failure so the next error message / manual
            # inspection can see what Demucs actually wrote.
            if encode_ok:
                shutil.rmtree(run_dir, ignore_errors=True)

        report(1.0, "fet")
        return target_instrumental, (
            target_vocals if target_vocals and target_vocals.is_file() else None
        )


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
