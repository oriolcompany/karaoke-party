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
