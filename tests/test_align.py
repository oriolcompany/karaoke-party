from karaoke_party.align import AsrWord, align_line_words, align_tokens_globally
from karaoke_party.lyrics import LyricLine


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
