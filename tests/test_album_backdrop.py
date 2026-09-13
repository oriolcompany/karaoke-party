from __future__ import annotations

import json
from pathlib import Path

import pytest

from karaoke_party import album_backdrop as backdrop_mod
from karaoke_party.album_backdrop import (
    album_backdrop_key,
    album_has_backdrop,
    delete_album_backdrop,
    find_album_backdrop,
    list_album_backdrop_keys,
    save_album_backdrop,
    sniff_image_mime,
)


PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0"
    b"\x00\x00\x00\x03\x00\x01\x00\x05\xfe\xd4\x00\x00\x00\x00IEND\xaeB`\x82"
)
JPEG_MIN = b"\xff\xd8\xff\xd9"


@pytest.fixture
def backdrop_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(backdrop_mod, "album_backdrops_dir", lambda: tmp_path / "album-backdrops")
    return tmp_path / "album-backdrops"


def test_album_key_uses_same_fallbacks_as_ui() -> None:
    assert album_backdrop_key("", "") == album_backdrop_key("Artista desconegut", "Sense àlbum")


def test_sniff_png_and_jpeg() -> None:
    assert sniff_image_mime(PNG_1X1) == "image/png"
    assert sniff_image_mime(JPEG_MIN) == "image/jpeg"
    assert sniff_image_mime(b"not-an-image") == ""


def test_save_find_replace_delete(backdrop_root: Path) -> None:
    key = album_backdrop_key("Queen", "A Night at the Opera")
    path = save_album_backdrop(key, PNG_1X1, artist="Queen", album="A Night at the Opera")
    assert path.is_file()
    assert path.suffix == ".png"
    assert find_album_backdrop(key) == path
    assert album_has_backdrop(key)
    assert key in list_album_backdrop_keys()
    meta = json.loads((path.parent / "meta.json").read_text(encoding="utf-8"))
    assert meta["album_key"] == key

    replaced = save_album_backdrop(key, JPEG_MIN, artist="Queen", album="A Night at the Opera")
    assert replaced.suffix == ".jpg"
    assert find_album_backdrop(key) == replaced
    assert not path.exists()

    assert delete_album_backdrop(key) is True
    assert find_album_backdrop(key) is None
    assert not album_has_backdrop(key)


def test_rejects_empty_and_unknown_bytes(backdrop_root: Path) -> None:
    key = album_backdrop_key("A", "B")
    with pytest.raises(ValueError, match="buida"):
        save_album_backdrop(key, b"")
    with pytest.raises(ValueError, match="JPG"):
        save_album_backdrop(key, b"hello")
