"""Read / write / remove embedded album art in audio files."""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

import httpx
from mutagen import File as MutagenFile
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, ID3, ID3NoHeaderError
from mutagen.mp4 import MP4, MP4Cover

# Song matches need a solid artist + title signal; album matches are a fallback.
MIN_SONG_SCORE = 6
MIN_ALBUM_SCORE = 5
# Title-only lookups require a near-exact title (score 3+) to avoid random hits.
MIN_TITLE_ONLY_SCORE = 3
_NOISE_RE = re.compile(
    r"\b(feat|ft|featuring|remaster(?:ed)?|live|radio\s*edit|acoustic|version|"
    r"official(?:\s*video)?|lyrics?|audio|hd|hq|explicit|deluxe)\b",
    re.IGNORECASE,
)


def mime_from_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".png":
        return "image/png"
    if suffix == ".webp":
        return "image/webp"
    return "image/jpeg"


def normalize_cover_mime(mime: str) -> str:
    mime = (mime or "image/jpeg").split(";", 1)[0].strip().lower()
    if mime in {"image/jpeg", "image/jpg", "image/png"}:
        return "image/jpeg" if mime == "image/jpg" else mime
    return "image/jpeg"


def extract_embedded_cover(audio_path: Path) -> tuple[bytes, str] | None:
    """Return (bytes, mime) for the first embedded cover, or None."""
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

    try:
        audio = MutagenFile(str(audio_path))
    except Exception:
        audio = None

    if audio is not None:
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


def write_embedded_cover(audio_path: Path, data: bytes, mime: str = "image/jpeg") -> None:
    """Embed cover art into the audio file. Raises on failure."""
    if not data:
        raise ValueError("cover image is empty")
    audio_path = Path(audio_path)
    suffix = audio_path.suffix.lower()
    mime = normalize_cover_mime(mime)

    if suffix == ".mp3":
        try:
            tags = ID3(str(audio_path))
        except ID3NoHeaderError:
            tags = ID3()
        tags.delall("APIC")
        tags.add(APIC(encoding=3, mime=mime, type=3, desc="Cover", data=data))
        tags.save(str(audio_path))
        return

    if suffix in {".m4a", ".mp4", ".aac"}:
        audio = MP4(str(audio_path))
        fmt = MP4Cover.FORMAT_PNG if "png" in mime else MP4Cover.FORMAT_JPEG
        audio["covr"] = [MP4Cover(data, imageformat=fmt)]
        audio.save()
        return

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
        return

    raise RuntimeError(f"cover embedding not supported for {suffix or 'unknown'} files")


def remove_embedded_cover(audio_path: Path) -> None:
    """Remove embedded cover art from the audio file. Raises on failure."""
    audio_path = Path(audio_path)
    suffix = audio_path.suffix.lower()

    if suffix == ".mp3":
        try:
            tags = ID3(str(audio_path))
        except ID3NoHeaderError:
            return
        tags.delall("APIC")
        tags.save(str(audio_path))
        return

    if suffix in {".m4a", ".mp4", ".aac"}:
        audio = MP4(str(audio_path))
        if audio.tags and "covr" in audio.tags:
            del audio.tags["covr"]
            audio.save()
        return

    if suffix == ".flac":
        audio = FLAC(str(audio_path))
        audio.clear_pictures()
        audio.save()
        return

    raise RuntimeError(f"cover removal not supported for {suffix or 'unknown'} files")


def load_cover_file(path: Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    if not data:
        raise ValueError("image file is empty")
    return data, mime_from_path(path)


def _fold_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _normalize_match(text: str) -> str:
    text = _fold_accents(text or "").lower()
    text = re.sub(r"\(.*?\)|\[.*?\]", " ", text)
    text = _NOISE_RE.sub(" ", text)
    text = re.sub(r"[^\w]+", "", text, flags=re.UNICODE)
    return text


def _similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if a in b or b in a:
        shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
        if len(shorter) >= 4 and len(shorter) / len(longer) >= 0.6:
            return 0.92
    return SequenceMatcher(None, a, b).ratio()


def _score_artist(want: str, got: str) -> int:
    if not want or not got:
        return 0
    if want == got:
        return 3
    ratio = _similarity(want, got)
    if ratio >= 0.92:
        return 3
    if ratio >= 0.82:
        return 2
    return 0


def _score_title(want: str, got: str) -> int:
    if not want or not got:
        return 0
    if want == got:
        return 4
    ratio = _similarity(want, got)
    if ratio >= 0.92:
        return 3
    if ratio >= 0.85:
        return 2
    return 0


def _score_album(want: str, got: str) -> int:
    if not want or not got:
        return 0
    if want == got:
        return 2
    if _similarity(want, got) >= 0.88:
        return 2
    if _similarity(want, got) >= 0.8:
        return 1
    return 0


def _pick_itunes_song(
    results: list[dict],
    *,
    artist: str,
    title: str,
    album: str,
) -> dict | None:
    """Return the best matching iTunes song row, or None."""
    want_artist = _normalize_match(artist)
    want_title = _normalize_match(title)
    want_album = _normalize_match(album)
    if not want_title:
        return None
    if not want_artist:
        return _pick_itunes_song_by_title(results, title=title, album=album)

    scored: list[tuple[int, int, int, dict]] = []
    for row in results:
        got_artist = _normalize_match(str(row.get("artistName") or ""))
        got_title = _normalize_match(
            str(row.get("trackName") or row.get("trackCensoredName") or "")
        )
        got_album = _normalize_match(
            str(row.get("collectionName") or row.get("collectionCensoredName") or "")
        )
        artist_score = _score_artist(want_artist, got_artist)
        title_score = _score_title(want_title, got_title)
        album_score = _score_album(want_album, got_album)
        total = artist_score + title_score + album_score
        scored.append((total, artist_score, title_score, row))

    if not scored:
        return None
    scored.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    total, artist_score, title_score, best = scored[0]
    if total >= MIN_SONG_SCORE and artist_score >= 2 and title_score >= 2:
        return best
    return None


def _pick_itunes_song_by_title(
    results: list[dict],
    *,
    title: str,
    album: str = "",
) -> dict | None:
    """Pick a song when only the title is known (flat YouTube-style filenames).

    Requires a near-exact title and a clear artist consensus among strong hits,
    so generic titles do not latch onto the wrong recording.
    """
    want_title = _normalize_match(title)
    want_album = _normalize_match(album)
    if not want_title:
        return None

    scored: list[tuple[int, int, str, dict]] = []
    for row in results:
        got_artist = _normalize_match(str(row.get("artistName") or ""))
        got_title = _normalize_match(
            str(row.get("trackName") or row.get("trackCensoredName") or "")
        )
        got_album = _normalize_match(
            str(row.get("collectionName") or row.get("collectionCensoredName") or "")
        )
        title_score = _score_title(want_title, got_title)
        if title_score < MIN_TITLE_ONLY_SCORE:
            continue
        album_score = _score_album(want_album, got_album) if want_album else 0
        scored.append((title_score, album_score, got_artist, row))

    if not scored:
        return None

    exact = [item for item in scored if item[0] >= 4]
    pool = exact or scored

    if want_album:
        album_hits = [item for item in pool if item[1] >= 2]
        if album_hits:
            pool = album_hits

    artists = [artist for _ts, _als, artist, _row in pool if artist]
    if not artists:
        return None

    counts = Counter(artists)
    top_artist, top_count = counts.most_common(1)[0]
    if len(counts) > 1:
        second_count = counts.most_common(2)[1][1]
        # Reject ties / weak majorities on ambiguous titles ("Hello", "Home", …).
        if top_count == second_count or top_count <= len(pool) // 2:
            return None

    chosen = [item for item in pool if item[2] == top_artist]
    if not chosen:
        return None

    def _rank(item: tuple[int, int, str, dict]) -> tuple[int, int, int, int]:
        title_score, album_score, _artist, row = item
        collection = str(
            row.get("collectionName") or row.get("collectionCensoredName") or ""
        ).casefold()
        is_single = collection.endswith(" - single") or " - single" in collection
        track_count = int(row.get("trackCount") or 0)
        return (title_score, album_score, 0 if is_single else 1, track_count)

    chosen.sort(key=_rank, reverse=True)
    return chosen[0][3]


def _pick_itunes_song_artwork(
    results: list[dict],
    *,
    artist: str,
    title: str,
    album: str,
) -> str | None:
    row = _pick_itunes_song(results, artist=artist, title=title, album=album)
    if not row:
        return None
    url = row.get("artworkUrl100") or row.get("artworkUrl60")
    return str(url) if url else None


def _pick_itunes_album_artwork(
    results: list[dict],
    *,
    artist: str,
    album: str,
) -> str | None:
    want_artist = _normalize_match(artist)
    want_album = _normalize_match(album)
    if not want_artist or not want_album:
        return None

    scored: list[tuple[int, str]] = []
    for row in results:
        url = row.get("artworkUrl100") or row.get("artworkUrl60")
        if not url:
            continue
        got_artist = _normalize_match(str(row.get("artistName") or ""))
        got_album = _normalize_match(
            str(row.get("collectionName") or row.get("collectionCensoredName") or "")
        )
        total = _score_artist(want_artist, got_artist) + _score_album(want_album, got_album)
        scored.append((total, str(url)))

    if not scored:
        return None
    scored.sort(key=lambda item: item[0], reverse=True)
    best_score, best_url = scored[0]
    if best_score >= MIN_ALBUM_SCORE:
        return best_url
    return None


def _upsized_artwork_url(url: str) -> str:
    return re.sub(r"\d+x\d+bb", "600x600bb", url)


def _download_image(client: httpx.Client, url: str) -> tuple[bytes, str] | None:
    image = client.get(url)
    if image.status_code != 200 or not image.content:
        return None
    mime = image.headers.get("content-type") or "image/jpeg"
    if ";" in mime:
        mime = mime.split(";", 1)[0].strip()
    if len(image.content) < 500:
        return None
    return image.content, mime


def _itunes_search(
    client: httpx.Client,
    *,
    term: str,
    entity: str,
    country: str | None = None,
    limit: int = 25,
    attribute: str | None = None,
) -> list[dict]:
    params: dict[str, str | int] = {
        "term": term,
        "media": "music",
        "entity": entity,
        "limit": limit,
    }
    if country:
        params["country"] = country
    if attribute:
        params["attribute"] = attribute
    response = client.get("https://itunes.apple.com/search", params=params)
    if response.status_code != 200:
        return []
    return list((response.json() or {}).get("results") or [])


def _itunes_row_to_metadata(row: dict, *, title: str, artist: str, album: str) -> dict[str, str]:
    release = str(row.get("releaseDate") or "")
    track_no = row.get("trackNumber")
    return {
        "title": str(
            row.get("trackName") or row.get("trackCensoredName") or title
        ).strip(),
        "artist": str(row.get("artistName") or artist).strip(),
        "album": str(
            row.get("collectionName")
            or row.get("collectionCensoredName")
            or album
        ).strip(),
        "date": release[:4],
        "track": str(track_no) if track_no not in (None, "") else "",
    }


def lookup_itunes_metadata(
    artist: str,
    title: str,
    album: str = "",
    *,
    client: httpx.Client | None = None,
) -> dict[str, str] | None:
    """Resolve track metadata via iTunes Search (same matcher as cover art).

    Works with artist+title, or title alone (flat download filenames).
    Returns title/artist/album/date/track when a confident song match is found.
    """
    artist = (artist or "").strip()
    title = (title or "").strip()
    album = (album or "").strip()
    if not title:
        return None

    headers = {"User-Agent": "music-cataloger/0.1 (local music tagger)"}
    owns_client = client is None
    if client is None:
        client = httpx.Client(timeout=20.0, headers=headers, follow_redirects=True)
    try:
        if artist:
            countries: list[str | None] = [None, "es", "us", "fr", "gb"]
            queries = [f"{artist} {title}", f"{title} {artist}", title]
            for country in countries:
                for query in queries:
                    results = _itunes_search(
                        client, term=query, entity="song", country=country
                    )
                    row = _pick_itunes_song(
                        results, artist=artist, title=title, album=album
                    )
                    if row:
                        return _itunes_row_to_metadata(
                            row, title=title, artist=artist, album=album
                        )
            return None

        # Title-only: prefer the Spanish store first (Catalan / Iberian catalogues).
        countries = ["es", None, "us", "fr", "gb"]
        for country in countries:
            results = _itunes_search(
                client,
                term=title,
                entity="song",
                country=country,
                attribute="songTerm",
                limit=40,
            )
            if not results:
                results = _itunes_search(
                    client, term=title, entity="song", country=country, limit=40
                )
            row = _pick_itunes_song(
                results, artist="", title=title, album=album
            )
            if row:
                return _itunes_row_to_metadata(
                    row, title=title, artist="", album=album
                )
        return None
    finally:
        if owns_client:
            client.close()


def fetch_itunes_cover(
    artist: str,
    title: str,
    album: str = "",
    *,
    client: httpx.Client | None = None,
) -> tuple[bytes, str] | None:
    """Fetch cover art from iTunes, then Deezer as fallback."""
    artist = (artist or "").strip()
    title = (title or "").strip()
    album = (album or "").strip()
    if not ((artist and title) or (artist and album)):
        return None

    headers = {"User-Agent": "music-cataloger/0.1 (local music tagger)"}
    owns_client = client is None
    if client is None:
        client = httpx.Client(timeout=20.0, headers=headers, follow_redirects=True)
    try:
        found = _fetch_itunes_cover(client, artist=artist, title=title, album=album)
        if found:
            return found
        return _fetch_deezer_cover(client, artist=artist, title=title, album=album)
    finally:
        if owns_client:
            client.close()


def _fetch_itunes_cover(
    client: httpx.Client,
    *,
    artist: str,
    title: str,
    album: str,
) -> tuple[bytes, str] | None:
    countries: list[str | None] = [None, "es", "us", "fr", "gb"]
    song_queries: list[str] = []
    if artist and title:
        song_queries.extend([f"{artist} {title}", f"{title} {artist}", title])
    album_queries: list[str] = []
    if artist and album:
        album_queries.append(f"{artist} {album}")

    for country in countries:
        for query in song_queries:
            results = _itunes_search(client, term=query, entity="song", country=country)
            artwork = _pick_itunes_song_artwork(
                results, artist=artist, title=title, album=album
            )
            if artwork:
                downloaded = _download_image(client, _upsized_artwork_url(artwork))
                if downloaded:
                    return downloaded

        for query in album_queries:
            results = _itunes_search(client, term=query, entity="album", country=country)
            artwork = _pick_itunes_album_artwork(results, artist=artist, album=album)
            if artwork:
                downloaded = _download_image(client, _upsized_artwork_url(artwork))
                if downloaded:
                    return downloaded
    return None


def _fetch_deezer_cover(
    client: httpx.Client,
    *,
    artist: str,
    title: str,
    album: str,
) -> tuple[bytes, str] | None:
    """Deezer often indexes European/Catalan releases better than iTunes."""
    queries: list[str] = []
    if artist and title:
        queries.append(f'artist:"{artist}" track:"{title}"')
        queries.append(f"{artist} {title}")
    if artist and album:
        queries.append(f'artist:"{artist}" album:"{album}"')

    want_artist = _normalize_match(artist)
    want_title = _normalize_match(title)
    want_album = _normalize_match(album)

    for query in queries:
        response = client.get("https://api.deezer.com/search", params={"q": query, "limit": 12})
        if response.status_code != 200:
            continue
        rows = list((response.json() or {}).get("data") or [])
        best: tuple[int, str] | None = None
        for row in rows:
            album_info = row.get("album") or {}
            url = (
                album_info.get("cover_xl")
                or album_info.get("cover_big")
                or album_info.get("cover_medium")
            )
            if not url:
                continue
            got_artist = _normalize_match(str((row.get("artist") or {}).get("name") or ""))
            got_title = _normalize_match(str(row.get("title") or ""))
            got_album = _normalize_match(str(album_info.get("title") or ""))
            artist_score = _score_artist(want_artist, got_artist)
            title_score = _score_title(want_title, got_title)
            album_score = _score_album(want_album, got_album)
            total = artist_score + title_score + album_score
            # Album-query rows may have weak title; allow album path.
            album_ok = artist_score >= 2 and album_score >= 2 and total >= MIN_ALBUM_SCORE
            song_ok = (
                artist_score >= 2
                and title_score >= 2
                and total >= MIN_SONG_SCORE
            )
            if not (song_ok or album_ok):
                continue
            if best is None or total > best[0]:
                best = (total, str(url))
        if best:
            downloaded = _download_image(client, best[1])
            if downloaded:
                return downloaded
    return None
