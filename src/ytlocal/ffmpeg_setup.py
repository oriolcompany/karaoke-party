"""Ensure a local ffmpeg binary is available for yt-dlp."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Callable
from urllib.request import Request, urlopen

from ytlocal.branding import APP_NAME
from ytlocal.paths import app_dir, data_dir

# Official Windows essentials build mirrored by Gyan. ~80–100 MB.
FFMPEG_ZIP_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

ProgressFn = Callable[[str], None]


def ffmpeg_home() -> Path:
    override = os.environ.get("YTLOCAL_FFMPEG", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return (data_dir() / "ffmpeg").resolve()


def _find_ffmpeg_exe(root: Path) -> Path | None:
    direct = root / "bin" / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    if direct.is_file():
        return direct
    name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    if root.is_dir():
        matches = sorted(root.rglob(name))
        if matches:
            return matches[0]
    return None


def ffmpeg_path() -> Path | None:
    """Return an existing ffmpeg executable, or None."""
    which = shutil.which("ffmpeg")
    if which:
        return Path(which)

    local = _find_ffmpeg_exe(ffmpeg_home())
    if local:
        return local

    # Bundled next to the .exe (optional manual drop-in)
    from ytlocal.paths import app_dir

    bundled = _find_ffmpeg_exe(app_dir() / "ffmpeg")
    if bundled:
        return bundled
    return None


def ffmpeg_location() -> str | None:
    """Directory or binary path for yt-dlp's ffmpeg_location option."""
    path = ffmpeg_path()
    if not path:
        return None
    # yt-dlp accepts either the binary or its parent directory.
    return str(path.parent if path.name.lower().startswith("ffmpeg") else path)


def _download(url: str, destination: Path, progress: ProgressFn | None = None) -> None:
    req = Request(url, headers={"User-Agent": f"{APP_NAME}/0.1"})
    with urlopen(req, timeout=120) as response:  # noqa: S310 - fixed trusted URL
        total = response.headers.get("Content-Length")
        total_bytes = int(total) if total and total.isdigit() else None
        downloaded = 0
        chunk_size = 1024 * 256
        with destination.open("wb") as out:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out.write(chunk)
                downloaded += len(chunk)
                if progress and total_bytes:
                    pct = downloaded * 100 / total_bytes
                    progress(f"Descarregant ffmpeg… {pct:5.1f}%")
                elif progress:
                    progress(f"Descarregant ffmpeg… {downloaded // (1024 * 1024)} MB")


def _install_from_zip(zip_path: Path, target: Path, progress: ProgressFn | None = None) -> Path:
    if progress:
        progress("Extraient ffmpeg…")
    if target.exists():
        shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target)

    exe = _find_ffmpeg_exe(target)
    if not exe:
        raise RuntimeError("No s'ha trobat ffmpeg.exe dins de l'arxiu descarregat")
    return exe


def ensure_ffmpeg(progress: ProgressFn | None = None, *, auto_install: bool = True) -> Path:
    """
    Return a usable ffmpeg path.

    If missing and auto_install is True, download a portable Windows build
    into Documents/Local Youtube Downloader/ffmpeg/.
    """
    existing = ffmpeg_path()
    if existing:
        if progress:
            progress(f"ffmpeg trobat: {existing}")
        return existing

    if not auto_install:
        raise RuntimeError(
            "No s'ha trobat ffmpeg. Instal·la'l o defineix YTLOCAL_FFMPEG amb una carpeta local."
        )

    if os.name != "nt":
        raise RuntimeError(
            "No s'ha trobat ffmpeg al PATH. Instal·la ffmpeg al sistema i torna-ho a provar."
        )

    home = ffmpeg_home()
    home.mkdir(parents=True, exist_ok=True)
    if progress:
        progress("No s'ha trobat ffmpeg — descarregant versió portable (una vegada, ~100 MB)…")

    with tempfile.TemporaryDirectory(prefix="ytlocal-ffmpeg-") as tmp:
        zip_path = Path(tmp) / "ffmpeg-essentials.zip"
        try:
            _download(FFMPEG_ZIP_URL, zip_path, progress=progress)
        except Exception as exc:
            raise RuntimeError(
                f"No s'ha pogut descarregar ffmpeg automàticament: {exc}. "
                "Instal·la ffmpeg manualment i assegura't que estigui al PATH."
            ) from exc
        exe = _install_from_zip(zip_path, home, progress=progress)

    if progress:
        progress(f"ffmpeg a punt: {exe}")
    return exe


def print_progress(message: str) -> None:
    sys.stdout.write(f"\r{message:<80}")
    sys.stdout.flush()
    if not message.endswith("%") and "MB" not in message:
        sys.stdout.write("\n")
