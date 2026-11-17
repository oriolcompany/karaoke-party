"""YouTube download runtime selection."""

from __future__ import annotations

from ytlocal.downloader import youtube_extractor_args
from ytlocal.error_messages import friendly_reason
from ytlocal.js_runtime import _parse_version, ensure_node


def test_youtube_clients_follow_yt_dlp_defaults() -> None:
    clients = youtube_extractor_args()["youtube"]["player_client"]
    assert clients[0] == "default"
    assert "web" not in clients
    assert "mweb" not in clients


def test_format_error_is_explained() -> None:
    text = friendly_reason(
        "ERROR: [youtube] abcdefghijk: Requested format is not available. "
        "Use --list-formats for a list of available formats"
    )
    assert "YouTube" in text
    assert "list-formats" not in text


def test_parse_deno_version() -> None:
    assert _parse_version("deno 2.3.1 (release, x86_64-pc-windows-msvc)") == (2, 3, 1)
    assert _parse_version("v22.14.0") == (22, 14, 0)
    assert _parse_version("no version") is None


def test_ensure_node_does_not_install_when_disabled(monkeypatch) -> None:
    def fail_winget(*_args, **_kwargs):
        raise AssertionError("winget no s'ha de cridar")

    monkeypatch.setattr("ytlocal.js_runtime._find_node", lambda: None)
    monkeypatch.setattr("ytlocal.js_runtime._install_node_with_winget", fail_winget)
    assert ensure_node(auto_install=False) is None


def test_ensure_node_uses_winget_when_missing(monkeypatch, tmp_path) -> None:
    calls: list[str] = []
    node = tmp_path / "node.exe"
    node.write_bytes(b"")

    monkeypatch.setattr("ytlocal.js_runtime.os.name", "nt")
    monkeypatch.setattr(
        "ytlocal.js_runtime._install_node_with_winget",
        lambda _progress: calls.append("winget"),
    )

    def found_after_install() -> Path | None:
        if calls:
            return node
        return None

    monkeypatch.setattr("ytlocal.js_runtime._find_node", found_after_install)
    assert ensure_node(auto_install=True) == node
    assert calls == ["winget"]
