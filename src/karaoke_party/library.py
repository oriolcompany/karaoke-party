from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mutagen import File as MutagenFile

from .config import AUDIO_EXTENSIONS


@dataclass
class TrackInfo:
    id: str
    path: str
    title: str
    artist: str
    album: str
    duration: float
    relpath: str


def _tag(audio: MutagenFile, *keys: str) -> str:
    tags = getattr(audio, "tags", None) or {}
    for key in keys:
        value = tags.get(key)
        if not value:
            continue
        if isinstance(value, list):
            value = value[0] if value else ""
        text = str(value).strip()
        if text:
            return text
    return ""


def scan_library(root: Path) -> list[TrackInfo]:
    tracks: list[TrackInfo] = []
    if not root.is_dir():
        return tracks
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in AUDIO_EXTENSIONS:
            continue
        if path.name.startswith("._"):
            continue
        try:
            audio = MutagenFile(path, easy=True)
        except Exception:
            audio = None
        title = ""
        artist = ""
        album = ""
        duration = 0.0
        if audio is not None:
            title = _tag(audio, "title", "Title", "©nam")
            artist = _tag(audio, "artist", "Author", "©ART")
            album = _tag(audio, "album", "Album", "©alb")
            duration = float(getattr(audio, "info", None).length or 0) if getattr(audio, "info", None) else 0.0
        if not title:
            title = path.stem
        if not artist:
            artist = path.parent.name
        rel = path.relative_to(root).as_posix()
        track_id = rel
        tracks.append(
            TrackInfo(
                id=track_id,
                path=str(path),
                title=title,
                artist=artist,
                album=album,
                duration=duration,
                relpath=rel,
            )
        )
    return tracks
