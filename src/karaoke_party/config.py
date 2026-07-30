from __future__ import annotations

import os
from pathlib import Path

DEFAULT_PORT = 8765
AUDIO_EXTENSIONS = {".mp3", ".m4a", ".flac", ".ogg", ".wav", ".opus"}


def default_music_root() -> Path | None:
    env = os.environ.get("KARAOKE_MUSIC_ROOT", "").strip()
    if env:
        return Path(env)
    candidate = Path(
        r"C:\Users\orico\Documents\GitHub\local-youtube-downloader"
        r"\dist\LocalYoutubeDownloader\downloads"
    )
    if candidate.is_dir():
        return candidate
    return None


def cache_dir(root: Path | None = None) -> Path:
    base = root or Path.cwd()
    path = base / ".cache" / "lyrics"
    path.mkdir(parents=True, exist_ok=True)
    return path


def aligned_cache_dir(root: Path | None = None) -> Path:
    base = root or Path.cwd()
    path = base / ".cache" / "aligned"
    path.mkdir(parents=True, exist_ok=True)
    return path
