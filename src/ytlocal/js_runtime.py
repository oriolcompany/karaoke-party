"""Locate Node.js (or an existing Deno) for yt-dlp's YouTube challenges.

Deno is not downloaded. A missing Node.js 22+ is installed with winget, which
uses the Windows certificate store. Python's own downloader fails on some PCs
with CERTIFICATE_VERIFY_FAILED.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Callable

ProgressFn = Callable[[str], None]

_DENO_MIN = (2, 3, 0)
_NODE_MIN = (22, 0, 0)
_VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")
_WINGET_NODE_ID = "OpenJS.NodeJS.LTS"


def _parse_version(text: str) -> tuple[int, int, int] | None:
    match = _VERSION_RE.search(text or "")
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def _binary_version(path: Path) -> tuple[int, int, int] | None:
    try:
        result = subprocess.run(
            [str(path), "--version"],
            capture_output=True,
            text=True,
            timeout=20,
            cwd=str(path.parent),
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return _parse_version(f"{result.stdout}\n{result.stderr}")


def _acceptable(path: Path | None, minimum: tuple[int, int, int]) -> Path | None:
    if path is None or not path.is_file():
        return None
    version = _binary_version(path)
    if version is None or version < minimum:
        return None
    return path


def _find_deno() -> Path | None:
    """Use Deno only when it is already installed. Never download it."""
    on_path = shutil.which("deno")
    found = _acceptable(Path(on_path) if on_path else None, _DENO_MIN)
    if found:
        return found
    cached = _cached_deno()
    return _acceptable(cached, _DENO_MIN)


def _cached_deno() -> Path | None:
    base = os.environ.get("KARAOKE_CACHE_DIR", "").strip()
    if not base and os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or ""
        if base:
            base = str(Path(base) / "KaraokeParty")
    if not base:
        return None
    name = "deno.exe" if os.name == "nt" else "deno"
    candidate = Path(base) / "deno" / name
    return candidate if candidate.is_file() else None


def _node_candidates() -> list[Path]:
    paths: list[Path] = []
    on_path = shutil.which("node")
    if on_path:
        paths.append(Path(on_path))
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    local = os.environ.get("LOCALAPPDATA", "")
    paths.append(Path(program_files) / "nodejs" / "node.exe")
    paths.append(Path(program_files_x86) / "nodejs" / "node.exe")
    if local:
        paths.append(Path(local) / "Programs" / "nodejs" / "node.exe")
    return paths


def _find_node() -> Path | None:
    seen: set[str] = set()
    for candidate in _node_candidates():
        key = str(candidate).lower()
        if key in seen:
            continue
        seen.add(key)
        found = _acceptable(candidate, _NODE_MIN)
        if found:
            return found
    return None


def _install_node_with_winget(progress: ProgressFn | None) -> None:
    winget = shutil.which("winget")
    if not winget:
        if progress:
            progress(
                "No s'ha trobat winget. Instal·la Node.js 22 o superior des de https://nodejs.org"
            )
        return
    if progress:
        progress("Instal·lant Node.js 22 o superior (una vegada, per les descàrregues de YouTube)…")
        progress("Si Windows demana permís, accepta'l.")
    subprocess.run(
        [
            winget,
            "install",
            "-e",
            "--id",
            _WINGET_NODE_ID,
            "--accept-package-agreements",
            "--accept-source-agreements",
            "--disable-interactivity",
        ],
        check=False,
    )


def ensure_node(progress: ProgressFn | None = None, *, auto_install: bool = True) -> Path | None:
    """Return Node.js >= 22, installing the LTS with winget on Windows when missing."""
    existing = _find_node()
    if existing:
        return existing
    if not auto_install or os.name != "nt":
        return None
    _install_node_with_winget(progress)
    installed = _find_node()
    if installed and progress:
        progress(f"Node.js a punt: {installed}")
    elif progress:
        progress(
            "No s'ha pogut instal·lar Node.js. "
            "Les descàrregues bàsiques poden funcionar igualment."
        )
    return installed


def resolve_js_runtimes(
    *,
    auto_install: bool = True,
    progress: ProgressFn | None = None,
) -> dict[str, dict[str, str]]:
    """Runtimes yt-dlp will accept. Node 22+ is installed when nothing is present."""
    runtimes: dict[str, dict[str, str]] = {}
    deno = _find_deno()
    node = _find_node()
    if deno is None and node is None and auto_install:
        node = ensure_node(progress=progress)
    if deno:
        runtimes["deno"] = {"path": str(deno)}
    if node:
        runtimes["node"] = {"path": str(node)}
    return runtimes
