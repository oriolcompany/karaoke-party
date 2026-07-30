from __future__ import annotations

import re
import threading
from collections.abc import Callable
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from .lyrics import LyricLine, LyricWord, estimate_words

_model = None
_model_lock = threading.Lock()
_model_name: str | None = None

DEFAULT_MODEL_SIZE = "small"


@dataclass
class AsrWord:
    text: str
    start: float
    end: float


@dataclass
class _TokenRef:
    line_index: int
    token_index: int
    text: str
    norm: str


def alignment_available() -> bool:
    try:
        import faster_whisper  # noqa: F401

        return True
    except ImportError:
        return False


def _normalize(token: str) -> str:
    return re.sub(r"[^\wÀ-ÿ]+", "", token.lower(), flags=re.UNICODE)


def _similar(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


def _split_tokens(text: str) -> list[str]:
    return [part for part in re.split(r"(\s+)", text) if part and not part.isspace()]


def _get_model(model_size: str = DEFAULT_MODEL_SIZE):
    global _model, _model_name
    with _model_lock:
        if _model is not None and _model_name == model_size:
            return _model
        from faster_whisper import WhisperModel

        _model = WhisperModel(model_size, device="cpu", compute_type="int8")
        _model_name = model_size
        return _model


def transcribe_words(
    audio_path: Path,
    language: str = "ca",
    model_size: str = DEFAULT_MODEL_SIZE,
    initial_prompt: str | None = None,
    on_progress: Callable[[float], None] | None = None,
) -> list[AsrWord]:
    model = _get_model(model_size)
    # VAD often deletes sung vocals as "non-speech"; keep it off for karaoke.
    # beam_size=1 keeps CPU sync usable for background queue jobs.
    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        word_timestamps=True,
        vad_filter=False,
        beam_size=1,
        best_of=1,
        condition_on_previous_text=False,
        initial_prompt=initial_prompt,
    )
    duration = float(getattr(info, "duration", 0) or 0)
    words: list[AsrWord] = []
    for segment in segments:
        if on_progress is not None and duration > 0:
            try:
                on_progress(min(0.99, float(segment.end) / duration))
            except Exception:  # noqa: BLE001 — progress must not abort ASR
                pass
        for word in segment.words or []:
            text = (word.word or "").strip()
            if not text:
                continue
            words.append(AsrWord(text=text, start=float(word.start), end=float(word.end)))
    if on_progress is not None:
        try:
            on_progress(1.0)
        except Exception:  # noqa: BLE001
            pass
    return words


def _interpolate_missing(words: list[LyricWord], line_start: float, line_end: float) -> list[LyricWord]:
    if not words:
        return []
    filled = list(words)
    known_indexes = [i for i, word in enumerate(filled) if word.time >= 0]
    if not known_indexes:
        return estimate_words(line_start, line_end, " ".join(word.text for word in filled))

    for i, word in enumerate(filled):
        if word.time >= 0:
            continue
        prev_i = max((k for k in known_indexes if k < i), default=None)
        next_i = min((k for k in known_indexes if k > i), default=None)
        if prev_i is None and next_i is not None:
            span = max(0.12, (filled[next_i].time - line_start) / max(1, next_i))
            start = line_start + i * span
            end = start + span
        elif next_i is None and prev_i is not None:
            span = max(0.12, (line_end - filled[prev_i].end) / max(1, len(filled) - prev_i))
            start = filled[prev_i].end + (i - prev_i - 1) * span
            end = start + span
        elif prev_i is not None and next_i is not None:
            gap = filled[next_i].time - filled[prev_i].end
            steps = next_i - prev_i
            span = max(0.08, gap / steps)
            start = filled[prev_i].end + (i - prev_i - 1) * span
            end = start + span
        else:
            start = line_start
            end = line_start + 0.3
        filled[i] = LyricWord(time=start, end=max(end, start + 0.08), text=word.text)
    return filled


def align_line_words(
    line_text: str,
    line_start: float,
    line_end: float,
    asr_words: list[AsrWord],
) -> list[LyricWord]:
    """Match one line inside a time window (used by tests / fallback)."""
    tokens = _split_tokens(line_text)
    if not tokens:
        return []

    window = [
        word
        for word in asr_words
        if word.end >= line_start - 0.8 and word.start <= line_end + 0.6
    ]
    if len(window) < max(1, len(tokens) // 3):
        window = [
            word
            for word in asr_words
            if word.end >= line_start - 2.5 and word.start <= line_end + 2.0
        ]

    aligned: list[LyricWord] = []
    cursor = 0
    for token in tokens:
        norm = _normalize(token)
        match_idx = None
        match_score = 0.0
        limit = min(len(window), cursor + 10)
        for idx in range(cursor, limit):
            score = _similar(norm, _normalize(window[idx].text))
            if score > match_score:
                match_score = score
                match_idx = idx
            if score >= 0.92:
                break
        if match_idx is not None and match_score >= 0.55:
            hit = window[match_idx]
            aligned.append(LyricWord(time=hit.start, end=max(hit.end, hit.start + 0.05), text=token))
            cursor = match_idx + 1
        else:
            aligned.append(LyricWord(time=-1.0, end=-1.0, text=token))

    return _interpolate_missing(aligned, line_start, line_end)


def _best_asr_index(norm: str, asr_norms: list[str], start: int, stop: int) -> tuple[int | None, float]:
    best_i = None
    best_score = 0.0
    for idx in range(start, min(stop, len(asr_norms))):
        score = _similar(norm, asr_norms[idx])
        if score > best_score:
            best_score = score
            best_i = idx
        if score >= 0.95:
            break
    return best_i, best_score


def align_tokens_globally(
    lines: list[LyricLine],
    asr_words: list[AsrWord],
) -> list[list[LyricWord]]:
    """Match lyric tokens to ASR words across the whole song (handles intro offset)."""
    tokens: list[_TokenRef] = []
    for line_index, line in enumerate(lines):
        for token_index, text in enumerate(_split_tokens(line.text)):
            tokens.append(
                _TokenRef(
                    line_index=line_index,
                    token_index=token_index,
                    text=text,
                    norm=_normalize(text),
                )
            )

    line_tokens = [_split_tokens(line.text) for line in lines]
    placeholders: list[list[LyricWord]] = [
        [LyricWord(time=-1.0, end=-1.0, text=token) for token in toks] for toks in line_tokens
    ]
    if not tokens or not asr_words:
        return placeholders

    lyric_norms = [token.norm for token in tokens]
    asr_norms = [_normalize(word.text) for word in asr_words]
    matcher = SequenceMatcher(a=lyric_norms, b=asr_norms, autojunk=False)

    asr_cursor = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for offset in range(i2 - i1):
                token = tokens[i1 + offset]
                hit = asr_words[j1 + offset]
                placeholders[token.line_index][token.token_index] = LyricWord(
                    time=hit.start,
                    end=max(hit.end, hit.start + 0.05),
                    text=token.text,
                )
            asr_cursor = j2
            continue

        if tag in {"replace", "delete"}:
            # Fuzzy-fill lyric tokens that SequenceMatcher did not exact-match.
            local_asr_start = max(asr_cursor, j1 - 2)
            local_asr_stop = min(len(asr_words), max(j2 + 8, local_asr_start + (i2 - i1) * 3 + 4))
            cursor = local_asr_start
            for token in tokens[i1:i2]:
                if not token.norm:
                    continue
                match_idx, score = _best_asr_index(token.norm, asr_norms, cursor, local_asr_stop)
                if match_idx is not None and score >= 0.62:
                    hit = asr_words[match_idx]
                    placeholders[token.line_index][token.token_index] = LyricWord(
                        time=hit.start,
                        end=max(hit.end, hit.start + 0.05),
                        text=token.text,
                    )
                    cursor = match_idx + 1
            asr_cursor = max(asr_cursor, j2, cursor)

        if tag == "insert":
            asr_cursor = max(asr_cursor, j2)

    return placeholders


def align_lyrics(
    audio_path: Path,
    lines: list[LyricLine],
    *,
    language: str = "ca",
    model_size: str = DEFAULT_MODEL_SIZE,
    on_progress: Callable[[float], None] | None = None,
) -> list[LyricLine]:
    """Align known lyric lines to the audio with faster-whisper word timestamps."""
    if not lines:
        return []
    if not audio_path.is_file():
        raise FileNotFoundError(str(audio_path))

    prompt = " ".join(line.text for line in lines[:16]).strip()
    asr_words = transcribe_words(
        audio_path,
        language=language,
        model_size=model_size,
        initial_prompt=(prompt[:900] or None),
        on_progress=on_progress,
    )
    if not asr_words:
        return [
            LyricLine(
                time=line.time,
                text=line.text,
                words=estimate_words(
                    line.time,
                    lines[i + 1].time if i + 1 < len(lines) else None,
                    line.text,
                ),
            )
            for i, line in enumerate(lines)
        ]

    per_line = align_tokens_globally(lines, asr_words)
    aligned_lines: list[LyricLine] = []
    for index, line in enumerate(lines):
        next_time = (
            lines[index + 1].time
            if index + 1 < len(lines)
            else (asr_words[-1].end + 0.4 if asr_words else line.time + 4.0)
        )
        words = per_line[index]
        known = [word for word in words if word.time >= 0]
        if known:
            line_start = known[0].time
            line_end = known[-1].end + 0.35
            # Prefer ASR-derived bounds; fall back softly to LRCLIB gap if sparse.
            if len(known) < max(1, len(words) // 3):
                line_start = min(line.time, line_start) if line.time > 0 else line_start
                line_end = max(next_time, line_end)
            words = _interpolate_missing(words, line_start, line_end)
            line_time = words[0].time if words else line.time
        else:
            line_time = line.time
            words = estimate_words(line.time, next_time, line.text)
        aligned_lines.append(LyricLine(time=line_time, text=line.text, words=words))
    return aligned_lines
