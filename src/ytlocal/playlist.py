"""Mass download of YouTube playlists."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yt_dlp

from ytlocal.downloader import Mode, download, resolve_js_runtimes, youtube_extractor_args
from ytlocal.error_messages import format_error_with_title, is_usable_title
from ytlocal.paths import downloads_dir

ProgressCallback = Callable[[dict[str, Any]], None]


@dataclass
class PlaylistResult:
    title: str
    total: int
    downloaded: int
    failed: int
    files: list[Path] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)


def is_playlist_url(url: str) -> bool:
    """Heuristic: playlist / mix / channel tab URLs."""
    lower = url.lower()
    if "list=" in lower:
        return True
    if "/playlist" in lower:
        return True
    if "/channel/" in lower and "/videos" in lower:
        return True
    if "@" in lower and ("/videos" in lower or "/playlists" in lower):
        return True
    return False


def _safe_folder_name(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", name).strip(" .")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return (cleaned[:120] or "playlist").rstrip(".")


def _entry_url(entry: dict[str, Any]) -> str | None:
    if not entry:
        return None
    if entry.get("url") and str(entry["url"]).startswith("http"):
        return str(entry["url"])
    video_id = entry.get("id")
    if video_id and entry.get("_type") in {None, "url", "video"}:
        # Flat playlist entries are usually bare video ids
        if re.fullmatch(r"[\w-]{11}", str(video_id)):
            return f"https://www.youtube.com/watch?v={video_id}"
        if str(video_id).startswith("http"):
            return str(video_id)
    webpage = entry.get("webpage_url")
    if webpage:
        return str(webpage)
    return None


def resolve_playlist(url: str) -> tuple[str, list[dict[str, Any]]]:
    """Fetch playlist metadata and flat entry list without downloading."""
    opts: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "skip_download": True,
        "ignoreerrors": True,
        "retries": 5,
        "source_address": "0.0.0.0",
        "extractor_args": youtube_extractor_args(),
        "remote_components": ["ejs:github"],
    }
    js_runtimes = resolve_js_runtimes()
    if js_runtimes:
        opts["js_runtimes"] = js_runtimes
    try:
        from ytlocal.settings import cookie_ydl_opts

        opts.update(cookie_ydl_opts())
    except Exception:
        pass
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    if info is None:
        raise RuntimeError("Could not resolve playlist")

    title = info.get("title") or "playlist"
    raw_entries = info.get("entries")
    if raw_entries is None:
        # Single video passed to playlist flow
        return title, [info]

    entries = [e for e in raw_entries if e]
    if not entries:
        raise RuntimeError("Playlist is empty or unavailable")
    return title, entries


def download_playlist(
    url: str,
    *,
    mode: Mode = "audio",
    quality: str = "best",
    out_dir: Path | None = None,
    progress_hook: ProgressCallback | None = None,
    continue_on_error: bool = True,
) -> PlaylistResult:
    """Download every item in a playlist into a dedicated subfolder."""
    if not url or not url.strip():
        raise ValueError("URL is required")

    def emit(**payload: Any) -> None:
        if progress_hook:
            progress_hook(payload)

    emit(status="resolving", index=0, total=0, item_title=None, item_percent=None)

    playlist_title, entries = resolve_playlist(url)
    total = len(entries)
    base = Path(out_dir) if out_dir else downloads_dir()
    destination = base / _safe_folder_name(playlist_title)
    destination.mkdir(parents=True, exist_ok=True)

    emit(
        status="resolved",
        playlist_title=playlist_title,
        index=0,
        total=total,
        item_title=None,
        item_percent=None,
        out_dir=str(destination),
    )

    files: list[Path] = []
    errors: list[str] = []
    failures: list[dict[str, Any]] = []
    downloaded = 0

    for index, entry in enumerate(entries, start=1):
        item_title = entry.get("title") or entry.get("id") or f"item {index}"
        item_url = _entry_url(entry)
        if not item_url:
            msg = format_error_with_title("Missing URL", item_title, "", playlist_title)
            errors.append(f"{index}/{total}: {msg}")
            failures.append(
                {
                    "title": item_title,
                    "url": "",
                    "error": "Missing URL",
                    "playlist_title": playlist_title,
                }
            )
            emit(
                status="item_error",
                playlist_title=playlist_title,
                index=index,
                total=total,
                item_title=item_title,
                item_url=None,
                item_percent=None,
                error=msg,
                downloaded=downloaded,
                failed=len(errors),
            )
            if not continue_on_error:
                raise RuntimeError(msg)
            continue

        emit(
            status="downloading",
            playlist_title=playlist_title,
            index=index,
            total=total,
            item_title=item_title,
            item_url=item_url,
            item_percent=0,
            downloaded=downloaded,
            failed=len(errors),
        )

        def item_hook(d: dict, *, _index=index, _title=item_title) -> None:
            hooked_title = d.get("video_title")
            if is_usable_title(str(hooked_title) if hooked_title else None):
                _title = str(hooked_title).strip()
            status = d.get("status")
            if status == "downloading":
                total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                got = d.get("downloaded_bytes") or 0
                percent = round(got / total_bytes * 100, 1) if total_bytes else None
                emit(
                    status="downloading",
                    playlist_title=playlist_title,
                    index=_index,
                    total=total,
                    item_title=_title,
                    item_url=item_url,
                    item_percent=percent,
                    filename=Path(d.get("filename") or "").name or None,
                    downloaded=downloaded,
                    failed=len(errors),
                )
            elif status == "finished":
                emit(
                    status="processing",
                    playlist_title=playlist_title,
                    index=_index,
                    total=total,
                    item_title=_title,
                    item_url=item_url,
                    item_percent=100,
                    downloaded=downloaded,
                    failed=len(errors),
                )

        try:
            # Small gap between items reduces rate-limit / 403 bursts on large playlists.
            if index > 1:
                time.sleep(1.5)
            result = download(
                item_url,
                mode=mode,
                quality=quality,
                out_dir=destination,
                progress_hook=item_hook,
            )
            files.extend(result.files)
            downloaded += 1
            emit(
                status="item_done",
                playlist_title=playlist_title,
                index=index,
                total=total,
                item_title=result.title or item_title,
                item_url=item_url,
                item_percent=100,
                downloaded=downloaded,
                failed=len(errors),
                files=[p.name for p in result.files],
            )
        except Exception as exc:
            resolved = getattr(exc, "title", None)
            if is_usable_title(str(resolved) if resolved else None):
                item_title = str(resolved).strip()
            msg = format_error_with_title(str(exc), item_title, item_url, playlist_title)
            errors.append(f"{index}/{total}: {msg}")
            failures.append(
                {
                    "title": item_title,
                    "url": item_url,
                    "error": str(exc),
                    "playlist_title": playlist_title,
                }
            )
            emit(
                status="item_error",
                playlist_title=playlist_title,
                index=index,
                total=total,
                item_title=item_title,
                item_url=item_url,
                item_percent=None,
                error=msg,
                downloaded=downloaded,
                failed=len(errors),
            )
            if not continue_on_error:
                raise

    emit(
        status="done",
        playlist_title=playlist_title,
        index=total,
        total=total,
        item_title=None,
        item_percent=100,
        downloaded=downloaded,
        failed=len(errors),
        files=[p.name for p in files],
        errors=errors,
        failures=failures,
        out_dir=str(destination),
    )

    return PlaylistResult(
        title=playlist_title,
        total=total,
        downloaded=downloaded,
        failed=len(errors),
        files=files,
        errors=errors,
        failures=failures,
    )
