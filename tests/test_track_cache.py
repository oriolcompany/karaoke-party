"""Per-song tracks/<key>/ layout and zip export/import."""

from __future__ import annotations

from pathlib import Path

from karaoke_party.lyrics import cache_key
from karaoke_party.track_cache import (
    clear_track_files,
    export_track_zip,
    import_track_zip,
    lyrics_path,
    read_meta,
    track_status,
    write_meta,
    youtube_path,
)


def test_export_import_roundtrip(tmp_path: Path) -> None:
    key = cache_key("Artist", "Song", 180.0)
    write_meta(tmp_path, key, artist="Artist", title="Song", duration=180.0, album="Album")
    lyrics_path(tmp_path, key).write_text('{"synced": true, "lines": []}', encoding="utf-8")
    (tmp_path / key / "cover.jpg").write_bytes(b"art")
    (tmp_path / key / "instrumental.mp3").write_bytes(b"inst")
    youtube_path(tmp_path, key).write_text('{"found": true, "video_id": "dQw4w9WgXcQ"}', encoding="utf-8")

    zip_path = tmp_path / "song.zip"
    export_track_zip(tmp_path, key, zip_path)
    assert zip_path.is_file()

    other = tmp_path / "other-root"
    other.mkdir()
    imported = import_track_zip(other, zip_path)
    assert imported == key
    meta = read_meta(other, key)
    assert meta is not None
    assert meta["artist"] == "Artist"
    assert meta["title"] == "Song"
    status = track_status(other, key)
    assert status["lyrics"]
    assert status["cover"]
    assert status["instrumental"]
    assert status["youtube"]
    assert (other / key / "cover.jpg").read_bytes() == b"art"
    assert (other / key / "youtube.json").is_file()


def test_import_accepts_wrapped_folder(tmp_path: Path) -> None:
    import zipfile

    key = cache_key("A", "B", 10.0)
    nested = tmp_path / "pack" / "track"
    nested.mkdir(parents=True)
    (nested / "meta.json").write_text(
        '{"key": "%s", "artist": "A", "title": "B", "duration": 10}' % key,
        encoding="utf-8",
    )
    (nested / "lyrics.json").write_text('{"synced": false, "lines": []}', encoding="utf-8")
    zip_path = tmp_path / "wrapped.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for path in nested.iterdir():
            archive.write(path, arcname=f"track/{path.name}")

    root = tmp_path / "tracks"
    root.mkdir()
    assert import_track_zip(root, zip_path) == key
    assert (root / key / "lyrics.json").is_file()


def test_clear_youtube_scope_only(tmp_path: Path) -> None:
    key = cache_key("Artist", "Song", 180.0)
    write_meta(tmp_path, key, artist="Artist", title="Song", duration=180.0)
    lyrics_path(tmp_path, key).write_text("{}", encoding="utf-8")
    youtube_path(tmp_path, key).write_text("{}", encoding="utf-8")

    removed = clear_track_files(tmp_path, key, {"youtube"})
    assert removed["youtube"] == 1
    assert removed["lyrics"] == 0
    assert not youtube_path(tmp_path, key).is_file()
    assert lyrics_path(tmp_path, key).is_file()
