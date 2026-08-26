from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx

LRC_LINE_RE = re.compile(r"\[(\d{1,2}):(\d{2})(?:\.(\d{1,3}))?\](.*)")
ENHANCED_WORD_RE = re.compile(r"<(\d{1,2}):(\d{2})(?:\.(\d{1,3}))?>([^<]*)")
# Drop featured-artist suffixes and common version tags so LRCLIB/lyrics.ovh match.
_FEAT_SUFFIX_RE = re.compile(
    r"\s*[\(\[]?\s*(?:feat\.?|ft\.?|featuring)\b.*",
    re.IGNORECASE,
)
_VERSION_PAREN_RE = re.compile(
    r"\s*[\(\[][^)\]]*\b(?:remix|remaster(?:ed)?|radio\s*edit|acoustic|live|"
    r"instrumental|karaoke|version)\b[^)\]]*[\)\]]",
    re.IGNORECASE,
)
_OVH_HEADER_RE = re.compile(r"^paroles de la chanson\b.*$", re.IGNORECASE)
LRCLIB_BASE = os.environ.get("KARAOKE_LRCLIB_BASE", "https://lrclib.net").rstrip("/")
LRCLIB_GET = f"{LRCLIB_BASE}/api/get"
LRCLIB_SEARCH = f"{LRCLIB_BASE}/api/search"
LYRICS_OVH_BASE = os.environ.get("KARAOKE_LYRICS_OVH_BASE", "https://api.lyrics.ovh").rstrip("/")
RETRY_BASE_DELAY = 1.0
MAX_RETRY_DELAY = 8.0
DEFAULT_TIMEOUT = 20.0
PROBE_TIMEOUT = 8.0
PROBE_ERROR_SOURCE = "probe-error"
LOCAL_LYRICS_MAX_BYTES = 512_000
MANUAL_LYRICS_MAX_CHARS = 200_000
DURATION_CLOSE_SECONDS = 8.0
DURATION_ACCEPT_SECONDS = 20.0
# Bump when the aligner changes so old, less precise timings are recomputed
# instead of being served forever from disk. v5: Meta MMS syllable alignment.
ALIGNED_CACHE_VERSION = 5


@dataclass
class LyricWord:
    time: float
    end: float
    text: str
    glue: bool = False


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


def sung_word_duration(text: str) -> float:
    """Typical sung length for a token; used to keep pickups from eating pauses."""
    letters = sum(1 for char in text if char.isalnum()) or 1
    return max(0.12, min(0.70, 0.08 * letters + 0.10))


def tighten_phrase_onsets(lines: list[LyricLine]) -> list[LyricLine]:
    """Keep the first word of each line from painting through the pre-phrase pause.

    Whisper (and leftover interpolation) often stamps a short pickup like "I" or
    "Un" from the previous line's end up to the second word. The karaoke fill
    then crawls through silence before anyone has sung it.
    """
    prev_end: float | None = None
    for line in lines:
        words = line.words
        if not words:
            continue
        first = words[0]
        expected = sung_word_duration(first.text)
        duration = first.end - first.time
        gap_before = 0.0 if prev_end is None else first.time - prev_end
        absorbed = gap_before < 0.12
        letters = sum(1 for char in first.text if char.isalnum()) or 1
        hold_after_pause = letters >= 4 and gap_before > 0.25 and duration > 0.8
        if hold_after_pause:
            prev_end = words[-1].end
            continue
        short_pickup = letters <= 3 and duration > expected * 1.5 and (
            absorbed or prev_end is None or duration > 0.7
        )
        long_span = duration > max(1.0, expected * 2.5)
        absorbed_stretch = absorbed and duration > expected * 1.8
        if len(words) == 1:
            if letters <= 3 and duration > 0.8 and absorbed:
                first.time = max(first.time, first.end - expected)
                line.time = first.time
            prev_end = words[-1].end
            continue
        if short_pickup or long_span or absorbed_stretch:
            boundary = min(first.end, words[1].time)
            first.time = max(first.time, boundary - expected)
            if first.end < first.time + 0.08:
                first.end = first.time + 0.08
            line.time = first.time
        prev_end = words[-1].end
    return lines


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


def clean_query_text(value: str) -> str:
    """Strip feat./version clutter from artist or title for lookups."""
    text = value.strip()
    text = _VERSION_PAREN_RE.sub("", text)
    text = _FEAT_SUFFIX_RE.sub("", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip(" -–—")


def _duration_param(duration: float | None) -> int | None:
    if duration is None or duration <= 0:
        return None
    return int(round(duration))


def payload_from_text(text: str, source: str) -> LyricsPayload | None:
    """Build a payload from pasted or downloaded text (LRC or plain lines)."""
    raw = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not raw:
        return None
    nonempty = [line for line in raw.splitlines() if line.strip()]
    if not nonempty:
        return None
    lrc_lines = parse_lrc(raw)
    if lrc_lines and (
        len(lrc_lines) >= 2 or len(lrc_lines) >= max(1, int(len(nonempty) * 0.5))
    ):
        plain = "\n".join(line.text for line in lrc_lines)
        return LyricsPayload(synced=True, source=source, lines=lrc_lines, plain=plain)
    rough = [
        LyricLine(time=float(index * 4), text=line.strip())
        for index, line in enumerate(nonempty)
    ]
    return LyricsPayload(
        synced=False,
        source=source,
        lines=attach_word_timings(rough),
        plain="\n".join(nonempty),
    )


def _format_lrc_time(seconds: float) -> str:
    total_cs = int(round(max(0.0, float(seconds)) * 100.0))
    minutes, cs = divmod(total_cs, 6000)
    secs, cs = divmod(cs, 100)
    return f"[{minutes:02d}:{secs:02d}.{cs:02d}]"


def payload_to_text(payload: LyricsPayload | None) -> str:
    """Serialize a payload back to plain text or LRC for the editor / tags."""
    if payload is None:
        return ""
    if payload.synced and payload.lines:
        return "\n".join(
            f"{_format_lrc_time(line.time)}{line.text.strip()}"
            for line in payload.lines
            if (line.text or "").strip()
        )
    plain = (payload.plain or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if plain:
        return plain
    return "\n".join(line.text.strip() for line in payload.lines if (line.text or "").strip())


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
        words = [
            LyricWord(
                time=float(word["time"]),
                end=float(word["end"]),
                text=str(word.get("text") or ""),
                glue=bool(word.get("glue", False)),
            )
            for word in row.get("words") or []
        ]
        lines.append(
            LyricLine(time=float(row["time"]), text=str(row.get("text") or ""), words=words)
        )
    if not lines:
        return None
    return LyricsPayload(
        synced=True,
        source=str(data.get("source") or "aligned"),
        lines=tighten_phrase_onsets(lines),
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
            return LyricsPayload(
                synced=True,
                source=source,
                lines=lines,
                plain=plain or "\n".join(line.text for line in lines),
            )
    if plain:
        return payload_from_text(plain, source)
    return None


def _compact_params(params: dict[str, Any]) -> dict[str, Any]:
    compact: dict[str, Any] = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        compact[key] = value
    return compact


def _lrclib_get_queries(
    artist: str,
    title: str,
    album: str,
    duration: float | None,
) -> list[dict[str, Any]]:
    """Increasingly relaxed /api/get queries; duration mismatches are a common miss."""
    duration_i = _duration_param(duration)
    cleaned_artist = clean_query_text(artist) or artist
    cleaned_title = clean_query_text(title) or title
    attempts: list[dict[str, Any]] = []

    def add(params: dict[str, Any]) -> None:
        compact = _compact_params(params)
        if compact and compact not in attempts:
            attempts.append(compact)

    add(
        {
            "artist_name": artist,
            "track_name": title,
            "album_name": album,
            "duration": duration_i,
        }
    )
    if duration_i is not None:
        add({"artist_name": artist, "track_name": title, "album_name": album})
    add({"artist_name": artist, "track_name": title, "duration": duration_i})
    if cleaned_artist != artist or cleaned_title != title:
        add(
            {
                "artist_name": cleaned_artist,
                "track_name": cleaned_title,
                "duration": duration_i,
            }
        )
    return attempts


def _record_duration(record: dict[str, Any]) -> float | None:
    raw = record.get("duration")
    if raw is None:
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def _best_lrclib_record(
    results: list[Any],
    duration: float | None,
) -> dict[str, Any] | None:
    """Prefer close duration, then synced lyrics, then any plain text."""
    scored: list[tuple[tuple[int, int, float], dict[str, Any]]] = []
    target = float(duration) if duration and duration > 0 else None
    for record in results:
        if not isinstance(record, dict):
            continue
        if not (record.get("syncedLyrics") or record.get("plainLyrics") or "").strip():
            continue
        rec_dur = _record_duration(record)
        delta = abs(rec_dur - target) if target is not None and rec_dur is not None else 25.0
        band = 0 if delta <= DURATION_CLOSE_SECONDS else (1 if delta <= DURATION_ACCEPT_SECONDS else 2)
        synced = 0 if (record.get("syncedLyrics") or "").strip() else 1
        scored.append(((band, synced, delta), record))
    if not scored:
        return None
    scored.sort(key=lambda item: item[0])
    return scored[0][1]


def _read_text_file(path: Path) -> str | None:
    try:
        if not path.is_file() or path.stat().st_size > LOCAL_LYRICS_MAX_BYTES:
            return None
        data = path.read_bytes()
    except OSError:
        return None
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def _sidecar_candidates(audio_path: Path) -> list[tuple[Path, str]]:
    stem = audio_path.with_suffix("")
    return [
        (stem.with_suffix(".lrc"), "local-lrc"),
        (stem.with_suffix(".LRC"), "local-lrc"),
        (stem.with_suffix(".txt"), "local-txt"),
        (stem.with_suffix(".TXT"), "local-txt"),
    ]


def _find_sidecar(audio_path: Path) -> tuple[Path, str] | None:
    seen: set[Path] = set()
    for candidate, source in _sidecar_candidates(audio_path):
        try:
            resolved = candidate.resolve()
        except OSError:
            resolved = candidate
        if resolved in seen:
            continue
        seen.add(resolved)
        try:
            if candidate.is_file() and candidate.stat().st_size > 0:
                return candidate, source
        except OSError:
            continue
    return None


def _group_timed_tokens(tokens: list[tuple[float, str]]) -> list[LyricLine]:
    """Turn SYLT word/line stamps into karaoke lines (gap or newline splits)."""
    lines: list[LyricLine] = []
    bucket: list[tuple[float, str]] = []

    def flush() -> None:
        if not bucket:
            return
        words: list[LyricWord] = []
        for index, (start, text) in enumerate(bucket):
            end = bucket[index + 1][0] if index + 1 < len(bucket) else start + sung_word_duration(text)
            words.append(LyricWord(time=start, end=max(end, start + 0.05), text=text))
        lines.append(
            LyricLine(
                time=bucket[0][0],
                text=" ".join(part for _, part in bucket),
                words=words,
            )
        )
        bucket.clear()

    last_time: float | None = None
    for start, raw in tokens:
        pieces = raw.replace("\r", "").split("\n")
        for index, piece in enumerate(pieces):
            if index > 0:
                flush()
            text = piece.strip()
            if not text:
                continue
            if last_time is not None and start - last_time > 1.8:
                flush()
            bucket.append((start, text))
            last_time = start
    flush()
    return lines


def _payload_from_id3_tags(tags: Any) -> LyricsPayload | None:
    getall = getattr(tags, "getall", None)
    if not callable(getall):
        return None
    for frame in getall("SYLT"):
        fmt = int(getattr(frame, "format", 2) or 2)
        if fmt != 2:
            continue
        tokens: list[tuple[float, str]] = []
        for item in getattr(frame, "text", None) or []:
            if not isinstance(item, (tuple, list)) or len(item) < 2:
                continue
            text = str(item[0] or "").strip()
            try:
                stamp = float(item[1])
            except (TypeError, ValueError):
                continue
            if not text:
                continue
            tokens.append((stamp / 1000.0, text))
        if tokens:
            lines = _group_timed_tokens(tokens)
            if lines:
                return LyricsPayload(
                    synced=True,
                    source="local-sylt",
                    lines=lines,
                    plain="\n".join(line.text for line in lines),
                )
    for frame in getall("USLT"):
        text = str(getattr(frame, "text", "") or "").strip()
        payload = payload_from_text(text, "local-uslt")
        if payload:
            return payload
    return None


def _payload_from_generic_tags(tags: Any) -> LyricsPayload | None:
    keys = (
        "LYRICS",
        "UNSYNCEDLYRICS",
        "lyrics",
        "©lyr",
        "----:com.apple.iTunes:LYRICS",
    )
    for key in keys:
        try:
            value = tags.get(key)
        except Exception:
            continue
        if value is None:
            continue
        items = value if isinstance(value, list) else [value]
        chunks: list[str] = []
        for item in items:
            text = getattr(item, "text", item)
            if isinstance(text, list):
                text = "\n".join(str(part) for part in text if part)
            chunks.append(str(text or "").strip())
        payload = payload_from_text("\n".join(part for part in chunks if part), "local-tags")
        if payload:
            return payload
    return None


def read_sidecar_lyrics(audio_path: Path | str | None) -> LyricsPayload | None:
    """Read ``song.lrc`` / ``song.txt`` next to the audio file."""
    if not audio_path:
        return None
    path = Path(audio_path)
    found = _find_sidecar(path)
    if found is None:
        return None
    candidate, source = found
    raw = _read_text_file(candidate)
    if not raw:
        return None
    return payload_from_text(raw, source)


def read_local_lyrics(audio_path: Path | str | None) -> LyricsPayload | None:
    """Sidecar .lrc/.txt first, then ID3 SYLT/USLT and other embedded tags."""
    sidecar = read_sidecar_lyrics(audio_path)
    if sidecar is not None:
        return sidecar
    if not audio_path:
        return None
    path = Path(audio_path)
    if not path.is_file():
        return None
    try:
        from mutagen import File as MutagenFile
        from mutagen.id3 import ID3
    except ImportError:
        return None
    tags = None
    try:
        audio = MutagenFile(path)
    except Exception:
        audio = None
    if audio is not None:
        tags = audio.tags
    if tags is None:
        try:
            tags = ID3(path)
        except Exception:
            tags = None
    if tags is None:
        return None
    return _payload_from_id3_tags(tags) or _payload_from_generic_tags(tags)


def _id3_has_lyrics(tags: Any) -> bool:
    getall = getattr(tags, "getall", None)
    if not callable(getall):
        return False
    return bool(getall("USLT") or getall("SYLT"))


def _embed_id3_lyrics(audio_path: Path, text: str, *, overwrite: bool) -> bool:
    from mutagen.id3 import ID3, ID3NoHeaderError, USLT

    try:
        tags = ID3(str(audio_path))
    except ID3NoHeaderError:
        tags = ID3()
    except Exception:
        return False
    if _id3_has_lyrics(tags) and not overwrite:
        return False
    try:
        tags.delall("USLT")
        tags.delall("SYLT")
        tags.add(USLT(encoding=3, lang="cat", desc="", text=text))
        tags.save(str(audio_path))
        return True
    except Exception:
        return False


def embed_lyrics_in_audio(audio_path: Path | str, text: str, *, overwrite: bool = False) -> bool:
    """Write lyrics into the audio file tags. Returns True when the file changed."""
    raw = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not raw:
        return False
    path = Path(audio_path)
    if not path.is_file():
        return False
    suffix = path.suffix.lower()
    try:
        if suffix in {".mp3", ".wav"}:
            return _embed_id3_lyrics(path, raw, overwrite=overwrite)

        if suffix in {".m4a", ".mp4", ".aac"}:
            from mutagen.mp4 import MP4

            audio = MP4(str(path))
            if audio.get("\xa9lyr") and not overwrite:
                return False
            audio["\xa9lyr"] = [raw]
            audio.save()
            return True

        if suffix == ".flac":
            from mutagen.flac import FLAC

            audio = FLAC(str(path))
            existing = any(key in audio for key in ("LYRICS", "UNSYNCEDLYRICS", "lyrics"))
            if existing and not overwrite:
                return False
            for key in ("UNSYNCEDLYRICS", "lyrics"):
                if key in audio:
                    del audio[key]
            audio["LYRICS"] = [raw]
            audio.save()
            return True

        if suffix in {".ogg", ".opus"}:
            from mutagen import File as MutagenFile

            audio = MutagenFile(str(path))
            if audio is None:
                return False
            tags = audio.tags
            if tags is None:
                return False
            existing = any(key in tags for key in ("LYRICS", "UNSYNCEDLYRICS", "lyrics"))
            if existing and not overwrite:
                return False
            for key in ("UNSYNCEDLYRICS", "lyrics"):
                if key in tags:
                    del tags[key]
            tags["LYRICS"] = [raw]
            audio.save()
            return True

        return _embed_id3_lyrics(path, raw, overwrite=overwrite)
    except Exception:
        return False


def maybe_embed_lyrics(audio_path: Path | str | None, payload: LyricsPayload | None) -> bool:
    """Embed fetched lyrics when the audio file has none yet."""
    if audio_path is None or payload is None or not payload.lines:
        return False
    if read_local_lyrics(audio_path) is not None:
        return False
    return embed_lyrics_in_audio(audio_path, payload_to_text(payload), overwrite=False)


def write_local_lyrics(audio_path: Path | str | None, payload: LyricsPayload) -> bool:
    """Overwrite the local store (sidecar if present, plus embedded tags)."""
    if audio_path is None or not payload.lines:
        return False
    path = Path(audio_path)
    text = payload_to_text(payload)
    if not text:
        return False
    wrote = False
    sidecar = _find_sidecar(path)
    if sidecar is not None:
        candidate, _source = sidecar
        try:
            candidate.write_text(text + "\n", encoding="utf-8")
            wrote = True
        except OSError:
            pass
    if embed_lyrics_in_audio(path, text, overwrite=True):
        wrote = True
    return wrote


def save_manual_lyrics(
    cache_dir: Path,
    *,
    artist: str,
    title: str,
    album: str = "",
    duration: float | None = None,
    text: str,
    aligned_cache: Path | None = None,
    audio_path: Path | str | None = None,
) -> LyricsPayload:
    """Persist pasted lyrics and drop any previous Whisper alignment."""
    if len(text) > MANUAL_LYRICS_MAX_CHARS:
        raise ValueError("La lletra és massa llarga")
    payload = payload_from_text(text, "manual")
    if payload is None:
        raise ValueError("La lletra és buida")
    key = cache_key(artist, title, duration)
    save_cached(
        cache_dir,
        key,
        payload,
        artist=artist,
        title=title,
        duration=duration,
        album=album,
    )
    write_local_lyrics(audio_path, payload)
    if aligned_cache is not None:
        clear_aligned_keys(aligned_cache, [key])
    return payload


class LyricsUnavailable(RuntimeError):
    """A lyrics provider could not be reached (timeout, throttling, server error).

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
    params: dict[str, Any] | None = None,
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


def _json_body(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return None


async def _lrclib_get_payload(
    client: httpx.AsyncClient,
    params: dict[str, Any],
    *,
    attempts: int,
) -> LyricsPayload | None:
    response = await _get_with_retry(client, LRCLIB_GET, params, attempts=attempts)
    if response.status_code != 200:
        return None
    data = _json_body(response)
    if isinstance(data, dict):
        return _from_lrclib_record(data, "lrclib")
    return None


async def _lrclib_search_payload(
    client: httpx.AsyncClient,
    artist: str,
    title: str,
    duration: float | None,
    *,
    attempts: int,
) -> LyricsPayload | None:
    cleaned_artist = clean_query_text(artist) or artist
    cleaned_title = clean_query_text(title) or title
    queries: list[dict[str, Any]] = []
    named = _compact_params({"artist_name": cleaned_artist, "track_name": cleaned_title})
    if named:
        queries.append(named)
    original_named = _compact_params({"artist_name": artist, "track_name": title})
    if original_named and original_named not in queries:
        queries.append(original_named)
    queries.append({"q": f"{artist} {title}".strip()})

    for params in queries:
        response = await _get_with_retry(client, LRCLIB_SEARCH, params, attempts=attempts)
        if response.status_code != 200:
            continue
        data = _json_body(response)
        records = data if isinstance(data, list) else []
        record = _best_lrclib_record(records, duration)
        if record is None:
            continue
        payload = _from_lrclib_record(record, "lrclib-search")
        if payload:
            return payload
    return None


async def _fetch_from_lrclib(
    client: httpx.AsyncClient,
    artist: str,
    title: str,
    album: str,
    duration: float | None,
    *,
    attempts: int,
) -> LyricsPayload | None:
    for params in _lrclib_get_queries(artist, title, album, duration):
        payload = await _lrclib_get_payload(client, params, attempts=attempts)
        if payload:
            return payload
    return await _lrclib_search_payload(
        client, artist, title, duration, attempts=attempts
    )


def _ovh_lyrics_text(data: Any) -> str:
    if not isinstance(data, dict):
        return ""
    raw = str(data.get("lyrics") or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [line for line in raw.splitlines() if not _OVH_HEADER_RE.match(line.strip())]
    return "\n".join(lines).strip()


async def _fetch_from_lyrics_ovh(
    client: httpx.AsyncClient,
    artist: str,
    title: str,
    *,
    attempts: int,
) -> LyricsPayload | None:
    pairs: list[tuple[str, str]] = [(artist.strip(), title.strip())]
    cleaned = (clean_query_text(artist), clean_query_text(title))
    if cleaned[0] and cleaned[1] and cleaned not in pairs:
        pairs.append(cleaned)
    last_error: Exception | None = None
    saw_response = False
    for artist_q, title_q in pairs:
        if not artist_q or not title_q:
            continue
        url = f"{LYRICS_OVH_BASE}/v1/{quote(artist_q, safe='')}/{quote(title_q, safe='')}"
        try:
            response = await _get_with_retry(client, url, attempts=attempts)
        except LyricsUnavailable as exc:
            last_error = exc
            continue
        saw_response = True
        if response.status_code != 200:
            continue
        payload = payload_from_text(_ovh_lyrics_text(_json_body(response)), "lyrics-ovh")
        if payload:
            return payload
    if last_error is not None and not saw_response:
        raise last_error
    return None


async def fetch_lyrics(
    artist: str,
    title: str,
    album: str = "",
    duration: float | None = None,
    cache_dir: Path | None = None,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    attempts: int = 3,
    audio_path: Path | str | None = None,
) -> LyricsPayload:
    """Resolve lyrics: local file → cache → LRCLIB → lyrics.ovh.

    Remote hits are embedded into the audio file when it has no lyrics yet.
    """
    key = cache_key(artist, title, duration)
    cached: LyricsPayload | None = None
    if cache_dir:
        try:
            cached = load_cached(cache_dir, key)
        except (OSError, ValueError):
            cached = None

    local = read_local_lyrics(audio_path)
    if local is not None:
        if cache_dir:
            save_cached(
                cache_dir,
                key,
                local,
                artist=artist,
                title=title,
                duration=duration,
                album=album,
            )
        return local

    if cached is not None and cached.lines:
        maybe_embed_lyrics(audio_path, cached)
        return cached
    if cached is not None:
        return cached

    headers = {"User-Agent": "karaoke-party/0.1 (local karaoke app)"}
    payload: LyricsPayload | None = None
    lrclib_error: LyricsUnavailable | None = None
    ovh_error: LyricsUnavailable | None = None
    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        try:
            payload = await _fetch_from_lrclib(
                client, artist, title, album, duration, attempts=attempts
            )
        except LyricsUnavailable as exc:
            lrclib_error = exc
        if payload is None:
            try:
                payload = await _fetch_from_lyrics_ovh(
                    client, artist, title, attempts=min(attempts, 2)
                )
            except LyricsUnavailable as exc:
                ovh_error = exc

    if payload is None and lrclib_error is not None and ovh_error is not None:
        raise lrclib_error
    if payload is None and lrclib_error is not None:
        raise lrclib_error
    if payload is None:
        payload = LyricsPayload(synced=False, source="none", lines=[], plain="")

    if cache_dir:
        try:
            existing = load_cached(cache_dir, key)
        except (OSError, ValueError):
            existing = None
        if existing is not None and existing.lines and existing.source == "manual":
            maybe_embed_lyrics(audio_path, existing)
            return existing
        if existing is not None and existing.lines and not payload.lines:
            maybe_embed_lyrics(audio_path, existing)
            return existing
        save_cached(
            cache_dir,
            key,
            payload,
            artist=artist,
            title=title,
            duration=duration,
            album=album,
        )
    maybe_embed_lyrics(audio_path, payload)
    return payload


async def track_has_lyrics(
    artist: str,
    title: str,
    album: str = "",
    duration: float | None = None,
    *,
    lyrics_cache: Path,
    aligned_cache: Path | None = None,
    audio_path: Path | str | None = None,
) -> bool:
    """Return True when synced/plain lyrics exist (uses cache, then lookup)."""
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
        audio_path=audio_path,
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
    audio_path: Path | str | None = None,
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
    if cached.lines:
        return True, cached.source
    sidecar = read_sidecar_lyrics(audio_path)
    if sidecar is not None and sidecar.lines:
        return True, sidecar.source
    return False, cached.source


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
