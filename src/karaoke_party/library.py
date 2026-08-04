from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from mutagen import File as MutagenFile

from .config import AUDIO_EXTENSIONS
from .covers import covers_cache_dir, extract_embedded_cover, find_cached_cover
from .lyrics import cache_key


@dataclass
class TrackInfo:
    id: str
    path: str
    title: str
    artist: str
    album: str
    duration: float
    relpath: str
    track: int = 0
    disc: int = 0
    year: int = 0
    cover_hash: str = ""


def _cover_hash_for(path: Path, artist: str, title: str, duration: float) -> str:
    """Fingerprint of the cover image used for this track (embedded or cache)."""
    try:
        embedded = extract_embedded_cover(path)
        if embedded and embedded[0]:
            return hashlib.sha1(embedded[0]).hexdigest()
        cached = find_cached_cover(cache_key(artist, title, duration), covers_cache_dir())
        if cached is not None and cached.is_file():
            data = cached.read_bytes()
            if data:
                return hashlib.sha1(data).hexdigest()
    except Exception:
        return ""
    return ""


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


def _parse_number(value: str) -> int:
    """Parse tags like '3', '3/12', or 'A3' into an int (0 if unknown)."""
    if not value:
        return 0
    head = value.split("/", 1)[0].strip()
    try:
        return int(head)
    except ValueError:
        digits = "".join(ch for ch in head if ch.isdigit())
        return int(digits) if digits else 0


def _parse_year(value: str) -> int:
    """Parse tags like '2020', '2020-05-01', or '2020/05/01' into a year."""
    if not value:
        return 0
    digits = "".join(ch for ch in value.strip() if ch.isdigit())
    if len(digits) < 4:
        return 0
    year = int(digits[:4])
    return year if 1000 <= year <= 2100 else 0


def _sort_key(track: TrackInfo) -> tuple:
    # Artist A–Z; within artist, newest album first; then disc/track order.
    return (
        track.artist.casefold(),
        -track.year,
        track.album.casefold(),
        track.disc,
        track.track if track.track > 0 else 10**9,
        track.title.casefold(),
        track.relpath.casefold(),
    )


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
        track_no = 0
        disc_no = 0
        year = 0
        duration = 0.0
        if audio is not None:
            title = _tag(audio, "title", "Title", "©nam")
            artist = _tag(audio, "artist", "Author", "©ART")
            album = _tag(audio, "album", "Album", "©alb")
            track_no = _parse_number(_tag(audio, "tracknumber", "track", "trkn"))
            disc_no = _parse_number(_tag(audio, "discnumber", "disc", "disk"))
            year = _parse_year(_tag(audio, "date", "year", "originaldate", "©day", "Year"))
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
                track=track_no,
                disc=disc_no,
                year=year,
                cover_hash=_cover_hash_for(path, artist, title, duration),
            )
        )
    # Use the best year seen on any track of the album so mates stay together.
    album_years: dict[tuple[str, str], int] = {}
    for track in tracks:
        key = (track.artist.casefold(), track.album.casefold())
        album_years[key] = max(album_years.get(key, 0), track.year)
    for track in tracks:
        track.year = album_years[(track.artist.casefold(), track.album.casefold())]
    tracks.sort(key=_sort_key)
    return tracks
