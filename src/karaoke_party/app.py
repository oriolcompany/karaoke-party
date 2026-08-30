from __future__ import annotations

import argparse
import asyncio
import logging
import re
import sys
import threading
import time
import uuid
import webbrowser
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import __version__
from .align import (
    align_lyrics,
    alignment_available,
    preload_whisper_model,
    whisper_model_status,
)
from .config import (
    DEFAULT_PORT,
    aligned_cache_dir,
    app_cache_root,
    cache_dir,
    default_music_root,
    save_last_music_root,
    stems_cache_dir,
)
from .deps import check_dependencies, require_dependencies
from .gpu_setup import diagnose as diagnose_gpu
from .covers import (
    covers_cache_dir,
    migrate_cached_covers_into_audio,
    refresh_track_cover_cache,
    resolve_cover,
)
from .folder_picker import pick_music_folder
from .library import TrackInfo, _sort_key, scan_library
from .ratings import get_rating, load_ratings, normalize_rating, set_rating
from .lyrics import (
    PROBE_ERROR_SOURCE,
    PROBE_TIMEOUT,
    LyricsPayload,
    LyricsUnavailable,
    cache_key,
    clear_lyrics_cache,
    clear_lyrics_keys,
    clear_probe_errors,
    fetch_lyrics,
    load_aligned_cached,
    load_cached,
    lyrics_status_and_source,
    save_aligned_cached,
    save_cached,
    save_manual_lyrics,
    maybe_embed_lyrics,
    payload_to_text,
    read_local_lyrics,
)
from .syllables import expand_syllable_tokens, has_syllable_glue, refine_syllable_timings
from .stems import (
    SeparationError,
    clear_work_dir,
    ensure_vocals,
    ffmpeg_available,
    has_instrumental,
    instrumental_path,
    model_name,
    separate_track,
    separation_available,
)
from .track_cache import CACHE_SCOPES as _CACHE_SCOPES
from .video import (
    VideoRenderError,
    download_filename,
    karaoke_is_current,
    mark_karaoke_exported,
    mux_stage_recording,
)


log = logging.getLogger("karaoke_party")


def _project_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


WEB_DIR = _project_root() / "web"

@asynccontextmanager
async def _lifespan(_app: FastAPI):
    # Make sure %LOCALAPPDATA%\KaraokeParty (tracks/, stems-work/, …) exists
    # before any worker touches the cache — otherwise a failed first run can
    # look like "the folder was never created".
    root = app_cache_root()
    cache_dir()
    stems_cache_dir()
    log.info("Cache root: %s", root)
    # Download/load Whisper (then Meta MMS) at startup so the first song does
    # not stall the align queue on a multi-GB model fetch.
    preload_whisper_model()
    yield


app = FastAPI(title="Karaoke Party", lifespan=_lifespan)
_music_root: Path | None = default_music_root()
_tracks: dict[str, TrackInfo] = {}
_align_jobs: dict[str, dict] = {}
_align_lock = threading.Lock()
_align_queue: list[tuple[str, TrackInfo, str]] = []
_align_worker_started = False
_align_wake = threading.Event()
_probe_lock = threading.Lock()
_probe_state: dict = {
    "running": False,
    "done": 0,
    "total": 0,
    "found": 0,
    "offline": False,
}
# Track ids already probed this session. Prevents restart loops when LRCLIB
# errors leave the on-disk cache empty (status still "unknown").
_probe_attempted: set[str] = set()
# After one full probe pass for the current root, do not auto-restart.
_probe_pass_complete: bool = False
# Bumped to invalidate in-flight workers when the probe is reset/replaced.
_probe_generation: int = 0
_probe_thread: threading.Thread | None = None
PROBE_CONCURRENCY = 3
# Consecutive network failures after which the pass stops calling LRCLIB.
OFFLINE_FAILURE_STREAK = 5
_cover_resync_lock = threading.Lock()
_cover_resync_state: dict = {
    "running": False,
    "done": 0,
    "total": 0,
    "updated": 0,
}
_cover_resync_thread: threading.Thread | None = None
_cover_refresh_lock = threading.Lock()
_cover_refresh_state: dict = {
    "running": False,
    "done": 0,
    "total": 0,
    "updated": 0,
    "same": 0,
    "missing": 0,
    "failed": 0,
}
_cover_refresh_thread: threading.Thread | None = None
COVER_RESYNC_CONCURRENCY = 3
_stem_jobs: dict[str, dict] = {}
_stem_lock = threading.Lock()
# (job_id or None, track). Bulk items carry no job id and only move the counters.
_stem_queue: list[tuple[str | None, TrackInfo]] = []
_stem_worker_started = False
_stem_wake = threading.Event()
_stem_bulk_state: dict = {
    "running": False,
    "done": 0,
    "total": 0,
    "failed": 0,
    "current": "",
    "error": "",
}
_youtube_bulk_lock = threading.Lock()
_youtube_bulk_state: dict = {
    "running": False,
    "done": 0,
    "total": 0,
    "found": 0,
    "skipped": 0,
    "missed": 0,
    "errors": 0,
    "current": "",
    "error": "",
    "scope": "missing",
}
_youtube_bulk_thread: threading.Thread | None = None
_video_jobs: dict[str, dict] = {}
_video_lock = threading.Lock()
_video_queue: list[tuple[str, TrackInfo, str, str]] = []
_video_worker_started = False
_video_wake = threading.Event()


class SetRootBody(BaseModel):
    path: str


class BrowseFolderBody(BaseModel):
    initial: str | None = None


class AlignBody(BaseModel):
    track_id: str
    language: str = "ca"


class VideoBody(BaseModel):
    track_id: str
    language: str = "ca"
    lyrics_layout: str = "stack"


class ResyncCoverBody(BaseModel):
    track_id: str


class ResyncLyricsBody(BaseModel):
    """scope: all = every track; missing = only songs without lyrics now."""

    scope: str = "all"


class SaveLyricsBody(BaseModel):
    track_id: str
    text: str


class RatingBody(BaseModel):
    track_id: str
    rating: int


class YoutubeSearchBody(BaseModel):
    """scope: missing = only songs without a clip; all = overwrite every track."""

    scope: str = "missing"


class StemsBody(BaseModel):
    track_id: str


class TrackCacheBody(BaseModel):
    track_id: str = ""
    # Empty = every song-related cache bucket.
    scopes: list[str] | None = None
    language: str = "ca"


def _normalize_cache_scopes(scopes: list[str] | None) -> set[str]:
    if not scopes:
        return set(_CACHE_SCOPES)
    chosen = {str(item).strip().lower() for item in scopes if str(item).strip()}
    unknown = chosen - _CACHE_SCOPES
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"scopes desconeguts: {', '.join(sorted(unknown))}",
        )
    if not chosen:
        raise HTTPException(status_code=400, detail="Cal almenys un scope")
    return chosen


def _track_cache_status(track: TrackInfo) -> dict:
    from .track_cache import aligned_path as aligned_file_path
    from .track_cache import track_status
    from .youtube import load_cached as load_youtube_cached

    key = cache_key(track.artist, track.title, track.duration)
    root = cache_dir()
    files = track_status(root, key)
    lyrics = load_cached(root, key)
    aligned = load_aligned_cached(root, key)
    youtube = load_youtube_cached(root, key)
    return {
        "track_id": track.id,
        "title": track.title,
        "artist": track.artist,
        "key": key,
        "dir": files.get("dir") or "",
        "lyrics": bool(lyrics and lyrics.lines),
        "lyrics_source": (lyrics.source if lyrics else ""),
        "aligned": aligned is not None,
        "aligned_file": aligned_file_path(root, key).is_file(),
        "instrumental": files["instrumental"],
        "vocals": files["vocals"],
        "cover": files["cover"],
        "youtube": bool(youtube and youtube.get("found") and youtube.get("video_id")),
        "whisper_aligned": aligned is not None,
    }


def _clear_track_cache(track: TrackInfo, scopes: set[str]) -> dict[str, int]:
    from .track_cache import clear_track_files

    key = cache_key(track.artist, track.title, track.duration)
    removed = clear_track_files(cache_dir(), key, scopes)
    if "lyrics" in scopes:
        with _probe_lock:
            _probe_attempted.discard(track.id)
    if "aligned" in scopes:
        with _align_lock:
            for job_id, job in list(_align_jobs.items()):
                if job.get("track_id") == track.id and job.get("status") in {
                    "queued",
                    "running",
                    "done",
                }:
                    if job.get("status") != "running":
                        _align_jobs.pop(job_id, None)
    return removed


def _reset_probe_state() -> None:
    global _probe_pass_complete, _probe_generation
    with _probe_lock:
        _probe_generation += 1
        _probe_attempted.clear()
        _probe_pass_complete = False
        _probe_state.update(
            {"running": False, "done": 0, "total": 0, "found": 0, "offline": False}
        )


def _migrate_covers_background(tracks: list[TrackInfo]) -> None:
    """Promote disk-cached covers into audio tags without blocking the UI."""
    try:
        migrate_cached_covers_into_audio(tracks, covers_cache_dir())
    except Exception:
        pass


def _reload_library(root: Path, *, reset_probe: bool | None = None) -> list[TrackInfo]:
    """Rescan music files. Probe state resets only when the root folder changes."""
    global _music_root, _tracks
    new_root = root.expanduser().resolve()
    old_root = _music_root.resolve() if _music_root is not None else None
    root_changed = old_root is None or new_root != old_root
    _music_root = new_root
    if new_root.is_dir():
        save_last_music_root(new_root)
    tracks = scan_library(new_root)
    _tracks = {track.id: track for track in tracks}
    if reset_probe if reset_probe is not None else root_changed:
        _reset_probe_state()
    threading.Thread(
        target=_migrate_covers_background,
        args=(list(tracks),),
        daemon=True,
        name="cover-migrate",
    ).start()
    return tracks


def _resolve_track(track_id: str) -> TrackInfo:
    track = _tracks.get(track_id)
    if track is None and _music_root is not None:
        # Rescan must not wipe probe progress (covers/audio 404s used to restart it).
        _reload_library(_music_root, reset_probe=False)
        track = _tracks.get(track_id)
    if track is None:
        raise HTTPException(status_code=404, detail="Cançó no trobada")
    return track


def _lines_for_client(lines: list) -> list[dict]:
    prepared = lines if has_syllable_glue(lines) else expand_syllable_tokens(lines)
    return [asdict(line) for line in prepared]


def _with_audio_syllables(key: str, payload: LyricsPayload) -> LyricsPayload:
    """Upgrade word-level Whisper timings to MMS (or energy) syllable splits."""
    if has_syllable_glue(payload.lines):
        return payload
    from .track_cache import vocals_path

    vocals = vocals_path(aligned_cache_dir(), key)
    has_vocals = vocals.is_file()
    lines = refine_syllable_timings(vocals if has_vocals else None, payload.lines)
    updated = LyricsPayload(
        synced=payload.synced,
        source=payload.source,
        lines=lines,
        plain=payload.plain,
    )
    if has_vocals:
        try:
            save_aligned_cached(aligned_cache_dir(), key, updated)
        except OSError:
            pass
    return updated


def _lyrics_response(track: TrackInfo, track_id: str, payload: LyricsPayload, *, aligned: bool) -> dict:
    return {
        "track_id": track_id,
        "title": track.title,
        "artist": track.artist,
        "synced": payload.synced,
        "aligned": aligned,
        "source": payload.source,
        "plain": payload.plain,
        "lines": _lines_for_client(payload.lines),
    }


def _align_done_payload(payload: LyricsPayload) -> dict:
    return {
        "status": "done",
        "aligned": True,
        "synced": True,
        "source": payload.source,
        "plain": payload.plain,
        "lines": _lines_for_client(payload.lines),
    }


def _set_align_job(job_id: str, **fields) -> None:
    with _align_lock:
        current = dict(_align_jobs.get(job_id) or {})
        current.update(fields)
        _align_jobs[job_id] = current


def _run_align_job(job_id: str, track: TrackInfo, language: str) -> None:
    key = cache_key(track.artist, track.title, track.duration)
    try:
        _set_align_job(job_id, status="running", progress=0.0, phase="lyrics")
        payload = asyncio.run(
            fetch_lyrics(
                artist=track.artist,
                title=track.title,
                album=track.album,
                duration=track.duration,
                cache_dir=cache_dir(),
                audio_path=track.path,
            )
        )
        if not payload.lines:
            _set_align_job(job_id, status="error", error="No hi ha lletra per alinear", progress=0.0)
            return

        def on_whisper_progress(ratio: float) -> None:
            _set_align_job(job_id, status="running", progress=round(float(ratio), 3), phase="whisper")

        def on_stem_progress(ratio: float, phase: str) -> None:
            _set_align_job(
                job_id,
                status="running",
                progress=round(float(ratio), 3),
                phase="stems",
                stem_phase=phase,
            )

        # Always isolate vocals before Whisper. Cached stems are reused; otherwise
        # separation runs here so no code path can transcribe the full mix.
        _set_align_job(job_id, status="running", progress=0.0, phase="stems")
        try:
            source_audio = ensure_vocals(
                Path(track.path),
                key,
                stems_cache_dir(),
                on_progress=on_stem_progress,
            )
        except SeparationError as exc:
            _set_align_job(job_id, status="error", error=str(exc), progress=0.0, phase="stems")
            return

        whisper = whisper_model_status()
        if whisper.get("loading") or not whisper.get("ready"):
            _set_align_job(job_id, status="running", progress=0.0, phase="model")
        else:
            _set_align_job(job_id, status="running", progress=0.0, phase="whisper")
        aligned_lines = align_lyrics(
            source_audio,
            payload.lines,
            language=language,
            on_progress=on_whisper_progress,
        )
        aligned_payload = LyricsPayload(
            synced=True,
            source="whisper-align",
            lines=aligned_lines,
            plain=payload.plain,
        )
        save_aligned_cached(
            aligned_cache_dir(),
            key,
            aligned_payload,
            artist=track.artist,
            title=track.title,
            duration=track.duration,
            album=track.album,
        )
        _set_align_job(job_id, **_align_done_payload(aligned_payload), progress=1.0, phase="done")
    except Exception as exc:  # noqa: BLE001 — surface to client poll
        _set_align_job(job_id, status="error", error=str(exc), progress=0.0)


def _align_worker_loop() -> None:
    while True:
        _align_wake.wait(timeout=1.0)
        while True:
            with _align_lock:
                if not _align_queue:
                    _align_wake.clear()
                    break
                job_id, track, language = _align_queue.pop(0)
            _run_align_job(job_id, track, language)


def _ensure_align_worker() -> None:
    global _align_worker_started
    with _align_lock:
        if _align_worker_started:
            return
        _align_worker_started = True
    thread = threading.Thread(target=_align_worker_loop, name="align-worker", daemon=True)
    thread.start()


def _enqueue_align_job(job_id: str, track: TrackInfo, language: str) -> None:
    _ensure_align_worker()
    with _align_lock:
        _align_jobs[job_id] = {
            "status": "queued",
            "progress": 0.0,
            "phase": "queued",
            "track_id": track.id,
        }
        _align_queue.append((job_id, track, language))
    _align_wake.set()


def _public_video_job(job_id: str, job: dict) -> dict:
    return {"job_id": job_id, **{key: value for key, value in job.items() if not str(key).startswith("_")}}


def _set_video_job(job_id: str, **fields) -> None:
    with _video_lock:
        current = dict(_video_jobs.get(job_id) or {})
        current.update(fields)
        _video_jobs[job_id] = current


def _wait_for_alignment(
    track: TrackInfo,
    language: str,
    on_job,
) -> LyricsPayload:
    """Block until lyrics → stems → Whisper → MMS for this song is on disk."""
    key = cache_key(track.artist, track.title, track.duration)
    cached = load_aligned_cached(aligned_cache_dir(), key)
    if cached is not None:
        return _with_audio_syllables(key, cached)

    if not alignment_available():
        raise VideoRenderError('Instal·la l’alineació amb: pip install -e ".[align]"')
    if not separation_available():
        raise VideoRenderError(
            'Whisper necessita la separació de pistes · pip install -e ".[stems]"'
        )

    whisper = whisper_model_status()
    if whisper.get("error") and not whisper.get("ready") and not whisper.get("loading"):
        raise VideoRenderError(whisper.get("error") or "El model Whisper no s’ha pogut carregar")

    job_id = None
    with _align_lock:
        for existing_id, job in _align_jobs.items():
            if job.get("track_id") != track.id:
                continue
            if job.get("status") in {"queued", "running"}:
                job_id = existing_id
                break
    if job_id is None:
        job_id = uuid.uuid4().hex
        _enqueue_align_job(job_id, track, language)

    deadline = time.time() + 30 * 60
    while time.time() < deadline:
        with _align_lock:
            job = dict(_align_jobs.get(job_id) or {})
        on_job(job)
        status = job.get("status")
        if status == "done":
            cached = load_aligned_cached(aligned_cache_dir(), key)
            if cached is None:
                raise VideoRenderError("L’alineació ha acabat però no s’ha desat la lletra")
            return _with_audio_syllables(key, cached)
        if status == "error":
            raise VideoRenderError(job.get("error") or "Alineació fallida")
        if status == "unavailable":
            raise VideoRenderError(job.get("error") or "Alineació no disponible")
        time.sleep(0.8)
    raise VideoRenderError("La sincronització ha trigat massa")


def _run_video_job(job_id: str, track: TrackInfo, language: str, layout: str) -> None:
    key = cache_key(track.artist, track.title, track.duration)
    filename = download_filename(track.artist, track.title)
    try:
        existing = karaoke_is_current(aligned_cache_dir(), key)
        if existing is not None and load_aligned_cached(aligned_cache_dir(), key) is not None:
            _set_video_job(
                job_id,
                status="done",
                phase="done",
                progress=1.0,
                filename=filename,
                _path=str(existing),
            )
            return

        def on_align(job: dict) -> None:
            phase = str(job.get("phase") or job.get("status") or "queued")
            _set_video_job(
                job_id,
                status="running",
                phase=phase,
                progress=float(job.get("progress") or 0.0),
                stem_phase=job.get("stem_phase") or "",
                filename=filename,
            )

        _set_video_job(job_id, status="running", phase="lyrics", progress=0.0, filename=filename)
        payload = _wait_for_alignment(track, language, on_align)
        if not payload.lines:
            raise VideoRenderError("No hi ha lletra per al vídeo")

        existing = karaoke_is_current(aligned_cache_dir(), key)
        if existing is not None:
            _set_video_job(
                job_id,
                status="done",
                phase="done",
                progress=1.0,
                filename=filename,
                _path=str(existing),
            )
            return

        _set_video_job(
            job_id,
            status="ready",
            phase="capture",
            progress=1.0,
            filename=filename,
        )
    except VideoRenderError as exc:
        _set_video_job(job_id, status="error", error=str(exc), progress=0.0, filename=filename)
    except Exception as exc:  # noqa: BLE001 — surface to client poll
        _set_video_job(job_id, status="error", error=str(exc), progress=0.0, filename=filename)


def _video_worker_loop() -> None:
    while True:
        _video_wake.wait(timeout=1.0)
        while True:
            with _video_lock:
                if not _video_queue:
                    _video_wake.clear()
                    break
                job_id, track, language, layout = _video_queue.pop(0)
            _run_video_job(job_id, track, language, layout)


def _ensure_video_worker() -> None:
    global _video_worker_started
    with _video_lock:
        if _video_worker_started:
            return
        _video_worker_started = True
    thread = threading.Thread(target=_video_worker_loop, name="video-worker", daemon=True)
    thread.start()


def _enqueue_video_job(job_id: str, track: TrackInfo, language: str, layout: str) -> None:
    _ensure_video_worker()
    with _video_lock:
        _video_jobs[job_id] = {
            "status": "queued",
            "progress": 0.0,
            "phase": "queued",
            "track_id": track.id,
            "filename": download_filename(track.artist, track.title),
        }
        _video_queue.append((job_id, track, language, layout))
    _video_wake.set()


def _set_stem_job(job_id: str, **fields) -> None:
    with _stem_lock:
        current = dict(_stem_jobs.get(job_id) or {})
        current.update(fields)
        _stem_jobs[job_id] = current


def _run_stem_job(job_id: str | None, track: TrackInfo) -> None:
    key = cache_key(track.artist, track.title, track.duration)
    label = f"{track.artist} — {track.title}".strip(" —")
    bulk = job_id is None
    with _stem_lock:
        if bulk:
            _stem_bulk_state["current"] = label
    error = ""
    try:
        def on_progress(ratio: float, phase: str) -> None:
            if job_id:
                _set_stem_job(
                    job_id, status="running", progress=round(float(ratio), 3), phase=phase
                )

        if job_id:
            _set_stem_job(job_id, status="running", progress=0.0, phase="model")
        separate_track(Path(track.path), key, stems_cache_dir(), on_progress=on_progress)
        if job_id:
            _set_stem_job(job_id, status="done", progress=1.0, phase="done", ready=True)
        ok = True
    except Exception as exc:  # noqa: BLE001 — surface to client poll
        error = str(exc) or exc.__class__.__name__
        if job_id:
            _set_stem_job(job_id, status="error", error=error, progress=0.0)
        ok = False
    if not ok:
        log.warning("Separació fallida per «%s»: %s", label, error)
    if bulk:
        with _stem_lock:
            _stem_bulk_state["done"] += 1
            if not ok:
                _stem_bulk_state["failed"] += 1
                _stem_bulk_state["error"] = error
            if _stem_bulk_state["done"] >= _stem_bulk_state["total"]:
                _stem_bulk_state.update({"running": False, "current": ""})


def _stem_worker_loop() -> None:
    while True:
        _stem_wake.wait(timeout=1.0)
        while True:
            with _stem_lock:
                if not _stem_queue:
                    _stem_wake.clear()
                    break
                job_id, track = _stem_queue.pop(0)
            _run_stem_job(job_id, track)


def _ensure_stem_worker() -> None:
    global _stem_worker_started
    with _stem_lock:
        if _stem_worker_started:
            return
        _stem_worker_started = True
    threading.Thread(target=_stem_worker_loop, name="stem-worker", daemon=True).start()


def _enqueue_stem_job(job_id: str | None, track: TrackInfo, *, front: bool = False) -> None:
    _ensure_stem_worker()
    with _stem_lock:
        if job_id:
            _stem_jobs[job_id] = {
                "status": "queued",
                "progress": 0.0,
                "phase": "queued",
                "track_id": track.id,
                "ready": False,
            }
        if front:
            _stem_queue.insert(0, (job_id, track))
        else:
            _stem_queue.append((job_id, track))
    _stem_wake.set()


def _active_stem_job(track_id: str) -> tuple[str, dict] | None:
    with _stem_lock:
        for existing_id, job in _stem_jobs.items():
            if job.get("track_id") != track_id:
                continue
            if job.get("status") in {"queued", "running"}:
                return existing_id, dict(job)
    return None


def _library_snapshot() -> dict:
    if _music_root is None:
        return {
            "root": None,
            "tracks": [],
            "hidden_tracks": [],
            "pending_tracks": [],
            "total": 0,
            "with_lyrics": 0,
            "pending": 0,
            "hidden": 0,
            "errors": 0,
        }

    if not _tracks:
        _reload_library(_music_root)

    lyrics_path = cache_dir()
    aligned_path = aligned_cache_dir()
    playable_tracks: list[TrackInfo] = []
    hidden_tracks: list[TrackInfo] = []
    pending_tracks: list[TrackInfo] = []
    pending = 0
    hidden = 0
    errors = 0
    for track in _tracks.values():
        status, source = lyrics_status_and_source(
            track.artist,
            track.title,
            track.duration,
            lyrics_cache=lyrics_path,
            aligned_cache=aligned_path,
            audio_path=track.path,
        )
        if status is True:
            playable_tracks.append(track)
        elif status is False:
            hidden += 1
            hidden_tracks.append(track)
            if source == PROBE_ERROR_SOURCE:
                errors += 1
        elif track.id in _probe_attempted:
            # Soft-fail this session (network/API error): do not keep it pending.
            hidden += 1
            hidden_tracks.append(track)
            errors += 1
        else:
            pending += 1
            pending_tracks.append(track)

    playable_tracks.sort(key=_sort_key)
    hidden_tracks.sort(key=_sort_key)
    pending_tracks.sort(key=_sort_key)
    stems_path = stems_cache_dir()
    ratings = load_ratings()
    playable: list[dict] = []
    for track in playable_tracks:
        item = asdict(track)
        key = cache_key(track.artist, track.title, track.duration)
        item["whisper_aligned"] = load_aligned_cached(aligned_path, key) is not None
        item["has_lyrics"] = True
        item["has_instrumental"] = has_instrumental(stems_path, key)
        item["rating"] = get_rating(key, ratings)
        playable.append(item)

    hidden_items: list[dict] = []
    for track in hidden_tracks:
        item = asdict(track)
        key = cache_key(track.artist, track.title, track.duration)
        item["whisper_aligned"] = False
        item["has_lyrics"] = False
        item["rating"] = get_rating(key, ratings)
        hidden_items.append(item)

    pending_items: list[dict] = []
    for track in pending_tracks:
        item = asdict(track)
        key = cache_key(track.artist, track.title, track.duration)
        item["whisper_aligned"] = False
        item["has_lyrics"] = False
        item["lyrics_pending"] = True
        item["rating"] = get_rating(key, ratings)
        pending_items.append(item)

    with _probe_lock:
        probe = dict(_probe_state)
    with _cover_resync_lock:
        covers_resync = dict(_cover_resync_state)
    with _cover_refresh_lock:
        covers_refresh = dict(_cover_refresh_state)
    with _stem_lock:
        stems_state = dict(_stem_bulk_state)
        stems_state["queued"] = len(_stem_queue)
    with _youtube_bulk_lock:
        youtube_state = dict(_youtube_bulk_state)
    from .youtube import search_available as youtube_search_available
    from .youtube import youtube_enabled

    youtube_state["available"] = youtube_search_available() and youtube_enabled()
    return {
        "root": str(_music_root),
        "tracks": playable,
        "hidden_tracks": hidden_items,
        "pending_tracks": pending_items,
        "total": len(_tracks),
        "with_lyrics": len(playable),
        "pending": pending,
        "hidden": hidden,
        "errors": errors,
        "probe": probe,
        "covers_resync": covers_resync,
        "covers_refresh": covers_refresh,
        "stems": stems_state,
        "stems_available": separation_available(),
        "youtube": youtube_state,
    }


def _cache_probe_miss(track: TrackInfo, lyrics_path: Path) -> None:
    """Persist a negative result so the track leaves the pending set."""
    key = cache_key(track.artist, track.title, track.duration)
    save_cached(
        lyrics_path,
        key,
        LyricsPayload(synced=False, source=PROBE_ERROR_SOURCE, lines=[], plain=""),
    )


def _run_lyrics_probe(track_ids: list[str], generation: int) -> None:
    """Probe unknown tracks. Caller must set running/done/total under lock first."""
    global _probe_pass_complete
    lyrics_path = cache_dir()
    offline = threading.Event()
    consecutive_failures = 0

    async def _probe_one(track: TrackInfo) -> bool:
        payload = await fetch_lyrics(
            artist=track.artist,
            title=track.title,
            album=track.album,
            duration=track.duration,
            cache_dir=lyrics_path,
            timeout=PROBE_TIMEOUT,
            audio_path=track.path,
        )
        return bool(payload.lines)

    async def _probe_all() -> None:
        nonlocal consecutive_failures
        # Keep LRCLIB happy: too many parallel requests get throttled, and a
        # throttled response used to be stored as "this song has no lyrics".
        semaphore = asyncio.Semaphore(PROBE_CONCURRENCY)

        async def worker(track: TrackInfo) -> None:
            nonlocal consecutive_failures
            found = False
            try:
                async with semaphore:
                    with _probe_lock:
                        if generation != _probe_generation:
                            return
                    # LRCLIB is clearly unreachable: stop waiting on every
                    # remaining song and let the user retry later instead.
                    if offline.is_set():
                        raise LyricsUnavailable("LRCLIB unreachable")
                    found = await _probe_one(track)
                consecutive_failures = 0
            except Exception as exc:  # noqa: BLE001
                found = False
                if isinstance(exc, LyricsUnavailable):
                    consecutive_failures += 1
                    if consecutive_failures >= OFFLINE_FAILURE_STREAK:
                        offline.set()
                try:
                    _cache_probe_miss(track, lyrics_path)
                except Exception:  # noqa: BLE001
                    pass
            with _probe_lock:
                if generation != _probe_generation:
                    return
                _probe_state["done"] += 1
                _probe_state["offline"] = offline.is_set()
                if found:
                    _probe_state["found"] += 1

        await asyncio.gather(*(worker(_tracks[tid]) for tid in track_ids if tid in _tracks))

    try:
        asyncio.run(_probe_all())
    finally:
        with _probe_lock:
            if generation == _probe_generation:
                _probe_state["running"] = False
                _probe_pass_complete = True


def _ensure_lyrics_probe(
    *,
    force_all: bool = False,
    track_ids: list[str] | None = None,
) -> None:
    global _probe_pass_complete, _probe_thread
    if _music_root is None:
        return
    if not _tracks:
        _reload_library(_music_root, reset_probe=False)

    lyrics_path = cache_dir()
    aligned_path = aligned_cache_dir()
    with _probe_lock:
        if _probe_state["running"]:
            return
        # A previous generation may still be winding down after invalidation.
        if _probe_thread is not None and _probe_thread.is_alive():
            return
        # One pass per root: finishing must not restart from 0/N.
        forced = force_all or track_ids is not None
        if _probe_pass_complete and not forced:
            return
        if track_ids is not None:
            unknown = [
                tid
                for tid in track_ids
                if tid in _tracks and tid not in _probe_attempted
            ]
        elif force_all:
            unknown = [
                track.id
                for track in _tracks.values()
                if track.id not in _probe_attempted
            ]
        else:
            unknown = [
                track.id
                for track in _tracks.values()
                if track.id not in _probe_attempted
                and lyrics_status_and_source(
                    track.artist,
                    track.title,
                    track.duration,
                    lyrics_cache=lyrics_path,
                    aligned_cache=aligned_path,
                    audio_path=track.path,
                )[0]
                is None
            ]
        if not unknown:
            _probe_pass_complete = True
            return
        # Claim ids immediately so /api/library cannot start a second pass.
        _probe_attempted.update(unknown)
        generation = _probe_generation
        _probe_state.update(
            {
                "running": True,
                "done": 0,
                "total": len(unknown),
                "found": 0,
                "offline": False,
            }
        )
        thread = threading.Thread(
            target=_run_lyrics_probe,
            args=(list(unknown), generation),
            daemon=True,
            name="lyrics-probe",
        )
        _probe_thread = thread
    thread.start()


_gpu_status_cache: dict = {"at": 0.0, "payload": None}
_GPU_STATUS_TTL_SECONDS = 60.0


def _cached_gpu_status() -> dict:
    """Avoid re-running nvidia-smi / torch probes on every /api/health poll."""
    now = time.time()
    cached = _gpu_status_cache.get("payload")
    if cached is not None and now - float(_gpu_status_cache.get("at") or 0) < _GPU_STATUS_TTL_SECONDS:
        return cached
    payload = diagnose_gpu().to_dict()
    _gpu_status_cache["at"] = now
    _gpu_status_cache["payload"] = payload
    return payload


@app.get("/api/health")
def health() -> dict:
    dep_issues = check_dependencies()
    return {
        "ok": not dep_issues,
        "version": __version__,
        "music_root": str(_music_root) if _music_root else None,
        "tracks": len(_tracks),
        "cache": str(cache_dir()),
        "alignment": alignment_available(),
        "stems": separation_available(),
        "whisper": whisper_model_status(),
        "gpu": _cached_gpu_status(),
        "dependencies": {
            "ok": not dep_issues,
            "missing": [
                {"name": issue.name, "detail": issue.detail, "fix": issue.fix}
                for issue in dep_issues
            ],
        },
    }


@app.get("/api/whisper")
def whisper_status() -> dict:
    """Lightweight Whisper status for the settings UI (no GPU diagnose)."""
    return whisper_model_status()


@app.get("/api/library")
def library() -> dict:
    # Basic lyrics lookup is manual (settings) or the first step of Whisper align —
    # never kicked off just by opening the library.
    return _library_snapshot()


@app.post("/api/library/root")
def set_root(body: SetRootBody) -> dict:
    root = Path(body.path)
    if not root.is_dir():
        raise HTTPException(status_code=400, detail="La carpeta no existeix")
    # Only reset the probe when the folder actually changes (same path must not
    # kill an in-flight pass and start another from 0/N).
    tracks = _reload_library(root)
    return {"root": str(root), "tracks": len(tracks)}


@app.post("/api/library/browse")
async def browse_library_folder(body: BrowseFolderBody | None = None) -> dict:
    """Open the native OS folder picker (local app only) and return the path."""
    initial = body.initial if body else None
    if not initial and _music_root is not None:
        initial = str(_music_root)
    path = await asyncio.to_thread(pick_music_folder, initial)
    return {"path": path, "cancelled": path is None}


@app.post("/api/library/retry")
def retry_failed_lyrics() -> dict:
    """User-triggered retry for songs whose lookup failed (never automatic)."""
    if _music_root is None:
        raise HTTPException(status_code=400, detail="Cap carpeta carregada")
    cleared = clear_probe_errors(cache_dir())
    _reset_probe_state()
    _ensure_lyrics_probe()
    return {"cleared": cleared}


def _wait_for_probe_idle() -> None:
    with _probe_lock:
        previous = _probe_thread
    if previous is not None and previous.is_alive():
        previous.join(timeout=60.0)


@app.post("/api/library/lyrics/resync")
def resync_basic_lyrics(body: ResyncLyricsBody | None = None) -> dict:
    """Force re-fetch of basic lyrics (local files, LRCLIB, lyrics.ovh).

    scope=all: every scanned track.
    scope=missing: only tracks that currently have no lyrics.
    """
    if _music_root is None:
        raise HTTPException(status_code=400, detail="Cap carpeta carregada")
    if not _tracks:
        _reload_library(_music_root, reset_probe=False)

    scope = (body.scope if body else "all") or "all"
    if scope not in {"all", "missing"}:
        raise HTTPException(status_code=400, detail="scope ha de ser 'all' o 'missing'")

    lyrics_path = cache_dir()
    aligned_path = aligned_cache_dir()

    if scope == "missing":
        targets: list[TrackInfo] = []
        keys: list[str] = []
        for track in _tracks.values():
            status, _source = lyrics_status_and_source(
                track.artist,
                track.title,
                track.duration,
                lyrics_cache=lyrics_path,
                aligned_cache=aligned_path,
                audio_path=track.path,
            )
            if status is True:
                continue
            targets.append(track)
            keys.append(cache_key(track.artist, track.title, track.duration))
        cleared = clear_lyrics_keys(lyrics_path, keys)
        _reset_probe_state()
        _wait_for_probe_idle()
        _ensure_lyrics_probe(track_ids=[track.id for track in targets])
    else:
        cleared = clear_lyrics_cache(lyrics_path)
        _reset_probe_state()
        # Let an in-flight probe wind down after generation bump before forcing a
        # full pass; otherwise _ensure_lyrics_probe would no-op while it is alive.
        _wait_for_probe_idle()
        _ensure_lyrics_probe(force_all=True)

    with _probe_lock:
        probe = dict(_probe_state)
    return {"cleared": cleared, "scope": scope, "probe": probe}


def _generic_cover_path() -> Path:
    generic = WEB_DIR / "album-generic.png"
    return generic if generic.is_file() else WEB_DIR / "album-generic.png"


async def _resync_cover_track(track: TrackInfo) -> bool:
    """Force remote cover lookup. True when a remote cover was applied."""
    result = await resolve_cover(
        Path(track.path),
        artist=track.artist,
        title=track.title,
        album=track.album,
        duration=track.duration,
        cache_dir=covers_cache_dir(),
        generic_path=_generic_cover_path(),
        force=True,
    )
    return result.source.startswith("remote")


def _run_cover_resync(track_ids: list[str]) -> None:
    async def _resync_all() -> None:
        sem = asyncio.Semaphore(COVER_RESYNC_CONCURRENCY)

        async def _one(track_id: str) -> None:
            track = _tracks.get(track_id)
            updated = False
            if track is not None:
                try:
                    async with sem:
                        updated = await _resync_cover_track(track)
                except Exception:
                    updated = False
            with _cover_resync_lock:
                _cover_resync_state["done"] += 1
                if updated:
                    _cover_resync_state["updated"] += 1

        await asyncio.gather(*(_one(tid) for tid in track_ids))

    try:
        asyncio.run(_resync_all())
    finally:
        with _cover_resync_lock:
            _cover_resync_state["running"] = False


def _run_cover_refresh(track_ids: list[str]) -> None:
    """Re-read embedded covers into the disk cache. Never writes audio tags."""
    cache = covers_cache_dir()
    try:
        for tid in track_ids:
            track = _tracks.get(tid)
            status = "failed"
            if track is not None:
                try:
                    status = refresh_track_cover_cache(
                        Path(track.path),
                        cache,
                        artist=track.artist,
                        title=track.title,
                        duration=track.duration,
                        album=track.album,
                    )
                except Exception:
                    status = "failed"
            with _cover_refresh_lock:
                _cover_refresh_state["done"] += 1
                if status == "updated":
                    _cover_refresh_state["updated"] += 1
                elif status == "same":
                    _cover_refresh_state["same"] += 1
                elif status == "missing":
                    _cover_refresh_state["missing"] += 1
                elif status == "failed":
                    _cover_refresh_state["failed"] += 1
    finally:
        with _cover_refresh_lock:
            _cover_refresh_state["running"] = False


@app.post("/api/library/covers/refresh")
def refresh_library_covers() -> dict:
    """User-triggered re-read of embedded artwork into the cover cache."""
    global _cover_refresh_thread
    if _music_root is None:
        raise HTTPException(status_code=400, detail="Cap carpeta carregada")
    if not _tracks:
        _reload_library(_music_root, reset_probe=False)
    track_ids = [track.id for track in sorted(_tracks.values(), key=_sort_key)]
    with _cover_refresh_lock:
        if _cover_refresh_state["running"]:
            return dict(_cover_refresh_state)
        if _cover_refresh_thread is not None and _cover_refresh_thread.is_alive():
            return dict(_cover_refresh_state)
        if not track_ids:
            return {
                "running": False,
                "done": 0,
                "total": 0,
                "updated": 0,
                "same": 0,
                "missing": 0,
                "failed": 0,
            }
        _cover_refresh_state.update(
            {
                "running": True,
                "done": 0,
                "total": len(track_ids),
                "updated": 0,
                "same": 0,
                "missing": 0,
                "failed": 0,
            }
        )
        thread = threading.Thread(
            target=_run_cover_refresh,
            args=(track_ids,),
            daemon=True,
            name="cover-refresh",
        )
        _cover_refresh_thread = thread
        state = dict(_cover_refresh_state)
    thread.start()
    return state


@app.get("/api/library/covers")
def library_covers_state() -> dict:
    with _cover_refresh_lock:
        refresh = dict(_cover_refresh_state)
    with _cover_resync_lock:
        resync = dict(_cover_resync_state)
    return {"refresh": refresh, "resync": resync}


@app.post("/api/library/covers/resync")
def resync_library_covers() -> dict:
    """User-triggered force re-fetch of cover art for every scanned track."""
    global _cover_resync_thread
    if _music_root is None:
        raise HTTPException(status_code=400, detail="Cap carpeta carregada")
    if not _tracks:
        _reload_library(_music_root, reset_probe=False)
    track_ids = list(_tracks)
    with _cover_resync_lock:
        if _cover_resync_state["running"]:
            return dict(_cover_resync_state)
        if _cover_resync_thread is not None and _cover_resync_thread.is_alive():
            return dict(_cover_resync_state)
        if not track_ids:
            return {"running": False, "done": 0, "total": 0, "updated": 0}
        _cover_resync_state.update(
            {"running": True, "done": 0, "total": len(track_ids), "updated": 0}
        )
        thread = threading.Thread(
            target=_run_cover_resync,
            args=(track_ids,),
            daemon=True,
            name="cover-resync",
        )
        _cover_resync_thread = thread
        state = dict(_cover_resync_state)
    thread.start()
    return state


@app.post("/api/covers/resync")
async def resync_cover(body: ResyncCoverBody) -> dict:
    """Force re-fetch cover art for one song (overwrites on remote hit)."""
    track = _resolve_track(body.track_id)
    result = await resolve_cover(
        Path(track.path),
        artist=track.artist,
        title=track.title,
        album=track.album,
        duration=track.duration,
        cache_dir=covers_cache_dir(),
        generic_path=_generic_cover_path(),
        force=True,
    )
    return {
        "track_id": body.track_id,
        "source": result.source,
        "updated": result.source.startswith("remote"),
    }


@app.get("/api/cache")
def track_cache_status(track_id: str = Query(...)) -> dict:
    track = _resolve_track(track_id)
    return _track_cache_status(track)


@app.post("/api/cache/clear")
def clear_track_cache(body: TrackCacheBody) -> dict:
    track = _resolve_track(body.track_id)
    scopes = _normalize_cache_scopes(body.scopes)
    removed = _clear_track_cache(track, scopes)
    return {
        "track_id": track.id,
        "cleared": removed,
        "total": sum(removed.values()),
        "cache": _track_cache_status(track),
    }


def _clear_cache_tree(path: Path) -> int:
    """Delete every file under a cache directory. Returns how many were removed."""
    if not path.is_dir():
        return 0
    removed = 0
    for child in path.rglob("*"):
        if not child.is_file():
            continue
        try:
            child.unlink()
            removed += 1
        except OSError:
            continue
    return removed


@app.post("/api/cache/clear-all")
def clear_all_cache(body: TrackCacheBody | None = None) -> dict:
    """Wipe lyrics / Whisper / stems / cover / YouTube caches for the whole library."""
    from .track_cache import clear_all_tracks

    scopes = _normalize_cache_scopes(body.scopes if body else None)
    removed = clear_all_tracks(cache_dir(), scopes)
    if "lyrics" in scopes:
        _reset_probe_state()
    if "aligned" in scopes:
        with _align_lock:
            _align_jobs.clear()
            _align_queue.clear()
    if "stems" in scopes:
        # Scratch leftovers from Demucs live outside track folders.
        clear_work_dir()
        with _stem_lock:
            _stem_jobs.clear()
            _stem_queue.clear()
            _stem_bulk_state.update(
                {
                    "running": False,
                    "done": 0,
                    "total": 0,
                    "failed": 0,
                    "current": "",
                    "error": "",
                }
            )
    return {"cleared": removed, "total": sum(removed.values())}


@app.get("/api/cache/export")
def export_track_cache(track_id: str = Query(...)):
    """Download one song's cache folder as a zip (copy/paste between PCs)."""
    from .track_cache import export_track_zip, track_dir

    track = _resolve_track(track_id)
    key = cache_key(track.artist, track.title, track.duration)
    folder = track_dir(cache_dir(), key)
    if not folder.is_dir():
        raise HTTPException(status_code=404, detail="Aquesta cançó no té memòria cau")
    export_root = app_cache_root() / "exports"
    export_root.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^\w\-]+", "_", f"{track.artist}-{track.title}")[:80] or key[:12]
    destination = export_root / f"{safe_name}-{key[:10]}.zip"
    export_track_zip(cache_dir(), key, destination)
    return FileResponse(
        destination,
        filename=destination.name,
        media_type="application/zip",
    )


@app.post("/api/cache/import")
async def import_track_cache(file: UploadFile = File(...)) -> dict:
    """Import a previously exported song-cache zip into tracks/<key>/."""
    from .track_cache import import_track_zip, read_meta

    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Cal un fitxer .zip de cau")
    imports_root = app_cache_root() / "imports"
    imports_root.mkdir(parents=True, exist_ok=True)
    temp_path = imports_root / f"upload-{uuid.uuid4().hex}.zip"
    try:
        temp_path.write_bytes(await file.read())
        key = import_track_zip(cache_dir(), temp_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        try:
            temp_path.unlink()
        except OSError:
            pass
    meta = read_meta(cache_dir(), key) or {}
    return {"key": key, "meta": meta, "cache": track_status_for_key(key)}


def track_status_for_key(key: str) -> dict:
    from .track_cache import track_status

    return track_status(cache_dir(), key)


@app.post("/api/cache/resync")
def resync_track_cache(body: TrackCacheBody) -> dict:
    """Wipe song caches related to lyrics sync, then re-fetch and re-align."""
    track = _resolve_track(body.track_id)
    scopes = _normalize_cache_scopes(body.scopes)
    # Resync always refreshes lyrics + whisper path; keep optional cover/stems
    # when the client asked for a narrower wipe.
    scopes |= {"lyrics", "aligned"}
    removed = _clear_track_cache(track, scopes)

    align_job: dict | None = None
    if alignment_available() and separation_available():
        job_id = uuid.uuid4().hex
        _enqueue_align_job(job_id, track, body.language or "ca")
        align_job = {"job_id": job_id, "status": "queued", "progress": 0.0, "phase": "queued"}
    else:
        with _probe_lock:
            _probe_attempted.discard(track.id)
        _ensure_lyrics_probe(track_ids=[track.id])

    return {
        "track_id": track.id,
        "cleared": removed,
        "total": sum(removed.values()),
        "align": align_job,
        "cache": _track_cache_status(track),
    }


@app.get("/api/audio/{track_id:path}")
def audio(track_id: str, mode: str = Query("original")):
    track = _resolve_track(track_id)
    if mode == "instrumental":
        key = cache_key(track.artist, track.title, track.duration)
        path = instrumental_path(stems_cache_dir(), key)
        if not path.is_file():
            raise HTTPException(status_code=404, detail="Encara no hi ha pista instrumental")
        return FileResponse(path, filename=path.name, media_type="audio/mpeg")
    path = Path(track.path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Falta el fitxer d’àudio")
    return FileResponse(path, filename=path.name, media_type="audio/mpeg")


def _stem_state_payload(track: TrackInfo) -> dict:
    key = cache_key(track.artist, track.title, track.duration)
    return {
        "track_id": track.id,
        "ready": has_instrumental(stems_cache_dir(), key),
        "available": separation_available(),
        "model": model_name(),
    }


@app.get("/api/stems")
def stems_state(track_id: str = Query(...)) -> dict:
    track = _resolve_track(track_id)
    payload = _stem_state_payload(track)
    active = _active_stem_job(track.id)
    if active is not None:
        job_id, job = active
        payload.update({"job_id": job_id, **job})
    return payload


@app.post("/api/stems")
def start_stems(body: StemsBody) -> dict:
    track = _resolve_track(body.track_id)
    payload = _stem_state_payload(track)
    if payload["ready"]:
        return {"job_id": None, "status": "done", **payload}
    if not separation_available():
        return {
            "job_id": None,
            "status": "unavailable",
            "error": 'Instal·la la separació amb: pip install -e ".[stems]"',
            **payload,
        }

    active = _active_stem_job(track.id)
    if active is not None:
        job_id, job = active
        return {"job_id": job_id, **payload, **job}

    job_id = uuid.uuid4().hex
    # A song someone is waiting on jumps ahead of any bulk batch.
    _enqueue_stem_job(job_id, track, front=True)
    return {"job_id": job_id, "status": "queued", "progress": 0.0, "phase": "queued", **payload}


@app.get("/api/stems/{job_id}")
def stems_status(job_id: str) -> dict:
    with _stem_lock:
        job = _stem_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Treball de separació no trobat")
    return {"job_id": job_id, **job}


@app.post("/api/library/stems/generate")
def generate_library_stems() -> dict:
    if _music_root is None:
        raise HTTPException(status_code=400, detail="Cap carpeta de música seleccionada")
    if not separation_available():
        raise HTTPException(
            status_code=400,
            detail='Instal·la la separació amb: pip install -e ".[stems]"',
        )
    snapshot = _library_snapshot()
    stems_path = stems_cache_dir()
    pending: list[TrackInfo] = []
    for item in snapshot.get("tracks") or []:
        track = _tracks.get(item["id"])
        if track is None:
            continue
        key = cache_key(track.artist, track.title, track.duration)
        if has_instrumental(stems_path, key):
            continue
        if _active_stem_job(track.id) is not None:
            continue
        pending.append(track)

    if not pending:
        return {"queued": 0, "running": False}

    with _stem_lock:
        if _stem_bulk_state["running"]:
            _stem_bulk_state["total"] += len(pending)
        else:
            _stem_bulk_state.update(
                {
                    "running": True,
                    "done": 0,
                    "total": len(pending),
                    "failed": 0,
                    "current": "",
                    "error": "",
                }
            )
    for track in pending:
        _enqueue_stem_job(None, track)
    return {"queued": len(pending), "running": True}


@app.get("/api/library/stems")
def library_stems_state() -> dict:
    with _stem_lock:
        state = dict(_stem_bulk_state)
        state["queued"] = len(_stem_queue)
    state["available"] = separation_available()
    state["model"] = model_name()
    return state


@app.get("/api/cover/{track_id:path}")
async def cover(track_id: str):
    track = _resolve_track(track_id)
    result = await resolve_cover(
        Path(track.path),
        artist=track.artist,
        title=track.title,
        album=track.album,
        duration=track.duration,
        cache_dir=covers_cache_dir(),
        generic_path=_generic_cover_path(),
    )
    if not result.path.is_file():
        raise HTTPException(status_code=404, detail="Portada no trobada")
    return FileResponse(
        result.path,
        media_type=result.mime,
        headers={"Cache-Control": "public, max-age=86400", "X-Cover-Source": result.source},
    )


@app.get("/api/lyrics")
async def lyrics(track_id: str = Query(...)):
    track = _resolve_track(track_id)
    key = cache_key(track.artist, track.title, track.duration)
    aligned = load_aligned_cached(aligned_cache_dir(), key)
    if aligned is not None:
        aligned = _with_audio_syllables(key, aligned)
        return _lyrics_response(track, track_id, aligned, aligned=True)

    payload = await fetch_lyrics(
        artist=track.artist,
        title=track.title,
        album=track.album,
        duration=track.duration,
        cache_dir=cache_dir(),
        audio_path=track.path,
    )
    return _lyrics_response(track, track_id, payload, aligned=False)


@app.get("/api/lyrics/local")
def local_lyrics(track_id: str = Query(...)) -> dict:
    """Lyrics stored on the audio file (sidecar or tags) for the editor."""
    track = _resolve_track(track_id)
    payload = read_local_lyrics(track.path)
    if payload is None:
        cached = load_cached(
            cache_dir(), cache_key(track.artist, track.title, track.duration)
        )
        if cached is not None and cached.lines:
            maybe_embed_lyrics(track.path, cached)
            payload = read_local_lyrics(track.path)
    return {
        "track_id": track_id,
        "title": track.title,
        "artist": track.artist,
        "source": payload.source if payload else "",
        "synced": bool(payload and payload.synced),
        "text": payload_to_text(payload),
    }


@app.post("/api/rating")
def save_rating(body: RatingBody) -> dict:
    """Set or clear the 0–5 star rating for a song (0 removes it)."""
    try:
        rating = normalize_rating(body.rating)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    track = _resolve_track(body.track_id)
    key = cache_key(track.artist, track.title, track.duration)
    stored = set_rating(key, rating)
    return {"track_id": track.id, "rating": stored}


@app.post("/api/lyrics")
def save_lyrics(body: SaveLyricsBody) -> dict:
    """Store pasted lyrics on the audio file and drop stale Whisper alignment."""
    track = _resolve_track(body.track_id)
    try:
        payload = save_manual_lyrics(
            cache_dir(),
            artist=track.artist,
            title=track.title,
            album=track.album,
            duration=track.duration,
            text=body.text,
            aligned_cache=aligned_cache_dir(),
            audio_path=track.path,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _lyrics_response(track, body.track_id, payload, aligned=False)


@app.get("/api/youtube")
async def youtube_clip(track_id: str = Query(...)):
    """Muted stage-background clip id for this song (cached per track)."""
    from .youtube import resolve_youtube_clip

    track = _resolve_track(track_id)
    return await asyncio.to_thread(
        resolve_youtube_clip,
        path=Path(track.path),
        artist=track.artist,
        title=track.title,
        duration=track.duration,
        album=track.album,
        cache_dir=cache_dir(),
    )


def _youtube_bulk_payload() -> dict:
    with _youtube_bulk_lock:
        return dict(_youtube_bulk_state)


def _run_youtube_bulk(track_ids: list[str]) -> None:
    from .youtube import resolve_youtube_clip

    root = cache_dir()
    try:
        for track_id in track_ids:
            track = _tracks.get(track_id)
            if track is None:
                with _youtube_bulk_lock:
                    _youtube_bulk_state["done"] += 1
                    _youtube_bulk_state["missed"] += 1
                continue
            label = f"{track.artist or 'Desconegut'} — {track.title or track.id}"
            with _youtube_bulk_lock:
                _youtube_bulk_state["current"] = label
            try:
                payload = resolve_youtube_clip(
                    path=Path(track.path),
                    artist=track.artist,
                    title=track.title,
                    duration=track.duration,
                    album=track.album,
                    cache_dir=root,
                    force=True,
                )
            except Exception as exc:
                log.exception("YouTube bulk failed for %s", label)
                with _youtube_bulk_lock:
                    _youtube_bulk_state["done"] += 1
                    _youtube_bulk_state["errors"] += 1
                    _youtube_bulk_state["error"] = str(exc)
                continue
            with _youtube_bulk_lock:
                _youtube_bulk_state["done"] += 1
                if payload.get("found") and payload.get("video_id"):
                    _youtube_bulk_state["found"] += 1
                elif payload.get("source") in {"error", "unavailable"}:
                    _youtube_bulk_state["errors"] += 1
                    _youtube_bulk_state["error"] = str(payload.get("source") or "error")
                else:
                    _youtube_bulk_state["missed"] += 1
    finally:
        with _youtube_bulk_lock:
            _youtube_bulk_state["running"] = False
            _youtube_bulk_state["current"] = ""


@app.post("/api/library/youtube/search")
def search_library_youtube(body: YoutubeSearchBody | None = None) -> dict:
    """Search YouTube clips one by one.

    scope=missing: skip songs that already have a cached hit.
    scope=all: re-search every track and overwrite cached clips.
    """
    global _youtube_bulk_thread
    from .youtube import has_youtube_hit, search_available, youtube_enabled

    if _music_root is None:
        raise HTTPException(status_code=400, detail="Cap carpeta de música seleccionada")
    if not youtube_enabled():
        raise HTTPException(
            status_code=400,
            detail="Cerca de videoclips desactivada (KARAOKE_YOUTUBE=0)",
        )
    if not search_available():
        raise HTTPException(status_code=400, detail="Falta yt-dlp · pip install -e .")
    if not _tracks:
        _reload_library(_music_root, reset_probe=False)

    scope = (body.scope if body else "missing") or "missing"
    if scope not in {"all", "missing"}:
        raise HTTPException(status_code=400, detail="scope ha de ser 'all' o 'missing'")

    with _youtube_bulk_lock:
        if _youtube_bulk_state["running"]:
            return dict(_youtube_bulk_state)
        if _youtube_bulk_thread is not None and _youtube_bulk_thread.is_alive():
            return dict(_youtube_bulk_state)

    root = cache_dir()
    pending: list[TrackInfo] = []
    skipped = 0
    for track in sorted(_tracks.values(), key=_sort_key):
        if scope == "missing" and has_youtube_hit(
            root, track.artist, track.title, track.duration
        ):
            skipped += 1
            continue
        pending.append(track)

    if not pending:
        return {
            "running": False,
            "queued": 0,
            "done": 0,
            "total": 0,
            "found": 0,
            "skipped": skipped,
            "missed": 0,
            "errors": 0,
            "current": "",
            "error": "",
            "scope": scope,
        }

    with _youtube_bulk_lock:
        _youtube_bulk_state.update(
            {
                "running": True,
                "done": 0,
                "total": len(pending),
                "found": 0,
                "skipped": skipped,
                "missed": 0,
                "errors": 0,
                "current": "",
                "error": "",
                "scope": scope,
            }
        )
        thread = threading.Thread(
            target=_run_youtube_bulk,
            args=([track.id for track in pending],),
            daemon=True,
            name="youtube-bulk",
        )
        _youtube_bulk_thread = thread
        state = dict(_youtube_bulk_state)
        state["queued"] = len(pending)
    thread.start()
    return state


@app.get("/api/library/youtube")
def library_youtube_state() -> dict:
    from .youtube import search_available, youtube_enabled

    state = _youtube_bulk_payload()
    state["available"] = search_available() and youtube_enabled()
    return state


@app.post("/api/align")
def start_align(body: AlignBody) -> dict:
    track = _resolve_track(body.track_id)
    key = cache_key(track.artist, track.title, track.duration)
    cached = load_aligned_cached(aligned_cache_dir(), key)
    if cached is not None:
        cached = _with_audio_syllables(key, cached)
        return {"job_id": None, **_align_done_payload(cached)}

    if not alignment_available():
        return {
            "job_id": None,
            "status": "unavailable",
            "error": 'Instal·la l’alineació amb: pip install -e ".[align]"',
        }

    if not separation_available():
        return {
            "job_id": None,
            "status": "unavailable",
            "error": 'Whisper necessita la separació de pistes · pip install -e ".[stems]"',
        }

    whisper = whisper_model_status()
    if whisper.get("error") and not whisper.get("ready") and not whisper.get("loading"):
        return {
            "job_id": None,
            "status": "unavailable",
            "error": whisper.get("error") or "El model Whisper no s’ha pogut carregar",
        }

    # Reuse an in-flight / queued job for the same track.
    with _align_lock:
        for existing_id, job in _align_jobs.items():
            if job.get("track_id") != track.id:
                continue
            if job.get("status") in {"queued", "running"}:
                return {
                    "job_id": existing_id,
                    "status": job.get("status") or "running",
                    "progress": job.get("progress", 0.0),
                    "phase": job.get("phase"),
                }

    job_id = uuid.uuid4().hex
    _enqueue_align_job(job_id, track, body.language or "ca")
    return {"job_id": job_id, "status": "queued", "progress": 0.0, "phase": "queued"}


@app.get("/api/align/{job_id}")
def align_status(job_id: str) -> dict:
    with _align_lock:
        job = _align_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Treball d’alineació no trobat")
    return {"job_id": job_id, **job}


@app.post("/api/video")
def start_video(body: VideoBody) -> dict:
    track = _resolve_track(body.track_id)
    layout = "dual" if body.lyrics_layout == "dual" else "stack"
    language = body.language or "ca"
    key = cache_key(track.artist, track.title, track.duration)

    if not ffmpeg_available():
        return {
            "job_id": None,
            "status": "unavailable",
            "error": "Cal ffmpeg per crear el vídeo karaoke",
        }

    existing = karaoke_is_current(aligned_cache_dir(), key)
    if existing is not None and load_aligned_cached(aligned_cache_dir(), key) is not None:
        job_id = uuid.uuid4().hex
        stored = {
            "status": "done",
            "phase": "done",
            "progress": 1.0,
            "track_id": track.id,
            "filename": download_filename(track.artist, track.title),
            "_path": str(existing),
        }
        with _video_lock:
            _video_jobs[job_id] = stored
        return _public_video_job(job_id, stored)

    with _video_lock:
        for existing_id, job in _video_jobs.items():
            if job.get("track_id") != track.id:
                continue
            if job.get("status") in {"queued", "running", "ready"}:
                return _public_video_job(existing_id, dict(job))

    job_id = uuid.uuid4().hex
    _enqueue_video_job(job_id, track, language, layout)
    with _video_lock:
        job = dict(_video_jobs[job_id])
    return _public_video_job(job_id, job)


@app.get("/api/video/{job_id}")
def video_status(job_id: str) -> dict:
    with _video_lock:
        job = _video_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Treball de vídeo no trobat")
    return _public_video_job(job_id, job)


@app.get("/api/video/{job_id}/file")
def video_file(job_id: str):
    with _video_lock:
        job = _video_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Treball de vídeo no trobat")
    if job.get("status") != "done":
        raise HTTPException(status_code=409, detail="El vídeo encara no està a punt")
    path = Path(str(job.get("_path") or ""))
    if not path.is_file():
        raise HTTPException(status_code=404, detail="No s’ha trobat el fitxer MP4")
    name = str(job.get("filename") or path.name)
    return FileResponse(path, filename=name, media_type="video/mp4")


@app.post("/api/video/upload")
async def upload_stage_video(
    track_id: str = Query(...),
    file: UploadFile = File(...),
) -> dict:
    """Accept a browser capture of the live stage and mux it with original audio."""
    from .track_cache import karaoke_path

    track = _resolve_track(track_id)
    key = cache_key(track.artist, track.title, track.duration)
    if load_aligned_cached(aligned_cache_dir(), key) is None:
        raise HTTPException(status_code=409, detail="Cal sincronitzar la lletra abans de gravar")
    if not ffmpeg_available():
        raise HTTPException(status_code=400, detail="Cal ffmpeg per crear el vídeo karaoke")

    suffix = Path(file.filename or "stage.webm").suffix.lower()
    if suffix not in {".h264", ".webm", ".mp4", ".mkv"}:
        suffix = ".webm"
    work_root = app_cache_root() / "video-work"
    work_root.mkdir(parents=True, exist_ok=True)
    rec_path = work_root / f"stage-{uuid.uuid4().hex}{suffix}"
    output = karaoke_path(aligned_cache_dir(), key)
    try:
        rec_path.write_bytes(await file.read())
        if rec_path.stat().st_size <= 0:
            raise HTTPException(status_code=400, detail="La gravació de l’escenari és buida")
        mux_stage_recording(
            video_path=rec_path,
            audio_path=Path(track.path),
            output_path=output,
            duration=float(track.duration) or 0.0,
        )
        mark_karaoke_exported(aligned_cache_dir(), key)
    except HTTPException:
        raise
    except VideoRenderError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        try:
            rec_path.unlink()
        except OSError:
            pass

    job_id = uuid.uuid4().hex
    filename = download_filename(track.artist, track.title)
    stored = {
        "status": "done",
        "phase": "done",
        "progress": 1.0,
        "track_id": track.id,
        "filename": filename,
        "_path": str(output),
    }
    with _video_lock:
        _video_jobs[job_id] = stored
    return _public_video_job(job_id, stored)


@app.middleware("http")
async def _no_store_for_ui(request, call_next):
    """Never let a browser keep an old app.js: it used to poll every 2s."""
    response = await call_next(request)
    path = request.url.path
    if path.endswith((".js", ".css", ".html")) or path == "/":
        response.headers["Cache-Control"] = "no-store, max-age=0"
    # HTTP localhost → HTTPS YouTube. strict-origin-when-cross-origin omits
    # Referer on that hop, and the embed then shows "video no disponible" (153).
    response.headers["Referrer-Policy"] = "origin"
    return response


if WEB_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")


def main() -> None:
    parser = argparse.ArgumentParser(description="Karaoke Party local web server")
    parser.add_argument("--music", type=Path, help="Music library folder")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the app in the default browser",
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Do not abort when Whisper/stems/torchaudio/ffmpeg are missing (dev only)",
    )
    args = parser.parse_args()
    if not args.skip_deps:
        require_dependencies()
    if args.music:
        _reload_library(args.music)
    elif _music_root is not None:
        _reload_library(_music_root)

    url = f"http://{args.host}:{args.port}"
    if args.open:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()

    # String import breaks under PyInstaller; pass the app object instead.
    uvicorn.run(app, host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
