"""Catalog and YouTube download sections inside Karaoke Party."""

from __future__ import annotations

import base64
import logging
import threading
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Literal

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

log = logging.getLogger("karaoke_party.studio")

router = APIRouter(prefix="/api/studio", tags=["studio"])

_root_getter: Callable[[], Path | None] = lambda: None
_reload_library: Callable[[Path], None] | None = None

_lock = threading.Lock()
_catalog_jobs: dict[str, dict[str, Any]] = {}
_download_jobs: dict[str, dict[str, Any]] = {}

_MAX_TRACKS = 5000
_MAX_COVER_BYTES = 8 * 1024 * 1024
_AUDIO_VIDEO = {".mp3", ".m4a", ".flac", ".ogg", ".wav", ".aac", ".opus", ".wma", ".mp4", ".mkv", ".webm"}


def bind_library(*, root_getter: Callable[[], Path | None], reload_library: Callable[[Path], None]) -> None:
    global _root_getter, _reload_library
    _root_getter = root_getter
    _reload_library = reload_library


def _library_root() -> Path | None:
    root = _root_getter()
    if root is None:
        return None
    try:
        return Path(root).expanduser().resolve()
    except OSError:
        return None


def _maybe_reload(root: Path) -> None:
    current = _library_root()
    if _reload_library is None or current is None:
        return
    if current == root.resolve():
        try:
            _reload_library(root)
        except Exception:
            log.exception("library reload failed")


def _library_folder() -> Path:
    """The catalog always uses the karaoke library. It is not a separate folder."""
    folder = _library_root()
    if folder is None or not folder.is_dir():
        raise HTTPException(status_code=400, detail="Encara no hi ha carpeta de karaoke")
    return folder


def _safe_child(root: Path, rel: str) -> Path:
    text = (rel or "").replace("\\", "/").strip().lstrip("/")
    if not text or ":" in text:
        raise HTTPException(status_code=400, detail="Ruta no vàlida")
    parts = Path(text).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise HTTPException(status_code=400, detail="Ruta no vàlida")
    candidate = (root / text).resolve()
    if candidate != root and root not in candidate.parents:
        raise HTTPException(status_code=400, detail="Ruta fora de la carpeta")
    return candidate


def _catalog_modules():
    try:
        from music_cataloger.acoustid_client import resolve_fpcalc
        from music_cataloger.config import CatalogerConfig
        from music_cataloger.covers import (
            extract_embedded_cover,
            fetch_itunes_cover,
            remove_embedded_cover,
            write_embedded_cover,
        )
        from music_cataloger.editor import is_incomplete, rename_to_filename, tags_to_candidate
        from music_cataloger.settings import load_settings, save_settings
        from music_cataloger.tagger import FileResult, MusicCataloger
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"El catàleg no està disponible ({exc}). Instal·la les dependències amb pip install -e .",
        ) from exc
    return {
        "CatalogerConfig": CatalogerConfig,
        "MusicCataloger": MusicCataloger,
        "FileResult": FileResult,
        "extract_embedded_cover": extract_embedded_cover,
        "fetch_itunes_cover": fetch_itunes_cover,
        "write_embedded_cover": write_embedded_cover,
        "remove_embedded_cover": remove_embedded_cover,
        "is_incomplete": is_incomplete,
        "rename_to_filename": rename_to_filename,
        "tags_to_candidate": tags_to_candidate,
        "load_settings": load_settings,
        "save_settings": save_settings,
        "resolve_fpcalc": resolve_fpcalc,
    }


class CatalogRunBody(BaseModel):
    write: bool = False
    rename_files: bool = False
    use_musicbrainz: bool = True
    use_acoustid: bool = False
    only_incomplete: bool = False
    ignore_existing_tags: bool = False
    artist: str = ""
    limit: int = 0


class CatalogSettingsBody(BaseModel):
    acoustid_api_key: str | None = None


class SaveRow(BaseModel):
    rel: str
    title: str = ""
    artist: str = ""
    album: str = ""
    date: str = ""
    track: str = ""
    albumartist: str = ""
    file: str = ""
    cover_action: str = ""
    cover_b64: str = ""
    cover_mime: str = ""


class CatalogSaveBody(BaseModel):
    rename: bool = False
    rows: list[SaveRow] = Field(default_factory=list)


class CoverSearchBody(BaseModel):
    artist: str = ""
    title: str = ""
    album: str = ""


class DownloadBody(BaseModel):
    url: str = Field(min_length=1)
    mode: Literal["audio", "video"] = "audio"
    quality: str = "best"
    kind: Literal["auto", "single", "playlist"] = "auto"
    destination: Literal["library", "downloads"] = "library"


class YtSettingsBody(BaseModel):
    cookies_browser: str | None = None
    cookies_file: str | None = None


def _public_file_result(row: Any) -> dict[str, Any]:
    data = asdict(row)
    notes = data.get("notes") or []
    data["notes"] = [str(note) for note in notes[:8]]
    return data


def _snapshot_catalog(job_id: str) -> dict[str, Any]:
    with _lock:
        job = dict(_catalog_jobs.get(job_id) or {})
    if not job:
        raise HTTPException(status_code=404, detail="Tasca no trobada")
    job.pop("_lock", None)
    return job


@router.get("/catalog/settings")
def catalog_settings() -> dict[str, Any]:
    mods = _catalog_modules()
    stored = mods["load_settings"]()
    key = str(stored.get("acoustid_api_key") or "")
    hint = ""
    if len(key) >= 8:
        hint = f"{key[:4]}…{key[-4:]}"
    elif key:
        hint = "••••"
    fpcalc = mods["resolve_fpcalc"]()
    root = _library_root()
    return {
        "root": str(root) if root else "",
        "acoustid_configured": bool(key.strip()),
        "acoustid_key_hint": hint,
        "fpcalc": str(fpcalc) if fpcalc else "",
        "fpcalc_ready": fpcalc is not None,
    }


@router.put("/catalog/settings")
def put_catalog_settings(body: CatalogSettingsBody) -> dict[str, Any]:
    mods = _catalog_modules()
    if body.acoustid_api_key is not None:
        mods["save_settings"]({"acoustid_api_key": body.acoustid_api_key.strip()})
    return catalog_settings()


@router.get("/catalog/tracks")
def catalog_tracks() -> dict[str, Any]:
    folder = _library_folder()
    from .library import scan_library

    mods = _catalog_modules()
    cataloger = mods["MusicCataloger"](mods["CatalogerConfig"](root=folder, use_musicbrainz=False, use_acoustid=False))
    rows: list[dict[str, Any]] = []
    truncated = False
    for track in scan_library(folder):
        if len(rows) >= _MAX_TRACKS:
            truncated = True
            break
        path = Path(track.path)
        try:
            tags = cataloger.read_existing(path)
        except Exception:
            tags = {}
        title = tags.get("title") or track.title
        artist = tags.get("artist") or track.artist
        album = tags.get("album") or track.album
        date = tags.get("date") or (str(track.year) if track.year else "")
        number = tags.get("track") or (str(track.track) if track.track else "")
        merged = {
            "title": title,
            "artist": artist,
            "album": album,
            "date": date,
            "track": number,
            "albumartist": tags.get("albumartist", ""),
        }
        parent = str(Path(track.relpath).parent.as_posix())
        if parent == ".":
            parent = ""
        rows.append(
            {
                "rel": track.relpath,
                "file": path.name,
                "folder": parent,
                "title": title,
                "artist": artist,
                "album": album,
                "date": date,
                "track": number,
                "albumartist": merged["albumartist"],
                "incomplete": mods["is_incomplete"](merged),
                "has_cover": bool(track.cover_hash),
            }
        )
    rows.sort(key=lambda item: (item["artist"].casefold(), item["album"].casefold(), item["track"], item["title"].casefold(), item["rel"].casefold()))
    incomplete = sum(1 for item in rows if item["incomplete"])
    return {"root": str(folder), "count": len(rows), "incomplete": incomplete, "truncated": truncated, "tracks": rows}


@router.get("/catalog/cover")
def catalog_cover(rel: str = "") -> Response:
    folder = _library_folder()
    path = _safe_child(folder, rel)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Fitxer no trobat")
    mods = _catalog_modules()
    cover = mods["extract_embedded_cover"](path)
    if cover is None:
        raise HTTPException(status_code=404, detail="Sense portada")
    data, mime = cover
    return Response(content=data, media_type=mime or "image/jpeg")


@router.post("/catalog/cover/search")
def catalog_cover_search(body: CoverSearchBody) -> dict[str, str]:
    mods = _catalog_modules()
    found = mods["fetch_itunes_cover"](body.artist, body.title, body.album)
    if not found:
        raise HTTPException(status_code=404, detail="No s'ha trobat cap portada")
    data, mime = found
    if len(data) > _MAX_COVER_BYTES:
        raise HTTPException(status_code=400, detail="La imatge és massa gran")
    return {"mime": mime or "image/jpeg", "data_b64": base64.b64encode(data).decode("ascii")}


@router.post("/catalog/save")
def catalog_save(body: CatalogSaveBody) -> dict[str, Any]:
    if not body.rows:
        raise HTTPException(status_code=400, detail="No hi ha canvis per desar")
    folder = _library_folder()
    mods = _catalog_modules()
    cataloger = mods["MusicCataloger"](mods["CatalogerConfig"](root=folder, use_musicbrainz=False, use_acoustid=False))
    saved = 0
    renamed = 0
    covers = 0
    errors: list[dict[str, str]] = []
    updated: list[dict[str, str]] = []
    for row in body.rows:
        try:
            path = _safe_child(folder, row.rel)
            if not path.is_file():
                raise RuntimeError("El fitxer ja no existeix")
            tags = {
                "title": row.title.strip(),
                "artist": row.artist.strip(),
                "album": row.album.strip(),
                "date": row.date.strip()[:4],
                "track": row.track.strip(),
                "albumartist": row.albumartist.strip(),
                "file": (row.file or path.name).strip(),
            }
            original = cataloger.read_existing(path)
            original["file"] = path.name
            tags_changed = any(tags.get(key, "") != original.get(key, "") for key in ("title", "artist", "album", "date", "track", "albumartist", "file"))
            action = row.cover_action.strip().lower()
            if action not in {"", "set", "remove"}:
                raise RuntimeError("Acció de portada no vàlida")
            if tags_changed:
                if not tags["title"] or not tags["artist"]:
                    raise RuntimeError("Cal títol i artista per escriure les etiquetes")
                cataloger.write_tags(path, mods["tags_to_candidate"](tags))
                desired = tags["file"]
                if desired and desired != path.name:
                    path = mods["rename_to_filename"](path, desired)
                    renamed += 1
                elif body.rename:
                    new_path = cataloger.maybe_rename(path, mods["tags_to_candidate"](tags))
                    if new_path != path:
                        path = new_path
                        renamed += 1
            if action == "set":
                if not row.cover_b64:
                    raise RuntimeError("Falta la imatge de la portada")
                try:
                    blob = base64.b64decode(row.cover_b64, validate=True)
                except Exception as exc:
                    raise RuntimeError("Imatge de portada no vàlida") from exc
                if not blob or len(blob) > _MAX_COVER_BYTES:
                    raise RuntimeError("Imatge de portada no vàlida")
                mods["write_embedded_cover"](path, blob, row.cover_mime or "image/jpeg")
                covers += 1
            elif action == "remove":
                mods["remove_embedded_cover"](path)
                covers += 1
            saved += 1
            updated.append({"rel": row.rel, "new_rel": path.relative_to(folder).as_posix(), "file": path.name})
        except HTTPException:
            raise
        except Exception as exc:
            errors.append({"rel": row.rel, "error": str(exc)})
    _maybe_reload(folder)
    return {"saved": saved, "renamed": renamed, "covers": covers, "errors": errors, "updated": updated}


def _run_catalog(job_id: str, folder: Path, body: CatalogRunBody, api_key: str) -> None:
    mods = _catalog_modules()
    config = mods["CatalogerConfig"](
        root=folder,
        write=body.write,
        rename_files=body.rename_files,
        use_musicbrainz=body.use_musicbrainz,
        use_acoustid=body.use_acoustid,
        acoustid_api_key=api_key,
        only_incomplete=body.only_incomplete,
        ignore_existing_tags=body.ignore_existing_tags,
        limit=max(0, body.limit),
        artist_filter=body.artist.strip() or None,
    )

    def on_progress(done: int, total: int, result: Any) -> None:
        with _lock:
            job = _catalog_jobs.get(job_id)
            if not job:
                return
            job["done"] = done
            job["total"] = total
            job["status"] = "running"
            if result is None:
                return
            public = _public_file_result(result)
            job["results"].append(public)
            if len(job["results"]) > 400:
                job["results"] = job["results"][-400:]
            job["changed"] += int(bool(public.get("changed")))
            job["errors"] += int(bool(public.get("error")))
            job["mb_matched"] += int(bool(public.get("mb_matched")))
            job["acoustid_matched"] += int(bool(public.get("acoustid_matched")))
            job["current"] = public.get("title") or public.get("path") or ""

    try:
        mods["MusicCataloger"](config).run(on_progress=on_progress)
        with _lock:
            job = _catalog_jobs.get(job_id)
            if job:
                job["status"] = "done"
                job["current"] = ""
        if body.write:
            _maybe_reload(folder)
    except Exception as exc:
        log.exception("catalog run failed")
        with _lock:
            job = _catalog_jobs.get(job_id)
            if job:
                job["status"] = "error"
                job["error"] = str(getattr(exc, "detail", "") or exc)


@router.post("/catalog/run")
def catalog_run(body: CatalogRunBody) -> dict[str, Any]:
    folder = _library_folder()
    mods = _catalog_modules()
    api_key = str(mods["load_settings"]().get("acoustid_api_key") or "").strip()
    if body.use_acoustid and not api_key:
        raise HTTPException(
            status_code=400,
            detail="Cal una clau d'AcoustID. La pots demanar a acoustid.org/api-key.",
        )
    if body.use_acoustid and mods["resolve_fpcalc"]() is None:
        raise HTTPException(status_code=400, detail="No s'ha trobat fpcalc per a l'empremta d'àudio")
    job_id = uuid.uuid4().hex
    with _lock:
        _catalog_jobs[job_id] = {
            "id": job_id,
            "status": "running",
            "done": 0,
            "total": 0,
            "changed": 0,
            "errors": 0,
            "mb_matched": 0,
            "acoustid_matched": 0,
            "current": "",
            "error": "",
            "write": body.write,
            "results": [],
        }
    threading.Thread(target=_run_catalog, args=(job_id, folder, body, api_key), daemon=True).start()
    return {"job_id": job_id}


@router.get("/catalog/run/{job_id}")
def catalog_run_status(job_id: str) -> dict[str, Any]:
    return _snapshot_catalog(job_id)


def _yt():
    from ytlocal.downloader import download
    from ytlocal.error_messages import format_error_with_title, is_usable_title
    from ytlocal.failures import add_failure, clear_failures, get_failure, list_failures, remove_failure
    from ytlocal.paths import downloads_dir
    from ytlocal.playlist import download_playlist, is_playlist_url
    from ytlocal.settings import get_settings, probe_cookies, update_settings

    return {
        "download": download,
        "download_playlist": download_playlist,
        "is_playlist_url": is_playlist_url,
        "add_failure": add_failure,
        "clear_failures": clear_failures,
        "get_failure": get_failure,
        "list_failures": list_failures,
        "remove_failure": remove_failure,
        "downloads_dir": downloads_dir,
        "get_settings": get_settings,
        "update_settings": update_settings,
        "probe_cookies": probe_cookies,
        "format_error_with_title": format_error_with_title,
        "is_usable_title": is_usable_title,
    }


def _download_dir(destination: str) -> Path:
    if destination == "library":
        root = _library_root()
        if root is None or not root.is_dir():
            raise HTTPException(status_code=400, detail="Encara no hi ha carpeta de karaoke. Tria-la a la portada o desa a Descàrregues.")
        return root
    return _yt()["downloads_dir"]()


def _update_download(job_id: str, **kwargs: Any) -> None:
    with _lock:
        job = _download_jobs.get(job_id)
        if not job:
            return
        job.update(kwargs)
        job["updated_at"] = time.time()


def _download_snapshot(job_id: str) -> dict[str, Any]:
    with _lock:
        job = dict(_download_jobs.get(job_id) or {})
    if not job:
        raise HTTPException(status_code=404, detail="Tasca no trobada")
    return job


def _resolved_title(is_usable, *candidates: Any) -> str | None:
    for candidate in candidates:
        if is_usable(str(candidate) if candidate else None):
            return str(candidate).strip()
    return None


def _run_single(job_id: str, url: str, mode: str, quality: str, out_dir: Path, destination: str) -> None:
    yt = _yt()

    def hook(payload: dict) -> None:
        status = payload.get("status")
        video_title = _resolved_title(yt["is_usable_title"], payload.get("video_title"))
        extra = {"title": video_title} if video_title else {}
        if status == "downloading":
            total = payload.get("total_bytes") or payload.get("total_bytes_estimate") or 0
            downloaded = payload.get("downloaded_bytes") or 0
            percent = round(downloaded / total * 100, 1) if total else None
            _update_download(
                job_id,
                status="downloading",
                percent=percent,
                filename=Path(payload.get("filename") or "").name or None,
                **extra,
            )
        elif status == "finished":
            _update_download(job_id, status="processing", percent=100, **extra)

    try:
        result = yt["download"](url, mode=mode, quality=quality, out_dir=out_dir, progress_hook=hook)
        _update_download(
            job_id,
            status="done",
            percent=100,
            title=result.title,
            files=[path.name for path in result.files],
            error=None,
        )
        if destination == "library":
            _maybe_reload(out_dir)
    except Exception as exc:
        title = _resolved_title(yt["is_usable_title"], getattr(exc, "title", None), _download_snapshot(job_id).get("title"))
        message = yt["format_error_with_title"](str(exc), title, url)
        yt["add_failure"](title=title or url, url=url, error=str(exc), mode=mode, quality=quality, kind="single")
        _update_download(job_id, status="error", error=message, title=title)


def _run_playlist(job_id: str, url: str, mode: str, quality: str, out_dir: Path, destination: str) -> None:
    yt = _yt()

    def hook(payload: dict) -> None:
        status = payload.get("status")
        total_items = payload.get("total") or 0
        index = payload.get("index") or 0
        item_percent = payload.get("item_percent")
        overall = None
        if total_items:
            base = max(index - 1, 0) / total_items * 100
            if item_percent is not None:
                overall = round(base + (item_percent / total_items), 1)
            elif status in {"item_done", "done"}:
                overall = round(index / total_items * 100, 1)
            else:
                overall = round(base, 1)
        mapped = status
        if status in {"resolving", "resolved"}:
            mapped = "queued" if status == "resolving" else "downloading"
        elif status in {"item_done", "item_error", "processing"}:
            mapped = "processing" if status == "processing" else "downloading"
        elif status == "done":
            mapped = "done"
        _update_download(
            job_id,
            status=mapped,
            percent=overall,
            filename=payload.get("filename"),
            title=payload.get("playlist_title") or _download_snapshot(job_id).get("title"),
            item_title=payload.get("item_title"),
            index=index,
            total_items=total_items,
            downloaded_items=payload.get("downloaded") or 0,
            failed_items=payload.get("failed") or 0,
            files=payload.get("files") or _download_snapshot(job_id).get("files") or [],
            error=payload.get("error") if status == "error" else None,
        )

    try:
        result = yt["download_playlist"](
            url,
            mode=mode,
            quality=quality,
            out_dir=out_dir,
            progress_hook=hook,
            continue_on_error=True,
        )
        for failure in result.failures:
            if not failure.get("url"):
                continue
            yt["add_failure"](
                title=str(failure.get("title") or failure["url"]),
                url=str(failure["url"]),
                error=str(failure.get("error") or "Download failed"),
                mode=mode,
                quality=quality,
                kind="playlist_item",
                playlist_title=str(failure.get("playlist_title") or result.title),
            )
        first_failure = result.failures[0] if result.failures else {}
        first_title = _resolved_title(yt["is_usable_title"], first_failure.get("title"), result.title)
        first_error = str(first_failure.get("error") or (result.errors[0] if result.errors else "No s'ha descarregat res"))
        job_error = None
        if not result.downloaded:
            job_error = yt["format_error_with_title"](first_error, first_title, str(first_failure.get("url") or url), result.title)
        _update_download(
            job_id,
            status="done" if result.downloaded else "error",
            percent=100,
            title=result.title,
            files=[path.name for path in result.files],
            downloaded_items=result.downloaded,
            failed_items=result.failed,
            total_items=result.total,
            error=job_error,
        )
        if result.downloaded and destination == "library":
            _maybe_reload(out_dir)
        if result.downloaded == 0 and result.errors:
            yt["add_failure"](
                title=first_title or result.title or url,
                url=str(first_failure.get("url") or url),
                error=first_error,
                mode=mode,
                quality=quality,
                kind="playlist",
                playlist_title=result.title,
            )
    except Exception as exc:
        title = _resolved_title(yt["is_usable_title"], getattr(exc, "title", None), _download_snapshot(job_id).get("title"))
        message = yt["format_error_with_title"](str(exc), title, url)
        yt["add_failure"](title=title or url, url=url, error=str(exc), mode=mode, quality=quality, kind="playlist")
        _update_download(job_id, status="error", error=message, title=title)


def _progress_payload(job: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": job.get("status"),
        "percent": job.get("percent"),
        "filename": job.get("filename"),
        "title": job.get("title"),
        "item_title": job.get("item_title"),
        "index": job.get("index") or 0,
        "total_items": job.get("total_items") or 0,
        "downloaded_items": job.get("downloaded_items") or 0,
        "failed_items": job.get("failed_items") or 0,
        "files": job.get("files") or [],
        "kind": job.get("kind") or "single",
        "url": job.get("url"),
        "destination": job.get("destination"),
        "error": job.get("error"),
    }


@router.post("/yt/download")
def start_download(body: DownloadBody) -> dict[str, Any]:
    url = body.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="Cal una URL")
    quality = body.quality.lower()
    if quality not in {"best", "192k", "720p", "1080p"}:
        raise HTTPException(status_code=400, detail=f"Qualitat no vàlida: {body.quality}")
    yt = _yt()
    if body.kind == "playlist":
        use_playlist = True
    elif body.kind == "single":
        use_playlist = False
    else:
        use_playlist = yt["is_playlist_url"](url)
    out_dir = _download_dir(body.destination)
    job_id = uuid.uuid4().hex
    with _lock:
        _download_jobs[job_id] = {
            "id": job_id,
            "url": url,
            "status": "queued",
            "percent": 0,
            "filename": None,
            "title": None,
            "item_title": None,
            "index": 0,
            "total_items": 0,
            "downloaded_items": 0,
            "failed_items": 0,
            "files": [],
            "error": None,
            "kind": "playlist" if use_playlist else "single",
            "destination": body.destination,
            "out_dir": str(out_dir),
            "updated_at": time.time(),
        }
    target = _run_playlist if use_playlist else _run_single
    threading.Thread(
        target=target,
        args=(job_id, url, body.mode, quality, out_dir, body.destination),
        daemon=True,
    ).start()
    return {"job_id": job_id, "kind": "playlist" if use_playlist else "single", "url": url, "out_dir": str(out_dir)}


@router.get("/yt/progress/{job_id}")
def download_progress(job_id: str) -> dict[str, Any]:
    return _progress_payload(_download_snapshot(job_id))


@router.get("/yt/config")
def yt_config() -> dict[str, Any]:
    yt = _yt()
    root = _library_root()
    downloads = yt["downloads_dir"]()
    return {
        "library_root": str(root) if root else "",
        "downloads_dir": str(downloads),
        "settings": yt["get_settings"](),
    }


@router.put("/yt/settings")
def put_yt_settings(body: YtSettingsBody) -> dict[str, Any]:
    yt = _yt()
    patch = body.model_dump(exclude_none=True)
    try:
        settings = yt["update_settings"](patch)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"settings": settings}


@router.post("/yt/cookies")
async def upload_cookies(file: UploadFile = File(...)) -> dict[str, Any]:
    blob = await file.read()
    if not blob:
        raise HTTPException(status_code=400, detail="El fitxer de cookies és buit")
    if len(blob) > 2_000_000:
        raise HTTPException(status_code=400, detail="El fitxer de cookies és massa gran")
    yt = _yt()
    from ytlocal.settings import default_cookies_txt

    path = default_cookies_txt()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    settings = yt["update_settings"]({"cookies_browser": "file", "cookies_file": str(path)})
    return {"settings": settings, "path": str(path)}


@router.get("/yt/failures")
def yt_failures() -> list[dict[str, Any]]:
    return _yt()["list_failures"]()


@router.delete("/yt/failures")
def yt_clear_failures() -> dict[str, int]:
    return {"removed": _yt()["clear_failures"]()}


@router.delete("/yt/failures/{failure_id}")
def yt_delete_failure(failure_id: str) -> dict[str, bool]:
    if not _yt()["remove_failure"](failure_id):
        raise HTTPException(status_code=404, detail="Error no trobat")
    return {"removed": True}


@router.post("/yt/failures/{failure_id}/retry")
def yt_retry_failure(failure_id: str) -> dict[str, Any]:
    record = _yt()["get_failure"](failure_id)
    if not record:
        raise HTTPException(status_code=404, detail="Error no trobat")
    url = str(record.get("url") or "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="Aquest error no té URL per reintentar")
    _yt()["remove_failure"](failure_id)
    kind = record.get("kind") or "auto"
    if kind == "playlist_item":
        kind = "single"
    return {
        "url": url,
        "mode": record.get("mode") or "audio",
        "quality": record.get("quality") or "best",
        "kind": kind,
        "title": record.get("title"),
    }


def _list_media(root: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if not root.is_dir():
        return items
    for path in root.rglob("*"):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix.lower() not in _AUDIO_VIDEO or path.name.endswith((".part", ".ytdl", ".temp")):
            continue
        try:
            resolved = path.resolve()
            if resolved != root and root not in resolved.parents:
                continue
            stat = resolved.stat()
            rel = resolved.relative_to(root).as_posix()
        except OSError:
            continue
        items.append({"name": resolved.name, "rel": rel, "size": stat.st_size, "mtime": stat.st_mtime})
    items.sort(key=lambda item: item["mtime"], reverse=True)
    return items[:200]


@router.get("/yt/files")
def yt_files(destination: Literal["library", "downloads"] = "downloads") -> dict[str, Any]:
    try:
        root = _download_dir(destination)
    except HTTPException:
        if destination == "library":
            return {"root": "", "files": []}
        raise
    return {"root": str(root), "files": _list_media(root)}


@router.get("/yt/file")
def yt_file(
    rel: str = Query(...),
    destination: Literal["library", "downloads"] = "downloads",
) -> Response:
    root = _download_dir(destination)
    path = _safe_child(root, rel)
    if not path.is_file() or path.suffix.lower() not in _AUDIO_VIDEO:
        raise HTTPException(status_code=404, detail="Fitxer no trobat")
    from fastapi.responses import FileResponse

    return FileResponse(path, filename=path.name)
