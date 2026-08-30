"""Cover matching must prefer missing art over the wrong art."""

from __future__ import annotations

from pathlib import Path

import pytest

from karaoke_party.covers import (
    MIN_ITUNES_SCORE,
    _cache_path_for_embedded,
    _pick_itunes_artwork,
    clear_cover_cache,
    find_cached_cover,
    find_folder_cover,
    migrate_cached_covers_into_audio,
    refresh_cover_cache_from_embedded,
    resolve_cover,
)


def _row(artist: str, title: str, album: str, url: str = "https://example/a.jpg") -> dict:
    return {
        "artistName": artist,
        "trackName": title,
        "collectionName": album,
        "artworkUrl100": url,
    }


def test_rejects_zero_score_itunes_hit() -> None:
    results = [_row("Someone Else", "Totally Different", "Nope", "https://wrong/a.jpg")]
    assert _pick_itunes_artwork(results, artist="Queen", title="Bohemian Rhapsody", album="") is None


def test_rejects_title_substring_without_artist() -> None:
    results = [_row("Taylor Swift", "Love Story", "Fearless", "https://wrong/love.jpg")]
    assert _pick_itunes_artwork(results, artist="Someone", title="Love", album="") is None


def test_accepts_exact_artist_and_title() -> None:
    results = [
        _row("Wrong Artist", "Bohemian Rhapsody", "X", "https://wrong.jpg"),
        _row("Queen", "Bohemian Rhapsody", "A Night at the Opera", "https://right.jpg"),
    ]
    assert (
        _pick_itunes_artwork(results, artist="Queen", title="Bohemian Rhapsody", album="")
        == "https://right.jpg"
    )


def test_album_bonus_does_not_beat_exact_title_match() -> None:
    results = [
        _row("Queen", "Another One Bites the Dust", "A Night at the Opera", "https://album.jpg"),
        _row("Queen", "Bohemian Rhapsody", "Greatest Hits", "https://song.jpg"),
    ]
    assert (
        _pick_itunes_artwork(
            results, artist="Queen", title="Bohemian Rhapsody", album="A Night at the Opera"
        )
        == "https://song.jpg"
    )


def test_min_score_requires_artist_and_title() -> None:
    # Title-only exact is score 4 — below the bar when we know the artist.
    results = [_row("Not Queen", "Bohemian Rhapsody", "X", "https://wrong.jpg")]
    assert _pick_itunes_artwork(results, artist="Queen", title="Bohemian Rhapsody", album="") is None
    assert MIN_ITUNES_SCORE == 7


def test_extract_embedded_cover_reads_id3_without_audio_stream(tmp_path: Path) -> None:
    from mutagen.id3 import APIC, ID3, TIT2

    from karaoke_party.covers import extract_embedded_cover

    audio = tmp_path / "tags-only.mp3"
    audio.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 32)
    tags = ID3()
    tags.add(TIT2(encoding=3, text="Song"))
    tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=b"\xff\xd8art"))
    tags.save(str(audio))
    found = extract_embedded_cover(audio)
    assert found is not None
    assert found[0] == b"\xff\xd8art"
    assert "jpeg" in found[1]


def test_folder_cover_ignored_in_flat_library(tmp_path: Path) -> None:
    cover = tmp_path / "cover.jpg"
    cover.write_bytes(b"fake")
    # Flat Songs dump: many tracks share one leftover cover.jpg.
    tracks = []
    for i in range(20):
        path = tmp_path / f"song_{i}.mp3"
        path.write_bytes(b"\x00")
        tracks.append(path)
    assert find_folder_cover(tracks[0]) is None


def test_folder_cover_used_for_album_folder(tmp_path: Path) -> None:
    cover = tmp_path / "cover.jpg"
    cover.write_bytes(b"fake")
    for i in range(8):
        (tmp_path / f"track_{i}.mp3").write_bytes(b"\x00")
    assert find_folder_cover(tmp_path / "track_0.mp3") == cover


def test_clear_cover_cache_removes_digest_files(tmp_path: Path) -> None:
    key = "abc123deadbeef"
    cache = tmp_path / "cache"
    cache.mkdir()

    cached = _cache_path_for_embedded(key, "image/jpeg", cache)
    cached.write_bytes(b"old")
    (cache / "other.jpg").write_bytes(b"keep")
    assert clear_cover_cache(key, cache) == 1
    assert not cached.exists()
    assert (cache / "other.jpg").is_file()


def test_migrate_embeds_cached_cover_when_missing(tmp_path: Path, monkeypatch) -> None:
    from karaoke_party.lyrics import cache_key

    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"\x00")
    cache = tmp_path / "cache"
    cache.mkdir()
    key = cache_key("Artist", "Song", 180.0)
    cached = _cache_path_for_embedded(key, "image/jpeg", cache)
    cached.write_bytes(b"cover-bytes")

    class Item:
        def __init__(self, path: Path):
            self.path = path
            self.artist = "Artist"
            self.title = "Song"
            self.album = "Album"
            self.duration = 180.0

    calls: list[tuple] = []

    def fake_embed(path: Path, data: bytes, mime: str) -> bool:
        calls.append((path, data, mime))
        return True

    monkeypatch.setattr("karaoke_party.covers.extract_embedded_cover", lambda path: None)
    monkeypatch.setattr("karaoke_party.covers.embed_cover_in_audio", fake_embed)

    result = migrate_cached_covers_into_audio([Item(audio)], cache)
    assert result["from_cache"] == 1
    assert calls == [(audio, b"cover-bytes", "image/jpeg")]
    assert find_cached_cover(key, cache) == cached


def test_migrate_copies_cover_from_album_mate(tmp_path: Path, monkeypatch) -> None:
    donor = tmp_path / "a1.mp3"
    target = tmp_path / "a2.mp3"
    donor.write_bytes(b"\x00")
    target.write_bytes(b"\x00")
    cache = tmp_path / "cache"
    cache.mkdir()

    class Item:
        def __init__(self, path: Path, artist: str, album: str):
            self.path = path
            self.artist = artist
            self.album = album

    monkeypatch.setattr(
        "karaoke_party.covers.extract_embedded_cover",
        lambda path: (b"album-art", "image/jpeg") if path == donor else None,
    )
    calls: list[Path] = []

    def fake_embed(path: Path, data: bytes, mime: str) -> bool:
        calls.append(path)
        return True

    monkeypatch.setattr("karaoke_party.covers.embed_cover_in_audio", fake_embed)

    result = migrate_cached_covers_into_audio(
        [Item(donor, "Artist", "Album"), Item(target, "Artist", "Album")],
        cache,
    )
    assert result["from_album"] == 1
    assert target in calls


def test_migrate_skips_when_already_embedded(tmp_path: Path, monkeypatch) -> None:
    from karaoke_party.lyrics import cache_key

    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"\x00")
    cache = tmp_path / "cache"
    cache.mkdir()
    key = cache_key("Artist", "Song", 180.0)
    cached = _cache_path_for_embedded(key, "image/jpeg", cache)
    cached.write_bytes(b"cover-bytes")

    class Item:
        def __init__(self, path: Path):
            self.path = path
            self.artist = "Artist"
            self.title = "Song"
            self.album = "Album"
            self.duration = 180.0

    monkeypatch.setattr(
        "karaoke_party.covers.extract_embedded_cover",
        lambda path: (b"already", "image/jpeg"),
    )
    monkeypatch.setattr(
        "karaoke_party.covers.embed_cover_in_audio",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("should not embed")),
    )

    result = migrate_cached_covers_into_audio([Item(audio)], cache)
    assert result["from_cache"] == 0
    assert result["skipped"] == 1


def _cover_item(path: Path, artist: str = "Artist", title: str = "Song", duration: float = 180.0):
    class Item:
        def __init__(self) -> None:
            self.path = path
            self.artist = artist
            self.title = title
            self.album = "Album"
            self.duration = duration

    return Item()


def test_refresh_writes_cache_from_embedded_without_embedding(tmp_path: Path, monkeypatch) -> None:
    from karaoke_party.lyrics import cache_key

    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"\x00")
    cache = tmp_path / "cache"
    cache.mkdir()

    monkeypatch.setattr(
        "karaoke_party.covers.extract_embedded_cover",
        lambda path: (b"fresh-art", "image/jpeg"),
    )
    monkeypatch.setattr(
        "karaoke_party.covers.embed_cover_in_audio",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not embed")),
    )

    result = refresh_cover_cache_from_embedded([_cover_item(audio)], cache)
    assert result["updated"] == 1
    key = cache_key("Artist", "Song", 180.0)
    cached = find_cached_cover(key, cache)
    assert cached is not None
    assert cached.read_bytes() == b"fresh-art"


def test_refresh_overwrites_stale_cache(tmp_path: Path, monkeypatch) -> None:
    from karaoke_party.lyrics import cache_key

    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"\x00")
    cache = tmp_path / "cache"
    cache.mkdir()
    key = cache_key("Artist", "Song", 180.0)
    stale = _cache_path_for_embedded(key, "image/jpeg", cache)
    stale.write_bytes(b"old-wrong")

    monkeypatch.setattr(
        "karaoke_party.covers.extract_embedded_cover",
        lambda path: (b"from-mp3", "image/jpeg"),
    )
    monkeypatch.setattr(
        "karaoke_party.covers.embed_cover_in_audio",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not embed")),
    )

    result = refresh_cover_cache_from_embedded([_cover_item(audio)], cache)
    assert result["updated"] == 1
    cached = find_cached_cover(key, cache)
    assert cached is not None
    assert cached.read_bytes() == b"from-mp3"


def test_refresh_leaves_cache_when_no_embedded(tmp_path: Path, monkeypatch) -> None:
    from karaoke_party.lyrics import cache_key

    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"\x00")
    cache = tmp_path / "cache"
    cache.mkdir()
    key = cache_key("Artist", "Song", 180.0)
    cached = _cache_path_for_embedded(key, "image/jpeg", cache)
    cached.write_bytes(b"keep-me")

    monkeypatch.setattr("karaoke_party.covers.extract_embedded_cover", lambda path: None)
    monkeypatch.setattr(
        "karaoke_party.covers.embed_cover_in_audio",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not embed")),
    )

    result = refresh_cover_cache_from_embedded([_cover_item(audio)], cache)
    assert result["missing"] == 1
    assert result["updated"] == 0
    assert cached.read_bytes() == b"keep-me"


def test_refresh_same_when_cache_matches_embedded(tmp_path: Path, monkeypatch) -> None:
    from karaoke_party.lyrics import cache_key

    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"\x00")
    cache = tmp_path / "cache"
    cache.mkdir()
    key = cache_key("Artist", "Song", 180.0)
    cached = _cache_path_for_embedded(key, "image/jpeg", cache)
    cached.write_bytes(b"same-bytes")

    monkeypatch.setattr(
        "karaoke_party.covers.extract_embedded_cover",
        lambda path: (b"same-bytes", "image/jpeg"),
    )
    monkeypatch.setattr(
        "karaoke_party.covers.embed_cover_in_audio",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not embed")),
    )

    result = refresh_cover_cache_from_embedded([_cover_item(audio)], cache)
    assert result["same"] == 1
    assert result["updated"] == 0
    assert cached.read_bytes() == b"same-bytes"


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_force_overwrites_embedded_when_remote_hits(tmp_path: Path, monkeypatch) -> None:
    from karaoke_party.lyrics import cache_key

    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"\x00")
    cache = tmp_path / "cache"
    cache.mkdir()
    generic = tmp_path / "generic.png"
    generic.write_bytes(b"generic")
    key = cache_key("Artist", "Song", None)
    stale = _cache_path_for_embedded(key, "image/jpeg", cache)
    stale.write_bytes(b"stale")

    async def fake_remote(artist: str, title: str, album: str = ""):
        return b"new-cover-bytes", "image/jpeg"

    monkeypatch.setattr("karaoke_party.covers.fetch_remote_cover", fake_remote)
    monkeypatch.setattr("karaoke_party.covers.embed_cover_in_audio", lambda *a, **k: True)

    result = await resolve_cover(
        audio,
        artist="Artist",
        title="Song",
        cache_dir=cache,
        generic_path=generic,
        force=True,
    )
    assert result.source == "remote-embedded"
    assert result.path.read_bytes() == b"new-cover-bytes"
    assert not stale.exists() or result.path.read_bytes() != b"stale"


@pytest.mark.anyio
async def test_resolve_embeds_from_cache_when_tags_empty(tmp_path: Path, monkeypatch) -> None:
    from karaoke_party.lyrics import cache_key

    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"\x00")
    cache = tmp_path / "cache"
    cache.mkdir()
    generic = tmp_path / "generic.png"
    generic.write_bytes(b"generic")
    key = cache_key("Artist", "Song", None)
    cached = _cache_path_for_embedded(key, "image/jpeg", cache)
    cached.write_bytes(b"from-cache")

    monkeypatch.setattr("karaoke_party.covers.extract_embedded_cover", lambda path: None)
    monkeypatch.setattr("karaoke_party.covers.find_folder_cover", lambda path: None)
    monkeypatch.setattr("karaoke_party.covers.embed_cover_in_audio", lambda *a, **k: True)

    async def no_remote(artist: str, title: str, album: str = ""):
        return None

    monkeypatch.setattr("karaoke_party.covers.fetch_remote_cover", no_remote)

    result = await resolve_cover(
        audio,
        artist="Artist",
        title="Song",
        cache_dir=cache,
        generic_path=generic,
    )
    assert result.source == "cache-embedded"
    assert result.path.read_bytes() == b"from-cache"


@pytest.mark.anyio
async def test_force_keeps_embedded_when_remote_misses(tmp_path: Path, monkeypatch) -> None:
    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"\x00")
    cache = tmp_path / "cache"
    cache.mkdir()
    generic = tmp_path / "generic.png"
    generic.write_bytes(b"generic")

    async def fake_remote(artist: str, title: str, album: str = ""):
        return None

    monkeypatch.setattr("karaoke_party.covers.fetch_remote_cover", fake_remote)
    monkeypatch.setattr(
        "karaoke_party.covers.extract_embedded_cover",
        lambda path: (b"keep-me", "image/jpeg"),
    )

    result = await resolve_cover(
        audio,
        artist="Artist",
        title="Song",
        cache_dir=cache,
        generic_path=generic,
        force=True,
    )
    assert result.source == "embedded"
    assert result.path.read_bytes() == b"keep-me"
