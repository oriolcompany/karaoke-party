"""Startup dependency checks."""

from __future__ import annotations

import pytest

from karaoke_party.deps import DependencyIssue, check_dependencies, require_dependencies


def test_check_dependencies_reports_missing_modules(monkeypatch) -> None:
    monkeypatch.setattr(
        "karaoke_party.deps._module_available",
        lambda name: name not in {"faster_whisper", "audio_separator"},
    )
    monkeypatch.setattr("karaoke_party.deps.shutil.which", lambda _name: "C:/ffmpeg.exe")

    issues = check_dependencies()
    names = {issue.name for issue in issues}
    assert "faster-whisper" in names
    assert "audio-separator" in names
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
        require_dependencies()
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "audio-separator" in err
    assert "stems" in err


def test_require_dependencies_ok_when_empty(monkeypatch) -> None:
    monkeypatch.setattr("karaoke_party.deps.check_dependencies", lambda: [])
    require_dependencies()  # does not raise
