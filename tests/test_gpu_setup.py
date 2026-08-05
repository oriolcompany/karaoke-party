"""GPU / CUDA bootstrap helpers."""

from __future__ import annotations

from karaoke_party.gpu_setup import GpuStatus, preferred_torch_cuda_tag


def test_preferred_torch_cuda_tag_picks_highest_compatible() -> None:
    assert preferred_torch_cuda_tag("13.3") == "cu130"
    assert preferred_torch_cuda_tag("12.8") == "cu128"
    assert preferred_torch_cuda_tag("12.6") == "cu126"
    assert preferred_torch_cuda_tag("12.1") == "cu121"
    assert preferred_torch_cuda_tag("11.8") == "cu118"
    assert preferred_torch_cuda_tag("bogus") == "cu126"


def test_gpu_status_ok_without_nvidia() -> None:
    status = GpuStatus(has_nvidia=False)
    assert status.ok is True


def test_gpu_status_requires_torch_and_cublas_when_nvidia() -> None:
    broken = GpuStatus(
        has_nvidia=True,
        torch_cuda_available=False,
        whisper_cublas12_ok=False,
    )
    assert broken.ok is False

    conflict = GpuStatus(
        has_nvidia=True,
        torch_cuda_available=True,
        whisper_cublas12_ok=True,
        conflicting_cudnn_cu12=True,
    )
    assert conflict.ok is False

    ready = GpuStatus(
        has_nvidia=True,
        torch_cuda_available=True,
        whisper_cublas12_ok=True,
    )
    assert ready.ok is True


def test_ensure_gpu_cpu_only_is_noop(monkeypatch, capsys) -> None:
    from karaoke_party import gpu_setup

    monkeypatch.setattr(gpu_setup, "has_nvidia_gpu", lambda: False)
    status = gpu_setup.ensure_gpu(install=True)
    assert status.has_nvidia is False
    assert status.ok is True
    assert "CPU" in capsys.readouterr().out


def test_ensure_gpu_repairs_missing_cuda(monkeypatch, capsys) -> None:
    from karaoke_party import gpu_setup

    monkeypatch.setattr(gpu_setup, "has_nvidia_gpu", lambda: True)
    monkeypatch.setattr(gpu_setup, "_gpu_name", lambda: "Fake GPU")
    monkeypatch.setattr(gpu_setup, "_driver_cuda_version", lambda: "13.3")

    probes = iter(
        [
            (True, "2.0.0+cpu", "", False),  # before repair
            (True, "2.0.0+cu130", "13.0", True),  # after torch
        ]
    )
    cublas = iter([False, True])
    packages = {"nvidia-cudnn-cu12": True}

    monkeypatch.setattr(gpu_setup, "_probe_torch", lambda: next(probes))
    monkeypatch.setattr(gpu_setup, "_probe_cublas12", lambda: next(cublas))
    monkeypatch.setattr(
        gpu_setup,
        "_package_installed",
        lambda name: packages.get(name, False),
    )

    installed: list[str] = []

    def fake_torch(tag: str, stream=None) -> None:
        installed.append(f"torch/{tag}")

    def fake_cuda12(stream=None) -> None:
        installed.append("cuda12")

    def fake_uninstall(names: list[str], stream=None) -> None:
        for name in names:
            packages[name] = False
            installed.append(f"uninstall:{name}")

    monkeypatch.setattr(gpu_setup, "_install_torch_cuda", fake_torch)
    monkeypatch.setattr(gpu_setup, "_install_cuda12_libs", fake_cuda12)
    monkeypatch.setattr(gpu_setup, "_pip_uninstall", fake_uninstall)

    status = gpu_setup.ensure_gpu(install=True)
    assert status.ok is True
    assert "torch/cu130" in status.repaired
    assert "remove-cudnn-cu12" in status.repaired
    assert "cuda12-libs" in status.repaired
    assert installed == [
        "torch/cu130",
        "uninstall:nvidia-cudnn-cu12",
        "cuda12",
    ]
    out = capsys.readouterr().out
    assert "Fake GPU" in out
