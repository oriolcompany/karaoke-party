"""Find an embeddable music video for a local track.

Search is ``artist + title`` via yt-dlp. The first organic YouTube hit wins
(ads, trailers, Topic audio, and other promo are skipped). Only the video id
is cached. The browser then loads a muted YouTube iframe as stage wallpaper;
local audio stays the karaoke clock.
"""

from __future__ import annotations

import importlib.util
import json
import logging
import os
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from mutagen import File as MutagenFile

from .lyrics import cache_key as track_cache_key


log = logging.getLogger("karaoke_party")

YOUTUBE_CACHE_VERSION = 6
SEARCH_COUNT = 8
# Artist+title already required. Lyrics videos are rejected, not used as fallback.
MIN_ACCEPT_SCORE = 5
# Track vs video length: reject wild mismatches so a 3-minute song does not
# pick a 1-hour mix, but still allow a short official intro/outro.
MAX_DURATION_RATIO = 0.22
MAX_DURATION_DELTA = 40.0
# First organic hit is often the official clip, longer than the album cut.
MAX_FIRST_HIT_RATIO = 0.55
MAX_FIRST_HIT_DELTA = 90.0

YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
YOUTUBE_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/|shorts/|live/)|youtu\.be/)"
    r"([A-Za-z0-9_-]{11})"
)
YOUTUBE_BRACKET_RE = re.compile(r"\[([A-Za-z0-9_-]{11})\]")

SKIP_TOKENS = {
    "a",
    "al",
    "als",
    "an",
    "and",
    "d",
    "da",
    "de",
    "del",
    "di",
    "du",
    "el",
    "els",
    "en",
    "et",
    "feat",
    "featuring",
    "ft",
    "i",
    "la",
    "le",
    "les",
    "lo",
    "of",
    "the",
    "to",
    "un",
    "una",
    "vs",
    "with",
    "y",
}

REJECT_TITLE_RE = re.compile(
    r"(?:"
    r"\b1\s*h(?:our)?s?\b|"
    r"\b10\s*hours?\b|"
    r"\bhour\s+loop\b|"
    r"\bofficial\s+audio\b|"
    r"\baudio\s+only\b|"
    r"\bfull\s+album\b|"
    r"\bnightcore\b|"
    r"\b8d\s+audio\b|"
    r"\bslowed(?:\s*&\s*reverb)?\b|"
    r"\bkaraoke\b|"
    r"\binstrumental\b|"
    r"\bcover\s+by\b|"
    r"\breact(?:ion)?\b|"
    r"\bmashup\b|"
    r"\b(?:lyric|lyrics|lletra|letra)s?\b"
    r")",
    re.IGNORECASE,
)

OFFICIAL_VIDEO_RE = re.compile(
    r"(?:official\s+(?:music\s+)?video|videoclip\s+oficial|v[ií]deo\s+oficial|official\s+mv)\b",
    re.IGNORECASE,
)
LIVE_RE = re.compile(r"\b(?:live|en\s+directe|en\s+concert|vevo\s+lift)\b", re.IGNORECASE)
REMIX_RE = re.compile(r"\b(?:remix|nightcore|sped\s*up)\b", re.IGNORECASE)
# Paid placements and promo clips that YouTube often parks above the real hit.
AD_PROMO_RE = re.compile(
    r"(?:"
    r"\b(?:anuncis?|anuncios?|publicitat|publicidad|patrocinad[oa]|sponsored|promoted)\b|"
    r"\b(?:tv\s+)?(?:commercial|spot)\b|"
    r"\bads?\b|"
    r"\b(?:official\s+)?(?:movie\s+)?trailer\b|"
    r"\bteaser\b|"
    r"\bpreview\b|"
    r"\bpre[- ]?save\b|"
    r"\bpre[- ]?order\b|"
    r"\bout\s+now\b|"
    r"\bavailable\s+now\b|"
    r"\blisten\s+on\b|"
    r"\bstream\s+(?:now|on)\b|"
    r"\bbehind\s+the\s+scenes\b|"
    r"\bmaking\s+of\b|"
    r"\binterview\b|"
    r"\bmerch(?:andise)?\b|"
    r"\btour\s+dates?\b|"
    r"\balbum\s+announcement\b"
    r")",
    re.IGNORECASE,
)
TOPIC_CHANNEL_RE = re.compile(r"\s+[-–—]\s+topic$", re.IGNORECASE)


@dataclass(frozen=True)
class YoutubeClip:
    video_id: str
    title: str
    channel: str = ""
    duration: float = 0.0
    source: str = ""
    score: int = 0


class _QuietLogger:
    def debug(self, msg: str) -> None:
        del msg

    def info(self, msg: str) -> None:
        del msg

    def warning(self, msg: str) -> None:
        del msg

    def error(self, msg: str) -> None:
        del msg


def youtube_enabled() -> bool:
    return os.environ.get("KARAOKE_YOUTUBE", "1").strip().lower() not in {"0", "false", "no"}


def search_available() -> bool:
    return importlib.util.find_spec("yt_dlp") is not None


def empty_payload(source: str = "none") -> dict[str, Any]:
    return {
        "found": False,
        "video_id": "",
        "title": "",
        "channel": "",
        "duration": 0.0,
        "source": source,
        "score": 0,
        "candidates": [],
    }


def clip_payload(clip: YoutubeClip, *, candidates: list[str] | None = None) -> dict[str, Any]:
    ids: list[str] = []
    if clip.video_id:
        ids.append(clip.video_id)
    for video_id in candidates or []:
        if is_video_id(video_id) and video_id not in ids:
            ids.append(video_id)
    return {
        "found": True,
        "video_id": clip.video_id,
        "title": clip.title,
        "channel": clip.channel,
        "duration": float(clip.duration or 0),
        "source": clip.source,
        "score": int(clip.score),
        "candidates": ids,
    }


def is_video_id(value: str) -> bool:
    return bool(YOUTUBE_ID_RE.fullmatch((value or "").strip()))


def extract_youtube_id(text: str) -> str | None:
    """Return a YouTube id from a URL, yt-dlp `[id]` filename, or raw id."""
    blob = (text or "").strip()
    if not blob:
        return None
    url = YOUTUBE_URL_RE.search(blob)
    if url and is_video_id(url.group(1)):
        return url.group(1)
    bracket = YOUTUBE_BRACKET_RE.search(blob)
    if bracket and is_video_id(bracket.group(1)):
        return bracket.group(1)
    if is_video_id(blob):
        return blob
    return None


def extract_youtube_id_from_file(path: Path) -> str | None:
    """Prefer a tagged source URL, then a yt-dlp-style `[id]` in the filename."""
    try:
        resolved = Path(path)
    except TypeError:
        return None
    from_name = extract_youtube_id(resolved.name)
    blob_parts = [resolved.name]
    try:
        audio = MutagenFile(str(resolved))
    except Exception:
        audio = None
    tags = getattr(audio, "tags", None) if audio is not None else None
    if tags is not None:
        try:
            values = list(tags.values())
        except Exception:
            values = [tags]
        for value in values:
            blob_parts.append(str(value))
    tagged = extract_youtube_id("\n".join(blob_parts))
    return tagged or from_name


def _fold(text: str) -> str:
    """Lowercase and strip diacritics so tècnic and tecnic compare equal."""
    raw = (text or "").replace("l·l", "ll").replace("L·L", "ll")
    raw = raw.replace("ŀl", "ll").replace("ĿL", "ll").replace("ŀ", "l")
    stripped = unicodedata.normalize("NFKD", raw)
    return "".join(ch for ch in stripped if not unicodedata.combining(ch)).lower()


def _normalize(text: str) -> str:
    return re.sub(r"[^\w]+", "", _fold(text), flags=re.UNICODE)


def _tokens(text: str) -> list[str]:
    return [
        part
        for part in re.split(r"[^\w]+", _fold(text))
        if part and part not in SKIP_TOKENS
    ]


def _title_matched(track_title: str, video_title: str) -> bool:
    want = [token for token in _tokens(track_title) if len(token) >= 2]
    if not want:
        return bool(_normalize(track_title)) and _normalize(track_title) in _normalize(
            video_title
        )
    have = set(_tokens(video_title))
    if all(token in have for token in want):
        return True
    return bool(_normalize(track_title)) and _normalize(track_title) in _normalize(video_title)


def _title_mostly_matched(track_title: str, video_title: str) -> bool:
    """First-hit fallback: extra album words in the tag must not hide the song."""
    want = [token for token in _tokens(track_title) if len(token) >= 4]
    if not want:
        return _title_matched(track_title, video_title)
    have = set(_tokens(video_title))
    hits = sum(1 for token in want if token in have)
    return hits >= min(2, len(want))


def _artist_matched(artist: str, video_title: str, channel: str) -> bool:
    hay_title = _normalize(video_title)
    hay_channel = _normalize(channel)
    want = _normalize(artist)
    if want and (want in hay_title or want in hay_channel):
        return True
    tokens = [token for token in _tokens(artist) if len(token) >= 3]
    if not tokens:
        return False
    have = set(_tokens(video_title)) | set(_tokens(channel))
    return all(token in have for token in tokens)


def _duration_ok(
    track_duration: float,
    video_duration: float,
    *,
    first_hit: bool = False,
) -> bool:
    if track_duration <= 0 or video_duration <= 0:
        return True
    delta = abs(video_duration - track_duration)
    ratio = delta / track_duration
    if first_hit:
        return delta <= MAX_FIRST_HIT_DELTA or ratio <= MAX_FIRST_HIT_RATIO
    return delta <= MAX_DURATION_DELTA or ratio <= MAX_DURATION_RATIO


def _badge_text(entry: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("badges", "owner_badges", "ownerBadges"):
        raw = entry.get(key)
        if isinstance(raw, str):
            parts.append(raw)
            continue
        if not isinstance(raw, list):
            continue
        for item in raw:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("label") or item.get("style") or item.get("tooltip") or ""))
    return " ".join(part for part in parts if part)


def _is_ad_or_promo(entry: dict[str, Any], video_title: str, channel: str) -> bool:
    """Skip paid placements, auto-generated audio, and promotional clips."""
    if any(entry.get(flag) for flag in ("is_sponsored", "sponsored", "promoted", "is_ad", "advertisement")):
        return True
    kind = str(entry.get("_type") or "").lower()
    if kind in {"playlist", "channel"}:
        return True
    ie_key = str(entry.get("ie_key") or "")
    if ie_key in {"YoutubeTab", "YoutubePlaylist", "YoutubeSearch"}:
        return True
    title_l = (video_title or "").strip().lower()
    if title_l.startswith("mix -") or title_l.startswith("mix –"):
        return True
    if TOPIC_CHANNEL_RE.search((channel or "").strip()):
        return True
    if AD_PROMO_RE.search(video_title or ""):
        return True
    if AD_PROMO_RE.search(_badge_text(entry)):
        return True
    return False


def _unusable_search_hit(entry: dict[str, Any]) -> bool:
    """True for ads, promo, lyrics, karaoke, and other non-clip results."""
    if not isinstance(entry, dict):
        return True
    if entry.get("live_status") in {"is_live", "is_upcoming"}:
        return True
    video_id = str(entry.get("id") or "").strip()
    if not is_video_id(video_id):
        video_id = extract_youtube_id(
            str(entry.get("url") or entry.get("webpage_url") or "")
        ) or ""
    if not is_video_id(video_id):
        return True
    video_title = str(entry.get("title") or "")
    channel = str(entry.get("channel") or entry.get("uploader") or "")
    if entry.get("playable_in_embed") is False:
        return True
    if _is_ad_or_promo(entry, video_title, channel):
        return True
    if REJECT_TITLE_RE.search(video_title):
        return True
    return False


def score_youtube_entry(
    entry: dict[str, Any],
    *,
    artist: str,
    title: str,
    duration: float = 0.0,
    first_hit: bool = False,
) -> YoutubeClip | None:
    """Return a clip if this search hit is a real video for the song."""
    if not isinstance(entry, dict):
        return None
    if entry.get("live_status") in {"is_live", "is_upcoming"}:
        return None

    video_id = str(entry.get("id") or "").strip()
    if not is_video_id(video_id):
        video_id = extract_youtube_id(
            str(entry.get("url") or entry.get("webpage_url") or "")
        ) or ""
    if not is_video_id(video_id):
        return None

    video_title = str(entry.get("title") or "")
    channel = str(entry.get("channel") or entry.get("uploader") or "")
    try:
        video_duration = float(entry.get("duration") or 0)
    except (TypeError, ValueError):
        video_duration = 0.0

    if entry.get("playable_in_embed") is False:
        return None
    if _is_ad_or_promo(entry, video_title, channel):
        return None
    if REJECT_TITLE_RE.search(video_title):
        return None
    title_ok = _title_matched(title, video_title)
    artist_ok = (not artist) or _artist_matched(artist, video_title, channel)
    if not title_ok and first_hit and artist_ok:
        title_ok = _title_mostly_matched(title, video_title)
    if not title_ok:
        return None
    if artist and not artist_ok:
        return None
    if not _duration_ok(duration, video_duration, first_hit=first_hit):
        return None

    score = 7
    if OFFICIAL_VIDEO_RE.search(video_title):
        score += 5
    channel_l = channel.lower()
    if "vevo" in channel_l or channel_l.endswith("official") or "oficial" in channel_l:
        score += 2
    if duration > 0 and video_duration > 0:
        delta = abs(video_duration - duration)
        if delta <= 8:
            score += 2
        elif delta <= 20:
            score += 1
    if LIVE_RE.search(video_title):
        score -= 2
    if REMIX_RE.search(video_title):
        score -= 2

    if score < MIN_ACCEPT_SCORE:
        return None
    return YoutubeClip(
        video_id=video_id,
        title=video_title,
        channel=channel,
        duration=video_duration,
        source="yt-dlp-search",
        score=score,
    )


def pick_youtube_clips(
    entries: list[dict[str, Any]],
    *,
    artist: str,
    title: str,
    duration: float = 0.0,
    limit: int = 4,
) -> list[YoutubeClip]:
    """Organic hits in YouTube order: first result first, then embed fallbacks."""
    found: list[YoutubeClip] = []
    organic = 0
    for index, entry in enumerate(entries):
        if _unusable_search_hit(entry):
            continue
        clip = score_youtube_entry(
            entry,
            artist=artist,
            title=title,
            duration=duration,
            first_hit=(organic == 0),
        )
        organic += 1
        if clip is None:
            continue
        found.append(
            YoutubeClip(
                video_id=clip.video_id,
                title=clip.title,
                channel=clip.channel,
                duration=clip.duration,
                source=clip.source,
                score=max(clip.score, SEARCH_COUNT - index),
            )
        )
        if len(found) >= limit:
            break
    return found


def pick_youtube_clip(
    entries: list[dict[str, Any]],
    *,
    artist: str,
    title: str,
    duration: float = 0.0,
) -> YoutubeClip | None:
    """Prefer YouTube's first organic hit for artist+title, skipping ads/promo."""
    clips = pick_youtube_clips(
        entries, artist=artist, title=title, duration=duration, limit=1
    )
    return clips[0] if clips else None


def _search_youtube(query: str) -> list[dict[str, Any]]:
    import yt_dlp

    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": True,
        "noplaylist": True,
        "ignoreerrors": True,
        "socket_timeout": 15,
        "logger": _QuietLogger(),
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"ytsearch{SEARCH_COUNT}:{query}", download=False)
    if not isinstance(info, dict):
        return []
    return [row for row in (info.get("entries") or []) if isinstance(row, dict)]


def youtube_path(cache_dir: Path, key: str) -> Path:
    from .track_cache import youtube_path as cached_path

    return cached_path(cache_dir, key)


def load_cached(cache_dir: Path, key: str) -> dict[str, Any] | None:
    path = youtube_path(cache_dir, key)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    try:
        version = int(data.get("version") or 0)
    except (TypeError, ValueError):
        version = 0
    if version < YOUTUBE_CACHE_VERSION:
        return None
    payload = empty_payload(str(data.get("source") or "cache"))
    payload["found"] = bool(data.get("found") and data.get("video_id"))
    payload["video_id"] = str(data.get("video_id") or "") if payload["found"] else ""
    payload["title"] = str(data.get("title") or "")
    payload["channel"] = str(data.get("channel") or "")
    try:
        payload["duration"] = float(data.get("duration") or 0)
    except (TypeError, ValueError):
        payload["duration"] = 0.0
    try:
        payload["score"] = int(data.get("score") or 0)
    except (TypeError, ValueError):
        payload["score"] = 0
    if payload["found"] and not is_video_id(payload["video_id"]):
        return None
    candidates: list[str] = []
    raw_candidates = data.get("candidates")
    if isinstance(raw_candidates, list):
        for item in raw_candidates:
            video_id = str(item or "").strip()
            if is_video_id(video_id) and video_id not in candidates:
                candidates.append(video_id)
    if payload["video_id"] and payload["video_id"] not in candidates:
        candidates.insert(0, payload["video_id"])
    payload["candidates"] = candidates
    return payload


def save_cached(
    cache_dir: Path,
    key: str,
    payload: dict[str, Any],
    *,
    artist: str = "",
    title: str = "",
    duration: float | None = None,
    album: str = "",
) -> None:
    from .track_cache import ensure_track_dir, write_meta

    ensure_track_dir(cache_dir, key)
    if artist or title:
        write_meta(
            cache_dir,
            key,
            artist=artist,
            title=title,
            duration=duration,
            album=album,
        )
    data = {
        "version": YOUTUBE_CACHE_VERSION,
        "found": bool(payload.get("found") and payload.get("video_id")),
        "video_id": str(payload.get("video_id") or ""),
        "title": str(payload.get("title") or ""),
        "channel": str(payload.get("channel") or ""),
        "duration": float(payload.get("duration") or 0),
        "source": str(payload.get("source") or ""),
        "score": int(payload.get("score") or 0),
        "candidates": [
            video_id
            for video_id in (payload.get("candidates") or [])
            if is_video_id(str(video_id))
        ],
    }
    youtube_path(cache_dir, key).write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def resolve_youtube_clip(
    *,
    path: Path | None,
    artist: str,
    title: str,
    duration: float,
    album: str = "",
    cache_dir: Path,
    search: Callable[[str], list[dict[str, Any]]] | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Return a cached or freshly searched clip payload for one track."""
    key = track_cache_key(artist, title, duration)
    if not force:
        cached = load_cached(cache_dir, key)
        if cached is not None:
            return cached

    file_id = extract_youtube_id_from_file(path) if path else None
    if file_id:
        payload = clip_payload(
            YoutubeClip(
                video_id=file_id,
                title=title,
                channel=artist,
                duration=duration,
                source="file",
                score=99,
            )
        )
        save_cached(
            cache_dir,
            key,
            payload,
            artist=artist,
            title=title,
            duration=duration,
            album=album,
        )
        return payload

    if not youtube_enabled():
        return empty_payload("disabled")

    query = " ".join(part for part in (artist, title) if part).strip()
    if not query:
        payload = empty_payload("none")
        save_cached(
            cache_dir,
            key,
            payload,
            artist=artist,
            title=title,
            duration=duration,
            album=album,
        )
        return payload

    search_fn = search if search is not None else _search_youtube
    if search is None and not search_available():
        return empty_payload("unavailable")

    try:
        entries = search_fn(query)
    except Exception:
        log.exception("YouTube search failed for %s", query)
        return empty_payload("error")

    if not entries:
        log.warning("YouTube search returned no results for %s", query)
        return empty_payload("error")

    clips = pick_youtube_clips(entries, artist=artist, title=title, duration=duration)
    if clips:
        log.info("YouTube hit %s → %s (%s)", query, clips[0].video_id, clips[0].title)
        payload = clip_payload(
            clips[0],
            candidates=[clip.video_id for clip in clips],
        )
    else:
        sample = ", ".join(
            str(row.get("title") or row.get("id") or "?") for row in entries[:3]
        )
        log.info("YouTube miss %s · %s resultats · %s", query, len(entries), sample)
        payload = empty_payload("none")
    save_cached(
        cache_dir,
        key,
        payload,
        artist=artist,
        title=title,
        duration=duration,
        album=album,
    )
    return payload


def has_youtube_hit(cache_dir: Path, artist: str, title: str, duration: float) -> bool:
    """True when this track already has a cached, usable video id."""
    cached = load_cached(cache_dir, track_cache_key(artist, title, duration))
    return bool(cached and cached.get("found") and cached.get("video_id"))
