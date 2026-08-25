from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from .lyrics import LyricLine, LyricWord

_STRONG = set("aeo")
_VOWEL_BASE = set("aeiouy")
_HIATUS = set("íúïÍÚÏ")
_ACCENTED_STRONG = set("àèéòóÀÈÉÒÓ")
_ONSET_CC = {
    "bl",
    "br",
    "cl",
    "cr",
    "dr",
    "fl",
    "fr",
    "gl",
    "gr",
    "pl",
    "pr",
    "tr",
    "tl",
    "vl",
    "vr",
}
_CLITIC_LEFT = {"l", "d", "n", "m", "t", "s"}


def _base(char: str) -> str:
    folded = "".join(
        piece
        for piece in unicodedata.normalize("NFD", char.lower())
        if unicodedata.category(piece) != "Mn"
    )
    return folded[:1] if folded else ""


def _is_vowel(char: str) -> bool:
    return _base(char) in _VOWEL_BASE


def _is_strong(char: str) -> bool:
    return _base(char) in _STRONG


def _peel(text: str) -> tuple[str, str, str]:
    start = 0
    end = len(text)
    while start < end and not text[start].isalnum() and text[start] not in "'’":
        start += 1
    while end > start and not text[end - 1].isalnum() and text[end - 1] not in "'’":
        end -= 1
    return text[:start], text[start:end], text[end:]


def _consonant_units(chunk: str, next_vowel: str) -> list[str]:
    units: list[str] = []
    index = 0
    lower = chunk.lower()
    follow = _base(next_vowel) if next_vowel else ""
    while index < len(chunk):
        pair = lower[index : index + 2]
        if pair in {"ll", "ny", "tx", "tj", "tz", "ix", "ch"}:
            units.append(chunk[index : index + 2])
            index += 2
            continue
        if pair in {"qu", "gu"} and follow in {"e", "i"}:
            units.append(chunk[index : index + 2])
            index += 2
            continue
        units.append(chunk[index])
        index += 1
    return units


def _onset_len(units: list[str]) -> int:
    if not units:
        return 0
    if len(units) == 1:
        return 1
    last_two = "".join(_base(part) for part in units[-2:]).replace("·", "")
    if last_two in _ONSET_CC:
        return 2
    return 1


def _vowel_groups(vowels: list[str]) -> list[tuple[int, int]]:
    groups: list[tuple[int, int]] = []
    index = 0
    count = len(vowels)
    while index < count:
        if (
            index + 2 < count
            and vowels[index] not in _HIATUS
            and vowels[index + 1] not in _HIATUS
            and vowels[index + 2] not in _HIATUS
            and not _is_strong(vowels[index])
            and _is_strong(vowels[index + 1])
            and not _is_strong(vowels[index + 2])
        ):
            groups.append((index, index + 3))
            index += 3
            continue
        if (
            index + 1 < count
            and vowels[index] not in _HIATUS
            and vowels[index + 1] not in _HIATUS
            and vowels[index + 1] not in _ACCENTED_STRONG
            and (
                _is_strong(vowels[index]) != _is_strong(vowels[index + 1])
                or (not _is_strong(vowels[index]) and not _is_strong(vowels[index + 1]))
            )
        ):
            groups.append((index, index + 2))
            index += 2
            continue
        groups.append((index, index + 1))
        index += 1
    return groups


def _nuclei_spans(core: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    index = 0
    length = len(core)
    while index < length:
        if not _is_vowel(core[index]):
            index += 1
            continue
        end = index
        while end < length and _is_vowel(core[end]):
            end += 1
        run = list(core[index:end])
        for start, stop in _vowel_groups(run):
            spans.append((index + start, index + stop))
        index = end
    return spans


def _syllabify_letters(core: str) -> list[str]:
    if not core:
        return []
    nuclei = _nuclei_spans(core)
    if not nuclei:
        return [core]

    starts = [0]
    for prev, current in zip(nuclei, nuclei[1:]):
        between = core[prev[1] : current[0]]
        next_vowel = core[current[0]]
        units = _consonant_units(between, next_vowel)
        take = _onset_len(units)
        onset_chars = sum(len(unit) for unit in units[len(units) - take :]) if take else 0
        starts.append(current[0] - onset_chars)

    starts.append(len(core))
    parts = [core[starts[i] : starts[i + 1]] for i in range(len(starts) - 1)]
    return [part for part in parts if part]


def _syllabify_core(core: str) -> list[str]:
    if not core:
        return []
    if "-" in core or "·" in core:
        joiner = "-" if "-" in core else "·"
        pieces: list[str] = []
        for index, chunk in enumerate(re.split(r"[-·]", core)):
            syls = _syllabify_core(chunk) or [chunk]
            if index and pieces:
                pieces[-1] = pieces[-1] + joiner
            pieces.extend(syls)
        return [part for part in pieces if part]

    match = re.split(r"['’]", core, maxsplit=1)
    if len(match) == 2 and match[0] != "" and match[1] != "":
        left, right = match
        mark = "'" if "'" in core else "’"
        if left.lower() in _CLITIC_LEFT and _is_vowel(right[0]):
            rest = _syllabify_letters(right) or [right]
            rest[0] = left + mark + rest[0]
            return rest
        rest = _syllabify_letters(left) or [left]
        rest[-1] = rest[-1] + mark + right
        return rest
    return _syllabify_letters(core)


def syllabify_token(text: str) -> list[str]:
    """Split a lyric token into Catalan-ish syllables, keeping punctuation."""
    if not text.strip():
        return [text] if text else []
    prefix, core, suffix = _peel(text)
    if not core:
        return [text]
    parts = _syllabify_core(core) or [core]
    parts[0] = prefix + parts[0]
    parts[-1] = parts[-1] + suffix
    return parts


def _syllable_weight(text: str) -> int:
    letters = sum(1 for char in text if char.isalnum())
    vowels = sum(1 for char in text if _is_vowel(char))
    return max(1, letters + vowels)


def _proportional_rel_times(span: float, weights: list[int]) -> list[float]:
    total = sum(weights) or 1
    times = [0.0]
    acc = 0
    for weight in weights[:-1]:
        acc += weight
        times.append(span * acc / total)
    times.append(span)
    return times


def _tokens_from_splits(
    word: LyricWord,
    parts: list[str],
    rel_times: list[float],
) -> list[LyricWord]:
    span = max(0.05, float(word.end) - float(word.time))
    last = len(parts) - 1
    tokens: list[LyricWord] = []
    for index, part in enumerate(parts):
        start = float(word.time) + min(span, max(0.0, rel_times[index]))
        end = (
            float(word.end)
            if index == last
            else float(word.time) + min(span, max(0.0, rel_times[index + 1]))
        )
        tokens.append(
            LyricWord(
                time=start,
                end=max(end, start + 0.04),
                text=part,
                glue=index < last,
            )
        )
    return tokens


def expand_syllable_tokens(lines: list[LyricLine]) -> list[LyricLine]:
    """Subdivide each word's time span across its syllables for karaoke fill.

    Fallback when we cannot inspect the vocal audio: longer syllables get a
    larger slice of the Whisper word window.
    """
    expanded: list[LyricLine] = []
    for line in lines:
        tokens: list[LyricWord] = []
        for word in line.words:
            parts = syllabify_token(word.text)
            if len(parts) <= 1:
                tokens.append(
                    LyricWord(time=word.time, end=word.end, text=word.text, glue=False)
                )
                continue
            span = max(0.05, float(word.end) - float(word.time))
            rel = _proportional_rel_times(span, [_syllable_weight(part) for part in parts])
            tokens.extend(_tokens_from_splits(word, parts, rel))
        expanded.append(LyricLine(time=line.time, text=line.text, words=tokens))
    return expanded


def has_syllable_glue(lines: list[LyricLine]) -> bool:
    return any(word.glue for line in lines for word in line.words)


def _energy_split_times(samples, sr: int, weights: list[int]) -> list[float]:
    """Split a word-sized clip at energy valleys near each syllable's share."""
    import numpy as np
    import librosa

    n = len(weights)
    duration = len(samples) / float(sr)
    if n <= 1 or duration < 0.08:
        return _proportional_rel_times(duration, weights or [1])

    hop = 256
    frame = min(1024, max(256, len(samples) // 2))
    rms = librosa.feature.rms(y=samples, hop_length=hop, frame_length=frame)[0]
    if rms.size < n + 3:
        return _proportional_rel_times(duration, weights)

    energy = np.convolve(rms, np.ones(5) / 5.0, mode="same") + 1e-8
    cum = np.cumsum(energy)
    cum = cum / cum[-1]
    total_w = sum(weights) or n
    max_frame = len(energy) - 1
    radius = max(2, int(0.16 * sr / hop))
    frames = [0]
    acc = 0.0
    for weight in weights[:-1]:
        acc += weight
        target = acc / total_w
        index = int(np.searchsorted(cum, target))
        index = min(max(index, frames[-1] + 2), max_frame - 1)
        low = max(frames[-1] + 1, index - radius)
        high = min(max_frame, index + radius + 1)
        band = np.arange(low, high)
        dist = ((band - index) / max(radius, 1)) ** 2
        frames.append(low + int(np.argmin(energy[low:high] + 0.12 * dist)))
    frames.append(max_frame)

    times = [min(duration, max(0.0, frame * hop / sr)) for frame in frames]
    times[0] = 0.0
    times[-1] = duration
    for index in range(1, len(times)):
        if times[index] <= times[index - 1]:
            times[index] = min(duration, times[index - 1] + 0.04)
    times[-1] = duration
    return times


def _refine_from_audio(audio_path: Path, lines: list[LyricLine]) -> list[LyricLine]:
    import librosa

    samples, sr = librosa.load(str(audio_path), sr=22050, mono=True)
    expanded: list[LyricLine] = []
    for line in lines:
        tokens: list[LyricWord] = []
        for word in line.words:
            parts = syllabify_token(word.text)
            if len(parts) <= 1:
                tokens.append(
                    LyricWord(time=word.time, end=word.end, text=word.text, glue=False)
                )
                continue
            start = max(0.0, float(word.time))
            end = max(start + 0.05, float(word.end))
            i0 = min(len(samples), max(0, int(start * sr)))
            i1 = min(len(samples), max(i0 + 1, int(end * sr)))
            clip = samples[i0:i1]
            weights = [_syllable_weight(part) for part in parts]
            rel = _energy_split_times(clip, sr, weights)
            clip_dur = max(len(clip) / float(sr), 1e-6)
            span = end - start
            scaled = [span * (time / clip_dur) for time in rel]
            scaled[0] = 0.0
            scaled[-1] = span
            tokens.extend(_tokens_from_splits(word, parts, scaled))
        expanded.append(LyricLine(time=line.time, text=line.text, words=tokens))
    return expanded


def refine_syllable_timings(
    audio_path: Path | None,
    lines: list[LyricLine],
) -> list[LyricLine]:
    """Place syllable boundaries on the vocal stem.

    Whisper only locates each phrase. Meta MMS then force-aligns the known
    lyric characters inside that window and we group them into Catalan
    syllables. If MMS is missing, fall back to energy valleys, then to a
    letter-weighted split of the Whisper word window.
    """
    if not lines:
        return lines
    if has_syllable_glue(lines):
        return lines
    if audio_path is not None and Path(audio_path).is_file():
        from .mms_align import align_syllables_mms, mms_enabled

        if mms_enabled():
            try:
                aligned = align_syllables_mms(Path(audio_path), lines)
            except Exception:  # noqa: BLE001 — energy / letters still work
                aligned = None
            if aligned is not None:
                return aligned
        try:
            return _refine_from_audio(Path(audio_path), lines)
        except Exception:  # noqa: BLE001 — fall back to proportional slices
            pass
    return expand_syllable_tokens(lines)
