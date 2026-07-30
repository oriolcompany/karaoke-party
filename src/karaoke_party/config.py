from __future__ import annotations

import os
from pathlib import Path

DEFAULT_PORT = 8765
AUDIO_EXTENSIONS = {".mp3", ".m4a", ".flac", ".ogg", ".wav", ".opus"}


def default_music_root() -> Path | None:
    env = os.environ.get("KARAOKE_MUSIC_ROOT", "").strip()
    if env:
        return Path(env)
    candidates = [
        Path(r"C:\Users\orico\Documents\Songs"),
        Path(r"C:\Users\orico\Documents\GitHub\local-youtube-downloader")
        / "dist"
        / "LocalYoutubeDownloader"
        / "downloads",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


def app_cache_root() -> Path:
    """Stable per-user cache root.

    Using the working directory made results disappear whenever the app was
    started from a different place (KaraokeParty.bat vs the built EXE), so the
    whole library was re-probed on every launch.
    """
    env = os.environ.get("KARAOKE_CACHE_DIR", "").strip()
    if env:
        return Path(env)
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if base:
            return Path(base) / "KaraokeParty"
    xdg = os.environ.get("XDG_CACHE_HOME", "").strip()
    if xdg:
        return Path(xdg) / "karaoke-party"
    return Path.home() / ".cache" / "karaoke-party"


def _legacy_cache_dir(name: str) -> Path:
    return Path.cwd() / ".cache" / name


def _migrate_legacy_cache(name: str, target: Path) -> None:
    legacy = _legacy_cache_dir(name)
    if not legacy.is_dir() or legacy == target:
        return
    for item in legacy.iterdir():
        if not item.is_file():
            continue
        destination = target / item.name
        if destination.exists():
            continue
        try:
            destination.write_bytes(item.read_bytes())
        except OSError:
            continue


def _resolve_cache_dir(name: str, root: Path | None) -> Path:
    base = root or app_cache_root()
    path = base / ".cache" / name if root else base / name
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        path = _legacy_cache_dir(name)
        path.mkdir(parents=True, exist_ok=True)
        return path
    if root is None:
        _migrate_legacy_cache(name, path)
    return path


def cache_dir(root: Path | None = None) -> Path:
    return _resolve_cache_dir("lyrics", root)


def aligned_cache_dir(root: Path | None = None) -> Path:
    return _resolve_cache_dir("aligned", root)
