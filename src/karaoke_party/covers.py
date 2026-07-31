from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import httpx
from mutagen import File as MutagenFile
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, ID3, ID3NoHeaderError
from mutagen.mp4 import MP4, MP4Cover

from .config import _resolve_cache_dir

FOLDER_COVER_NAMES = (
    "cover.jpg",
    "cover.jpeg",
    "cover.png",
    "cover.webp",
    "folder.jpg",
    "folder.jpeg",
    "folder.png",
    "AlbumArt.jpg",
    "AlbumArt.jpeg",
    "AlbumArt.png",
    "front.jpg",
    "Front.jpg",
    "album.jpg",
    "album.png",
)


@dataclass
class CoverResult:
    path: Path
    mime: str
    source: str


def covers_cache_dir(root: Path | None = None) -> Path:
    return _resolve_cache_dir("covers", root)


def _mime_from_suffix(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".png":
        return "image/png"
    if suffix == ".webp":
        return "image/webp"
    if suffix == ".gif":
        return "image/gif"
    return "application/octet-stream"


def _suffix_from_mime(mime: str) -> str:
    mime = (mime or "").lower()
    if "png" in mime:
        return ".png"
    if "webp" in mime:
        return ".webp"
    if "gif" in mime:
        return ".gif"
    return ".jpg"


def extract_embedded_cover(audio_path: Path) -> tuple[bytes, str] | None:
    """Read cover art embedded in the audio file tags."""
    try:
        audio = MutagenFile(str(audio_path))
    except Exception:
        return None
    if audio is None:
        return None

    # MP3 / ID3
    try:
        tags = ID3(str(audio_path))
        for frame in tags.values():
            if getattr(frame, "FrameID", "") == "APIC" or frame.__class__.__name__.startswith("APIC"):
                data = bytes(frame.data)
                mime = str(getattr(frame, "mime", None) or "image/jpeg")
                if data:
                    return data, mime
    except Exception:
        pass

    # MP4 / M4A
    if isinstance(audio, MP4) or (audio.tags and "covr" in getattr(audio, "tags", {})):
        try:
            covers = audio.tags.get("covr") if audio.tags else None
            if covers:
                cover = covers[0]
                data = bytes(cover)
                fmt = getattr(cover, "imageformat", None)
                mime = "image/png" if fmt == 14 else "image/jpeg"
                if data:
                    return data, mime
        except Exception:
            pass

    # FLAC / OGG pictures
    if isinstance(audio, FLAC) or hasattr(audio, "pictures"):
        try:
            pictures = list(getattr(audio, "pictures", []) or [])
            if pictures:
                pic = pictures[0]
                data = bytes(pic.data)
                mime = str(pic.mime or "image/jpeg")
                if data:
                    return data, mime
        except Exception:
            pass

    return None


def find_folder_cover(audio_path: Path) -> Path | None:
    """Use a folder image only when this looks like an album folder.

    A flat dump like Documents/Songs with dozens of tracks often has one leftover
    cover.jpg; applying it to every song is worse than the generic art.
    """
    from .config import AUDIO_EXTENSIONS

    folder = audio_path.parent
    audio_files = [
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS and not path.name.startswith("._")
    ]
    # Album folders are typically a handful of tracks; flat libraries are not.
    if len(audio_files) > 15:
        return None

    for name in FOLDER_COVER_NAMES:
        candidate = folder / name
        if candidate.is_file():
            return candidate
    # Any image that looks like artwork in the same folder.
    for pattern in ("*cover*.jpg", "*cover*.png", "*folder*.jpg", "*front*.jpg"):
        matches = sorted(folder.glob(pattern))
        if matches:
            return matches[0]
    return None


def _cache_path_for_embedded(audio_path: Path, mime: str, cache_dir: Path) -> Path:
    digest = hashlib.sha1(str(audio_path.resolve()).encode("utf-8")).hexdigest()
    return cache_dir / f"{digest}{_suffix_from_mime(mime)}"


# Exact artist+title is the bar for accepting a remote image. We never fall
# back to "first search result" — that is what put wrong covers on songs.
MIN_ITUNES_SCORE = 7  # artist exact (3) + title exact (4)


async def fetch_remote_cover(artist: str, title: str, album: str = "") -> tuple[bytes, str] | None:
    """Fetch artwork from iTunes Search API (only high-confidence matches)."""
    queries: list[str] = []
    # Always prefer artist+title. Title-only searches return random covers.
    if artist and title:
        queries.append(f"{artist} {title}")
    if artist and album:
        queries.append(f"{artist} {album}")
    if not queries:
        return None

    headers = {"User-Agent": "karaoke-party/0.1 (local karaoke app)"}
    async with httpx.AsyncClient(timeout=15.0, headers=headers, follow_redirects=True) as client:
        for query in queries:
            response = await client.get(
                "https://itunes.apple.com/search",
                params={
                    "term": query,
                    "media": "music",
                    "entity": "song",
                    "limit": 8,
                },
            )
            if response.status_code != 200:
                continue
            results = (response.json() or {}).get("results") or []
            artwork = _pick_itunes_artwork(results, artist=artist, title=title, album=album)
            if not artwork:
                continue
            # Prefer larger artwork when iTunes returns 100x100 thumbnails.
            artwork = re.sub(r"\d+x\d+bb", "600x600bb", artwork)
            image = await client.get(artwork)
            if image.status_code == 200 and image.content:
                mime = image.headers.get("content-type") or "image/jpeg"
                if ";" in mime:
                    mime = mime.split(";", 1)[0].strip()
                return image.content, mime
    return None


def _normalize(text: str) -> str:
    return re.sub(r"[^\wÀ-ÿ]+", "", (text or "").lower(), flags=re.UNICODE)


def _pick_itunes_artwork(
    results: list[dict],
    *,
    artist: str,
    title: str,
    album: str,
) -> str | None:
    """Return artwork URL only when artist+title match confidently."""
    if not results:
        return None
    want_artist = _normalize(artist)
    want_title = _normalize(title)
    want_album = _normalize(album)
    if not want_title:
        return None

    scored: list[tuple[int, str]] = []
    for row in results:
        url = row.get("artworkUrl100") or row.get("artworkUrl60")
        if not url:
            continue
        got_artist = _normalize(str(row.get("artistName") or ""))
        got_title = _normalize(str(row.get("trackName") or ""))
        got_album = _normalize(str(row.get("collectionName") or ""))

        score = 0
        if want_artist and got_artist == want_artist:
            score += 3
        if got_title == want_title:
            score += 4
        if want_album and got_album == want_album:
            score += 2
        # Substring title matches alone are too weak (e.g. "Love" → "Love Story").
        scored.append((score, str(url)))

    if not scored:
        return None
    scored.sort(key=lambda item: item[0], reverse=True)
    best_score, best_url = scored[0]
    # Need artist+title exact (7). Never return a weak / random hit.
    if best_score < MIN_ITUNES_SCORE:
        return None
    return best_url


def embed_cover_in_audio(audio_path: Path, data: bytes, mime: str) -> bool:
    """Embed cover art into the audio file tags. Returns True on success."""
    audio_path = Path(audio_path)
    suffix = audio_path.suffix.lower()
    mime = (mime or "image/jpeg").split(";", 1)[0].strip().lower()
    if mime not in {"image/jpeg", "image/jpg", "image/png"}:
        # ID3/MP4 cover frames are happiest with jpeg/png.
        mime = "image/jpeg"

    try:
        if suffix == ".mp3":
            try:
                tags = ID3(str(audio_path))
            except ID3NoHeaderError:
                tags = ID3()
            tags.delall("APIC")
            tags.add(
                APIC(
                    encoding=3,
                    mime=mime,
                    type=3,
                    desc="Cover",
                    data=data,
                )
            )
            tags.save(str(audio_path))
            return True

        if suffix in {".m4a", ".mp4", ".aac"}:
            audio = MP4(str(audio_path))
            fmt = MP4Cover.FORMAT_PNG if "png" in mime else MP4Cover.FORMAT_JPEG
            audio["covr"] = [MP4Cover(data, imageformat=fmt)]
            audio.save()
            return True

        if suffix == ".flac":
            audio = FLAC(str(audio_path))
            picture = Picture()
            picture.type = 3
            picture.mime = mime
            picture.desc = "Cover"
            picture.data = data
            audio.clear_pictures()
            audio.add_picture(picture)
            audio.save()
            return True

        if suffix in {".ogg", ".opus"}:
            # Ogg Vorbis/Opus picture embedding via mutagen is awkward; skip.
            return False

        # Generic fallback: try ID3-style save for unknown tagged files.
        try:
            tags = ID3(str(audio_path))
        except Exception:
            return False
        tags.delall("APIC")
        tags.add(APIC(encoding=3, mime=mime, type=3, desc="Cover", data=data))
        tags.save(str(audio_path))
        return True
    except Exception:
        return False


def _write_cover_cache(audio_path: Path, data: bytes, mime: str, cache_dir: Path) -> Path:
    cached = _cache_path_for_embedded(audio_path, mime, cache_dir)
    cached.write_bytes(data)
    return cached


async def resolve_cover(
    audio_path: Path,
    *,
    artist: str,
    title: str,
    album: str = "",
    cache_dir: Path,
    generic_path: Path,
) -> CoverResult:
    """
    Resolve cover art in order:
    1) embedded tags
    2) image file in the same folder
    3) remote lookup (embedded into the audio file when possible)
    4) generic fallback
    """
    audio_path = Path(audio_path)
    if not audio_path.is_file():
        return CoverResult(path=generic_path, mime="image/png", source="generic")

    embedded = extract_embedded_cover(audio_path)
    if embedded:
        data, mime = embedded
        cached = _write_cover_cache(audio_path, data, mime, cache_dir)
        return CoverResult(path=cached, mime=mime, source="embedded")

    folder_cover = find_folder_cover(audio_path)
    if folder_cover is not None:
        return CoverResult(
            path=folder_cover,
            mime=_mime_from_suffix(folder_cover),
            source="folder",
        )

    remote = await fetch_remote_cover(artist=artist, title=title, album=album)
    if remote:
        data, mime = remote
        if embed_cover_in_audio(audio_path, data, mime):
            cached = _write_cover_cache(audio_path, data, mime, cache_dir)
            return CoverResult(path=cached, mime=mime, source="remote-embedded")
        # Could not write tags — still serve from cache for this session.
        cached = _write_cover_cache(audio_path, data, mime, cache_dir)
        return CoverResult(path=cached, mime=mime, source="remote-cache")

    return CoverResult(path=generic_path, mime="image/png", source="generic")
