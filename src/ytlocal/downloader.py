"""yt-dlp wrapper with format presets and progress hooks."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal
from urllib.parse import quote
from urllib.request import Request, urlopen

import yt_dlp

from ytlocal.error_messages import is_usable_title, youtube_watch_url
from ytlocal.paths import downloads_dir

try:
    from ytlocal.ffmpeg_setup import ffmpeg_location
except Exception:  # pragma: no cover - import-time safety
    def ffmpeg_location() -> str | None:  # type: ignore[misc]
        return None

try:
    from ytlocal.settings import cookie_ydl_opts
except Exception:  # pragma: no cover
    def cookie_ydl_opts() -> dict[str, Any]:  # type: ignore[misc]
        return {}

Mode = Literal["audio", "video"]
ProgressCallback = Callable[[dict[str, Any]], None]

_FILENAME_TITLE_RE = re.compile(r"^(.+) \[[\w-]{11}\]$")


def default_downloads() -> Path:
    return downloads_dir()


# Kept for CLI/server convenience; resolved at import, refreshed via default_downloads().
DEFAULT_DOWNLOADS = downloads_dir()


@dataclass
class DownloadResult:
    title: str
    files: list[Path] = field(default_factory=list)


class DownloadFailed(RuntimeError):
    """Download error that may carry a resolved video title."""

    def __init__(self, message: str, *, title: str | None = None, url: str = ""):
        super().__init__(message)
        self.title = title
        self.url = url


def _audio_opts(quality: str) -> dict[str, Any]:
    preferred = "192" if quality == "192k" else "0"
    return {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": preferred,
            }
        ],
    }


def _video_opts(quality: str) -> dict[str, Any]:
    if quality == "720p":
        fmt = "bv*[height<=720]+ba/b[height<=720]/bv*+ba/b"
    elif quality == "1080p":
        fmt = "bv*[height<=1080]+ba/b[height<=1080]/bv*+ba/b"
    else:
        fmt = "bv*+ba/b"
    return {
        "format": fmt,
        "merge_output_format": "mp4",
    }


def resolve_js_runtimes() -> dict[str, dict[str, str]]:
    """Enable Deno/Node so yt-dlp can solve YouTube's player challenges."""
    from ytlocal.js_runtime import resolve_js_runtimes as _resolve

    return _resolve()


def youtube_extractor_args() -> dict[str, Any]:
    """Use yt-dlp's own clients.

    Forcing only ``web`` / ``mweb`` without a JS runtime leaves no audio or
    video formats, and yt-dlp then says the requested format is not available.
    ``android_vr`` URLs often 403, so those clients stay excluded.
    """
    return {
        "youtube": {
            "player_client": ["default", "-android_sdkless", "-android_vr"],
        }
    }


def build_ydl_opts(
    *,
    mode: Mode,
    quality: str,
    out_dir: Path,
    progress_hook: ProgressCallback | None = None,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    opts: dict[str, Any] = {
        "outtmpl": str(out_dir / "%(title).200B [%(id)s].%(ext)s"),
        "restrictfilenames": False,
        "windowsfilenames": True,
        "noplaylist": True,
        "ignoreerrors": False,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "progress_hooks": [progress_hook] if progress_hook else [],
        # Resilience against transient YouTube blocks.
        "retries": 10,
        "fragment_retries": 10,
        "file_access_retries": 3,
        "retry_sleep_functions": {
            "http": lambda n: min(2 ** n, 20),
            "fragment": lambda n: min(2 ** n, 20),
        },
        # Pace API / media requests a bit to reduce burst 403s.
        "sleep_interval_requests": 1,
        # IPv6 often triggers 403 on some ISPs / networks.
        "source_address": "0.0.0.0",
        "extractor_args": youtube_extractor_args(),
        # Allow fetching yt-dlp EJS challenge solvers when a JS runtime is available.
        "remote_components": ["ejs:github"],
    }
    js_runtimes = resolve_js_runtimes()
    if js_runtimes:
        opts["js_runtimes"] = js_runtimes
    location = ffmpeg_location()
    if location:
        opts["ffmpeg_location"] = location
    opts.update(cookie_ydl_opts())
    if mode == "audio":
        opts.update(_audio_opts(quality))
    else:
        opts.update(_video_opts(quality))
    return opts


def _title_from_progress(d: dict[str, Any]) -> str | None:
    info = d.get("info_dict") if isinstance(d.get("info_dict"), dict) else {}
    for key in ("title", "fulltitle"):
        value = info.get(key)
        if is_usable_title(str(value) if value else None):
            return str(value).strip()
    filename = d.get("filename") or d.get("tmpfilename") or ""
    if not filename:
        return None
    stem = Path(str(filename)).name
    stem = re.sub(r"\.part$", "", stem, flags=re.I)
    stem = Path(stem).stem
    match = _FILENAME_TITLE_RE.match(stem)
    if match and is_usable_title(match.group(1)):
        return match.group(1).strip()
    return None


def probe_video_title(url: str) -> str | None:
    """Best-effort title lookup without downloading media."""
    if not url or not url.strip():
        return None
    watch = youtube_watch_url(url.strip()) or url.strip()
    return _title_from_oembed(watch) or _title_from_ydl(watch)


def _title_from_oembed(url: str) -> str | None:
    try:
        oembed = f"https://www.youtube.com/oembed?url={quote(url, safe='')}&format=json"
        req = Request(oembed, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace"))
    except Exception:
        return None
    title = data.get("title") if isinstance(data, dict) else None
    if is_usable_title(str(title) if title else None):
        return str(title).strip()
    return None


def _title_from_ydl(url: str) -> str | None:
    class _Silent:
        def debug(self, msg: str) -> None:
            return None

        def info(self, msg: str) -> None:
            return None

        def warning(self, msg: str) -> None:
            return None

        def error(self, msg: str) -> None:
            return None

    opts: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
        "ignoreerrors": True,
        "retries": 1,
        "source_address": "0.0.0.0",
        "extractor_args": youtube_extractor_args(),
        "logger": _Silent(),
    }
    opts.update(cookie_ydl_opts())
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False, process=False)
    except Exception:
        return None
    if not info:
        return None
    title = info.get("title") or info.get("fulltitle")
    if is_usable_title(str(title) if title else None):
        return str(title).strip()
    return None


def _collect_entries(info: dict[str, Any]) -> list[dict[str, Any]]:
    if "entries" in info:
        return [e for e in (info.get("entries") or []) if e]
    return [info]


def _paths_from_info(ydl: yt_dlp.YoutubeDL, info: dict[str, Any], mode: Mode) -> list[Path]:
    paths: list[Path] = []
    for entry in _collect_entries(info):
        requested = entry.get("requested_downloads") or []
        for item in requested:
            filepath = item.get("filepath")
            if filepath:
                paths.append(Path(filepath))
        if not requested:
            prepared = Path(ydl.prepare_filename(entry))
            if mode == "audio":
                prepared = prepared.with_suffix(".mp3")
            elif prepared.suffix.lower() not in {".mp4", ".mkv", ".webm"}:
                prepared = prepared.with_suffix(".mp4")
            paths.append(prepared)
    # Deduplicate while preserving order
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


def download(
    url: str,
    *,
    mode: Mode = "audio",
    quality: str = "best",
    out_dir: Path | None = None,
    progress_hook: ProgressCallback | None = None,
) -> DownloadResult:
    """Download a YouTube URL to ``out_dir`` and return resulting paths."""
    if not url or not url.strip():
        raise ValueError("URL is required")

    destination = Path(out_dir) if out_dir else downloads_dir()
    before_mtime: dict[Path, float] = {}
    if destination.exists():
        before_mtime = {
            p.resolve(): p.stat().st_mtime
            for p in destination.glob("*")
            if p.is_file()
        }

    captured_title: list[str | None] = [None]

    def wrapped_hook(d: dict[str, Any]) -> None:
        found = _title_from_progress(d)
        if found:
            captured_title[0] = found
        if progress_hook:
            payload = dict(d)
            if captured_title[0]:
                payload["video_title"] = captured_title[0]
            progress_hook(payload)

    opts = build_ydl_opts(
        mode=mode,
        quality=quality,
        out_dir=destination,
        progress_hook=wrapped_hook,
    )

    title = url
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                raise RuntimeError("Download failed: no video information returned")
            entries = _collect_entries(info)
            titles = [e.get("title") for e in entries if e.get("title")]
            if len(titles) == 1:
                title = titles[0]
            elif titles:
                title = f"{len(titles)} videos"
            else:
                title = info.get("title") or title
            candidate_paths = _paths_from_info(ydl, info, mode)
    except DownloadFailed:
        raise
    except Exception as exc:
        resolved = captured_title[0] or probe_video_title(url)
        raise DownloadFailed(str(exc), title=resolved, url=url) from exc

    files: list[Path] = []
    for path in candidate_paths:
        if path.is_file():
            files.append(path)
            continue
        # Audio post-process may leave a different extension
        if mode == "audio":
            alt = path.with_suffix(".mp3")
            if alt.is_file():
                files.append(alt)

    if not files and destination.exists():
        for path in destination.glob("*"):
            if not path.is_file() or path.name.startswith("."):
                continue
            resolved = path.resolve()
            prev = before_mtime.get(resolved)
            if prev is None or path.stat().st_mtime > prev:
                files.append(path)
        files.sort(key=lambda p: p.stat().st_mtime)

    return DownloadResult(title=title, files=files)
