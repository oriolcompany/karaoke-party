"""Startup dependency checks for Karaoke Party.

Whisper alignment always needs stem separation first, so both extras plus
ffmpeg are required before the server starts.
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class DependencyIssue:
    name: str
    detail: str
    fix: str

    def format(self) -> str:
        return f"{self.name}: {self.detail}\n  → {self.fix}"


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def check_dependencies() -> list[DependencyIssue]:
    """Return missing required runtime dependencies (empty when ready)."""
    issues: list[DependencyIssue] = []

    for module, label in (
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("mutagen", "mutagen"),
        ("httpx", "httpx"),
        ("multipart", "python-multipart"),
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

    if shutil.which("ffmpeg") is None:
        issues.append(
            DependencyIssue(
                name="ffmpeg",
                detail="no es troba al PATH (cal per generar stems MP3)",
                fix="Instal·la ffmpeg i afegeix-lo al PATH · https://ffmpeg.org/download.html",
            )
        )

    return issues


def require_dependencies(*, stream=None) -> None:
    """Exit the process if required dependencies are missing."""
    issues = check_dependencies()
    if not issues:
        return
    out = stream or sys.stderr
    print("Karaoke Party: falten dependències necessàries:\n", file=out)
    for issue in issues:
        print(f" • {issue.format()}\n", file=out)
    print("Instal·la el que falta i torna a arrencar.", file=out)
    raise SystemExit(1)
