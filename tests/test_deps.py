"""Startup dependency checks."""

from __future__ import annotations

import os

import pytest

from karaoke_party.deps import (
    DependencyIssue,
    check_dependencies,
    ensure_ffmpeg,
    ensure_python_packages,
    require_dependencies,
)


def test_check_dependencies_reports_missing_modules(monkeypatch) -> None:
    monkeypatch.setattr(
        "karaoke_party.deps._module_available",
        lambda name: name not in {"faster_whisper", "audio_separator", "torchaudio"},
    )
    monkeypatch.setattr("karaoke_party.deps.shutil.which", lambda _name: "C:/ffmpeg.exe")

    issues = check_dependencies()
    names = {issue.name for issue in issues}
    assert "faster-whisper" in names
    assert "audio-separator" in names
    assert "torchaudio" in names
    assert "ffmpeg" not in names


def test_check_dependencies_reports_missing_ffmpeg(monkeypatch) -> None:
    monkeypatch.setattr("karaoke_party.deps._module_available", lambda _name: True)
    monkeypatch.setattr("karaoke_party.deps.shutil.which", lambda _name: None)

    issues = check_dependencies()
    assert len(issues) == 1
    assert issues[0].name == "ffmpeg"


def test_require_dependencies_exits_when_missing(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "karaoke_party.deps.check_dependencies",
        lambda: [
            DependencyIssue(
                name="audio-separator",
                detail="missing",
                fix='pip install -e ".[stems]"',
            )
        ],
    )
    with pytest.raises(SystemExit) as exc:
        require_dependencies(install=False)
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "audio-separator" in err
    assert "stems" in err


def test_require_dependencies_ok_when_empty(monkeypatch) -> None:
    monkeypatch.setattr("karaoke_party.deps.check_dependencies", lambda: [])
    require_dependencies(install=False)  # does not raise


def test_ensure_python_packages_skips_when_ready(monkeypatch) -> None:
    def fail_pip(*_args, **_kwargs):
        raise AssertionError("pip no s'ha de cridar")

    monkeypatch.setattr("karaoke_party.deps._module_available", lambda _name: True)
    monkeypatch.setattr("karaoke_party.deps._pip_install", fail_pip)
    ensure_python_packages()


def test_ensure_python_packages_installs_missing_base(monkeypatch, tmp_path) -> None:
    calls: list[str] = []
    monkeypatch.setattr("karaoke_party.deps._project_root", lambda: tmp_path)
    monkeypatch.setattr(
        "karaoke_party.deps._module_available",
        lambda name: name != "acoustid",
    )
    monkeypatch.setattr(
        "karaoke_party.deps._pip_install",
        lambda _root, spec: calls.append(spec),
    )
    monkeypatch.setattr(
        "karaoke_party.deps.subprocess.run",
        lambda *_args, **_kwargs: None,
    )
    ensure_python_packages()
    assert calls == ["."]


def test_ensure_ffmpeg_uses_cached_binary(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("PATH", os.environ.get("PATH", ""))
    exe = tmp_path / "build" / "bin" / "ffmpeg.exe"
    exe.parent.mkdir(parents=True)
    exe.write_bytes(b"")
    monkeypatch.setattr("karaoke_party.deps.shutil.which", lambda _name: None)
    monkeypatch.setattr("karaoke_party.deps._ffmpeg_home", lambda: tmp_path)
    found = ensure_ffmpeg()
    assert found == exe
    assert str(exe.parent).lower() in os.environ["PATH"].lower()
