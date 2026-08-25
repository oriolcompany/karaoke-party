from __future__ import annotations

import os
import re
import threading
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path

from .lyrics import LyricLine, LyricWord, estimate_words, sung_word_duration, tighten_phrase_onsets

_model = None
# Status reads must never wait on a multi-GB HuggingFace download. Keep a
# short state lock separate from the load lock that serialises model builds.
_state_lock = threading.Lock()
_load_lock = threading.Lock()
_model_name: str | None = None
_model_device: str | None = None
_model_compute: str | None = None
_preload_started = False
_model_state: dict = {
    "ready": False,
    "loading": False,
    "error": "",
    "model": "",
    "device": "",
    "compute": "",
    "configured_model": "",
    "configured_device": "",
    "configured_compute": "",
}


def _env_int(name: str, default: int, minimum: int = 1) -> int:
    try:
        return max(minimum, int((os.environ.get(name) or "").strip() or default))
    except ValueError:
        return default


# CUDA 12 packages Whisper/ctranslate2 may need on Windows. Never add the
# pip ``nvidia-cudnn-cu12`` folder: mixing those DLLs with torch's CUDA 13
# cuDNN causes CUDNN_STATUS_SUBLIBRARY_VERSION_MISMATCH in Demucs.
_WHISPER_CUDA12_DLL_PACKAGES = frozenset({"cublas", "cuda_runtime", "cuda_nvrtc"})


def _add_cuda_dll_dirs() -> None:
    """On Windows, let ctranslate2 see the CUDA DLLs installed with pip.

    ctranslate2 is built against CUDA 12, while torch may ship CUDA 13 — on
    recent GPUs that is the only build with matching kernels — so the
    standalone cuBLAS 12 wheels are added to the search path. cuDNN stays
    with torch alone.
    """
    if os.name != "nt":
        return
    candidates: list[Path] = []
    try:
        import torch

        candidates.append(Path(torch.__file__).resolve().parent / "lib")
    except Exception:  # noqa: BLE001 — optional path hint only
        pass
    try:
        import nvidia

        for root in nvidia.__path__:
            for path in sorted(Path(root).glob("*/bin")):
                if path.parent.name.lower() in _WHISPER_CUDA12_DLL_PACKAGES:
                    candidates.append(path)
    except Exception:  # noqa: BLE001 — optional path hint only
        pass
    for path in candidates:
        if not path.is_dir():
            continue
        try:
            os.add_dll_directory(str(path))
        except OSError:
            continue


def _cublas12_loadable() -> bool:
    """faster-whisper/ctranslate2 CUDA builds need cuBLAS 12, not only a GPU."""
    if os.name != "nt":
        return True
    _add_cuda_dll_dirs()
    try:
        import ctypes

        ctypes.WinDLL("cublas64_12.dll")
        return True
    except OSError:
        return False


def _cuda_available() -> bool:
    """True only when ctranslate2 sees a GPU *and* its CUDA 12 runtime can load."""
    # Importing ctranslate2 already pulls in its CUDA DLLs, so the search path
    # has to be set up before the import, not just before the cuBLAS probe.
    _add_cuda_dll_dirs()
    try:
        import ctranslate2

        if int(ctranslate2.get_cuda_device_count()) <= 0:
            return False
    except Exception:  # noqa: BLE001 — missing CUDA build must fall back to CPU
        return False
    return _cublas12_loadable()


def _default_device() -> str:
    env = (os.environ.get("KARAOKE_WHISPER_DEVICE") or "").strip().lower()
    if env in {"cpu", "cuda", "auto"}:
        if env == "auto":
            return "cuda" if _cuda_available() else "cpu"
        if env == "cuda" and not _cuda_available():
            return "cpu"
        return env
    return "cuda" if _cuda_available() else "cpu"


def _compute_for(device: str) -> str:
    env = (os.environ.get("KARAOKE_WHISPER_COMPUTE") or "").strip()
    if env:
        return env
    return "int8" if device == "cpu" else "float16"


WHISPER_DEVICE = _default_device()
WHISPER_COMPUTE_TYPE = _compute_for(WHISPER_DEVICE)


def _default_model_size() -> str:
    env = (os.environ.get("KARAOKE_WHISPER_MODEL") or "").strip()
    if env:
        return env
    # large-v3 is noticeably better on sung Catalan; float16 fits an 8 GB GPU.
    return "large-v3" if WHISPER_DEVICE == "cuda" else "medium"


DEFAULT_MODEL_SIZE = _default_model_size()
WHISPER_BEAM_SIZE = _env_int(
    "KARAOKE_WHISPER_BEAM",
    5 if WHISPER_DEVICE == "cuda" else 3,
)

# Matching thresholds. A token pair below MATCH_MIN is never linked: leaving a
# hole for interpolation beats pinning a word onto the wrong audio position.
MATCH_MIN = 0.58
# One/two letter tokens ("a", "hi", "el") match almost anything by ratio, so they
# only count on a near exact hit.
SHORT_TOKEN_LEN = 2
SHORT_TOKEN_MIN = 0.95
# Dropping a lyric token must hurt more than skipping ASR noise, otherwise the
# path would rather ignore the lyrics than accept a slightly fuzzy match.
SKIP_LYRIC_PENALTY = 0.42
SKIP_ASR_PENALTY = 0.06
# Prefer a plain 1:1 link when a merge scores the same.
MERGE_PENALTY = 0.04
# Diagonal band around the proportional path. The length difference is added
# because ASR often carries whole blocks the lyrics do not have (long intros,
# hallucinated "lalala" outros), which shifts the true path off the diagonal.
BAND_MIN_RADIUS = 200
BAND_MAX_CELLS = 8_000_000
# Phrase search window around an LRC cue. Wider than a single word so a
# slightly late/early LRCLIB timestamp still finds the sung line. The phrase
# scorer (not the window edge) is what stops choruses colliding.
ANCHOR_PAD_BEFORE = 8.0
ANCHOR_PAD_AFTER = 6.0
# Among spans that score close to the best, prefer the earliest start so a
# missing middle word interpolates instead of skipping the first token, and so
# a misheard last word cannot latch onto the next line.
PHRASE_EARLY_TAU = 0.12
SHORT_PHRASE_LOOKAHEAD = 24

_PTR_NONE = 0
_PTR_MATCH = 1
_PTR_SKIP_LYRIC = 2
_PTR_SKIP_ASR = 3
_PTR_MERGE_ASR = 4  # one lyric token spans two ASR words ("l'amor" vs "l'" "amor")
_PTR_MERGE_LYRIC = 5  # two lyric tokens share one ASR word ("que et" vs "quet")

_NEG = float("-inf")


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


def whisper_model_status() -> dict:
    """Snapshot for /api/health and the settings UI.

    Always includes the configured defaults, even before the first load, so the
    UI can show ``large-v3 · cuda`` while the model is still downloading.
    Never waits on ``_load_lock`` — that lock is held for the whole download.
    """
    with _state_lock:
        status = dict(_model_state)
    status["configured_model"] = DEFAULT_MODEL_SIZE
    status["configured_device"] = WHISPER_DEVICE
    status["configured_compute"] = WHISPER_COMPUTE_TYPE
    if not status.get("model"):
        status["model"] = DEFAULT_MODEL_SIZE
    if not status.get("device"):
        status["device"] = WHISPER_DEVICE
    if not status.get("compute"):
        status["compute"] = WHISPER_COMPUTE_TYPE
    return status


def _update_model_state(**fields) -> None:
    with _state_lock:
        _model_state.update(fields)


def _normalize(token: str) -> str:
    # Apostrophes vanish on purpose: "l'amor" → "lamor", matching Whisper's
    # "l'" + "amor" once those two ASR tokens are merged. Accents are folded so
    # Catalan lyrics still match when Whisper drifts into Spanish ("destí"/"destino").
    folded = "".join(
        char
        for char in unicodedata.normalize("NFD", token.lower())
        if unicodedata.category(char) != "Mn"
    )
    return re.sub(r"[^\w]+", "", folded, flags=re.UNICODE)


@lru_cache(maxsize=200_000)
def _similar(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


def _match_score(lyric_norm: str, asr_norm: str) -> float:
    """Similarity of a candidate link, or 0 when the pair must not be linked."""
    if not lyric_norm or not asr_norm:
        return 0.0
    score = _similar(lyric_norm, asr_norm)
    if score < MATCH_MIN:
        return 0.0
    if min(len(lyric_norm), len(asr_norm)) <= SHORT_TOKEN_LEN and score < SHORT_TOKEN_MIN:
        return 0.0
    return score


def _split_tokens(text: str) -> list[str]:
    return [part for part in re.split(r"(\s+)", text) if part and not part.isspace()]


def _load_whisper_model(size: str, device: str, compute: str):
    from faster_whisper import WhisperModel

    _add_cuda_dll_dirs()
    return WhisperModel(size, device=device, compute_type=compute)


def _get_model(model_size: str | None = None):
    """Load (and cache) the Whisper model. Falls back to CPU if CUDA libs mismatch."""
    global _model, _model_name, _model_device, _model_compute, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE
    size = model_size or DEFAULT_MODEL_SIZE
    with _load_lock:
        with _state_lock:
            if _model is not None and _model_name == size:
                return _model

        preferred = WHISPER_DEVICE
        _update_model_state(
            ready=False,
            loading=True,
            error="",
            model=size,
            device=preferred,
            compute=WHISPER_COMPUTE_TYPE,
        )
        devices = [preferred]
        if preferred == "cuda":
            devices.append("cpu")

        last_error: Exception | None = None
        for device in devices:
            compute = WHISPER_COMPUTE_TYPE if device == preferred else _compute_for(device)
            try:
                # Download/load happens outside _state_lock so /api/whisper stays responsive.
                model = _load_whisper_model(size, device, compute)
                with _state_lock:
                    _model = model
                    _model_name = size
                    _model_device = device
                    _model_compute = compute
                    WHISPER_DEVICE = device
                    WHISPER_COMPUTE_TYPE = compute
                    _model_state.update(
                        {
                            "ready": True,
                            "loading": False,
                            "error": "",
                            "model": size,
                            "device": device,
                            "compute": compute,
                        }
                    )
                    return _model
            except Exception as exc:  # noqa: BLE001 — try next device
                last_error = exc
                continue

        error = str(last_error or "No s’ha pogut carregar Whisper")
        _update_model_state(
            ready=False,
            loading=False,
            error=error,
            model=size,
            device=preferred,
            compute=WHISPER_COMPUTE_TYPE,
        )
        raise RuntimeError(error) from last_error


def preload_whisper_model() -> None:
    """Download/load the default model in a background thread at server start."""
    global _preload_started
    if not alignment_available():
        return
    with _state_lock:
        if _preload_started or _model is not None:
            return
        _preload_started = True
        _model_state.update(
            {
                "ready": False,
                "loading": True,
                "error": "",
                "model": DEFAULT_MODEL_SIZE,
                "device": WHISPER_DEVICE,
                "compute": WHISPER_COMPUTE_TYPE,
            }
        )

    def _run() -> None:
        try:
            _get_model(DEFAULT_MODEL_SIZE)
        except Exception:  # noqa: BLE001 — status already recorded for /api/health
            pass

    threading.Thread(target=_run, name="whisper-preload", daemon=True).start()


def _reset_model_cache() -> None:
    global _model, _model_name, _model_device, _model_compute
    with _load_lock:
        with _state_lock:
            _model = None
            _model_name = None
            _model_device = None
            _model_compute = None
            _model_state.update({"ready": False, "loading": False})


def _transcribe_kwargs(language: str, initial_prompt: str | None) -> dict:
    return {
        "language": language,
        "word_timestamps": True,
        # VAD often deletes sung vocals as "non-speech".
        "vad_filter": False,
        "beam_size": WHISPER_BEAM_SIZE,
        "best_of": WHISPER_BEAM_SIZE,
        "temperature": 0.0,
        "condition_on_previous_text": False,
        "initial_prompt": initial_prompt,
        # Tighten hallucination filters a bit for music (Whisper invents outros).
        "compression_ratio_threshold": 2.2,
        "log_prob_threshold": -0.9,
    }


def transcribe_words(
    audio_path: Path,
    language: str = "ca",
    model_size: str | None = None,
    initial_prompt: str | None = None,
    on_progress: Callable[[float], None] | None = None,
) -> list[AsrWord]:
    global WHISPER_DEVICE, WHISPER_COMPUTE_TYPE
    model = _get_model(model_size)
    kwargs = _transcribe_kwargs(language, initial_prompt)
    try:
        segments, info = model.transcribe(str(audio_path), **kwargs)
    except Exception as exc:  # noqa: BLE001 — CUDA runtime gaps show up at transcribe time
        message = str(exc).lower()
        if WHISPER_DEVICE == "cuda" and ("cublas" in message or "cuda" in message):
            _reset_model_cache()
            WHISPER_DEVICE = "cpu"
            WHISPER_COMPUTE_TYPE = _compute_for("cpu")
            model = _get_model(model_size)
            segments, info = model.transcribe(str(audio_path), **kwargs)
        else:
            raise
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
            # Pack unmatched pickups against the first match. Spreading them from
            # line_start paints the first word through the pause before the phrase.
            widths = [
                max(0.10, min(0.40, sung_word_duration(filled[k].text)))
                for k in range(next_i)
            ]
            start = filled[next_i].time - sum(widths) + sum(widths[:i])
            end = start + widths[i]
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


def _empty_words(tokens: list[str]) -> list[LyricWord]:
    return [LyricWord(time=-1.0, end=-1.0, text=token) for token in tokens]


def _word_from_asr(
    text: str,
    asr_words: list[AsrWord],
    asr_from: int,
    asr_to: int,
    share: int,
) -> LyricWord:
    start = asr_words[asr_from].start
    end = max(asr_words[asr_to].end, start + 0.05)
    if share:
        middle = start + (end - start) / 2
        start, end = (start, middle) if share == 1 else (middle, end)
    return LyricWord(time=start, end=max(end, start + 0.05), text=text)


def _phrase_threshold(concat: str) -> float:
    if len(concat) <= 2:
        return 0.92
    if len(concat) <= 5:
        return 0.70
    return 0.48


def _phrase_similarity(lyric_concat: str, asr_concat: str) -> float:
    """Length-aware similarity so eating the next phrase scores worse than a fuzzy line."""
    if not lyric_concat or not asr_concat:
        return 0.0
    ratio = _similar(lyric_concat, asr_concat)
    if ratio < 0.35:
        return 0.0
    char_pen = min(len(lyric_concat), len(asr_concat)) / max(len(lyric_concat), len(asr_concat))
    return ratio * (0.5 + 0.5 * char_pen)


def _locate_phrase(
    lyric_concat: str,
    n_tokens: int,
    asr_norms: list[str],
    asr_starts: list[float],
    j_min: int,
    j_max: int,
    expected_time: float | None,
) -> tuple[int, int] | None:
    """Best ASR span [from, to) for a lyric line, or None if nothing is close enough.

    Scores every plausible window, then among spans near the best score picks the
    earliest start. That keeps a misheard last word from latching onto the next
    line, and a missing middle word from dropping the first token of the line.
    """
    if not lyric_concat or j_min >= j_max or n_tokens < 1:
        return None

    min_len = max(1, n_tokens - 2)
    max_len = n_tokens + 3
    threshold = _phrase_threshold(lyric_concat)
    scored: list[tuple[float, float, int, int]] = []
    best_raw = 0.0

    for j in range(j_min, j_max):
        max_here = min(max_len, j_max - j)
        for length in range(min_len, max_here + 1):
            raw = _phrase_similarity(lyric_concat, "".join(asr_norms[j : j + length]))
            if raw <= 0:
                continue
            ranked = raw
            if expected_time is not None:
                ranked *= 0.85 + 0.15 / (1.0 + abs(asr_starts[j] - expected_time) / 4.0)
            scored.append((ranked, raw, j, j + length))
            if raw > best_raw:
                best_raw = raw

    if best_raw < threshold or not scored:
        return None

    near = [row for row in scored if row[1] >= best_raw - PHRASE_EARLY_TAU]
    near.sort(key=lambda row: (row[2], -row[0]))
    return near[0][2], near[0][3]


def _asr_index_range(
    asr_words: list[AsrWord],
    t0: float,
    t1: float,
    j_min: int,
) -> tuple[int, int]:
    lo: int | None = None
    hi = j_min
    for index in range(j_min, len(asr_words)):
        word = asr_words[index]
        if word.start >= t1:
            break
        if word.end < t0:
            continue
        if lo is None:
            lo = index
        hi = index + 1
    if lo is None:
        return j_min, j_min
    return lo, hi


def _align_tokens_to_asr(tokens: list[str], asr_slice: list[AsrWord]) -> list[LyricWord]:
    """Word-level DP inside an already-chosen phrase span. Unmatched stay at -1."""
    words = _empty_words(tokens)
    if not tokens or not asr_slice:
        return words
    pairs = _align_path(
        [_normalize(token) for token in tokens],
        [_normalize(word.text) for word in asr_slice],
    )
    for lyric_index, asr_from, asr_to, share in pairs:
        words[lyric_index] = _word_from_asr(
            tokens[lyric_index], asr_slice, asr_from, asr_to, share
        )
    return words


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
        if word.end >= line_start - ANCHOR_PAD_BEFORE and word.start <= line_end + ANCHOR_PAD_AFTER
    ]
    aligned = _empty_words(tokens)
    if window:
        concat = "".join(_normalize(token) for token in tokens)
        located = _locate_phrase(
            concat,
            len(tokens),
            [_normalize(word.text) for word in window],
            [word.start for word in window],
            0,
            len(window),
            line_start,
        )
        span = window[located[0] : located[1]] if located else window
        aligned = _align_tokens_to_asr(tokens, span)
    return _interpolate_missing(aligned, line_start, line_end)


def _band(i: int, n: int, m: int, radius: int) -> tuple[int, int]:
    center = int(round(i * m / n)) if n else 0
    return max(0, center - radius), min(m, center + radius)


def _align_path(lyric_norms: list[str], asr_norms: list[str]) -> list[tuple[int, int, int, int]]:
    """Monotonic best-path match between lyric tokens and ASR words.

    Returns (lyric_index, asr_from, asr_to, share) tuples, where share is 0 for a
    full span, 1 for the first half of a shared ASR word and 2 for the second.
    A monotonic path is what keeps repeated choruses from stealing each other's
    timings, which a per-token nearest-match scan cannot guarantee.
    """
    n, m = len(lyric_norms), len(asr_norms)
    if not n or not m:
        return []

    radius = max(BAND_MIN_RADIUS, abs(m - n) + int(0.15 * max(n, m)))
    if n * (2 * radius + 1) > BAND_MAX_CELLS:
        radius = max(BAND_MIN_RADIUS, BAND_MAX_CELLS // (2 * n) if n else BAND_MIN_RADIUS)
    width = m + 1
    ptr = bytearray(width * (n + 1))

    prev2: list[float] | None = None
    prev = [-SKIP_ASR_PENALTY * j for j in range(width)]
    for j in range(1, width):
        ptr[j] = _PTR_SKIP_ASR

    for i in range(1, n + 1):
        cur = [_NEG] * width
        base = i * width
        low, high = _band(i, n, m, radius)
        if low == 0:
            cur[0] = -SKIP_LYRIC_PENALTY * i
            ptr[base] = _PTR_SKIP_LYRIC
        lyric = lyric_norms[i - 1]
        previous_lyric = lyric_norms[i - 2] if i >= 2 else ""

        for j in range(max(1, low), high + 1):
            best = prev[j] - SKIP_LYRIC_PENALTY
            code = _PTR_SKIP_LYRIC

            value = cur[j - 1] - SKIP_ASR_PENALTY
            if value > best:
                best, code = value, _PTR_SKIP_ASR

            score = _match_score(lyric, asr_norms[j - 1])
            if score:
                value = prev[j - 1] + score
                if value > best:
                    best, code = value, _PTR_MATCH

            if j >= 2:
                merged = _match_score(lyric, asr_norms[j - 2] + asr_norms[j - 1])
                if merged:
                    value = prev[j - 2] + merged - MERGE_PENALTY
                    if value > best:
                        best, code = value, _PTR_MERGE_ASR

            if i >= 2 and prev2 is not None:
                merged = _match_score(previous_lyric + lyric, asr_norms[j - 1])
                if merged:
                    value = prev2[j - 1] + merged - MERGE_PENALTY
                    if value > best:
                        best, code = value, _PTR_MERGE_LYRIC

            cur[j] = best
            ptr[base + j] = code

        prev2 = prev
        prev = cur

    pairs: list[tuple[int, int, int, int]] = []
    i, j = n, m
    while i > 0 or j > 0:
        code = ptr[i * width + j] if (i or j) else _PTR_NONE
        if code == _PTR_MATCH:
            pairs.append((i - 1, j - 1, j - 1, 0))
            i -= 1
            j -= 1
        elif code == _PTR_MERGE_ASR:
            pairs.append((i - 1, j - 2, j - 1, 0))
            i -= 1
            j -= 2
        elif code == _PTR_MERGE_LYRIC:
            pairs.append((i - 1, j - 1, j - 1, 2))
            pairs.append((i - 2, j - 1, j - 1, 1))
            i -= 2
            j -= 1
        elif code == _PTR_SKIP_LYRIC:
            i -= 1
        elif code == _PTR_SKIP_ASR:
            j -= 1
        elif i > 0 and j > 0:
            i -= 1
            j -= 1
        elif i > 0:
            i -= 1
        else:
            j -= 1

    pairs.reverse()
    return pairs


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

    asr_norms = [_normalize(word.text) for word in asr_words]
    pairs = _align_path([token.norm for token in tokens], asr_norms)

    for lyric_index, asr_from, asr_to, share in pairs:
        token = tokens[lyric_index]
        placeholders[token.line_index][token.token_index] = _word_from_asr(
            token.text, asr_words, asr_from, asr_to, share
        )

    return placeholders


def _has_sync_anchors(lines: list[LyricLine]) -> bool:
    """True when line times look like real LRC sync, not the plain i*4 fallback."""
    times = [float(line.time) for line in lines if float(line.time) > 0]
    if len(times) < max(3, len(lines) // 4):
        return False
    if len(times) >= 3:
        gaps = [times[i + 1] - times[i] for i in range(len(times) - 1)]
        if gaps and all(abs(gap - 4.0) < 0.051 for gap in gaps):
            return False
    return True


def align_tokens_by_phrases(
    lines: list[LyricLine],
    asr_words: list[AsrWord],
    *,
    use_time_windows: bool,
) -> list[list[LyricWord]]:
    """Locate each lyric line in the ASR, then word-align inside that span.

    A whole-line vote stops one misheard word from stealing the next phrase.
    When ``use_time_windows`` is set, search is biased toward LRCLIB cues so
    repeated choruses stay on their own verse.
    """
    line_tokens = [_split_tokens(line.text) for line in lines]
    result = [_empty_words(tokens) for tokens in line_tokens]
    if not asr_words:
        return result

    asr_norms = [_normalize(word.text) for word in asr_words]
    asr_starts = [word.start for word in asr_words]
    last_j = 0

    for index, (line, tokens) in enumerate(zip(lines, line_tokens)):
        if not tokens:
            continue
        concat = "".join(_normalize(token) for token in tokens)
        if use_time_windows:
            next_time = (
                float(lines[index + 1].time)
                if index + 1 < len(lines) and float(lines[index + 1].time) > float(line.time)
                else float(line.time) + 8.0
            )
            t0 = max(0.0, float(line.time) - ANCHOR_PAD_BEFORE)
            t1 = next_time + ANCHOR_PAD_AFTER
            j_min, j_max = _asr_index_range(asr_words, t0, t1, last_j)
            expected: float | None = float(line.time)
        else:
            j_min = last_j
            if len(concat) <= 6:
                j_max = min(len(asr_words), last_j + max(SHORT_PHRASE_LOOKAHEAD, len(tokens) * 10))
            else:
                j_max = len(asr_words)
            expected = None

        located = _locate_phrase(
            concat,
            len(tokens),
            asr_norms,
            asr_starts,
            j_min,
            j_max,
            expected,
        )
        if located is None:
            continue
        start, end = located
        result[index] = _align_tokens_to_asr(tokens, asr_words[start:end])
        last_j = max(last_j, end)
    return result


def align_tokens_with_anchors(
    lines: list[LyricLine],
    asr_words: list[AsrWord],
) -> list[list[LyricWord]]:
    """Align each line near its LRCLIB timestamp using phrase-first matching."""
    return align_tokens_by_phrases(lines, asr_words, use_time_windows=True)


def _enforce_monotonic(lines: list[LyricLine]) -> list[LyricLine]:
    """Never let a word start before the previous one: backwards jumps read as a bug."""
    flat = [word for line in lines for word in line.words]
    last_start = _NEG
    for word in flat:
        if word.time < last_start:
            word.time = last_start
        if word.end < word.time + 0.05:
            word.end = word.time + 0.05
        last_start = word.time
    for word, following in zip(flat, flat[1:]):
        if word.end > following.time + 0.05:
            word.end = max(word.time + 0.05, following.time)
    for line in lines:
        if line.words:
            line.time = line.words[0].time
    return lines


def align_lyrics(
    audio_path: Path,
    lines: list[LyricLine],
    *,
    language: str = "ca",
    model_size: str | None = None,
    on_progress: Callable[[float], None] | None = None,
) -> list[LyricLine]:
    """Align known lyric lines to the audio with faster-whisper word timestamps."""
    if not lines:
        return []
    if not audio_path.is_file():
        raise FileNotFoundError(str(audio_path))

    # Feed as much of the known lyric text as Whisper accepts — this biases
    # Catalan singing away from Spanish lookalikes.
    prompt = " ".join(line.text for line in lines).strip()
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

    use_anchors = _has_sync_anchors(lines)
    per_line = align_tokens_by_phrases(lines, asr_words, use_time_windows=use_anchors)
    matched = sum(1 for row in per_line for word in row if word.time >= 0)
    total = sum(len(row) for row in per_line) or 1
    if matched / total < 0.35:
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
            # Prefer ASR-derived bounds for the tail; do not pull line_start back
            # to the LRC cue or unmatched pickups fill the whole pre-phrase pause.
            if len(known) < max(1, len(words) // 3):
                line_end = max(next_time, line_end)
            words = _interpolate_missing(words, line_start, line_end)
            line_time = words[0].time if words else line.time
        else:
            line_time = line.time
            words = estimate_words(line.time, next_time, line.text)
        aligned_lines.append(LyricLine(time=line_time, text=line.text, words=words))
    return tighten_phrase_onsets(_enforce_monotonic(aligned_lines))
