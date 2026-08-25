"""Meta MMS forced alignment: known lyric characters → Catalan syllables.

Whisper only locates each sung phrase. MMS maps the lyric letters onto the
vocal inside that window; we then group those character spans with
``syllabify_token`` so karaoke fill is syllable-accurate.

The acoustic model is ``torchaudio.pipelines.MMS_FA`` (CC-BY-NC). CTC
alignment is implemented here so we do not depend on torchaudio's deprecated
``forced_align`` API.
"""

from __future__ import annotations

import logging
import os
import threading
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .lyrics import LyricLine, LyricWord
from .syllables import syllabify_token

log = logging.getLogger("karaoke_party.mms")

# MMS FA latin alphabet (plus apostrophe). Accents fold away; ç → c via NFD.
MMS_ALPHABET = frozenset("abcdefghijklmnopqrstuvwxyz'")
PAD_BEFORE = 0.25
PAD_AFTER = 0.35
MIN_SYL = 0.04
_NEG = -1e30

_lock = threading.Lock()
_pack: _MmsPack | None = None
_load_error: str | None = None


@dataclass
class CharSpan:
    char: str
    start: float
    end: float
    score: float = 1.0


@dataclass
class _MmsPack:
    model: Any
    labels: dict[str, int]
    sample_rate: int
    device: str
    blank_id: int


def mms_enabled() -> bool:
    env = (os.environ.get("KARAOKE_MMS") or "1").strip().lower()
    return env not in {"0", "off", "false", "no"}


def _mms_device() -> str:
    explicit = (os.environ.get("KARAOKE_MMS_DEVICE") or "").strip().lower()
    flag = (os.environ.get("KARAOKE_MMS") or "").strip().lower()
    requested = explicit or (flag if flag in {"cpu", "cuda"} else "")
    if requested == "cpu":
        return "cpu"
    try:
        import torch

        cuda_ok = bool(torch.cuda.is_available())
    except Exception:  # noqa: BLE001
        cuda_ok = False
    if requested == "cuda":
        return "cuda" if cuda_ok else "cpu"
    return "cuda" if cuda_ok else "cpu"


def normalize_for_mms(text: str) -> str:
    """Fold Catalan orthography onto the MMS latin alphabet."""
    if not text:
        return ""
    folded = unicodedata.normalize("NFD", text.replace("’", "'").replace("`", "'").replace("·", ""))
    chars: list[str] = []
    for char in folded.lower():
        if unicodedata.category(char) == "Mn":
            continue
        if char in MMS_ALPHABET:
            chars.append(char)
    return "".join(chars)


def ctc_forced_align(
    log_probs,
    token_ids: list[int],
    blank: int = 0,
) -> list[tuple[int, int, float]]:
    """Viterbi CTC alignment.

    ``log_probs`` is ``(time, vocab)`` in log-probability domain.
    Returns one ``(start_frame, end_frame_exclusive, mean_prob)`` per token.
    """
    import numpy as np

    if log_probs.ndim != 2 or not token_ids:
        return []
    time_count, vocab = log_probs.shape
    token_count = len(token_ids)
    if time_count < token_count or any(tid < 0 or tid >= vocab for tid in token_ids):
        return []

    # Even states are blank; odd states are transcript tokens.
    state_count = 2 * token_count + 1
    emit = np.empty(state_count, dtype=np.int32)
    for state in range(state_count):
        emit[state] = blank if state % 2 == 0 else token_ids[state // 2]

    scores = np.asarray(log_probs, dtype=np.float64)
    trellis = np.full((time_count, state_count), _NEG, dtype=np.float64)
    back = np.full((time_count, state_count), -1, dtype=np.int16)
    trellis[0, 0] = scores[0, emit[0]]
    if state_count > 1:
        trellis[0, 1] = scores[0, emit[1]]

    for time in range(1, time_count):
        row = scores[time]
        prev = trellis[time - 1]
        for state in range(state_count):
            best = prev[state]
            src = state
            if state >= 1 and prev[state - 1] > best:
                best = prev[state - 1]
                src = state - 1
            if (
                state >= 2
                and emit[state] != blank
                and emit[state] != emit[state - 2]
                and prev[state - 2] > best
            ):
                best = prev[state - 2]
                src = state - 2
            trellis[time, state] = best + row[emit[state]]
            back[time, state] = src

    end_state = state_count - 1
    if state_count >= 2 and trellis[time_count - 1, state_count - 2] > trellis[time_count - 1, end_state]:
        end_state = state_count - 2
    if trellis[time_count - 1, end_state] < _NEG / 2:
        return []

    states = np.empty(time_count, dtype=np.int32)
    state = int(end_state)
    for time in range(time_count - 1, -1, -1):
        states[time] = state
        if time > 0:
            state = int(back[time, state])
            if state < 0:
                return []

    spans: list[tuple[int, int, float] | None] = []
    for index, token_id in enumerate(token_ids):
        frames = np.flatnonzero(states == 2 * index + 1)
        if frames.size == 0:
            spans.append(None)
            continue
        start = int(frames[0])
        end = int(frames[-1]) + 1
        prob = float(np.exp(scores[start:end, token_id]).mean())
        spans.append((start, end, prob))

    last_end = 0
    filled: list[tuple[int, int, float]] = []
    for index, span in enumerate(spans):
        if span is not None:
            last_end = span[1]
            filled.append(span)
            continue
        nxt = next((item[0] for item in spans[index + 1 :] if item is not None), time_count)
        start = min(last_end, time_count - 1)
        end = max(start + 1, min(nxt, start + 1))
        filled.append((start, end, 0.0))
        last_end = end
    return filled


def syllables_from_char_spans(word: LyricWord, chars: list[CharSpan]) -> list[LyricWord]:
    """Group MMS character times into Catalan syllables of ``word.text``."""
    parts = syllabify_token(word.text)
    if not parts:
        return []
    last = len(parts) - 1
    if len(parts) == 1:
        if chars:
            start = chars[0].start
            end = max(chars[-1].end, start + MIN_SYL)
        else:
            start, end = float(word.time), max(float(word.end), float(word.time) + MIN_SYL)
        return [LyricWord(time=start, end=end, text=parts[0], glue=False)]

    mms_parts = [normalize_for_mms(part) for part in parts]
    encoded = "".join(mms_parts)
    heard = "".join(span.char for span in chars)
    if not chars or encoded != heard:
        window = (
            LyricWord(time=chars[0].start, end=max(chars[-1].end, chars[0].start + MIN_SYL), text=word.text)
            if chars
            else word
        )
        return _proportional_word(window, parts)

    tokens: list[LyricWord] = []
    cursor = 0
    for index, (part, mms) in enumerate(zip(parts, mms_parts)):
        if not mms:
            tokens.append(LyricWord(time=-1.0, end=-1.0, text=part, glue=index < last))
            continue
        group = chars[cursor : cursor + len(mms)]
        cursor += len(mms)
        start = group[0].start
        end = max(group[-1].end, start + MIN_SYL)
        tokens.append(LyricWord(time=start, end=end, text=part, glue=index < last))

    previous_end = next((token.time for token in tokens if token.time >= 0), float(word.time))
    for token in tokens:
        if token.time >= 0:
            previous_end = token.end
            continue
        token.time = previous_end
        token.end = token.time + MIN_SYL
        previous_end = token.end
    return tokens


def _proportional_word(word: LyricWord, parts: list[str]) -> list[LyricWord]:
    from .syllables import _proportional_rel_times, _syllable_weight, _tokens_from_splits

    span = max(MIN_SYL, float(word.end) - float(word.time))
    rel = _proportional_rel_times(span, [_syllable_weight(part) for part in parts])
    return _tokens_from_splits(word, parts, rel)


def _enforce_monotonic(tokens: list[LyricWord]) -> list[LyricWord]:
    if not tokens:
        return tokens
    last_start = tokens[0].time
    for token in tokens:
        if token.time < last_start:
            token.time = last_start
        if token.end < token.time + MIN_SYL:
            token.end = token.time + MIN_SYL
        last_start = token.time
    for current, following in zip(tokens, tokens[1:]):
        if current.glue and current.end < following.time:
            current.end = following.time
        if current.end > following.time:
            current.end = max(current.time + MIN_SYL, following.time)
    return tokens


def _torch_home() -> None:
    if os.environ.get("TORCH_HOME"):
        return
    try:
        from .config import app_cache_root

        os.environ["TORCH_HOME"] = str(app_cache_root() / "torch")
    except Exception:  # noqa: BLE001
        pass


def _load_mms_unlocked() -> _MmsPack:
    _torch_home()
    import torch
    from torchaudio.pipelines import MMS_FA as bundle

    device = _mms_device()
    log.info("Loading Meta MMS forced aligner (%s)", device)
    try:
        model = bundle.get_model(with_star=False)
        labels = bundle.get_dict(star=None)
    except TypeError:
        model = bundle.get_model()
        labels = {key: value for key, value in bundle.get_dict().items() if key != "*"}
    try:
        model = model.to(device)
    except Exception:
        device = "cpu"
        model = model.to(device)
    model.eval()
    blank = int(labels.get("-", 0))
    return _MmsPack(
        model=model,
        labels=labels,
        sample_rate=int(bundle.sample_rate),
        device=device,
        blank_id=blank,
    )


def _get_pack() -> _MmsPack | None:
    global _pack, _load_error
    if not mms_enabled():
        return None
    with _lock:
        if _pack is not None:
            return _pack
        if _load_error:
            return None
        try:
            _pack = _load_mms_unlocked()
            return _pack
        except Exception as exc:  # noqa: BLE001 — optional path; energy still works
            _load_error = str(exc)
            log.warning("MMS forced aligner unavailable: %s", exc)
            return None


def preload_mms_model() -> None:
    """Download/load MMS (call after Whisper so the first song is ready)."""
    _get_pack()


def _load_mono(path: Path, sample_rate: int):
    import numpy as np

    try:
        import torchaudio

        waveform, native = torchaudio.load(str(path))
        if waveform.size(0) > 1:
            waveform = waveform.mean(0, keepdim=True)
        if native != sample_rate:
            waveform = torchaudio.functional.resample(waveform, native, sample_rate)
        return waveform.squeeze(0).numpy().astype(np.float32, copy=False)
    except Exception:  # noqa: BLE001 — mp3 via librosa/ffmpeg
        import librosa

        samples, _ = librosa.load(str(path), sr=sample_rate, mono=True)
        return samples.astype(np.float32, copy=False)


def _emit(pack: _MmsPack, clip):
    import numpy as np
    import torch

    wav = torch.from_numpy(np.ascontiguousarray(clip)).float().unsqueeze(0)
    try:
        wav = wav.to(pack.device)
        with torch.inference_mode():
            emission, _ = pack.model(wav)
    except Exception as exc:  # noqa: BLE001 — CUDA OOM → CPU
        message = str(exc).lower()
        if pack.device != "cpu" and ("out of memory" in message or "cuda" in message):
            log.warning("MMS falling back to CPU: %s", exc)
            pack.model = pack.model.to("cpu")
            pack.device = "cpu"
            with torch.inference_mode():
                emission, _ = pack.model(wav.cpu())
        else:
            raise
    if emission.ndim == 3:
        emission = emission[0]
    return emission.detach().float().cpu().numpy()


def _align_line(pack: _MmsPack, samples, sample_rate: int, line: LyricLine) -> LyricLine | None:
    words = line.words
    if not words:
        return line
    duration = len(samples) / float(sample_rate)
    start = max(0.0, float(words[0].time) - PAD_BEFORE)
    end = min(duration, float(words[-1].end) + PAD_AFTER)
    if end - start < 0.08:
        return None
    i0 = int(start * sample_rate)
    i1 = max(i0 + 1, int(end * sample_rate))
    clip = samples[i0:i1]

    mms_words = [normalize_for_mms(word.text) for word in words]
    token_ids: list[int] = []
    slices: list[tuple[int, int]] = []
    encoded_words: list[str] = []
    for mms in mms_words:
        begin = len(token_ids)
        kept: list[str] = []
        for char in mms:
            token_id = pack.labels.get(char)
            if token_id is None or char in "-*":
                continue
            token_ids.append(int(token_id))
            kept.append(char)
        encoded_words.append("".join(kept))
        slices.append((begin, len(token_ids)))
    if not token_ids:
        return None

    emission = _emit(pack, clip)
    if emission.ndim != 2 or emission.shape[0] < len(token_ids) + 2:
        return None
    spans = ctc_forced_align(emission, token_ids, blank=pack.blank_id)
    if len(spans) != len(token_ids):
        return None

    frame_step = (len(clip) / float(sample_rate)) / float(emission.shape[0])

    def frame_time(frame: int) -> float:
        return start + frame * frame_step

    tokens: list[LyricWord] = []
    for word, encoded, (begin, stop) in zip(words, encoded_words, slices):
        if begin == stop:
            tokens.extend(syllables_from_char_spans(word, []))
            continue
        chars = [
            CharSpan(
                char=char,
                start=frame_time(span[0]),
                end=frame_time(span[1]),
                score=span[2],
            )
            for char, span in zip(encoded, spans[begin:stop])
        ]
        tokens.extend(syllables_from_char_spans(word, chars))
    if not tokens:
        return None
    tokens = _enforce_monotonic(tokens)
    return LyricLine(time=tokens[0].time, text=line.text, words=tokens)


def align_syllables_mms(audio_path: Path, lines: list[LyricLine]) -> list[LyricLine] | None:
    """Force-align known lyrics to ``audio_path`` and return syllable tokens.

    ``None`` means MMS is disabled or the model could not load; the caller
    should fall back to energy / letter splits. Lines that fail individually
    keep a letter-weighted syllable split of the Whisper window.
    """
    if not lines or not mms_enabled():
        return None
    pack = _get_pack()
    if pack is None:
        return None
    path = Path(audio_path)
    if not path.is_file():
        return None
    try:
        samples = _load_mono(path, pack.sample_rate)
    except Exception as exc:  # noqa: BLE001
        log.warning("MMS could not read %s: %s", path, exc)
        return None

    aligned: list[LyricLine | None] = []
    try:
        for line in lines:
            try:
                aligned.append(_align_line(pack, samples, pack.sample_rate, line))
            except Exception as exc:  # noqa: BLE001 — keep other lines
                log.debug("MMS skipped a line: %s", exc)
                aligned.append(None)
    except Exception as exc:  # noqa: BLE001
        log.warning("MMS alignment failed: %s", exc)
        return None
    if all(row is None for row in aligned):
        return None
    from .syllables import expand_syllable_tokens

    out: list[LyricLine] = []
    for row, line in zip(aligned, lines):
        if row is None:
            out.append(expand_syllable_tokens([line])[0])
        else:
            out.append(row)
    tokens = [word for line in out for word in line.words]
    _enforce_monotonic(tokens)
    for line in out:
        if line.words:
            line.time = line.words[0].time
    return out
