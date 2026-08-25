from __future__ import annotations

import os
from pathlib import Path

DEFAULT_PORT = 8765
AUDIO_EXTENSIONS = {".mp3", ".m4a", ".flac", ".ogg", ".wav", ".opus"}


def last_music_root_file() -> Path:
    return app_cache_root() / "music-root.txt"


def load_last_music_root() -> Path | None:
    """Last folder the user loaded, if it still exists on disk."""
    try:
        text = last_music_root_file().read_text(encoding="utf-8").strip().strip('"')
    except OSError:
        return None
    if not text:
        return None
    candidate = Path(text).expanduser()
    try:
        if candidate.is_dir():
            return candidate
    except OSError:
        return None
    return None


def save_last_music_root(root: Path) -> None:
    """Remember the music folder so the next launch can reopen it."""
    try:
        resolved = root.expanduser().resolve()
        if not resolved.is_dir():
            return
        last_music_root_file().write_text(str(resolved), encoding="utf-8")
    except OSError:
        return


def default_music_root() -> Path | None:
    env = os.environ.get("KARAOKE_MUSIC_ROOT", "").strip()
    if env:
        return Path(env)
    cached = load_last_music_root()
    if cached is not None:
        return cached
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
        path = Path(env)
    elif os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        path = Path(base) / "KaraokeParty" if base else Path.home() / "KaraokeParty"
    else:
        xdg = os.environ.get("XDG_CACHE_HOME", "").strip()
        path = Path(xdg) / "karaoke-party" if xdg else Path.home() / ".cache" / "karaoke-party"
    path.mkdir(parents=True, exist_ok=True)
    return path


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


def tracks_cache_dir() -> Path:
    """Per-song cache root: ``tracks/<key>/{lyrics,aligned,stems,cover}``."""
    from .track_cache import tracks_cache_dir as _tracks

    return _tracks()


def cache_dir(root: Path | None = None) -> Path:
    """Tracks root used for lyrics.json (``root`` kept for call-site compat)."""
    del root  # song cache is always under the app cache, not the music folder
    return tracks_cache_dir()


def aligned_cache_dir(root: Path | None = None) -> Path:
    """Same tracks root; aligned.json lives next to lyrics.json."""
    del root
    return tracks_cache_dir()


def stems_cache_dir() -> Path:
    """Same tracks root; instrumental/vocals live inside each song folder."""
    return tracks_cache_dir()


def stem_models_dir() -> Path:
    path = app_cache_root() / "stem-models"
    path.mkdir(parents=True, exist_ok=True)
    return path
