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

from .align import align_lyrics, alignment_available
from .config import DEFAULT_PORT, aligned_cache_dir, cache_dir, default_music_root
from .covers import covers_cache_dir, resolve_cover
from .library import TrackInfo, scan_library
from .lyrics import (
    LyricsPayload,
    cache_key,
    fetch_lyrics,
    load_aligned_cached,
    lyrics_status_cached,
    save_aligned_cached,
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
_probe_lock = threading.Lock()
_probe_state: dict = {
    "running": False,
    "done": 0,
    "total": 0,
    "found": 0,
}


class SetRootBody(BaseModel):
    path: str


class AlignBody(BaseModel):
    track_id: str
    language: str = "ca"


def _reload_library(root: Path) -> list[TrackInfo]:
    global _music_root, _tracks
    _music_root = root
    tracks = scan_library(root)
    _tracks = {track.id: track for track in tracks}
    return tracks


def _resolve_track(track_id: str) -> TrackInfo:
    track = _tracks.get(track_id)
    if track is None and _music_root is not None:
        _reload_library(_music_root)
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


def _run_align_job(job_id: str, track: TrackInfo, language: str) -> None:
    key = cache_key(track.artist, track.title, track.duration)
    try:
        payload = asyncio.run(
            fetch_lyrics(
                artist=track.artist,
                title=track.title,
                album=track.album,
                duration=track.duration,
                cache_dir=cache_dir(Path.cwd()),
            )
        )
        if not payload.lines:
            with _align_lock:
                _align_jobs[job_id] = {"status": "error", "error": "No hi ha lletra per alinear"}
            return

        aligned_lines = align_lyrics(Path(track.path), payload.lines, language=language)
        aligned_payload = LyricsPayload(
            synced=True,
            source="whisper-align",
            lines=aligned_lines,
            plain=payload.plain,
        )
        save_aligned_cached(aligned_cache_dir(Path.cwd()), key, aligned_payload)
        with _align_lock:
            _align_jobs[job_id] = _align_done_payload(aligned_payload)
    except Exception as exc:  # noqa: BLE001 — surface to client poll
        with _align_lock:
            _align_jobs[job_id] = {"status": "error", "error": str(exc)}


def _library_snapshot() -> dict:
    if _music_root is None:
        return {"root": None, "tracks": [], "total": 0, "with_lyrics": 0, "pending": 0, "hidden": 0}

    if not _tracks:
        _reload_library(_music_root)

    lyrics_path = cache_dir(Path.cwd())
    aligned_path = aligned_cache_dir(Path.cwd())
    playable: list[dict] = []
    pending = 0
    hidden = 0
    for track in _tracks.values():
        status = lyrics_status_cached(
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
        else:
            pending += 1

    return {
        "root": str(_music_root),
        "tracks": playable,
        "total": len(_tracks),
        "with_lyrics": len(playable),
        "pending": pending,
        "hidden": hidden,
        "probe": dict(_probe_state),
    }


def _run_lyrics_probe(track_ids: list[str]) -> None:
    lyrics_path = cache_dir(Path.cwd())
    with _probe_lock:
        _probe_state.update({"running": True, "done": 0, "total": len(track_ids), "found": 0})

    async def _probe_one(track: TrackInfo) -> bool:
        payload = await fetch_lyrics(
            artist=track.artist,
            title=track.title,
            album=track.album,
            duration=track.duration,
            cache_dir=lyrics_path,
        )
        return bool(payload.lines)

    async def _probe_all() -> None:
        semaphore = asyncio.Semaphore(6)

        async def worker(track: TrackInfo) -> None:
            async with semaphore:
                try:
                    found = await _probe_one(track)
                except Exception:  # noqa: BLE001
                    found = False
            with _probe_lock:
                _probe_state["done"] += 1
                if found:
                    _probe_state["found"] += 1

        await asyncio.gather(*(worker(_tracks[tid]) for tid in track_ids if tid in _tracks))

    try:
        asyncio.run(_probe_all())
    finally:
        with _probe_lock:
            _probe_state["running"] = False


def _ensure_lyrics_probe() -> None:
    if _music_root is None:
        return
    if not _tracks:
        _reload_library(_music_root)

    lyrics_path = cache_dir(Path.cwd())
    aligned_path = aligned_cache_dir(Path.cwd())
    unknown = [
        track.id
        for track in _tracks.values()
        if lyrics_status_cached(
            track.artist,
            track.title,
            track.duration,
            lyrics_cache=lyrics_path,
            aligned_cache=aligned_path,
        )
        is None
    ]
    if not unknown:
        return
    with _probe_lock:
        if _probe_state["running"]:
            return
    thread = threading.Thread(target=_run_lyrics_probe, args=(unknown,), daemon=True)
    thread.start()


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "music_root": str(_music_root) if _music_root else None,
        "tracks": len(_tracks),
        "alignment": alignment_available(),
    }


@app.get("/api/library")
def library() -> dict:
    snapshot = _library_snapshot()
    if snapshot.get("pending"):
        _ensure_lyrics_probe()
    return snapshot


@app.post("/api/library/root")
def set_root(body: SetRootBody) -> dict:
    root = Path(body.path)
    if not root.is_dir():
        raise HTTPException(status_code=400, detail="La carpeta no existeix")
    tracks = _reload_library(root)
    _ensure_lyrics_probe()
    return {"root": str(root), "tracks": len(tracks)}


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
        cache_dir=covers_cache_dir(Path.cwd()),
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
    aligned = load_aligned_cached(aligned_cache_dir(Path.cwd()), key)
    if aligned is not None:
        return _lyrics_response(track, track_id, aligned, aligned=True)

    payload = await fetch_lyrics(
        artist=track.artist,
        title=track.title,
        album=track.album,
        duration=track.duration,
        cache_dir=cache_dir(Path.cwd()),
    )
    return _lyrics_response(track, track_id, payload, aligned=False)


@app.post("/api/align")
def start_align(body: AlignBody) -> dict:
    track = _resolve_track(body.track_id)
    key = cache_key(track.artist, track.title, track.duration)
    cached = load_aligned_cached(aligned_cache_dir(Path.cwd()), key)
    if cached is not None:
        return {"job_id": None, **_align_done_payload(cached)}

    if not alignment_available():
        return {
            "job_id": None,
            "status": "unavailable",
            "error": 'Instal·la l’alineació amb: pip install -e ".[align]"',
        }

    job_id = uuid.uuid4().hex
    with _align_lock:
        _align_jobs[job_id] = {"status": "running"}
    thread = threading.Thread(
        target=_run_align_job,
        args=(job_id, track, body.language or "ca"),
        daemon=True,
    )
    thread.start()
    return {"job_id": job_id, "status": "running"}


@app.get("/api/align/{job_id}")
def align_status(job_id: str) -> dict:
    with _align_lock:
        job = _align_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Treball d’alineació no trobat")
    return {"job_id": job_id, **job}


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
