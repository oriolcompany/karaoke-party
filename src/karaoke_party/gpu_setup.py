"""Detect NVIDIA GPUs and repair the CUDA stack before the server starts.

Whisper (ctranslate2) needs CUDA 12 cuBLAS DLLs; Demucs/torch may need a
CUDA-enabled wheel that matches the driver. On a fresh machine it is common to
end up with a CPU-only torch (or CUDA 13 torch without the CUDA 12 libs Whisper
loads). This module diagnoses that and installs the missing pieces.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from shutil import which


# Highest torch CUDA tag whose runtime the driver can load.
_TORCH_CUDA_TAGS: tuple[tuple[float, str], ...] = (
    (13.0, "cu130"),
    (12.8, "cu128"),
    (12.6, "cu126"),
    (12.4, "cu124"),
    (12.1, "cu121"),
    (11.8, "cu118"),
)

# faster-whisper / ctranslate2 on Windows need CUDA 12 cuBLAS/runtime.
# Do NOT install nvidia-cudnn-cu12 next to torch cu13: adding those DLLs to the
# process search path mixes cuDNN builds and Demucs dies with
# CUDNN_STATUS_SUBLIBRARY_VERSION_MISMATCH.
_CUDA12_PACKAGES = (
    "nvidia-cublas-cu12",
    "nvidia-cuda-runtime-cu12",
    "nvidia-cuda-nvrtc-cu12",
)
_CONFLICTING_CUDNN_PACKAGE = "nvidia-cudnn-cu12"


@dataclass
class GpuStatus:
    has_nvidia: bool = False
    gpu_name: str = ""
    driver_cuda: str = ""
    torch_installed: bool = False
    torch_version: str = ""
    torch_cuda_build: str = ""
    torch_cuda_available: bool = False
    whisper_cublas12_ok: bool = False
    conflicting_cudnn_cu12: bool = False
    preferred_torch_tag: str = ""
    repaired: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        if not self.has_nvidia:
            return True
        return (
            self.torch_cuda_available
            and self.whisper_cublas12_ok
            and not self.conflicting_cudnn_cu12
            and not self.errors
        )

    def to_dict(self) -> dict:
        data = asdict(self)
        data["ok"] = self.ok
        return data


def _run(
    command: list[str],
    *,
    timeout: float = 120.0,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def _python() -> str:
    return sys.executable


def has_nvidia_gpu() -> bool:
    """True when nvidia-smi is on PATH and talks to a GPU."""
    if which("nvidia-smi") is None:
        return False
    try:
        result = _run(["nvidia-smi", "-L"], timeout=20.0)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0 and bool((result.stdout or "").strip())


def _gpu_name() -> str:
    try:
        result = _run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            timeout=20.0,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if result.returncode != 0:
        return ""
    line = (result.stdout or "").strip().splitlines()
    return line[0].strip() if line else ""


def _driver_cuda_version() -> str:
    """Max CUDA version the installed driver claims to support."""
    try:
        result = _run(["nvidia-smi"], timeout=20.0)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    text = f"{result.stdout or ''}\n{result.stderr or ''}"
    match = re.search(r"CUDA(?: UMD)? Version:\s*([\d.]+)", text, flags=re.IGNORECASE)
    return match.group(1) if match else ""


def preferred_torch_cuda_tag(driver_cuda: str) -> str:
    """Pick a torch wheel tag the driver can run (highest compatible)."""
    try:
        version = float(".".join(driver_cuda.split(".")[:2]))
    except ValueError:
        version = 12.6
    for minimum, tag in _TORCH_CUDA_TAGS:
        if version >= minimum:
            return tag
    return "cu118"


def _probe_torch() -> tuple[bool, str, str, bool]:
    """Return (installed, version, cuda_build, cuda_available) in a child process.

    A child process keeps a failed/old torch import from poisoning this one
    after we reinstall the wheel.
    """
    script = r"""
import json, sys
try:
    import torch
except Exception as exc:
    print(json.dumps({"installed": False, "version": "", "cuda_build": "", "cuda": False, "error": str(exc)}))
    sys.exit(0)
print(json.dumps({
    "installed": True,
    "version": str(getattr(torch, "__version__", "") or ""),
    "cuda_build": str(getattr(torch.version, "cuda", None) or ""),
    "cuda": bool(torch.cuda.is_available()),
}))
"""
    try:
        result = _run([_python(), "-c", script], timeout=60.0)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, "", "", False
    try:
        import json

        data = json.loads((result.stdout or "").strip() or "{}")
    except ValueError:
        return False, "", "", False
    return (
        bool(data.get("installed")),
        str(data.get("version") or ""),
        str(data.get("cuda_build") or ""),
        bool(data.get("cuda")),
    )


def _probe_cublas12() -> bool:
    """True when Whisper's CUDA 12 cuBLAS can be loaded (Windows-sensitive)."""
    if os.name != "nt":
        # On Linux the system/driver libs are usually enough.
        return True
    script = r"""
import os, sys
from pathlib import Path
allow = {"cublas", "cuda_runtime", "cuda_nvrtc"}
candidates = []
try:
    import torch
    candidates.append(Path(torch.__file__).resolve().parent / "lib")
except Exception:
    pass
try:
    import nvidia
    for root in nvidia.__path__:
        for path in sorted(Path(root).glob("*/bin")):
            if path.parent.name.lower() in allow:
                candidates.append(path)
except Exception:
    pass
for path in candidates:
    if path.is_dir():
        try:
            os.add_dll_directory(str(path))
        except OSError:
            pass
try:
    import ctypes
    ctypes.WinDLL("cublas64_12.dll")
    sys.exit(0)
except OSError:
    sys.exit(1)
"""
    try:
        result = _run([_python(), "-c", script], timeout=60.0)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def _package_installed(name: str) -> bool:
    # Dist names like nvidia-cudnn-cu12 are not always importable modules.
    script = (
        "import sys\n"
        "try:\n"
        "    from importlib.metadata import distribution\n"
        f"    distribution({name!r})\n"
        "    sys.exit(0)\n"
        "except Exception:\n"
        "    sys.exit(1)\n"
    )
    try:
        result = _run([_python(), "-c", script], timeout=30.0)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def _pip_install(packages: list[str], *, extra_args: list[str] | None = None, stream=None) -> None:
    out = stream or sys.stdout
    command = [_python(), "-m", "pip", "install", "--upgrade", *(extra_args or []), *packages]
    print(f"       pip install {' '.join(packages)}", file=out, flush=True)
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"pip ha fallat instal·lant: {', '.join(packages)}")


def _pip_uninstall(packages: list[str], stream=None) -> None:
    out = stream or sys.stdout
    command = [_python(), "-m", "pip", "uninstall", "-y", *packages]
    print(f"       pip uninstall {' '.join(packages)}", file=out, flush=True)
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"pip ha fallat desinstal·lant: {', '.join(packages)}")


def _install_torch_cuda(tag: str, stream=None) -> None:
    index = f"https://download.pytorch.org/whl/{tag}"
    # torchvision shares the same CUDA tag on the pytorch index; installing both
    # avoids leaving a CPU torchvision next to a CUDA torch.
    _pip_install(
        ["torch", "torchvision"],
        extra_args=["--index-url", index, "--extra-index-url", "https://pypi.org/simple"],
        stream=stream,
    )


def _install_cuda12_libs(stream=None) -> None:
    _pip_install(list(_CUDA12_PACKAGES), stream=stream)


def _torch_needs_no_cudnn_cu12(cuda_build: str) -> bool:
    """True when torch's own CUDA runtime would clash with nvidia-cudnn-cu12."""
    try:
        return float(".".join((cuda_build or "0").split(".")[:2])) >= 13.0
    except ValueError:
        return "cu13" in (cuda_build or "")


def diagnose() -> GpuStatus:
    """Read-only snapshot of GPU / torch / Whisper CUDA readiness."""
    status = GpuStatus()
    if not has_nvidia_gpu():
        status.messages.append("No s’ha detectat GPU NVIDIA · s’usarà CPU")
        return status

    status.has_nvidia = True
    status.gpu_name = _gpu_name()
    status.driver_cuda = _driver_cuda_version()
    status.preferred_torch_tag = preferred_torch_cuda_tag(status.driver_cuda)
    installed, version, cuda_build, cuda_ok = _probe_torch()
    status.torch_installed = installed
    status.torch_version = version
    status.torch_cuda_build = cuda_build
    status.torch_cuda_available = cuda_ok
    status.whisper_cublas12_ok = _probe_cublas12()
    status.conflicting_cudnn_cu12 = bool(
        status.torch_cuda_available
        and _torch_needs_no_cudnn_cu12(status.torch_cuda_build)
        and _package_installed(_CONFLICTING_CUDNN_PACKAGE)
    )

    label = status.gpu_name or "NVIDIA GPU"
    status.messages.append(
        f"GPU detectada: {label}"
        + (f" · driver CUDA {status.driver_cuda}" if status.driver_cuda else "")
    )
    if status.torch_cuda_available:
        status.messages.append(
            f"PyTorch CUDA OK ({status.torch_version or 'torch'}"
            + (f", build {status.torch_cuda_build}" if status.torch_cuda_build else "")
            + ")"
        )
    elif status.torch_installed:
        status.messages.append(
            f"PyTorch instal·lat sense CUDA usable ({status.torch_version or 'torch'})"
        )
    else:
        status.messages.append("PyTorch no està instal·lat")

    if status.whisper_cublas12_ok:
        status.messages.append("Llibreries CUDA 12 (Whisper) OK")
    else:
        status.messages.append("Falten llibreries CUDA 12 per a Whisper (cuBLAS)")
    if status.conflicting_cudnn_cu12:
        status.messages.append(
            "Conflicte: nvidia-cudnn-cu12 trenca Demucs amb PyTorch CUDA 13"
        )
    return status


def ensure_gpu(*, install: bool = True, stream=None) -> GpuStatus:
    """Diagnose and, when possible, repair the CUDA stack for this venv."""
    out = stream or sys.stdout
    if getattr(sys, "frozen", False):
        # PyInstaller builds cannot pip-install into themselves.
        status = diagnose()
        if status.has_nvidia and not status.ok:
            status.errors.append(
                "La build empaquetada no pot reparar CUDA sola · "
                "fes servir KaraokeParty.bat al repo o reinstal·la el venv"
            )
        for line in status.messages:
            print(f"       {line}", file=out, flush=True)
        for err in status.errors:
            print(f"       ! {err}", file=out, flush=True)
        return status

    status = diagnose()
    for line in status.messages:
        print(f"       {line}", file=out, flush=True)

    if not status.has_nvidia:
        return status

    if not install:
        if not status.ok:
            status.errors.append("GPU present però CUDA no està a punt (install=False)")
        return status

    try:
        if not status.torch_cuda_available:
            tag = status.preferred_torch_tag or "cu126"
            print(f"       Instal·lant PyTorch amb {tag}…", file=out, flush=True)
            _install_torch_cuda(tag, stream=out)
            status.repaired.append(f"torch/{tag}")
            installed, version, cuda_build, cuda_ok = _probe_torch()
            status.torch_installed = installed
            status.torch_version = version
            status.torch_cuda_build = cuda_build
            status.torch_cuda_available = cuda_ok
            if not cuda_ok:
                # Fall back one step (e.g. brand-new driver / missing wheel).
                fallback = _fallback_tag(tag)
                if fallback and fallback != tag:
                    print(f"       {tag} no ha activat CUDA · provant {fallback}…", file=out, flush=True)
                    _install_torch_cuda(fallback, stream=out)
                    status.repaired.append(f"torch/{fallback}")
                    installed, version, cuda_build, cuda_ok = _probe_torch()
                    status.torch_installed = installed
                    status.torch_version = version
                    status.torch_cuda_build = cuda_build
                    status.torch_cuda_available = cuda_ok
            if not status.torch_cuda_available:
                raise RuntimeError(
                    "PyTorch s’ha instal·lat però torch.cuda.is_available() segueix False"
                )
            print(
                f"       PyTorch CUDA OK ({status.torch_version}, build {status.torch_cuda_build})",
                file=out,
                flush=True,
            )
            status.conflicting_cudnn_cu12 = bool(
                _torch_needs_no_cudnn_cu12(status.torch_cuda_build)
                and _package_installed(_CONFLICTING_CUDNN_PACKAGE)
            )

        if status.conflicting_cudnn_cu12:
            print(
                "       Treient nvidia-cudnn-cu12 (conflicte amb PyTorch CUDA 13)…",
                file=out,
                flush=True,
            )
            _pip_uninstall([_CONFLICTING_CUDNN_PACKAGE], stream=out)
            status.repaired.append("remove-cudnn-cu12")
            status.conflicting_cudnn_cu12 = _package_installed(_CONFLICTING_CUDNN_PACKAGE)
            if status.conflicting_cudnn_cu12:
                raise RuntimeError("No s’ha pogut desinstal·lar nvidia-cudnn-cu12")
            print("       Conflicte cuDNN eliminat", file=out, flush=True)

        if not status.whisper_cublas12_ok:
            print("       Instal·lant llibreries CUDA 12 per a Whisper…", file=out, flush=True)
            _install_cuda12_libs(stream=out)
            status.repaired.append("cuda12-libs")
            status.whisper_cublas12_ok = _probe_cublas12()
            if not status.whisper_cublas12_ok:
                raise RuntimeError("No s’ha pogut carregar cublas64_12.dll després de la instal·lació")
            print("       Llibreries CUDA 12 OK", file=out, flush=True)
    except Exception as exc:  # noqa: BLE001 — surface as status, caller decides exit
        status.errors.append(str(exc) or exc.__class__.__name__)
        print(f"       ! {status.errors[-1]}", file=out, flush=True)

    if status.ok:
        if status.repaired:
            print("       GPU / CUDA reparat i a punt", file=out, flush=True)
        else:
            print("       GPU / CUDA ja estava a punt", file=out, flush=True)
    return status


def _fallback_tag(tag: str) -> str:
    tags = [item[1] for item in _TORCH_CUDA_TAGS]
    try:
        index = tags.index(tag)
    except ValueError:
        return "cu126"
    return tags[index + 1] if index + 1 < len(tags) else ""


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    install = "--check-only" not in args
    print("Comprovant GPU / CUDA…", flush=True)
    status = ensure_gpu(install=install)
    if status.has_nvidia and not status.ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
