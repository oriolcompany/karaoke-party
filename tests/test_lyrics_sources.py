"""Local files, relaxed LRCLIB matching, lyrics.ovh, and manual paste."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from mutagen.id3 import ID3, SYLT, USLT

from karaoke_party import lyrics as lyrics_mod
from karaoke_party.lyrics import (
    LyricsPayload,
    cache_key,
    embed_lyrics_in_audio,
    fetch_lyrics,
    load_aligned_cached,
    load_cached,
    lyrics_status_and_source,
    payload_to_text,
    read_local_lyrics,
    save_aligned_cached,
    save_cached,
    save_manual_lyrics,
)
from karaoke_party.lyrics import LyricLine, LyricWord

SYNCED = "[00:10.00]Hello\n[00:12.00]World\n"


def _client_factory(handler):
    transport = httpx.MockTransport(handler)
    original = httpx.AsyncClient

    class PatchedClient(original):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = transport
            super().__init__(*args, **kwargs)

    return PatchedClient


def _audio_stub(path: Path) -> Path:
    path.write_bytes(b"\xff\xfb\x90\x00" * 80)
    return path


@pytest.mark.anyio
async def test_get_retries_without_duration(tmp_path: Path, monkeypatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/get":
            if request.url.params.get("duration"):
                return httpx.Response(404, json={})
            return httpx.Response(200, json={"syncedLyrics": SYNCED, "plainLyrics": "Hello\nWorld"})
        return httpx.Response(200, json=[])

    monkeypatch.setattr(httpx, "AsyncClient", _client_factory(handler))
    monkeypatch.setattr(lyrics_mod, "RETRY_BASE_DELAY", 0.0)

    payload = await fetch_lyrics(artist="A", title="B", album="LP", duration=180, cache_dir=tmp_path)
    assert payload.synced is True
    assert payload.source == "lrclib"
    assert [line.text for line in payload.lines] == ["Hello", "World"]


@pytest.mark.anyio
async def test_search_picks_closest_duration(tmp_path: Path, monkeypatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/get":
            return httpx.Response(404, json={})
        if request.url.path == "/api/search":
            return httpx.Response(
                200,
                json=[
                    {
                        "duration": 90,
                        "syncedLyrics": "[00:01.00]Wrong\n",
                        "plainLyrics": "",
                    },
                    {
                        "duration": 181,
                        "syncedLyrics": "[00:01.00]Right\n",
                        "plainLyrics": "",
                    },
                ],
            )
        return httpx.Response(404, json={})

    monkeypatch.setattr(httpx, "AsyncClient", _client_factory(handler))
    monkeypatch.setattr(lyrics_mod, "RETRY_BASE_DELAY", 0.0)

    payload = await fetch_lyrics(artist="A", title="B", duration=180, cache_dir=tmp_path)
    assert [line.text for line in payload.lines] == ["Right"]
    assert payload.source == "lrclib-search"


@pytest.mark.anyio
async def test_cleaned_title_matches_lrclib(tmp_path: Path, monkeypatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/get":
            if request.url.params.get("track_name") == "Cançó":
                return httpx.Response(
                    200, json={"syncedLyrics": SYNCED, "plainLyrics": "Hello\nWorld"}
                )
            return httpx.Response(404, json={})
        return httpx.Response(200, json=[])

    monkeypatch.setattr(httpx, "AsyncClient", _client_factory(handler))
    monkeypatch.setattr(lyrics_mod, "RETRY_BASE_DELAY", 0.0)

    payload = await fetch_lyrics(
        artist="Artista",
        title="Cançó (feat. Algú)",
        duration=200,
        cache_dir=tmp_path,
    )
    assert payload.source == "lrclib"
    assert [line.text for line in payload.lines] == ["Hello", "World"]


@pytest.mark.anyio
async def test_lyrics_ovh_fallback(tmp_path: Path, monkeypatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.startswith("/v1/"):
            return httpx.Response(
                200,
                json={"lyrics": "Paroles de la chanson Hello par A\n\nHola\nAdéu"},
            )
        if request.url.path == "/api/get":
            return httpx.Response(404, json={})
        return httpx.Response(200, json=[])

    monkeypatch.setattr(httpx, "AsyncClient", _client_factory(handler))
    monkeypatch.setattr(lyrics_mod, "RETRY_BASE_DELAY", 0.0)

    payload = await fetch_lyrics(artist="A", title="B", cache_dir=tmp_path)
    assert payload.source == "lyrics-ovh"
    assert [line.text for line in payload.lines] == ["Hola", "Adéu"]


@pytest.mark.anyio
async def test_ovh_used_when_lrclib_is_down(tmp_path: Path, monkeypatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.startswith("/v1/"):
            return httpx.Response(200, json={"lyrics": "Hola\nAdéu"})
        return httpx.Response(503, json={})

    monkeypatch.setattr(httpx, "AsyncClient", _client_factory(handler))
    monkeypatch.setattr(lyrics_mod, "RETRY_BASE_DELAY", 0.0)

    payload = await fetch_lyrics(artist="A", title="B", cache_dir=tmp_path)
    assert payload.source == "lyrics-ovh"
    assert [line.text for line in payload.lines] == ["Hola", "Adéu"]


@pytest.mark.anyio
async def test_sidecar_lrc_beats_cached_miss(tmp_path: Path) -> None:
    audio = _audio_stub(tmp_path / "song.mp3")
    audio.with_suffix(".lrc").write_text("[00:05.00]Local line\n", encoding="utf-8")
    key = cache_key("A", "B", 10.0)
    save_cached(
        tmp_path,
        key,
        LyricsPayload(synced=False, source="none", lines=[], plain=""),
    )

    payload = await fetch_lyrics(
        artist="A",
        title="B",
        duration=10.0,
        cache_dir=tmp_path,
        audio_path=audio,
    )
    assert payload.source == "local-lrc"
    assert payload.lines[0].text == "Local line"
    cached = load_cached(tmp_path, key)
    assert cached is not None
    assert cached.lines[0].text == "Local line"

    save_cached(
        tmp_path,
        key,
        LyricsPayload(synced=False, source="none", lines=[], plain=""),
    )
    status, source = lyrics_status_and_source(
        "A",
        "B",
        10.0,
        lyrics_cache=tmp_path,
        audio_path=audio,
    )
    assert status is True
    assert source == "local-lrc"


def test_embedded_uslt_and_sylt(tmp_path: Path) -> None:
    uslt_path = _audio_stub(tmp_path / "uslt.mp3")
    tags = ID3()
    tags.add(USLT(encoding=3, lang="eng", desc="", text="Hola\nAdéu"))
    tags.save(uslt_path)
    uslt = read_local_lyrics(uslt_path)
    assert uslt is not None
    assert uslt.source == "local-uslt"
    assert [line.text for line in uslt.lines] == ["Hola", "Adéu"]

    sylt_path = _audio_stub(tmp_path / "sylt.mp3")
    tags = ID3()
    tags.add(
        SYLT(
            encoding=3,
            lang="eng",
            format=2,
            type=1,
            desc="",
            text=[("Hola", 1000), ("món", 1800)],
        )
    )
    tags.save(sylt_path)
    sylt = read_local_lyrics(sylt_path)
    assert sylt is not None
    assert sylt.source == "local-sylt"
    assert sylt.synced is True
    assert "Hola" in sylt.plain


def test_save_manual_lyrics_clears_alignment(tmp_path: Path) -> None:
    key = cache_key("A", "B", 12.0)
    save_aligned_cached(
        tmp_path,
        key,
        LyricsPayload(
            synced=True,
            source="whisper-align",
            lines=[
                LyricLine(
                    time=1.0,
                    text="old",
                    words=[LyricWord(time=1.0, end=1.4, text="old")],
                )
            ],
            plain="old",
        ),
        artist="A",
        title="B",
        duration=12.0,
    )
    assert load_aligned_cached(tmp_path, key) is not None

    payload = save_manual_lyrics(
        tmp_path,
        artist="A",
        title="B",
        duration=12.0,
        text="Nova\nLletra",
        aligned_cache=tmp_path,
    )
    assert payload.source == "manual"
    assert [line.text for line in payload.lines] == ["Nova", "Lletra"]
    assert load_aligned_cached(tmp_path, key) is None
    cached = load_cached(tmp_path, key)
    assert cached is not None and cached.source == "manual"


@pytest.mark.anyio
async def test_network_miss_does_not_overwrite_manual(tmp_path: Path, monkeypatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        save_manual_lyrics(tmp_path, artist="A", title="B", text="Ja hi és\nManual")
        if request.url.path == "/api/get":
            return httpx.Response(404, json={})
        return httpx.Response(200, json=[])

    monkeypatch.setattr(httpx, "AsyncClient", _client_factory(handler))
    monkeypatch.setattr(lyrics_mod, "RETRY_BASE_DELAY", 0.0)

    payload = await fetch_lyrics(artist="A", title="B", cache_dir=tmp_path)
    assert payload.source == "manual"
    assert [line.text for line in payload.lines] == ["Ja hi és", "Manual"]
    cached = load_cached(tmp_path, cache_key("A", "B", None))
    assert cached is not None and cached.source == "manual"


@pytest.mark.anyio
async def test_fetch_embeds_lyrics_when_file_has_none(tmp_path: Path, monkeypatch) -> None:
    audio = _audio_stub(tmp_path / "song.mp3")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/get":
            return httpx.Response(200, json={"syncedLyrics": SYNCED, "plainLyrics": "Hello\nWorld"})
        return httpx.Response(200, json=[])

    monkeypatch.setattr(httpx, "AsyncClient", _client_factory(handler))
    monkeypatch.setattr(lyrics_mod, "RETRY_BASE_DELAY", 0.0)

    payload = await fetch_lyrics(artist="A", title="B", cache_dir=tmp_path, audio_path=audio)
    assert payload.synced is True
    local = read_local_lyrics(audio)
    assert local is not None
    text = payload_to_text(local)
    assert "Hello" in text and "World" in text


@pytest.mark.anyio
async def test_fetch_does_not_overwrite_existing_local(tmp_path: Path, monkeypatch) -> None:
    audio = _audio_stub(tmp_path / "song.mp3")
    assert embed_lyrics_in_audio(audio, "Original\nLocal", overwrite=True)
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200, json={"syncedLyrics": SYNCED, "plainLyrics": "Hello\nWorld"})

    monkeypatch.setattr(httpx, "AsyncClient", _client_factory(handler))
    monkeypatch.setattr(lyrics_mod, "RETRY_BASE_DELAY", 0.0)

    payload = await fetch_lyrics(artist="A", title="B", cache_dir=tmp_path, audio_path=audio)
    assert [line.text for line in payload.lines] == ["Original", "Local"]
    assert calls["n"] == 0
    assert "Original" in payload_to_text(read_local_lyrics(audio))


@pytest.mark.anyio
async def test_cache_hit_embeds_into_empty_file(tmp_path: Path) -> None:
    audio = _audio_stub(tmp_path / "song.mp3")
    save_cached(
        tmp_path,
        cache_key("A", "B", None),
        LyricsPayload(
            synced=False,
            source="lrclib",
            lines=[LyricLine(time=0.0, text="Hola"), LyricLine(time=4.0, text="Adéu")],
            plain="Hola\nAdéu",
        ),
    )
    payload = await fetch_lyrics(artist="A", title="B", cache_dir=tmp_path, audio_path=audio)
    assert [line.text for line in payload.lines] == ["Hola", "Adéu"]
    local = read_local_lyrics(audio)
    assert local is not None
    assert "Hola" in payload_to_text(local)


def test_save_manual_lyrics_writes_to_audio(tmp_path: Path) -> None:
    audio = _audio_stub(tmp_path / "song.mp3")
    save_manual_lyrics(
        tmp_path,
        artist="A",
        title="B",
        text="Nova\nLletra",
        audio_path=audio,
    )
    local = read_local_lyrics(audio)
    assert local is not None
    assert [line.text for line in local.lines] == ["Nova", "Lletra"]


def test_save_manual_updates_sidecar(tmp_path: Path) -> None:
    audio = _audio_stub(tmp_path / "song.mp3")
    sidecar = audio.with_suffix(".lrc")
    sidecar.write_text("[00:01.00]Vella\n", encoding="utf-8")
    save_manual_lyrics(
        tmp_path,
        artist="A",
        title="B",
        text="[00:02.00]Nova\n",
        audio_path=audio,
    )
    assert "Nova" in sidecar.read_text(encoding="utf-8")
    assert "Vella" not in sidecar.read_text(encoding="utf-8")


@pytest.fixture
def anyio_backend():
    return "asyncio"
