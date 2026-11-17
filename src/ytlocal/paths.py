"""Resolve project paths for source installs and frozen executables."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from ytlocal.branding import APP_NAME


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def app_dir() -> Path:
    """Writable app directory (next to the .exe, or project root in dev)."""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def resource_dir() -> Path:
    """Bundled read-only resources (PyInstaller _MEIPASS, or project root in dev)."""
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parents[2]


def is_portable() -> bool:
    """
    Portable mode keeps downloads/ffmpeg/failed.json next to the app.

    Enabled when:
    - running the frozen .exe (default), or
    - a `portable` / `portable.txt` marker exists next to the app, or
    - YTLOCAL_PORTABLE=1
    """
    flag = os.environ.get("YTLOCAL_PORTABLE", "").strip().lower()
    if flag in {"1", "true", "yes", "on"}:
        return True
    if flag in {"0", "false", "no", "off"}:
        return False
    root = app_dir()
    if (root / "portable").is_file() or (root / "portable.txt").is_file():
        return True
    return is_frozen()


def data_dir() -> Path:
    """Root folder for downloads, ffmpeg cache and failed.json."""
    override = os.environ.get("YTLOCAL_DATA", "").strip()
    if override:
        path = Path(override).expanduser()
    elif is_portable():
        path = app_dir()
    else:
        path = Path.home() / "Documents" / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def downloads_dir() -> Path:
    """
    Download location.

    Override with env var YTLOCAL_DOWNLOADS if needed.
    """
    override = os.environ.get("YTLOCAL_DOWNLOADS", "").strip()
    if override:
        path = Path(override).expanduser()
    else:
        path = data_dir() / "downloads"
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def web_dir() -> Path:
    return resource_dir() / "web"
