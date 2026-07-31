"""Cover matching must prefer missing art over the wrong art."""

from __future__ import annotations

from pathlib import Path

from karaoke_party.covers import (
    MIN_ITUNES_SCORE,
    _pick_itunes_artwork,
    find_folder_cover,
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
