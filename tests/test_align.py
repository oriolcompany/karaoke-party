import pytest

from karaoke_party.align import (
    AlignmentError,
    AsrWord,
    RESUME_CLIP_PAD,
    _has_sync_anchors,
    _interpolate_missing,
    _normalize,
    _offset_if_clip_relative,
    _shift_lines_to_floor,
    align_from_anchor,
    align_line_words,
    align_tokens_by_phrases,
    align_tokens_globally,
    align_tokens_with_anchors,
)
from karaoke_party.lyrics import LyricLine, LyricWord


def test_align_line_words_matches_asr():
    asr = [
        AsrWord("bona", 10.0, 10.3),
        AsrWord("nit", 10.35, 10.6),
        AsrWord("amor", 10.7, 11.1),
    ]
    words = align_line_words("Bona nit, amor", 9.8, 12.0, asr)
    assert [w.text for w in words] == ["Bona", "nit,", "amor"]
    assert abs(words[0].time - 10.0) < 0.01
    assert abs(words[2].time - 10.7) < 0.01


def test_align_line_words_interpolates_gaps():
    asr = [
        AsrWord("un", 1.0, 1.2),
        AsrWord("tres", 2.0, 2.3),
    ]
    words = align_line_words("un dos tres", 0.9, 3.0, asr)
    assert [w.text for w in words] == ["un", "dos", "tres"]
    assert words[1].time >= words[0].end
    assert words[1].time < words[2].time


def test_align_tokens_globally_handles_intro_offset():
    lines = [
        LyricLine(time=0.0, text="Imposant llargues condemnes"),
        LyricLine(time=4.0, text="No em fareu pas penedir"),
    ]
    asr = [
        AsrWord("Imposant", 30.2, 30.9),
        AsrWord("llargues", 30.9, 31.6),
        AsrWord("condemnes", 31.6, 32.4),
        AsrWord("No", 32.4, 32.6),
        AsrWord("em", 32.6, 32.8),
        AsrWord("fareu", 32.8, 33.4),
        AsrWord("pas", 33.4, 33.8),
        AsrWord("penedir", 33.8, 34.5),
    ]
    per_line = align_tokens_globally(lines, asr)
    assert abs(per_line[0][0].time - 30.2) < 0.01
    assert abs(per_line[1][0].time - 32.4) < 0.01


def test_repeated_chorus_keeps_timings_monotonic():
    """A word repeated in a chorus must not borrow the other verse's timing."""
    lines = [
        LyricLine(time=0.0, text="canta amb mi"),
        LyricLine(time=4.0, text="canta amb mi"),
    ]
    asr = [
        AsrWord("canta", 1.0, 1.4),
        AsrWord("amb", 1.4, 1.6),
        AsrWord("mi", 1.6, 2.0),
        AsrWord("canta", 5.0, 5.4),
        AsrWord("amb", 5.4, 5.6),
        AsrWord("mi", 5.6, 6.0),
    ]
    per_line = align_tokens_globally(lines, asr)
    times = [word.time for line in per_line for word in line]
    assert times == sorted(times)
    assert abs(per_line[0][0].time - 1.0) < 0.01
    assert abs(per_line[1][0].time - 5.0) < 0.01


def test_apostrophe_token_split_by_whisper_is_merged():
    lines = [LyricLine(time=0.0, text="tot l'amor")]
    asr = [
        AsrWord("tot", 2.0, 2.3),
        AsrWord("l'", 2.35, 2.45),
        AsrWord("amor", 2.45, 3.0),
    ]
    per_line = align_tokens_globally(lines, asr)
    assert [word.text for word in per_line[0]] == ["tot", "l'amor"]
    assert abs(per_line[0][1].time - 2.35) < 0.01
    assert abs(per_line[0][1].end - 3.0) < 0.01


def test_two_lyric_tokens_share_one_asr_word():
    lines = [LyricLine(time=0.0, text="que et miro")]
    asr = [
        AsrWord("quet", 5.0, 5.4),
        AsrWord("miro", 5.4, 5.9),
    ]
    per_line = align_tokens_globally(lines, asr)
    words = per_line[0]
    assert [word.text for word in words] == ["que", "et", "miro"]
    assert abs(words[0].time - 5.0) < 0.01
    assert abs(words[1].time - 5.2) < 0.01
    assert abs(words[2].time - 5.4) < 0.01


def test_asr_noise_around_lyrics_is_skipped():
    lines = [LyricLine(time=0.0, text="bona nit")]
    asr = [
        AsrWord("subtitles", 0.5, 1.0),
        AsrWord("by", 1.0, 1.2),
        AsrWord("bona", 8.0, 8.4),
        AsrWord("nit", 8.4, 8.9),
        AsrWord("gracies", 12.0, 12.6),
    ]
    per_line = align_tokens_globally(lines, asr)
    assert abs(per_line[0][0].time - 8.0) < 0.01
    assert abs(per_line[0][1].time - 8.4) < 0.01


def test_unmatched_lyrics_stay_unmatched():
    lines = [LyricLine(time=0.0, text="paraules completament diferents")]
    asr = [AsrWord("xylophone", 1.0, 1.5)]
    per_line = align_tokens_globally(lines, asr)
    assert all(word.time < 0 for word in per_line[0])


def test_normalize_folds_accents_and_apostrophes():
    assert _normalize("l'amor") == "lamor"
    assert _normalize("destí") == "desti"
    assert _normalize("Àudio") == "audio"


def test_has_sync_anchors_rejects_plain_four_second_grid():
    lines = [LyricLine(time=float(i * 4), text=f"linia {i}") for i in range(6)]
    assert _has_sync_anchors(lines) is False
    synced = [
        LyricLine(time=12.4, text="una"),
        LyricLine(time=15.1, text="dues"),
        LyricLine(time=19.8, text="tres"),
        LyricLine(time=24.0, text="quatre"),
    ]
    assert _has_sync_anchors(synced) is True


def test_anchored_align_keeps_chorus_near_lrc_times():
    """With LRC cues, the second chorus must not latch onto the first ASR hit."""
    lines = [
        LyricLine(time=10.0, text="canta amb mi"),
        LyricLine(time=40.0, text="canta amb mi"),
    ]
    asr = [
        AsrWord("canta", 10.1, 10.5),
        AsrWord("amb", 10.5, 10.7),
        AsrWord("mi", 10.7, 11.1),
        AsrWord("canta", 40.2, 40.6),
        AsrWord("amb", 40.6, 40.8),
        AsrWord("mi", 40.8, 41.2),
    ]
    per_line = align_tokens_with_anchors(lines, asr)
    assert abs(per_line[0][0].time - 10.1) < 0.01
    assert abs(per_line[1][0].time - 40.2) < 0.01


def test_misheard_word_does_not_steal_next_phrase():
    """A fuzzy last word must not latch onto the next line's matching token."""
    lines = [
        LyricLine(time=10.0, text="el meu amor"),
        LyricLine(time=12.0, text="amor etern"),
    ]
    asr = [
        AsrWord("el", 10.0, 10.2),
        AsrWord("meu", 10.2, 10.4),
        AsrWord("cor", 10.4, 10.8),
        AsrWord("amor", 12.0, 12.4),
        AsrWord("etern", 12.4, 12.9),
    ]
    per_line = align_tokens_with_anchors(lines, asr)
    assert abs(per_line[0][0].time - 10.0) < 0.01
    assert abs(per_line[0][1].time - 10.2) < 0.01
    assert per_line[0][2].time < 11.5
    assert abs(per_line[1][0].time - 12.0) < 0.01
    assert abs(per_line[1][1].time - 12.4) < 0.01


def test_anchored_phrase_merges_whisper_apostrophe_split():
    lines = [LyricLine(time=10.0, text="tot l'amor")]
    asr = [
        AsrWord("tot", 10.0, 10.3),
        AsrWord("l'", 10.35, 10.45),
        AsrWord("amor", 10.45, 11.0),
    ]
    per_line = align_tokens_with_anchors(lines, asr)
    assert [word.text for word in per_line[0]] == ["tot", "l'amor"]
    assert abs(per_line[0][1].time - 10.35) < 0.01
    assert abs(per_line[0][1].end - 11.0) < 0.01


def test_extra_asr_word_inside_phrase_keeps_last_token_time():
    lines = [LyricLine(time=10.0, text="el meu amor")]
    asr = [
        AsrWord("el", 10.0, 10.2),
        AsrWord("meu", 10.2, 10.4),
        AsrWord("gran", 10.4, 10.7),
        AsrWord("amor", 10.7, 11.2),
    ]
    per_line = align_tokens_with_anchors(lines, asr)
    assert abs(per_line[0][0].time - 10.0) < 0.01
    assert abs(per_line[0][2].time - 10.7) < 0.01


def test_phrase_found_when_lrc_is_several_seconds_late():
    lines = [
        LyricLine(time=14.0, text="bona nit amor"),
        LyricLine(time=18.0, text="fins aviat"),
    ]
    asr = [
        AsrWord("bona", 10.0, 10.3),
        AsrWord("nit", 10.3, 10.6),
        AsrWord("amor", 10.6, 11.1),
        AsrWord("fins", 12.0, 12.3),
        AsrWord("aviat", 12.3, 12.8),
    ]
    per_line = align_tokens_with_anchors(lines, asr)
    assert abs(per_line[0][0].time - 10.0) < 0.01
    assert abs(per_line[1][0].time - 12.0) < 0.01


def test_phrase_walk_skips_intro_noise():
    lines = [
        LyricLine(time=0.0, text="Imposant llargues condemnes"),
        LyricLine(time=4.0, text="No em fareu pas penedir"),
    ]
    asr = [
        AsrWord("subtitles", 0.5, 1.0),
        AsrWord("by", 1.0, 1.2),
        AsrWord("Imposant", 30.2, 30.9),
        AsrWord("llargues", 30.9, 31.6),
        AsrWord("condemnes", 31.6, 32.4),
        AsrWord("No", 32.4, 32.6),
        AsrWord("em", 32.6, 32.8),
        AsrWord("fareu", 32.8, 33.4),
        AsrWord("pas", 33.4, 33.8),
        AsrWord("penedir", 33.8, 34.5),
    ]
    per_line = align_tokens_by_phrases(lines, asr, use_time_windows=False)
    assert abs(per_line[0][0].time - 30.2) < 0.01
    assert abs(per_line[1][0].time - 32.4) < 0.01


def test_unmatched_pickup_is_packed_against_first_match():
    """A missed 'I' must not fill the pause from the LRC cue to the next word."""
    words = _interpolate_missing(
        [
            LyricWord(time=-1.0, end=-1.0, text="I"),
            LyricWord(time=20.36, end=20.64, text="vàrem"),
            LyricWord(time=20.64, end=20.90, text="viure"),
        ],
        19.0,
        22.0,
    )
    assert words[0].end <= words[1].time + 0.02
    assert words[1].time - words[0].time <= 0.35
    assert words[0].time >= 19.9


def test_shift_lines_to_floor_keeps_shape() -> None:
    lines = [
        LyricLine(
            time=1.0,
            text="no em fareu",
            words=[LyricWord(1.0, 1.3, "no"), LyricWord(1.3, 1.8, "em")],
        )
    ]
    shifted = _shift_lines_to_floor(lines, 5.0)
    assert shifted[0].words[0].time == pytest.approx(5.0)
    assert shifted[0].words[1].time - shifted[0].words[0].time == pytest.approx(0.3)
    assert _shift_lines_to_floor(lines, 0.5) is lines


def test_align_from_anchor_keeps_prefix_and_places_tail_after_it(tmp_path, monkeypatch) -> None:
    audio = tmp_path / "vocals.wav"
    audio.write_bytes(b"not-a-real-wav")
    prefix = LyricLine(
        time=1.0,
        text="Avui cantem",
        words=[LyricWord(1.0, 1.4, "Avui"), LyricWord(1.4, 2.0, "cantem")],
    )
    tail = LyricLine(
        time=9.0,
        text="No em fareu",
        words=[LyricWord(9.0, 9.3, "No"), LyricWord(9.3, 9.6, "em"), LyricWord(9.6, 10.0, "fareu")],
    )
    anchor = 2.0

    def fake_extract(path, start):
        assert path == audio
        assert start == pytest.approx(anchor - RESUME_CLIP_PAD)
        return path

    def fake_transcribe(path, **_kwargs):
        # Just inside the locked phrase, then the real continuation.
        return [
            AsrWord("cantem", 0.05, 0.20),
            AsrWord("No", 0.31, 0.60),
            AsrWord("em", 0.60, 0.90),
            AsrWord("fareu", 0.90, 1.40),
        ]

    def fake_refine(path, lines):
        assert path == audio
        return lines

    monkeypatch.setattr("karaoke_party.align._extract_audio_from", fake_extract)
    monkeypatch.setattr("karaoke_party.align.transcribe_words", fake_transcribe)
    monkeypatch.setattr("karaoke_party.align.refine_syllable_timings", fake_refine)

    result = align_from_anchor(audio, [prefix, tail], from_line=0, language="ca")

    assert result[0].words[0].time == pytest.approx(1.0)
    assert result[0].words[1].end == pytest.approx(2.0)
    assert result[1].text == "No em fareu"
    assert result[1].words[0].time >= anchor - 0.02
    assert [word.text for word in result[1].words] == ["No", "em", "fareu"]
    assert result[1].words[0].time == pytest.approx(anchor)


def test_align_from_anchor_rejects_a_missing_tail(tmp_path) -> None:
    audio = tmp_path / "vocals.wav"
    audio.write_bytes(b"x")
    only = LyricLine(time=1.0, text="Avui", words=[LyricWord(1.0, 1.4, "Avui")])
    with pytest.raises(AlignmentError):
        align_from_anchor(audio, [only], from_line=0)


def test_align_from_anchor_errors_when_the_tail_is_silent(tmp_path, monkeypatch) -> None:
    audio = tmp_path / "vocals.wav"
    audio.write_bytes(b"x")
    lines = [
        LyricLine(time=1.0, text="Avui", words=[LyricWord(1.0, 2.0, "Avui")]),
        LyricLine(time=0.0, text="Després", words=[]),
    ]
    monkeypatch.setattr("karaoke_party.align._extract_audio_from", lambda _path, _start: audio)
    monkeypatch.setattr("karaoke_party.align.transcribe_words", lambda *_args, **_kwargs: [])
    with pytest.raises(AlignmentError):
        align_from_anchor(audio, lines, from_line=0)


def test_clip_offset_is_applied_only_when_times_fit_the_trimmed_file() -> None:
    relative = [AsrWord("no", 1.0, 1.4)]
    shifted = _offset_if_clip_relative(relative, clip_start=50.0, clip_duration=10.0)
    assert shifted[0].start == pytest.approx(51.0)

    already_absolute = [AsrWord("no", 60.0, 61.0)]
    kept = _offset_if_clip_relative(already_absolute, clip_start=50.0, clip_duration=10.0)
    assert kept[0].start == pytest.approx(60.0)


def test_align_from_anchor_does_not_slide_a_matched_line_when_the_opener_is_missing(
    tmp_path, monkeypatch
) -> None:
    audio = tmp_path / "vocals.wav"
    audio.write_bytes(b"x")
    prefix = LyricLine(time=8.0, text="Avui", words=[LyricWord(8.0, 10.0, "Avui")])
    tail = [
        LyricLine(time=0.0, text="qqqq qqqq", words=[]),
        LyricLine(time=0.0, text="casa meva", words=[]),
    ]

    def fake_transcribe(_path, **_kwargs):
        # Relative to the clip, just after the anchor. "qqqq" is not in the audio.
        return [
            AsrWord("casa", RESUME_CLIP_PAD + 0.4, RESUME_CLIP_PAD + 0.8),
            AsrWord("meva", RESUME_CLIP_PAD + 0.8, RESUME_CLIP_PAD + 1.3),
        ]

    monkeypatch.setattr("karaoke_party.align._extract_audio_from", lambda _path, _start: audio)
    monkeypatch.setattr("karaoke_party.align.transcribe_words", fake_transcribe)
    monkeypatch.setattr("karaoke_party.align.refine_syllable_timings", lambda _path, lines: lines)

    result = align_from_anchor(audio, [prefix, *tail], from_line=0, language="ca")
    casa = result[2]
    assert casa.text == "casa meva"
    assert casa.words[0].time == pytest.approx(10.4, abs=0.15)
    assert casa.words[0].time < 12.0
    assert result[1].words[0].time >= 10.0 - 0.05
    assert result[1].words[-1].end <= casa.words[0].time + 0.05


def test_align_from_anchor_rejects_a_match_a_minute_after_the_anchor(tmp_path, monkeypatch) -> None:
    audio = tmp_path / "vocals.wav"
    audio.write_bytes(b"x")
    prefix = LyricLine(time=10.0, text="Avui", words=[LyricWord(10.0, 14.0, "Avui")])
    tail = LyricLine(time=0.0, text="Plantem les tovalloles", words=[])

    def fake_transcribe(_path, **_kwargs):
        # The only copy is a later chorus, about a minute after the anchor.
        return [
            AsrWord("Plantem", RESUME_CLIP_PAD + 60.0, RESUME_CLIP_PAD + 60.6),
            AsrWord("les", RESUME_CLIP_PAD + 60.6, RESUME_CLIP_PAD + 60.9),
            AsrWord("tovalloles", RESUME_CLIP_PAD + 60.9, RESUME_CLIP_PAD + 61.6),
        ]

    monkeypatch.setattr("karaoke_party.align._extract_audio_from", lambda _path, _start: audio)
    monkeypatch.setattr("karaoke_party.align.transcribe_words", fake_transcribe)
    monkeypatch.setattr("karaoke_party.align.refine_syllable_timings", lambda _path, lines: lines)

    with pytest.raises(AlignmentError):
        align_from_anchor(audio, [prefix, tail], from_line=0, language="ca")


def test_align_from_anchor_follows_a_long_line_across_a_break(tmp_path, monkeypatch) -> None:
    audio = tmp_path / "vocals.wav"
    audio.write_bytes(b"x")
    prefix = LyricLine(time=10.0, text="Avui", words=[LyricWord(10.0, 14.0, "Avui")])
    tail = LyricLine(time=0.0, text="Aixi doncs si un dia vens i passes", words=[])
    spoken = ["Aixi", "doncs", "si", "un", "dia", "vens", "i", "passes"]

    def fake_transcribe(_path, **_kwargs):
        # Forty seconds after the anchor: an instrumental, then the real line.
        start = RESUME_CLIP_PAD + 40.0
        words = []
        for index, text in enumerate(spoken):
            words.append(AsrWord(text, start + index * 0.4, start + index * 0.4 + 0.35))
        return words

    monkeypatch.setattr("karaoke_party.align._extract_audio_from", lambda _path, _start: audio)
    monkeypatch.setattr("karaoke_party.align.transcribe_words", fake_transcribe)
    monkeypatch.setattr("karaoke_party.align.refine_syllable_timings", lambda _path, lines: lines)

    result = align_from_anchor(audio, [prefix, tail], from_line=0, language="ca")
    # clip_start + relative = (14 - pad) + (pad + 40) = 54
    assert result[1].words[0].time == pytest.approx(54.0, abs=0.2)
    assert result[1].words[0].time > 14.0 + 18.0


def test_align_from_anchor_rejects_a_short_line_a_long_way_after_the_anchor(
    tmp_path, monkeypatch
) -> None:
    audio = tmp_path / "vocals.wav"
    audio.write_bytes(b"x")
    prefix = LyricLine(time=10.0, text="Avui", words=[LyricWord(10.0, 14.0, "Avui")])
    tail = LyricLine(time=0.0, text="Al mar", words=[])

    def fake_transcribe(_path, **_kwargs):
        return [
            AsrWord("Al", RESUME_CLIP_PAD + 40.0, RESUME_CLIP_PAD + 40.3),
            AsrWord("mar", RESUME_CLIP_PAD + 40.3, RESUME_CLIP_PAD + 40.8),
        ]

    monkeypatch.setattr("karaoke_party.align._extract_audio_from", lambda _path, _start: audio)
    monkeypatch.setattr("karaoke_party.align.transcribe_words", fake_transcribe)
    monkeypatch.setattr("karaoke_party.align.refine_syllable_timings", lambda _path, lines: lines)

    with pytest.raises(AlignmentError):
        align_from_anchor(audio, [prefix, tail], from_line=0, language="ca")


def test_align_from_anchor_does_not_invent_a_long_unmatched_ending(tmp_path, monkeypatch) -> None:
    audio = tmp_path / "vocals.wav"
    audio.write_bytes(b"x")
    prefix = LyricLine(time=8.0, text="Avui", words=[LyricWord(8.0, 10.0, "Avui")])
    tail = [
        LyricLine(time=0.0, text="casa meva", words=[]),
        LyricLine(time=0.0, text="bona nit", words=[]),
        LyricLine(time=0.0, text="hola amic", words=[]),
        LyricLine(time=0.0, text="qqqq qqqq", words=[]),
        LyricLine(time=0.0, text="zzzz zzzz", words=[]),
        LyricLine(time=0.0, text="wwww wwww", words=[]),
    ]

    def fake_transcribe(_path, **_kwargs):
        start = RESUME_CLIP_PAD + 0.4
        spoken = ["casa", "meva", "bona", "nit", "hola", "amic"]
        return [
            AsrWord(text, start + index * 0.4, start + index * 0.4 + 0.35)
            for index, text in enumerate(spoken)
        ]

    monkeypatch.setattr("karaoke_party.align._extract_audio_from", lambda _path, _start: audio)
    monkeypatch.setattr("karaoke_party.align.transcribe_words", fake_transcribe)
    monkeypatch.setattr("karaoke_party.align.refine_syllable_timings", lambda _path, lines: lines)

    with pytest.raises(AlignmentError):
        align_from_anchor(audio, [prefix, *tail], from_line=0, language="ca")
