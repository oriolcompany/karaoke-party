from __future__ import annotations

from karaoke_party.library import (
    TrackInfo,
    _cover_hash_for,
    _parse_number,
    _parse_year,
    _sort_key,
    album_group_key,
    fold_name,
)


def test_parse_number() -> None:
    assert _parse_number("") == 0
    assert _parse_number("3") == 3
    assert _parse_number("3/12") == 3
    assert _parse_number(" 07 / 14 ") == 7
    assert _parse_number("A3") == 3


def test_parse_year() -> None:
    assert _parse_year("") == 0
    assert _parse_year("2020") == 2020
    assert _parse_year("2020-05-01") == 2020
    assert _parse_year("2020/05/01") == 2020
    assert _parse_year("99") == 0


def test_sort_key_orders_same_album_by_track() -> None:
    tracks = [
        TrackInfo("c", "c", "Three", "Artist", "Album", 1.0, "c", track=3, year=2020),
        TrackInfo("a", "a", "One", "Artist", "Album", 1.0, "a", track=1, year=2020),
        TrackInfo("b", "b", "Two", "Artist", "Album", 1.0, "b", track=2, year=2020),
    ]
    ordered = sorted(tracks, key=_sort_key)
    assert [t.title for t in ordered] == ["One", "Two", "Three"]


def test_sort_key_newest_album_first_within_artist() -> None:
    tracks = [
        TrackInfo("old1", "old1", "Old One", "Artist", "Old Album", 1.0, "old1", track=1, year=2010),
        TrackInfo("new2", "new2", "New Two", "Artist", "New Album", 1.0, "new2", track=2, year=2024),
        TrackInfo("new1", "new1", "New One", "Artist", "New Album", 1.0, "new1", track=1, year=2024),
        TrackInfo("old2", "old2", "Old Two", "Artist", "Old Album", 1.0, "old2", track=2, year=2010),
        TrackInfo("unk", "unk", "Unknown", "Artist", "Mystery", 1.0, "unk", track=1, year=0),
    ]
    ordered = sorted(tracks, key=_sort_key)
    assert [t.album for t in ordered] == [
        "New Album",
        "New Album",
        "Old Album",
        "Old Album",
        "Mystery",
    ]
    assert [t.title for t in ordered] == ["New One", "New Two", "Old One", "Old Two", "Unknown"]


def test_sort_key_uses_disc_then_track() -> None:
    tracks = [
        TrackInfo("d1t2", "d1t2", "B", "Artist", "Album", 1.0, "d1t2", track=2, disc=1, year=2020),
        TrackInfo("d2t1", "d2t1", "C", "Artist", "Album", 1.0, "d2t1", track=1, disc=2, year=2020),
        TrackInfo("d1t1", "d1t1", "A", "Artist", "Album", 1.0, "d1t1", track=1, disc=1, year=2020),
    ]
    ordered = sorted(tracks, key=_sort_key)
    assert [t.title for t in ordered] == ["A", "B", "C"]


def test_missing_track_number_sorts_after_numbered() -> None:
    tracks = [
        TrackInfo("x", "x", "Unknown", "Artist", "Album", 1.0, "x", track=0, year=2020),
        TrackInfo("a", "a", "One", "Artist", "Album", 1.0, "a", track=1, year=2020),
    ]
    ordered = sorted(tracks, key=_sort_key)
    assert [t.title for t in ordered] == ["One", "Unknown"]


def test_fold_name_treats_curly_apostrophes_as_plain() -> None:
    assert fold_name("Lax\u2019n\u2019Busto") == fold_name("Lax'n'Busto")
    assert album_group_key("Lax\u2019n\u2019Busto", "Llença't") == album_group_key(
        "Lax'n'Busto", "Llença't"
    )


def test_sort_key_groups_album_mates_despite_apostrophes() -> None:
    tracks = [
        TrackInfo("a", "a", "Llença't", "Lax'n'Busto", "Llença't", 1.0, "a", track=1, year=2000),
        TrackInfo(
            "b",
            "b",
            "Trepitja fort",
            "Lax\u2019n\u2019Busto",
            "Llença't",
            1.0,
            "b",
            track=2,
            year=2000,
        ),
        TrackInfo("c", "c", "Other", "Zebra", "ZZ", 1.0, "c", track=1, year=2000),
    ]
    ordered = sorted(tracks, key=_sort_key)
    assert [t.title for t in ordered[:2]] == ["Llença't", "Trepitja fort"]


def test_cover_hash_uses_embedded_bytes(tmp_path, monkeypatch) -> None:
    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"\x00")
    monkeypatch.setattr(
        "karaoke_party.library.extract_embedded_cover",
        lambda path: (b"same-cover-bytes", "image/jpeg"),
    )
    monkeypatch.setattr("karaoke_party.library.find_cached_cover", lambda key, cache: None)
    h1 = _cover_hash_for(audio, "Artist", "Song", 180.0)
    h2 = _cover_hash_for(audio, "Artist", "Song", 180.0)
    assert h1
    assert h1 == h2
    assert len(h1) == 40
