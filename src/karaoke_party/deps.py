"""Startup dependency checks for Karaoke Party.

Whisper alignment needs stem separation first, and syllable timings need
Meta MMS (torchaudio). Those extras plus ffmpeg are required on start.
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DependencyIssue:
    name: str
    detail: str
    fix: str

    def format(self) -> str:
        return f"{self.name}: {self.detail}\n  → {self.fix}"


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


_BASE_MODULES = (
    "fastapi",
    "uvicorn",
    "mutagen",
    "httpx",
    "multipart",
    "yt_dlp",
    "yt_dlp_ejs",
    "acoustid",
)
_ALIGN_MODULE = "faster_whisper"
_STEM_MODULES = ("audio_separator", "torchaudio")


def _project_root() -> Path | None:
    """Repo root when this file lives in the source tree."""
    for parent in Path(__file__).resolve().parents:
        marker = parent / "pyproject.toml"
        if not marker.is_file():
            continue
        try:
            text = marker.read_text(encoding="utf-8")
        except OSError:
            continue
        if "karaoke-party" in text:
            return parent
    return None


def _ffmpeg_home() -> Path:
    from karaoke_party.config import app_cache_root

    return app_cache_root() / "ffmpeg"


def _find_ffmpeg_exe(root: Path) -> Path | None:
    name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    direct = root / "bin" / name
    if direct.is_file():
        return direct
    if not root.is_dir():
        return None
    matches = sorted(path for path in root.rglob(name) if path.is_file())
    return matches[0] if matches else None


def _prepend_path(directory: Path) -> None:
    directory_text = str(directory)
    current = os.environ.get("PATH", "")
    parts = [part for part in current.split(os.pathsep) if part]
    if any(part.lower() == directory_text.lower() for part in parts):
        return
    os.environ["PATH"] = directory_text + (os.pathsep + current if current else "")


def _pip_install(root: Path, spec: str) -> None:
    command = [sys.executable, "-m", "pip", "install", "-e", spec]
    result = subprocess.run(command, cwd=root)
    if result.returncode != 0:
        raise SystemExit(f"pip install -e {spec} ha fallat (codi {result.returncode})")


def ensure_python_packages(*, stream=None) -> None:
    """Install missing Python packages into the current interpreter.

    No-op when everything is already importable, or when running a frozen EXE
    that cannot pip-install into itself. A fresh machine needs the source tree
    (``pyproject.toml``) so extras can be installed from there.
    """
    if getattr(sys, "frozen", False):
        return
    missing_base = [name for name in _BASE_MODULES if not _module_available(name)]
    missing_align = not _module_available(_ALIGN_MODULE)
    missing_stems = [name for name in _STEM_MODULES if not _module_available(name)]
    if not missing_base and not missing_align and not missing_stems:
        return

    root = _project_root()
    out = stream or sys.stdout
    if root is None:
        print(
            "Karaoke Party: falten paquets i no es troba el codi font per instal·lar-los.",
            file=out,
            flush=True,
        )
        return

    print("Instal·lant dependències que falten (només la primera vegada)…", file=out, flush=True)
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        cwd=root,
        check=False,
    )
    if missing_base:
        print("       Paquet base (web, etiquetes, YouTube, AcoustID)…", file=out, flush=True)
        _pip_install(root, ".")
    if missing_align:
        print("       Whisper (alineació de lletres)…", file=out, flush=True)
        _pip_install(root, ".[align]")
    if missing_stems:
        from karaoke_party.gpu_setup import has_nvidia_gpu

        specs = [".[stems]", ".[stems-cpu]"] if has_nvidia_gpu() else [".[stems-cpu]"]
        installed = False
        for spec in specs:
            label = "GPU NVIDIA" if spec == ".[stems]" else "CPU"
            print(f"       Separació de pistes ({label})…", file=out, flush=True)
            try:
                _pip_install(root, spec)
            except SystemExit:
                if spec == specs[-1]:
                    raise
                print("       La instal·lació GPU ha fallat · provant CPU…", file=out, flush=True)
                continue
            installed = True
            break
        if not installed:
            raise SystemExit("No s'ha pogut instal·lar la separació de pistes")
    importlib.invalidate_caches()


def ensure_ffmpeg(*, stream=None) -> Path | None:
    """Return ffmpeg, downloading a portable Windows build into the app cache."""
    found = shutil.which("ffmpeg")
    if found:
        return Path(found)

    cached = _find_ffmpeg_exe(_ffmpeg_home())
    if cached is not None:
        _prepend_path(cached.parent)
        return cached

    if os.name != "nt":
        return None

    out = stream or sys.stdout
    home = _ffmpeg_home()
    home.mkdir(parents=True, exist_ok=True)
    os.environ["YTLOCAL_FFMPEG"] = str(home)
    print(
        "No s'ha trobat ffmpeg. Descarregant una versió portable (~100 MB, una vegada)…",
        file=out,
        flush=True,
    )
    try:
        from ytlocal.ffmpeg_setup import ensure_ffmpeg as download_ffmpeg

        exe = download_ffmpeg(
            progress=lambda message: print(f"       {message}", file=out, flush=True)
        )
    except Exception as exc:  # noqa: BLE001 — surface a clear message, caller rechecks
        print(f"       No s'ha pogut descarregar ffmpeg: {exc}", file=out, flush=True)
        return None
    _prepend_path(Path(exe).parent)
    return Path(exe)


def check_dependencies() -> list[DependencyIssue]:
    """Return missing required runtime dependencies (empty when ready)."""
    issues: list[DependencyIssue] = []

    for module, label in (
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("mutagen", "mutagen"),
        ("httpx", "httpx"),
        ("multipart", "python-multipart"),
        ("yt_dlp", "yt-dlp"),
        ("yt_dlp_ejs", "yt-dlp-ejs"),
        ("acoustid", "pyacoustid"),
    ):
        if not _module_available(module):
            issues.append(
                DependencyIssue(
                    name=label,
                    detail="paquet base no instal·lat",
                    fix='pip install -e .',
                )
            )

    if not _module_available("faster_whisper"):
        issues.append(
            DependencyIssue(
                name="faster-whisper",
                detail="necessari per alinear lletres amb Whisper",
                fix='pip install -e ".[align]"',
            )
        )

    if not _module_available("audio_separator"):
        issues.append(
            DependencyIssue(
                name="audio-separator",
                detail="necessari per separar veu/instrumental (i per Whisper)",
                fix='pip install -e ".[stems]"   # GPU NVIDIA\n'
                '     o  pip install -e ".[stems-cpu]"   # només CPU',
            )
        )

    if not _module_available("torchaudio"):
        issues.append(
            DependencyIssue(
                name="torchaudio",
                detail="necessari per alinear síl·labes amb Meta MMS",
                fix='pip install torchaudio   # o  pip install -e ".[stems]"',
            )
        )

    if shutil.which("ffmpeg") is None:
        issues.append(
            DependencyIssue(
                name="ffmpeg",
                detail="no es troba al PATH (cal per generar stems MP3)",
                fix="KaraokeParty.bat el descarrega sol. Si ha fallat: https://ffmpeg.org/download.html",
            )
        )

    return issues


def ensure_js_runtime(*, stream=None) -> None:
    """Install Node.js 22+ when YouTube's challenge solver has no runtime yet."""
    out = stream or sys.stdout
    try:
        from ytlocal.js_runtime import resolve_js_runtimes

        resolve_js_runtimes(
            progress=lambda message: print(f"       {message}", file=out, flush=True)
        )
    except Exception as exc:  # noqa: BLE001 — downloads still work via yt-dlp's basic clients
        print(f"       Node.js no s'ha pogut preparar: {exc}", file=out, flush=True)


def ensure_dependencies(*, stream=None) -> list[DependencyIssue]:
    """Install anything missing, then report what is still absent."""
    ensure_python_packages(stream=stream)
    ensure_ffmpeg(stream=stream)
    ensure_js_runtime(stream=stream)
    return check_dependencies()


def require_dependencies(*, stream=None, install: bool = True) -> None:
    """Install missing dependencies, then exit if something is still missing."""
    issues = ensure_dependencies(stream=stream) if install else check_dependencies()
    if not issues:
        return
    out = stream or sys.stderr
    print("Karaoke Party: falten dependències necessàries:\n", file=out)
    for issue in issues:
        print(f" • {issue.format()}\n", file=out)
    print("Torna a executar KaraokeParty.bat perquè les instal·li, o fes-ho a mà.", file=out)
    raise SystemExit(1)


def main(argv: list[str] | None = None) -> int:
    """CLI used by KaraokeParty.bat before the server starts."""
    del argv
    print("Comprovant dependències…", flush=True)
    try:
        issues = ensure_dependencies()
    except SystemExit as exc:
        if exc.code not in (0, None):
            print(exc, file=sys.stderr)
            return int(exc.code) if isinstance(exc.code, int) else 1
        return 0
    if issues:
        for issue in issues:
            print(f" • {issue.format()}", file=sys.stderr)
        return 1
    print("Dependències a punt.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
