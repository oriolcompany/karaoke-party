from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import httpx

LRC_LINE_RE = re.compile(r"\[(\d{1,2}):(\d{2})(?:\.(\d{1,3}))?\](.*)")
ENHANCED_WORD_RE = re.compile(r"<(\d{1,2}):(\d{2})(?:\.(\d{1,3}))?>([^<]*)")
LRCLIB_BASE = os.environ.get("KARAOKE_LRCLIB_BASE", "https://lrclib.net").rstrip("/")
LRCLIB_GET = f"{LRCLIB_BASE}/api/get"
LRCLIB_SEARCH = f"{LRCLIB_BASE}/api/search"
RETRY_BASE_DELAY = 1.0
MAX_RETRY_DELAY = 8.0
DEFAULT_TIMEOUT = 20.0
PROBE_TIMEOUT = 8.0
PROBE_ERROR_SOURCE = "probe-error"
# Bump when the aligner changes so old, less precise timings are recomputed
# instead of being served forever from disk.
ALIGNED_CACHE_VERSION = 3


@dataclass
class LyricWord:
    time: float
    end: float
    text: str


@dataclass
class LyricLine:
    time: float
    text: str
    words: list[LyricWord] = field(default_factory=list)


@dataclass
class LyricsPayload:
    synced: bool
    source: str
    lines: list[LyricLine]
    plain: str = ""


def _timestamp(minutes: str, seconds: str, frac: str | None) -> float:
    piece = frac or "0"
    if len(piece) == 1:
        piece = piece + "00"
    elif len(piece) == 2:
        piece = piece + "0"
    return int(minutes) * 60 + int(seconds) + int(piece[:3]) / 1000.0


def _split_words(text: str) -> list[str]:
    return [part for part in re.split(r"(\s+)", text) if part and not part.isspace()]


def parse_enhanced_words(raw: str) -> tuple[str, list[LyricWord]]:
    """Parse Enhanced LRC word tags; return plain text and timed words."""
    matches = list(ENHANCED_WORD_RE.finditer(raw))
    if not matches:
        clean = ENHANCED_WORD_RE.sub("", raw).strip()
        return clean, []
    words: list[LyricWord] = []
    plain_parts: list[str] = []
    for index, match in enumerate(matches):
        start = _timestamp(match.group(1), match.group(2), match.group(3))
        text = match.group(4).strip()
        if not text:
            continue
        if index + 1 < len(matches):
            end = _timestamp(matches[index + 1].group(1), matches[index + 1].group(2), matches[index + 1].group(3))
        else:
            end = start + max(0.35, 0.12 * max(1, len(text)))
        words.append(LyricWord(time=start, end=max(end, start + 0.05), text=text))
        plain_parts.append(text)
    return " ".join(plain_parts), words


def estimate_words(line_time: float, next_time: float | None, text: str) -> list[LyricWord]:
    """Spread words across the line window when no word-level timings exist.

    LRCLIB usually only provides line starts, so this is an approximation: words are
    spaced evenly until just before the next line.
    """
    tokens = _split_words(text)
    if not tokens:
        return []
    span = (next_time - line_time) if next_time is not None else max(2.5, 0.35 * len(tokens))
    span = max(span, 0.4 * len(tokens))
    usable = span * 0.92
    step = usable / len(tokens)
    words: list[LyricWord] = []
    for index, token in enumerate(tokens):
        start = line_time + index * step
        end = line_time + (index + 1) * step
        words.append(LyricWord(time=start, end=end, text=token))
    return words


def attach_word_timings(lines: list[LyricLine]) -> list[LyricLine]:
    enriched: list[LyricLine] = []
    for index, line in enumerate(lines):
        next_time = lines[index + 1].time if index + 1 < len(lines) else None
        plain, enhanced = parse_enhanced_words(line.text)
        text = plain or line.text
        words = enhanced or estimate_words(line.time, next_time, text)
        if words and next_time is not None and words[-1].end > next_time:
            words[-1].end = next_time
        enriched.append(LyricLine(time=line.time, text=text, words=words))
    return enriched


def parse_lrc(content: str) -> list[LyricLine]:
    lines: list[LyricLine] = []
    for raw in content.splitlines():
        match = LRC_LINE_RE.match(raw.strip())
        if not match:
            continue
        start = _timestamp(match.group(1), match.group(2), match.group(3))
        text = match.group(4).strip()
        if not text:
            continue
        lines.append(LyricLine(time=start, text=text))
    lines.sort(key=lambda line: line.time)
    return attach_word_timings(lines)


def cache_key(artist: str, title: str, duration: float | None) -> str:
    raw = f"{artist.strip().lower()}|{title.strip().lower()}|{int(duration or 0)}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def load_cached(cache_dir: Path, key: str) -> LyricsPayload | None:
    from .track_cache import lyrics_path

    path = lyrics_path(cache_dir, key)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    # Rebuild word timings every load so estimator improvements apply even with old cache.
    base_lines = [
        LyricLine(time=float(row["time"]), text=str(row.get("text") or ""))
        for row in data.get("lines") or []
    ]
    lines = attach_word_timings(base_lines)
    return LyricsPayload(
        synced=bool(data.get("synced")),
        source=str(data.get("source") or "cache"),
        lines=lines,
        plain=str(data.get("plain") or ""),
    )


def load_aligned_cached(cache_dir: Path, key: str) -> LyricsPayload | None:
    from .track_cache import aligned_path

    path = aligned_path(cache_dir, key)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        version = int(data.get("align_version") or 1)
    except (TypeError, ValueError):
        version = 1
    if version < ALIGNED_CACHE_VERSION:
        return None
    lines: list[LyricLine] = []
    for row in data.get("lines") or []:
        words = [LyricWord(**word) for word in row.get("words") or []]
        lines.append(
            LyricLine(time=float(row["time"]), text=str(row.get("text") or ""), words=words)
        )
    if not lines:
        return None
    return LyricsPayload(
        synced=True,
        source=str(data.get("source") or "aligned"),
        lines=lines,
        plain=str(data.get("plain") or ""),
    )


def save_cached(
    cache_dir: Path,
    key: str,
    payload: LyricsPayload,
    extra: dict[str, Any] | None = None,
    *,
    artist: str = "",
    title: str = "",
    duration: float | None = None,
    album: str = "",
) -> None:
    from .track_cache import ensure_track_dir, lyrics_path, write_meta

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
    path = lyrics_path(cache_dir, key)
    data: dict[str, Any] = {
        "synced": payload.synced,
        "source": payload.source,
        "plain": payload.plain,
        "lines": [asdict(line) for line in payload.lines],
    }
    if extra:
        data.update(extra)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_aligned_cached(
    cache_dir: Path,
    key: str,
    payload: LyricsPayload,
    *,
    artist: str = "",
    title: str = "",
    duration: float | None = None,
    album: str = "",
) -> None:
    from .track_cache import aligned_path, ensure_track_dir, write_meta

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
    path = aligned_path(cache_dir, key)
    data: dict[str, Any] = {
        "synced": payload.synced,
        "source": payload.source,
        "plain": payload.plain,
        "lines": [asdict(line) for line in payload.lines],
        "align_version": ALIGNED_CACHE_VERSION,
    }
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _from_lrclib_record(record: dict[str, Any], source: str) -> LyricsPayload | None:
    synced = (record.get("syncedLyrics") or "").strip()
    plain = (record.get("plainLyrics") or "").strip()
    if synced:
        lines = parse_lrc(synced)
        if lines:
            return LyricsPayload(synced=True, source=source, lines=lines, plain=plain)
    if plain:
        rough = [
            LyricLine(time=float(i * 4), text=line.strip())
            for i, line in enumerate(plain.splitlines())
            if line.strip()
        ]
        lines = attach_word_timings(rough)
        return LyricsPayload(synced=False, source=source, lines=lines, plain=plain)
    return None


class LyricsUnavailable(RuntimeError):
    """LRCLIB could not be reached (timeout, throttling, server error).

    Distinct from "this song has no lyrics" so a transient failure is never
    cached as a permanent miss.
    """


def _retry_after_seconds(response: httpx.Response) -> float | None:
    raw = response.headers.get("retry-after")
    if not raw:
        return None
    try:
        return max(0.0, float(raw))
    except ValueError:
        return None


async def _get_with_retry(
    client: httpx.AsyncClient,
    url: str,
    params: dict[str, Any],
    *,
    attempts: int = 3,
) -> httpx.Response:
    """GET that retries throttling/server errors instead of giving up at once."""
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            response = await client.get(url, params=params)
        except httpx.HTTPError as exc:
            last_error = exc
        else:
            if response.status_code < 500 and response.status_code != 429:
                return response
            last_error = LyricsUnavailable(f"{url} returned {response.status_code}")
            wait = _retry_after_seconds(response)
            if wait is None:
                wait = RETRY_BASE_DELAY * (2**attempt)
            if attempt < attempts - 1:
                await asyncio.sleep(min(wait, MAX_RETRY_DELAY))
            continue
        if attempt < attempts - 1:
            await asyncio.sleep(min(RETRY_BASE_DELAY * (2**attempt), MAX_RETRY_DELAY))
    raise LyricsUnavailable(str(last_error) if last_error else f"{url} unreachable")


async def fetch_lyrics(
    artist: str,
    title: str,
    album: str = "",
    duration: float | None = None,
    cache_dir: Path | None = None,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    attempts: int = 3,
) -> LyricsPayload:
    key = cache_key(artist, title, duration)
    if cache_dir:
        cached = load_cached(cache_dir, key)
        if cached is not None:
            return cached

    headers = {"User-Agent": "karaoke-party/0.1 (local karaoke app)"}
    params: dict[str, Any] = {
        "artist_name": artist,
        "track_name": title,
    }
    if album:
        params["album_name"] = album
    if duration:
        params["duration"] = int(round(duration))

    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        response = await _get_with_retry(client, LRCLIB_GET, params, attempts=attempts)
        payload: LyricsPayload | None = None
        if response.status_code == 200:
            payload = _from_lrclib_record(response.json(), "lrclib")
        if payload is None:
            search = await _get_with_retry(
                client,
                LRCLIB_SEARCH,
                {"q": f"{artist} {title}"},
                attempts=attempts,
            )
            if search.status_code == 200:
                results = search.json() or []
                for record in results[:5]:
                    payload = _from_lrclib_record(record, "lrclib-search")
                    if payload and payload.synced:
                        break
                if payload is None and results:
                    payload = _from_lrclib_record(results[0], "lrclib-search")

    if payload is None:
        payload = LyricsPayload(synced=False, source="none", lines=[], plain="")

    if cache_dir:
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


async def track_has_lyrics(
    artist: str,
    title: str,
    album: str = "",
    duration: float | None = None,
    *,
    lyrics_cache: Path,
    aligned_cache: Path | None = None,
) -> bool:
    """Return True when synced/plain lyrics exist (uses cache, then LRCLIB)."""
    status = lyrics_status_cached(
        artist,
        title,
        duration,
        lyrics_cache=lyrics_cache,
        aligned_cache=aligned_cache,
    )
    if status is not None:
        return status
    payload = await fetch_lyrics(
        artist=artist,
        title=title,
        album=album,
        duration=duration,
        cache_dir=lyrics_cache,
    )
    return bool(payload.lines)


def lyrics_status_cached(
    artist: str,
    title: str,
    duration: float | None = None,
    *,
    lyrics_cache: Path,
    aligned_cache: Path | None = None,
) -> bool | None:
    """True = has lyrics, False = known miss, None = not checked yet."""
    status, _source = lyrics_status_and_source(
        artist,
        title,
        duration,
        lyrics_cache=lyrics_cache,
        aligned_cache=aligned_cache,
    )
    return status


def lyrics_status_and_source(
    artist: str,
    title: str,
    duration: float | None = None,
    *,
    lyrics_cache: Path,
    aligned_cache: Path | None = None,
) -> tuple[bool | None, str]:
    """Status plus the cache source, so probe errors stay distinguishable."""
    key = cache_key(artist, title, duration)
    if aligned_cache is not None and load_aligned_cached(aligned_cache, key) is not None:
        return True, "aligned"
    try:
        cached = load_cached(lyrics_cache, key)
    except (OSError, ValueError):
        return None, ""
    if cached is None:
        return None, ""
    return bool(cached.lines), cached.source


def clear_probe_errors(lyrics_cache: Path) -> int:
    """Drop cached entries that only failed because LRCLIB was unreachable."""
    from .track_cache import iter_track_keys, lyrics_path

    if not lyrics_cache.is_dir():
        return 0
    removed = 0
    for key in iter_track_keys(lyrics_cache):
        path = lyrics_path(lyrics_cache, key)
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if str(data.get("source") or "") != PROBE_ERROR_SOURCE:
            continue
        try:
            path.unlink()
            removed += 1
        except OSError:
            continue
    return removed


def clear_lyrics_cache(lyrics_cache: Path) -> int:
    """Remove all cached LRCLIB results so the next probe re-fetches."""
    from .track_cache import clear_all_tracks

    return clear_all_tracks(lyrics_cache, {"lyrics"})["lyrics"]


def clear_lyrics_keys(lyrics_cache: Path, keys: list[str]) -> int:
    """Remove specific cached LRCLIB entries by cache key."""
    from .track_cache import clear_track_files

    removed = 0
    for key in keys:
        removed += clear_track_files(lyrics_cache, key, {"lyrics"})["lyrics"]
    return removed


def clear_aligned_keys(aligned_cache: Path, keys: list[str]) -> int:
    """Remove Whisper alignment cache files by key (any version)."""
    from .track_cache import clear_track_files

    removed = 0
    for key in keys:
        removed += clear_track_files(aligned_cache, key, {"aligned"})["aligned"]
    return removed
