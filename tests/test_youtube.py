"""YouTube clip matching must prefer a miss over the wrong video."""

from __future__ import annotations

from pathlib import Path

from karaoke_party.lyrics import cache_key
from karaoke_party.youtube import (
    extract_youtube_id,
    extract_youtube_id_from_file,
    has_youtube_hit,
    pick_youtube_clip,
    resolve_youtube_clip,
    score_youtube_entry,
)


def _entry(
    video_id: str,
    title: str,
    channel: str = "QueenVEVO",
    duration: float = 355.0,
    **extra,
) -> dict:
    data = {
        "id": video_id,
        "title": title,
        "channel": channel,
        "duration": duration,
        "live_status": "not_live",
    }
    data.update(extra)
    return data


def test_extract_id_from_watch_and_short_urls() -> None:
    assert extract_youtube_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_youtube_id("https://youtu.be/dQw4w9WgXcQ?t=12") == "dQw4w9WgXcQ"
    assert extract_youtube_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_youtube_id("https://www.youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_extract_id_from_ytdlp_filename() -> None:
    assert extract_youtube_id("Queen - Bohemian Rhapsody [dQw4w9WgXcQ].mp3") == "dQw4w9WgXcQ"


def test_extract_id_from_file_name(tmp_path: Path) -> None:
    path = tmp_path / "Artist - Song [abcdefghijk].mp3"
    path.write_bytes(b"\x00")
    assert extract_youtube_id_from_file(path) == "abcdefghijk"


def test_rejects_unembeddable() -> None:
    results = [
        _entry(
            "xxxxxxxxxxx",
            "Queen - Bohemian Rhapsody (Official Video)",
            playable_in_embed=False,
        )
    ]
    assert (
        pick_youtube_clip(results, artist="Queen", title="Bohemian Rhapsody", duration=354)
        is None
    )


def test_rejects_official_audio() -> None:
    results = [
        _entry("xxxxxxxxxxx", "Queen - Bohemian Rhapsody (Official Audio)", duration=355)
    ]
    assert (
        pick_youtube_clip(results, artist="Queen", title="Bohemian Rhapsody", duration=354)
        is None
    )


def test_rejects_hour_loop() -> None:
    results = [_entry("yyyyyyyyyyy", "Bohemian Rhapsody 1 Hour Loop", duration=3600)]
    assert (
        pick_youtube_clip(results, artist="Queen", title="Bohemian Rhapsody", duration=354)
        is None
    )


def test_rejects_duration_mismatch() -> None:
    results = [
        _entry("zzzzzzzzzzz", "Queen - Bohemian Rhapsody (Official Video)", duration=3600)
    ]
    assert (
        pick_youtube_clip(results, artist="Queen", title="Bohemian Rhapsody", duration=354)
        is None
    )


def test_first_hit_allows_official_clip_longer_than_album_cut() -> None:
    results = [
        _entry(
            "0l10OvFwEik",
            "Aspencat - Música naix de la ràbia (Videoclip Oficial)",
            channel="Aspencat Oficial",
            duration=299,
        ),
        _entry(
            "ZJPbFQeitwA",
            "ASPENCAT - Música naix de la ràbia",
            channel="Aspencat Oficial",
            duration=236,
        ),
    ]
    clip = pick_youtube_clip(
        results,
        artist="Aspencat",
        title="Música naix de la ràbia",
        duration=236,
    )
    assert clip is not None
    assert clip.video_id == "0l10OvFwEik"


def test_album_words_in_tag_do_not_miss_first_hit() -> None:
    results = [
        _entry(
            "0l10OvFwEik",
            "Aspencat - Música naix de la ràbia (Videoclip Oficial)",
            channel="Aspencat Oficial",
            duration=299,
        )
    ]
    clip = pick_youtube_clip(
        results,
        artist="Aspencat",
        title="Música Naix de la Ràbia - Tot és Ara",
        duration=235,
    )
    assert clip is not None
    assert clip.video_id == "0l10OvFwEik"


def test_rejects_wrong_artist() -> None:
    results = [
        _entry(
            "aaaaaaaaaaa",
            "Someone Else - Bohemian Rhapsody (Official Video)",
            channel="Random",
        )
    ]
    assert (
        pick_youtube_clip(results, artist="Queen", title="Bohemian Rhapsody", duration=354)
        is None
    )


def test_prefers_official_video_over_lyrics() -> None:
    results = [
        _entry("lyricvideo1", "Queen - Bohemian Rhapsody (Official Lyric Video)"),
        _entry("officialvid", "Queen - Bohemian Rhapsody (Official Video)"),
    ]
    clip = pick_youtube_clip(
        results, artist="Queen", title="Bohemian Rhapsody", duration=354
    )
    assert clip is not None
    assert clip.video_id == "officialvid"


def test_catalan_diacritics_do_not_miss_official_clip() -> None:
    results = [
        _entry(
            "HhkOePktMSQ",
            "La Ludwig Band - Xavier, el tècnic de so",
            channel="La Ludwig Band",
            duration=347,
        )
    ]
    clip = pick_youtube_clip(
        results,
        artist="La Ludwig Band",
        title="Xavier, el tecnic de so",
        duration=337,
    )
    assert clip is not None
    assert clip.video_id == "HhkOePktMSQ"


def test_nfd_title_matches_nfc_video() -> None:
    import unicodedata

    results = [
        _entry(
            "HhkOePktMSQ",
            "La Ludwig Band - Xavier, el tècnic de so",
            channel="La Ludwig Band",
            duration=347,
        )
    ]
    title = unicodedata.normalize("NFD", "Xavier, el tècnic de so")
    clip = pick_youtube_clip(
        results,
        artist="La Ludwig Band",
        title=title,
        duration=337,
    )
    assert clip is not None
    assert clip.video_id == "HhkOePktMSQ"


def test_prefers_first_organic_result_over_later_official() -> None:
    results = [
        _entry("firstresult", "Queen - Bohemian Rhapsody"),
        _entry("officialvid", "Queen - Bohemian Rhapsody (Official Video)"),
    ]
    clip = pick_youtube_clip(
        results, artist="Queen", title="Bohemian Rhapsody", duration=354
    )
    assert clip is not None
    assert clip.video_id == "firstresult"


def test_skips_ads_and_promo_then_takes_first_organic() -> None:
    results = [
        _entry(
            "adadadadada",
            "Queen - Bohemian Rhapsody (Official Video)",
            sponsored=True,
        ),
        _entry("trailervid1", "Queen - Bohemian Rhapsody (Official Trailer)"),
        _entry(
            "topicaudio1",
            "Queen - Bohemian Rhapsody",
            channel="Queen - Topic",
        ),
        _entry("firstorgani", "Queen - Bohemian Rhapsody"),
        _entry("laterofficl", "Queen - Bohemian Rhapsody (Official Video)"),
    ]
    clip = pick_youtube_clip(
        results, artist="Queen", title="Bohemian Rhapsody", duration=354
    )
    assert clip is not None
    assert clip.video_id == "firstorgani"


def test_rejects_lyrics_video_even_when_it_is_the_only_hit() -> None:
    results = [_entry("lyricvideo1", "Queen - Bohemian Rhapsody (Lyrics)")]
    assert (
        pick_youtube_clip(results, artist="Queen", title="Bohemian Rhapsody", duration=354)
        is None
    )


def test_rejects_lletra_and_letra_videos() -> None:
    assert (
        pick_youtube_clip(
            [_entry("lletravideo", "La Ludwig Band - Millor amb ell (lletra)")],
            artist="La Ludwig Band",
            title="Millor amb ell",
            duration=234,
        )
        is None
    )
    assert (
        pick_youtube_clip(
            [_entry("letravideo1", "Queen - Bohemian Rhapsody (Letra)")],
            artist="Queen",
            title="Bohemian Rhapsody",
            duration=354,
        )
        is None
    )


def test_file_id_skips_search(tmp_path: Path) -> None:
    audio = tmp_path / "Queen - Bohemian Rhapsody [dQw4w9WgXcQ].mp3"
    audio.write_bytes(b"\x00")
    cache = tmp_path / "cache"
    cache.mkdir()

    def boom(_query: str) -> list[dict]:
        raise AssertionError("search should not run when the file already has an id")

    payload = resolve_youtube_clip(
        path=audio,
        artist="Queen",
        title="Bohemian Rhapsody",
        duration=354,
        cache_dir=cache,
        search=boom,
    )
    assert payload["found"] is True
    assert payload["video_id"] == "dQw4w9WgXcQ"
    assert payload["source"] == "file"

    key = cache_key("Queen", "Bohemian Rhapsody", 354)
    again = resolve_youtube_clip(
        path=audio,
        artist="Queen",
        title="Bohemian Rhapsody",
        duration=354,
        cache_dir=cache,
        search=boom,
    )
    assert again["video_id"] == "dQw4w9WgXcQ"
    assert (cache / key / "youtube.json").is_file()


def test_search_hit_is_cached(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    cache.mkdir()
    calls = {"n": 0}

    def search(_query: str) -> list[dict]:
        calls["n"] += 1
        return [_entry("officialvid", "Queen - Bohemian Rhapsody (Official Video)")]

    first = resolve_youtube_clip(
        path=None,
        artist="Queen",
        title="Bohemian Rhapsody",
        duration=354,
        cache_dir=cache,
        search=search,
    )
    second = resolve_youtube_clip(
        path=None,
        artist="Queen",
        title="Bohemian Rhapsody",
        duration=354,
        cache_dir=cache,
        search=search,
    )
    assert first["video_id"] == "officialvid"
    assert second["video_id"] == "officialvid"
    assert calls["n"] == 1


def test_search_miss_is_cached(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    cache.mkdir()
    calls = {"n": 0}

    def search(_query: str) -> list[dict]:
        calls["n"] += 1
        return [_entry("nopexxxxxxx", "Totally Different Song (Official Video)", channel="Nope")]

    first = resolve_youtube_clip(
        path=None,
        artist="Queen",
        title="Bohemian Rhapsody",
        duration=354,
        cache_dir=cache,
        search=search,
    )
    second = resolve_youtube_clip(
        path=None,
        artist="Queen",
        title="Bohemian Rhapsody",
        duration=354,
        cache_dir=cache,
        search=search,
    )
    assert first["found"] is False
    assert second["found"] is False
    assert calls["n"] == 1


def test_score_requires_title_tokens() -> None:
    clip = score_youtube_entry(
        _entry("otherother1", "Queen - Don't Stop Me Now (Official Video)"),
        artist="Queen",
        title="Bohemian Rhapsody",
        duration=354,
    )
    assert clip is None


def test_apostrophe_title_does_not_require_letter_d() -> None:
    clip = score_youtube_entry(
        _entry(
            "concertclip",
            "La Ludwig Band - D'un concert de la Mushkaa",
            channel="La Ludwig Band",
            duration=305,
        ),
        artist="La Ludwig Band",
        title="D'un concert de la Mushkaa",
        duration=305,
    )
    assert clip is not None
    assert clip.video_id == "concertclip"


def test_concert_in_song_title_is_not_a_live_reject() -> None:
    results = [
        _entry(
            "concertclip",
            "La Ludwig Band - D'un concert de la Mushkaa",
            channel="La Ludwig Band",
            duration=305,
        )
    ]
    clip = pick_youtube_clip(
        results,
        artist="La Ludwig Band",
        title="D'un concert de la Mushkaa",
        duration=305,
    )
    assert clip is not None
    assert clip.score >= 7


def test_empty_search_is_not_cached(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    cache.mkdir()
    calls = {"n": 0}

    def search(_query: str) -> list[dict]:
        calls["n"] += 1
        return []

    first = resolve_youtube_clip(
        path=None,
        artist="Queen",
        title="Bohemian Rhapsody",
        duration=354,
        cache_dir=cache,
        search=search,
    )
    second = resolve_youtube_clip(
        path=None,
        artist="Queen",
        title="Bohemian Rhapsody",
        duration=354,
        cache_dir=cache,
        search=search,
    )
    assert first["found"] is False
    assert first["source"] == "error"
    assert second["source"] == "error"
    assert calls["n"] == 2


def test_has_youtube_hit_only_when_found(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    cache.mkdir()
    assert has_youtube_hit(cache, "Queen", "Bohemian Rhapsody", 354) is False
    resolve_youtube_clip(
        path=None,
        artist="Queen",
        title="Bohemian Rhapsody",
        duration=354,
        cache_dir=cache,
        search=lambda _q: [_entry("officialvid", "Queen - Bohemian Rhapsody (Official Video)")],
    )
    assert has_youtube_hit(cache, "Queen", "Bohemian Rhapsody", 354) is True


def test_force_retries_cached_miss(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    cache.mkdir()
    calls = {"n": 0}

    def search(_query: str) -> list[dict]:
        calls["n"] += 1
        if calls["n"] == 1:
            return [_entry("nopexxxxxxx", "Totally Different Song (Official Video)", channel="Nope")]
        return [_entry("officialvid", "Queen - Bohemian Rhapsody (Official Video)")]

    first = resolve_youtube_clip(
        path=None,
        artist="Queen",
        title="Bohemian Rhapsody",
        duration=354,
        cache_dir=cache,
        search=search,
    )
    second = resolve_youtube_clip(
        path=None,
        artist="Queen",
        title="Bohemian Rhapsody",
        duration=354,
        cache_dir=cache,
        search=search,
    )
    third = resolve_youtube_clip(
        path=None,
        artist="Queen",
        title="Bohemian Rhapsody",
        duration=354,
        cache_dir=cache,
        search=search,
        force=True,
    )
    assert first["found"] is False
    assert second["found"] is False
    assert third["found"] is True
    assert third["video_id"] == "officialvid"
    assert calls["n"] == 2
