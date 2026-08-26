"""Transient LRCLIB failures must not be cached as "this song has no lyrics"."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from karaoke_party import lyrics as lyrics_mod
from karaoke_party.lyrics import (
    LyricsUnavailable,
    cache_key,
    clear_lyrics_cache,
    clear_lyrics_keys,
    clear_probe_errors,
    fetch_lyrics,
    load_cached,
    lyrics_status_and_source,
    save_cached,
    LyricsPayload,
)

SYNCED = "[00:10.00]Hello\n[00:12.00]World\n"


def _client_factory(handler):
    transport = httpx.MockTransport(handler)
    original = httpx.AsyncClient

    class PatchedClient(original):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = transport
            super().__init__(*args, **kwargs)

    return PatchedClient


@pytest.mark.anyio
async def test_throttled_lookup_raises_instead_of_caching_miss(tmp_path: Path, monkeypatch) -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(429, headers={"retry-after": "0"}, json={})

    monkeypatch.setattr(httpx, "AsyncClient", _client_factory(handler))
    monkeypatch.setattr(lyrics_mod, "RETRY_BASE_DELAY", 0.0)

    with pytest.raises(LyricsUnavailable):
        await fetch_lyrics(artist="A", title="B", cache_dir=tmp_path)

    assert calls["n"] >= 3  # LRCLIB, then lyrics.ovh if LRCLIB stays throttled
    assert list(tmp_path.glob("*.json")) == []  # nothing cached as a miss


@pytest.mark.anyio
async def test_retry_recovers_and_caches_lyrics(tmp_path: Path, monkeypatch) -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(503)
        return httpx.Response(200, json={"syncedLyrics": SYNCED, "plainLyrics": "Hello\nWorld"})

    monkeypatch.setattr(httpx, "AsyncClient", _client_factory(handler))
    monkeypatch.setattr(lyrics_mod, "RETRY_BASE_DELAY", 0.0)

    payload = await fetch_lyrics(artist="A", title="B", cache_dir=tmp_path)

    assert payload.synced is True
    assert [line.text for line in payload.lines] == ["Hello", "World"]
    cached = load_cached(tmp_path, cache_key("A", "B", None))
    assert cached is not None and cached.lines


@pytest.mark.anyio
async def test_genuine_missing_lyrics_is_cached_as_none(tmp_path: Path, monkeypatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/get":
            return httpx.Response(404, json={})
        return httpx.Response(200, json=[])

    monkeypatch.setattr(httpx, "AsyncClient", _client_factory(handler))
    monkeypatch.setattr(lyrics_mod, "RETRY_BASE_DELAY", 0.0)

    payload = await fetch_lyrics(artist="A", title="B", cache_dir=tmp_path)

    assert payload.lines == []
    cached = load_cached(tmp_path, cache_key("A", "B", None))
    assert cached is not None
    assert cached.source == "none"


def test_clear_probe_errors_only_removes_error_entries(tmp_path: Path) -> None:
    save_cached(
        tmp_path,
        cache_key("A", "Bad", None),
        LyricsPayload(synced=False, source="probe-error", lines=[], plain=""),
    )
    save_cached(
        tmp_path,
        cache_key("A", "NoLyrics", None),
        LyricsPayload(synced=False, source="none", lines=[], plain=""),
    )

    assert clear_probe_errors(tmp_path) == 1

    status, source = lyrics_status_and_source(
        "A", "Bad", None, lyrics_cache=tmp_path, aligned_cache=None
    )
    assert status is None  # retryable again
    status, source = lyrics_status_and_source(
        "A", "NoLyrics", None, lyrics_cache=tmp_path, aligned_cache=None
    )
    assert status is False and source == "none"


def test_clear_lyrics_cache_removes_all_entries(tmp_path: Path) -> None:
    save_cached(
        tmp_path,
        cache_key("A", "Hit", None),
        LyricsPayload(synced=True, source="lrclib", lines=[], plain="hi"),
    )
    save_cached(
        tmp_path,
        cache_key("A", "Miss", None),
        LyricsPayload(synced=False, source="none", lines=[], plain=""),
    )
    assert clear_lyrics_cache(tmp_path) == 2
    assert list(tmp_path.rglob("lyrics.json")) == []


def test_clear_lyrics_keys_removes_only_selected(tmp_path: Path) -> None:
    hit = cache_key("A", "Hit", None)
    miss = cache_key("A", "Miss", None)
    save_cached(tmp_path, hit, LyricsPayload(synced=True, source="lrclib", lines=[], plain="hi"))
    save_cached(tmp_path, miss, LyricsPayload(synced=False, source="none", lines=[], plain=""))
    assert clear_lyrics_keys(tmp_path, [miss]) == 1
    assert (tmp_path / hit / "lyrics.json").is_file()
    assert not (tmp_path / miss / "lyrics.json").exists()


@pytest.fixture
def anyio_backend():
    return "asyncio"
