from __future__ import annotations

import argparse
import asyncio
import sys
import threading
import uuid
import webbrowser
from dataclasses import asdict
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import __version__
from .align import align_lyrics, alignment_available
from .config import DEFAULT_PORT, aligned_cache_dir, cache_dir, default_music_root
from .covers import covers_cache_dir, resolve_cover
from .library import TrackInfo, scan_library
from .lyrics import (
    PROBE_ERROR_SOURCE,
    PROBE_TIMEOUT,
    LyricsPayload,
    LyricsUnavailable,
    cache_key,
    clear_probe_errors,
    fetch_lyrics,
    load_aligned_cached,
    lyrics_status_and_source,
    save_aligned_cached,
    save_cached,
)


def _project_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


WEB_DIR = _project_root() / "web"

app = FastAPI(title="Karaoke Party")
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


class SetRootBody(BaseModel):
    path: str


class AlignBody(BaseModel):
    track_id: str
    language: str = "ca"


def _reset_probe_state() -> None:
    global _probe_pass_complete, _probe_generation
    with _probe_lock:
        _probe_generation += 1
        _probe_attempted.clear()
        _probe_pass_complete = False
        _probe_state.update(
            {"running": False, "done": 0, "total": 0, "found": 0, "offline": False}
        )


def _reload_library(root: Path, *, reset_probe: bool | None = None) -> list[TrackInfo]:
    """Rescan music files. Probe state resets only when the root folder changes."""
    global _music_root, _tracks
    new_root = root.expanduser().resolve()
    old_root = _music_root.resolve() if _music_root is not None else None
    root_changed = old_root is None or new_root != old_root
    _music_root = new_root
    tracks = scan_library(new_root)
    _tracks = {track.id: track for track in tracks}
    if reset_probe if reset_probe is not None else root_changed:
        _reset_probe_state()
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


def _lyrics_response(track: TrackInfo, track_id: str, payload: LyricsPayload, *, aligned: bool) -> dict:
    return {
        "track_id": track_id,
        "title": track.title,
        "artist": track.artist,
        "synced": payload.synced,
        "aligned": aligned,
        "source": payload.source,
        "plain": payload.plain,
        "lines": [asdict(line) for line in payload.lines],
    }


def _align_done_payload(payload: LyricsPayload) -> dict:
    return {
        "status": "done",
        "aligned": True,
        "synced": True,
        "source": payload.source,
        "plain": payload.plain,
        "lines": [asdict(line) for line in payload.lines],
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
            )
        )
        if not payload.lines:
            _set_align_job(job_id, status="error", error="No hi ha lletra per alinear", progress=0.0)
            return

        def on_progress(ratio: float) -> None:
            _set_align_job(job_id, status="running", progress=round(float(ratio), 3), phase="whisper")

        _set_align_job(job_id, status="running", progress=0.0, phase="whisper")
        aligned_lines = align_lyrics(
            Path(track.path),
            payload.lines,
            language=language,
            on_progress=on_progress,
        )
        aligned_payload = LyricsPayload(
            synced=True,
            source="whisper-align",
            lines=aligned_lines,
            plain=payload.plain,
        )
        save_aligned_cached(aligned_cache_dir(), key, aligned_payload)
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


def _library_snapshot() -> dict:
    if _music_root is None:
        return {
            "root": None,
            "tracks": [],
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
    playable: list[dict] = []
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
        )
        if status is True:
            item = asdict(track)
            key = cache_key(track.artist, track.title, track.duration)
            item["whisper_aligned"] = load_aligned_cached(aligned_path, key) is not None
            playable.append(item)
        elif status is False:
            hidden += 1
            if source == PROBE_ERROR_SOURCE:
                errors += 1
        elif track.id in _probe_attempted:
            # Soft-fail this session (network/API error): do not keep it pending.
            hidden += 1
            errors += 1
        else:
            pending += 1

    with _probe_lock:
        probe = dict(_probe_state)
    return {
        "root": str(_music_root),
        "tracks": playable,
        "total": len(_tracks),
        "with_lyrics": len(playable),
        "pending": pending,
        "hidden": hidden,
        "errors": errors,
        "probe": probe,
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


def _ensure_lyrics_probe() -> None:
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
        if _probe_pass_complete:
            return
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


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "version": __version__,
        "music_root": str(_music_root) if _music_root else None,
        "tracks": len(_tracks),
        "cache": str(cache_dir()),
        "alignment": alignment_available(),
    }


@app.get("/api/library")
def library() -> dict:
    if _library_snapshot().get("pending"):
        _ensure_lyrics_probe()
    return _library_snapshot()


@app.post("/api/library/root")
def set_root(body: SetRootBody) -> dict:
    root = Path(body.path)
    if not root.is_dir():
        raise HTTPException(status_code=400, detail="La carpeta no existeix")
    # Only reset the probe when the folder actually changes (same path must not
    # kill an in-flight pass and start another from 0/N).
    tracks = _reload_library(root)
    _ensure_lyrics_probe()
    return {"root": str(root), "tracks": len(tracks)}


@app.post("/api/library/retry")
def retry_failed_lyrics() -> dict:
    """User-triggered retry for songs whose lookup failed (never automatic)."""
    if _music_root is None:
        raise HTTPException(status_code=400, detail="Cap carpeta carregada")
    cleared = clear_probe_errors(cache_dir())
    _reset_probe_state()
    _ensure_lyrics_probe()
    return {"cleared": cleared}


@app.get("/api/audio/{track_id:path}")
def audio(track_id: str):
    track = _resolve_track(track_id)
    path = Path(track.path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Falta el fitxer d’àudio")
    return FileResponse(path, filename=path.name, media_type="audio/mpeg")


@app.get("/api/cover/{track_id:path}")
async def cover(track_id: str):
    track = _resolve_track(track_id)
    generic = WEB_DIR / "album-generic.png"
    result = await resolve_cover(
        Path(track.path),
        artist=track.artist,
        title=track.title,
        album=track.album,
        cache_dir=covers_cache_dir(),
        generic_path=generic if generic.is_file() else WEB_DIR / "album-generic.png",
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
        return _lyrics_response(track, track_id, aligned, aligned=True)

    payload = await fetch_lyrics(
        artist=track.artist,
        title=track.title,
        album=track.album,
        duration=track.duration,
        cache_dir=cache_dir(),
    )
    return _lyrics_response(track, track_id, payload, aligned=False)


@app.post("/api/align")
def start_align(body: AlignBody) -> dict:
    track = _resolve_track(body.track_id)
    key = cache_key(track.artist, track.title, track.duration)
    cached = load_aligned_cached(aligned_cache_dir(), key)
    if cached is not None:
        return {"job_id": None, **_align_done_payload(cached)}

    if not alignment_available():
        return {
            "job_id": None,
            "status": "unavailable",
            "error": 'Instal·la l’alineació amb: pip install -e ".[align]"',
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


@app.middleware("http")
async def _no_store_for_ui(request, call_next):
    """Never let a browser keep an old app.js: it used to poll every 2s."""
    response = await call_next(request)
    path = request.url.path
    if path.endswith((".js", ".css", ".html")) or path == "/":
        response.headers["Cache-Control"] = "no-store, max-age=0"
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
    args = parser.parse_args()
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
