"""Per-song cache layout under ``tracks/<key>/``.

One folder holds everything for a song so export/import is a single copy:

- ``meta.json`` — artist, title, duration (human-readable + import checks)
- ``lyrics.json`` — lookup / local / manual / probe result
- ``aligned.json`` — Whisper word timings
- ``instrumental.mp3`` / ``vocals.mp3`` — stem separation
- ``cover.<ext>`` — artwork bytes
- ``youtube.json`` — YouTube clip id for the stage background
- ``karaoke.mp4`` — exported karaoke video (cover + lyric fill)
"""

from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from .config import app_cache_root

META_NAME = "meta.json"
LYRICS_NAME = "lyrics.json"
ALIGNED_NAME = "aligned.json"
INSTRUMENTAL_NAME = "instrumental.mp3"
VOCALS_NAME = "vocals.mp3"
COVER_PREFIX = "cover"
YOUTUBE_NAME = "youtube.json"
KARAOKE_NAME = "karaoke.mp4"
KARAOKE_META_NAME = "karaoke.json"

CACHE_SCOPES = frozenset({"lyrics", "aligned", "stems", "cover", "youtube"})


def tracks_cache_dir() -> Path:
    path = app_cache_root() / "tracks"
    path.mkdir(parents=True, exist_ok=True)
    return path


def stems_work_dir() -> Path:
    """Shared scratch for Demucs output — never inside a track folder."""
    path = app_cache_root() / "stems-work"
    path.mkdir(parents=True, exist_ok=True)
    return path


def track_dir(tracks_root: Path, key: str) -> Path:
    return Path(tracks_root) / key


def ensure_track_dir(tracks_root: Path, key: str) -> Path:
    path = track_dir(tracks_root, key)
    path.mkdir(parents=True, exist_ok=True)
    return path


def lyrics_path(tracks_root: Path, key: str) -> Path:
    return track_dir(tracks_root, key) / LYRICS_NAME


def aligned_path(tracks_root: Path, key: str) -> Path:
    return track_dir(tracks_root, key) / ALIGNED_NAME


def instrumental_path(tracks_root: Path, key: str) -> Path:
    return track_dir(tracks_root, key) / INSTRUMENTAL_NAME


def vocals_path(tracks_root: Path, key: str) -> Path:
    return track_dir(tracks_root, key) / VOCALS_NAME


def youtube_path(tracks_root: Path, key: str) -> Path:
    return track_dir(tracks_root, key) / YOUTUBE_NAME


def karaoke_path(tracks_root: Path, key: str) -> Path:
    return track_dir(tracks_root, key) / KARAOKE_NAME


def karaoke_meta_path(tracks_root: Path, key: str) -> Path:
    return track_dir(tracks_root, key) / KARAOKE_META_NAME


def find_cover_path(tracks_root: Path, key: str) -> Path | None:
    folder = track_dir(tracks_root, key)
    if not folder.is_dir():
        return None
    matches = sorted(folder.glob(f"{COVER_PREFIX}.*"))
    return matches[0] if matches else None


def cover_target(tracks_root: Path, key: str, mime: str) -> Path:
    suffix = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }.get((mime or "").lower(), ".jpg")
    folder = ensure_track_dir(tracks_root, key)
    # Drop any previous cover.* so we never keep two extensions.
    for old in folder.glob(f"{COVER_PREFIX}.*"):
        try:
            old.unlink()
        except OSError:
            continue
    return folder / f"{COVER_PREFIX}{suffix}"


def write_meta(
    tracks_root: Path,
    key: str,
    *,
    artist: str,
    title: str,
    duration: float | None = None,
    album: str = "",
) -> None:
    folder = ensure_track_dir(tracks_root, key)
    payload = {
        "key": key,
        "artist": artist,
        "title": title,
        "album": album or "",
        "duration": int(duration or 0),
    }
    (folder / META_NAME).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_meta(tracks_root: Path, key: str) -> dict[str, Any] | None:
    path = track_dir(tracks_root, key) / META_NAME
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def track_status(tracks_root: Path, key: str) -> dict[str, Any]:
    folder = track_dir(tracks_root, key)
    lyrics = lyrics_path(tracks_root, key)
    aligned = aligned_path(tracks_root, key)
    instrumental = instrumental_path(tracks_root, key)
    vocals = vocals_path(tracks_root, key)
    cover = find_cover_path(tracks_root, key)
    youtube = youtube_path(tracks_root, key)
    meta = read_meta(tracks_root, key) or {}
    return {
        "key": key,
        "dir": str(folder) if folder.is_dir() else "",
        "meta": meta,
        "lyrics": lyrics.is_file() and lyrics.stat().st_size > 0,
        "aligned": aligned.is_file() and aligned.stat().st_size > 0,
        "instrumental": instrumental.is_file() and instrumental.stat().st_size > 0,
        "vocals": vocals.is_file() and vocals.stat().st_size > 0,
        "cover": cover is not None and cover.is_file(),
        "youtube": youtube.is_file() and youtube.stat().st_size > 0,
    }


def _unlink(path: Path) -> int:
    if not path.is_file():
        return 0
    try:
        path.unlink()
        return 1
    except OSError:
        return 0


def clear_track_files(tracks_root: Path, key: str, scopes: set[str]) -> dict[str, int]:
    removed = {"lyrics": 0, "aligned": 0, "stems": 0, "cover": 0, "youtube": 0}
    if "lyrics" in scopes:
        removed["lyrics"] = _unlink(lyrics_path(tracks_root, key))
    if "aligned" in scopes:
        removed["aligned"] = _unlink(aligned_path(tracks_root, key))
        # Stale karaoke video would keep old syllable timings.
        _unlink(karaoke_path(tracks_root, key))
        _unlink(karaoke_meta_path(tracks_root, key))
    if "stems" in scopes:
        removed["stems"] = _unlink(instrumental_path(tracks_root, key)) + _unlink(
            vocals_path(tracks_root, key)
        )
    if "cover" in scopes:
        cover = find_cover_path(tracks_root, key)
        removed["cover"] = _unlink(cover) if cover else 0
    if "youtube" in scopes:
        removed["youtube"] = _unlink(youtube_path(tracks_root, key))

    folder = track_dir(tracks_root, key)
    if folder.is_dir() and not any(folder.iterdir()):
        try:
            folder.rmdir()
        except OSError:
            pass
    return removed


def clear_all_tracks(tracks_root: Path, scopes: set[str]) -> dict[str, int]:
    removed = {"lyrics": 0, "aligned": 0, "stems": 0, "cover": 0, "youtube": 0}
    root = Path(tracks_root)
    if not root.is_dir():
        return removed
    for folder in list(root.iterdir()):
        if not folder.is_dir() or folder.name.startswith("."):
            continue
        part = clear_track_files(root, folder.name, scopes)
        for name, count in part.items():
            removed[name] += count
    return removed


def iter_track_keys(tracks_root: Path) -> list[str]:
    root = Path(tracks_root)
    if not root.is_dir():
        return []
    return sorted(
        path.name for path in root.iterdir() if path.is_dir() and not path.name.startswith(".")
    )


def export_track_zip(tracks_root: Path, key: str, destination: Path) -> Path:
    folder = track_dir(tracks_root, key)
    if not folder.is_dir():
        raise FileNotFoundError(f"No hi ha cau per a la clau {key}")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(folder).as_posix())
    return destination


def import_track_zip(tracks_root: Path, archive_path: Path) -> str:
    """Import a song cache zip. Returns the track key used on disk."""
    archive_path = Path(archive_path)
    if not archive_path.is_file():
        raise FileNotFoundError(str(archive_path))

    with tempfile.TemporaryDirectory(prefix="karaoke-import-") as tmp:
        tmp_dir = Path(tmp)
        with zipfile.ZipFile(archive_path, "r") as archive:
            archive.extractall(tmp_dir)

        # Allow either a flat zip of track files or a single top-level folder.
        candidates = [tmp_dir]
        children = [path for path in tmp_dir.iterdir() if path.is_dir()]
        if len(children) == 1 and not (tmp_dir / META_NAME).is_file():
            candidates.insert(0, children[0])

        source: Path | None = None
        for candidate in candidates:
            if (candidate / META_NAME).is_file() or (candidate / LYRICS_NAME).is_file():
                source = candidate
                break
        if source is None:
            raise ValueError("El zip no sembla una cau de cançó (falta meta.json / lyrics.json)")

        meta: dict[str, Any] = {}
        meta_path = source / META_NAME
        if meta_path.is_file():
            try:
                loaded = json.loads(meta_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    meta = loaded
            except (OSError, ValueError):
                meta = {}

        key = str(meta.get("key") or "").strip()
        if not key:
            # Fall back to hashing meta fields when the zip is hand-edited.
            from .lyrics import cache_key

            key = cache_key(
                str(meta.get("artist") or ""),
                str(meta.get("title") or ""),
                float(meta.get("duration") or 0),
            )
        if not key or key in {".", ".."} or "/" in key or "\\" in key:
            raise ValueError("Clau de cau invàlida al zip")

        target = ensure_track_dir(tracks_root, key)
        for path in source.iterdir():
            if not path.is_file():
                continue
            shutil.copy2(path, target / path.name)
        return key
