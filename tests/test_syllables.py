from karaoke_party.lyrics import LyricLine, LyricWord
from karaoke_party.syllables import expand_syllable_tokens, syllabify_token


def test_syllabify_common_catalan_words() -> None:
    assert syllabify_token("casa") == ["ca", "sa"]
    assert syllabify_token("amor") == ["a", "mor"]
    assert syllabify_token("brindar") == ["brin", "dar"]
    assert syllabify_token("sempre") == ["sem", "pre"]
    assert syllabify_token("altra") == ["al", "tra"]
    assert syllabify_token("poma") == ["po", "ma"]
    assert syllabify_token("porta") == ["por", "ta"]
    assert syllabify_token("guerra") == ["guer", "ra"]
    assert syllabify_token("llengua") == ["llen", "gua"]
    assert syllabify_token("oblidar") == ["o", "bli", "dar"]
    assert syllabify_token("país") == ["pa", "ís"]
    assert syllabify_token("somiàvem") == ["so", "mi", "à", "vem"]
    assert syllabify_token("que") == ["que"]
    assert syllabify_token("I") == ["I"]


def test_syllabify_keeps_clitics_and_punctuation() -> None:
    assert syllabify_token("l'amor") == ["l'a", "mor"]
    assert syllabify_token("Dona'm") == ["Do", "na'm"]
    assert syllabify_token("nit,") == ["nit,"]
    assert syllabify_token("68") == ["68"]


def test_expand_syllables_splits_time_inside_the_word() -> None:
    lines = [
        LyricLine(
            time=10.0,
            text="brindar ja",
            words=[
                LyricWord(time=10.0, end=10.8, text="brindar"),
                LyricWord(time=10.8, end=11.1, text="ja"),
            ],
        )
    ]
    expanded = expand_syllable_tokens(lines)
    tokens = expanded[0].words
    assert [token.text for token in tokens] == ["brin", "dar", "ja"]
    assert tokens[0].glue is True
    assert tokens[1].glue is False
    assert tokens[2].glue is False
    assert abs(tokens[0].time - 10.0) < 0.001
    assert abs(tokens[1].end - 10.8) < 0.001
    assert tokens[0].end <= tokens[1].time + 0.001
    assert tokens[1].time > tokens[0].time
    assert abs(tokens[2].time - 10.8) < 0.001


def test_energy_split_puts_boundary_in_the_quiet_gap() -> None:
    import numpy as np
    from karaoke_party.syllables import _energy_split_times

    sr = 22050
    duration = 1.0
    samples = np.zeros(int(sr * duration), dtype=np.float32)
    t = np.arange(len(samples)) / sr
    # Two sung nuclei with a dip in the middle.
    burst1 = (t >= 0.08) & (t <= 0.32)
    burst2 = (t >= 0.62) & (t <= 0.92)
    samples[burst1] = 0.8 * np.sin(2 * np.pi * 220 * t[burst1])
    samples[burst2] = 0.8 * np.sin(2 * np.pi * 220 * t[burst2])
    times = _energy_split_times(samples, sr, [1, 1])
    assert times[0] == 0.0
    assert abs(times[-1] - duration) < 0.02
    assert 0.35 < times[1] < 0.62


def test_refine_syllable_timings_uses_audio_when_present(tmp_path, monkeypatch) -> None:
    import numpy as np
    import soundfile as sf
    from karaoke_party.syllables import refine_syllable_timings

    monkeypatch.setenv("KARAOKE_MMS", "0")

    sr = 22050
    samples = np.zeros(sr, dtype=np.float32)
    t = np.arange(sr) / sr
    samples[(t >= 0.08) & (t <= 0.32)] = 0.7
    samples[(t >= 0.62) & (t <= 0.92)] = 0.7
    wav = tmp_path / "vocals.wav"
    sf.write(wav, samples, sr)
    lines = [
        LyricLine(
            time=0.0,
            text="brindar",
            words=[LyricWord(time=0.0, end=1.0, text="brindar")],
        )
    ]
    refined = refine_syllable_timings(wav, lines)
    tokens = refined[0].words
    assert [token.text for token in tokens] == ["brin", "dar"]
    assert tokens[0].glue is True
    assert 0.32 < tokens[0].end < 0.66


def test_refine_prefers_mms_when_enabled(tmp_path, monkeypatch) -> None:
    from karaoke_party.syllables import refine_syllable_timings

    monkeypatch.setenv("KARAOKE_MMS", "1")
    fake = [
        LyricLine(
            time=0.0,
            text="brindar",
            words=[
                LyricWord(time=0.0, end=0.41, text="brin", glue=True),
                LyricWord(time=0.41, end=1.0, text="dar", glue=False),
            ],
        )
    ]
    monkeypatch.setattr(
        "karaoke_party.mms_align.align_syllables_mms",
        lambda _path, _lines: fake,
    )
    wav = tmp_path / "vocals.wav"
    wav.write_bytes(b"fake")
    lines = [
        LyricLine(
            time=0.0,
            text="brindar",
            words=[LyricWord(time=0.0, end=1.0, text="brindar")],
        )
    ]
    refined = refine_syllable_timings(wav, lines)
    assert [token.text for token in refined[0].words] == ["brin", "dar"]
    assert abs(refined[0].words[0].end - 0.41) < 0.001
