import numpy as np

from karaoke_party.lyrics import LyricLine, LyricWord
from karaoke_party.mms_align import (
    CharSpan,
    align_syllables_mms,
    ctc_forced_align,
    mms_enabled,
    normalize_for_mms,
    syllables_from_char_spans,
)


def test_normalize_catalan_for_mms() -> None:
    assert normalize_for_mms("País") == "pais"
    assert normalize_for_mms("l'amor") == "l'amor"
    assert normalize_for_mms("Dona’m") == "dona'm"
    assert normalize_for_mms("ça") == "ca"
    assert normalize_for_mms("Col·legi") == "collegi"
    assert normalize_for_mms("68") == ""
    assert normalize_for_mms("brindar") == "brindar"


def test_align_syllables_mms_disabled_returns_none(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("KARAOKE_MMS", "0")
    wav = tmp_path / "vocals.wav"
    wav.write_bytes(b"x")
    lines = [
        LyricLine(
            time=0.0,
            text="brindar",
            words=[LyricWord(time=0.0, end=1.0, text="brindar")],
        )
    ]
    assert align_syllables_mms(wav, lines) is None


def test_mms_enabled_env(monkeypatch) -> None:
    monkeypatch.setenv("KARAOKE_MMS", "0")
    assert mms_enabled() is False
    monkeypatch.setenv("KARAOKE_MMS", "cpu")
    assert mms_enabled() is True
    monkeypatch.setenv("KARAOKE_MMS", "1")
    assert mms_enabled() is True


def test_syllables_from_char_spans_splits_brindar() -> None:
    chars = [
        CharSpan("b", 1.00, 1.08),
        CharSpan("r", 1.08, 1.16),
        CharSpan("i", 1.16, 1.28),
        CharSpan("n", 1.28, 1.40),
        CharSpan("d", 1.40, 1.50),
        CharSpan("a", 1.50, 1.62),
        CharSpan("r", 1.62, 1.75),
    ]
    word = LyricWord(time=0.9, end=1.9, text="brindar")
    tokens = syllables_from_char_spans(word, chars)
    assert [token.text for token in tokens] == ["brin", "dar"]
    assert tokens[0].glue is True
    assert tokens[1].glue is False
    assert abs(tokens[0].time - 1.00) < 0.001
    assert abs(tokens[0].end - 1.40) < 0.001
    assert abs(tokens[1].time - 1.40) < 0.001
    assert abs(tokens[1].end - 1.75) < 0.001


def test_syllables_from_char_spans_keeps_clitic() -> None:
    chars = [
        CharSpan("l", 2.0, 2.05),
        CharSpan("'", 2.05, 2.08),
        CharSpan("a", 2.08, 2.18),
        CharSpan("m", 2.18, 2.28),
        CharSpan("o", 2.28, 2.40),
        CharSpan("r", 2.40, 2.52),
    ]
    word = LyricWord(time=2.0, end=2.6, text="l'amor")
    tokens = syllables_from_char_spans(word, chars)
    assert [token.text for token in tokens] == ["l'a", "mor"]
    assert tokens[0].glue is True
    assert abs(tokens[0].end - 2.18) < 0.001
    assert abs(tokens[1].time - 2.18) < 0.001


def test_ctc_aligns_two_token_peaks() -> None:
    time_count, vocab = 30, 5
    blank = 0
    log_p = np.full((time_count, vocab), -8.0)
    log_p[:, blank] = -0.2
    log_p[6:12, 1] = 0.0
    log_p[6:12, blank] = -5.0
    log_p[16:22, 2] = 0.0
    log_p[16:22, blank] = -5.0
    spans = ctc_forced_align(log_p, [1, 2], blank=blank)
    assert len(spans) == 2
    assert spans[0][0] <= 8 <= spans[0][1]
    assert spans[1][0] <= 18 <= spans[1][1]
    assert spans[0][1] <= spans[1][0]


def test_ctc_separates_repeated_letters() -> None:
    time_count, vocab = 40, 4
    blank = 0
    log_p = np.full((time_count, vocab), -8.0)
    log_p[:, blank] = -0.4
    log_p[6:14, 1] = 0.0
    log_p[6:14, blank] = -5.0
    log_p[14:18, blank] = 0.0
    log_p[18:28, 1] = 0.0
    log_p[18:28, blank] = -5.0
    spans = ctc_forced_align(log_p, [1, 1], blank=blank)
    assert len(spans) == 2
    assert spans[0][1] <= spans[1][0]
    assert 6 <= spans[0][0] <= 14
    assert 16 <= spans[1][0] <= 28
