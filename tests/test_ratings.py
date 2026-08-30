from __future__ import annotations

import pytest

from karaoke_party.lyrics import cache_key
from karaoke_party.ratings import get_rating, load_ratings, normalize_rating, set_rating


def test_normalize_rating_bounds() -> None:
    assert normalize_rating(0) == 0
    assert normalize_rating(5) == 5
    assert normalize_rating("3") == 3
    with pytest.raises(ValueError):
        normalize_rating(6)
    with pytest.raises(ValueError):
        normalize_rating(-1)
    with pytest.raises(ValueError):
        normalize_rating(True)
    with pytest.raises(ValueError):
        normalize_rating("x")


def test_set_and_get_rating(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("KARAOKE_CACHE_DIR", str(tmp_path / "cache"))
    key = cache_key("Artist", "Song", 180.0)
    assert get_rating(key) == 0
    assert set_rating(key, 4) == 4
    assert get_rating(key) == 4
    assert load_ratings()[key] == 4


def test_clear_rating_removes_key(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("KARAOKE_CACHE_DIR", str(tmp_path / "cache"))
    key = cache_key("Artist", "Song", 180.0)
    set_rating(key, 2)
    assert set_rating(key, 0) == 0
    assert get_rating(key) == 0
    assert key not in load_ratings()


def test_ratings_survive_reload(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("KARAOKE_CACHE_DIR", str(tmp_path / "cache"))
    key = cache_key("A", "B", 90.0)
    set_rating(key, 5)
    assert load_ratings() == {key: 5}
