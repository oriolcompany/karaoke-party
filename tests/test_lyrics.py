from karaoke_party.lyrics import (
    LyricLine,
    LyricWord,
    attach_word_timings,
    estimate_words,
    parse_enhanced_words,
    parse_lrc,
    tighten_phrase_onsets,
)


def test_parse_lrc_basic() -> None:
    content = """
[00:12.00]Line one
[00:15.50]Line two
[01:02.123]Line three
"""
    lines = parse_lrc(content)
    assert len(lines) == 3
    assert lines[0].time == 12.0
    assert lines[0].text == "Line one"
    assert lines[0].words
    assert lines[0].words[0].text == "Line"
    assert lines[0].words[1].text == "one"
    assert lines[0].words[0].time == 12.0
    assert lines[0].words[-1].end <= 15.5


def test_estimate_words_spread() -> None:
    words = estimate_words(10.0, 14.0, "Ai Dolors porta")
    assert len(words) == 3
    assert words[0].time == 10.0
    assert words[-1].end <= 14.0


def test_enhanced_lrc_words() -> None:
    plain, words = parse_enhanced_words("<00:12.00>Hello <00:12.40>world")
    assert plain == "Hello world"
    assert len(words) == 2
    assert words[0].time == 12.0
    assert words[1].time == 12.4


def test_attach_preserves_enhanced() -> None:
    from karaoke_party.lyrics import LyricLine

    lines = attach_word_timings(
        [LyricLine(time=1.0, text="<00:01.00>One <00:01.50>Two"), LyricLine(time=3.0, text="Next")]
    )
    assert lines[0].words[0].text == "One"
    assert lines[0].words[1].time == 1.5


def test_tighten_short_first_word_does_not_eat_pause() -> None:
    lines = [
        LyricLine(
            time=10.0,
            text="hola adéu",
            words=[
                LyricWord(time=10.0, end=10.4, text="hola"),
                LyricWord(time=10.4, end=10.8, text="adéu"),
            ],
        ),
        LyricLine(
            time=10.8,
            text="Un heroi",
            words=[
                LyricWord(time=10.8, end=14.4, text="Un"),
                LyricWord(time=14.4, end=14.9, text="heroi"),
            ],
        ),
    ]
    tighten_phrase_onsets(lines)
    first = lines[1].words[0]
    assert first.end - first.time < 0.45
    assert first.time > 13.9
    assert abs(lines[1].time - first.time) < 0.001


def test_tighten_keeps_held_word_after_a_pause() -> None:
    lines = [
        LyricLine(
            time=10.0,
            text="canta",
            words=[LyricWord(time=10.0, end=10.4, text="canta")],
        ),
        LyricLine(
            time=12.0,
            text="Amor etern",
            words=[
                LyricWord(time=12.0, end=14.0, text="Amor"),
                LyricWord(time=14.0, end=14.5, text="etern"),
            ],
        ),
    ]
    tighten_phrase_onsets(lines)
    first = lines[1].words[0]
    assert abs(first.time - 12.0) < 0.01
    assert abs(first.end - 14.0) < 0.01
