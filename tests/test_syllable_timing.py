"""Hand-tuned syllable times must be validated on save and never re-estimated."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi import HTTPException

from karaoke_party import app as party_app
from karaoke_party.app import SaveTimingBody, TimingLineBody, TimingWordBody
from karaoke_party.library import TrackInfo
from karaoke_party.lyrics import (
    ALIGNED_CACHE_VERSION,
    LyricLine,
    LyricsPayload,
    LyricWord,
    cache_key,
    load_aligned_cached,
    save_aligned_cached,
)
from karaoke_party.track_cache import aligned_path

TRACK = TrackInfo(
    id="song",
    path="/tmp/song.mp3",
    relpath="song.mp3",
    title="Cançó",
    artist="Artista",
    album="Àlbum",
    duration=180.0,
)
TRACK_KEY = cache_key(TRACK.artist, TRACK.title, TRACK.duration)


@pytest.fixture
def aligned_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "tracks"
    root.mkdir()
    monkeypatch.setattr(party_app, "aligned_cache_dir", lambda _root=None: root)
    monkeypatch.setattr(party_app, "_tracks", {TRACK.id: TRACK})
    monkeypatch.setattr(party_app, "_music_root", None)
    return root


def _word(time: float, end: float, text: str, glue: bool = False) -> TimingWordBody:
    return TimingWordBody(time=time, end=end, text=text, glue=glue)


def _body(lines: list[TimingLineBody]) -> SaveTimingBody:
    return SaveTimingBody(track_id=TRACK.id, lines=lines)


def test_save_timing_derives_line_time_from_first_syllable(aligned_root: Path) -> None:
    body = _body(
        [
            TimingLineBody(
                text="Brindar",
                words=[_word(4.2, 4.5, "brin", glue=True), _word(4.5, 5.0, "dar")],
            )
        ]
    )

    response = party_app.save_lyrics_timing(body)

    assert response["aligned"] is True
    assert response["manual"] is True
    assert response["lines"][0]["time"] == pytest.approx(4.2)
    stored = json.loads(aligned_path(aligned_root, TRACK_KEY).read_text(encoding="utf-8"))
    assert stored["manual_edit"] is True
    assert stored["lines"][0]["words"][0]["glue"] is True


def test_save_timing_builds_line_text_from_glued_syllables(aligned_root: Path) -> None:
    body = _body(
        [
            TimingLineBody(
                words=[
                    _word(1.0, 1.2, "bri", glue=True),
                    _word(1.2, 1.5, "sa"),
                    _word(1.6, 2.0, "nova"),
                ]
            )
        ]
    )

    response = party_app.save_lyrics_timing(body)

    assert response["lines"][0]["text"] == "brisa nova"


@pytest.mark.parametrize(
    ("lines", "message"),
    [
        ([TimingLineBody(text="Buida", words=[])], "no té cap síl·laba"),
        ([TimingLineBody(words=[_word(-1.0, 0.5, "hola")])], "negatiu"),
        ([TimingLineBody(words=[_word(2.0, 1.0, "hola")])], "abans de començar"),
        (
            [TimingLineBody(words=[_word(5.0, 5.4, "dos"), _word(1.0, 1.4, "un")])],
            "no van en ordre",
        ),
        ([TimingLineBody(words=[_word(900.0, 900.5, "tard")])], "fora de la durada"),
    ],
)
def test_save_timing_rejects_broken_input(
    aligned_root: Path, lines: list[TimingLineBody], message: str
) -> None:
    with pytest.raises(HTTPException) as excinfo:
        party_app.save_lyrics_timing(_body(lines))

    assert excinfo.value.status_code == 400
    assert message in excinfo.value.detail
    assert not aligned_path(aligned_root, TRACK_KEY).exists()


def test_manual_alignment_survives_a_cache_version_bump(aligned_root: Path) -> None:
    payload = LyricsPayload(
        synced=True,
        source="manual-sync",
        lines=[LyricLine(time=1.0, text="Hola", words=[LyricWord(1.0, 1.4, "Hola")])],
        manual=True,
    )
    save_aligned_cached(aligned_root, TRACK_KEY, payload)
    path = aligned_path(aligned_root, TRACK_KEY)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["align_version"] = ALIGNED_CACHE_VERSION - 1
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    loaded = load_aligned_cached(aligned_root, TRACK_KEY)

    assert loaded is not None
    assert loaded.manual is True


def test_stale_whisper_alignment_is_still_discarded(aligned_root: Path) -> None:
    payload = LyricsPayload(
        synced=True,
        source="whisper-align",
        lines=[LyricLine(time=1.0, text="Hola", words=[LyricWord(1.0, 1.4, "Hola")])],
    )
    save_aligned_cached(aligned_root, TRACK_KEY, payload)
    path = aligned_path(aligned_root, TRACK_KEY)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["align_version"] = ALIGNED_CACHE_VERSION - 1
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    assert load_aligned_cached(aligned_root, TRACK_KEY) is None


def test_manual_alignment_keeps_its_onsets(aligned_root: Path) -> None:
    # A long single-letter pickup is exactly what tighten_phrase_onsets rewrites.
    pickup = LyricWord(time=2.0, end=3.4, text="Un", glue=False)
    payload = LyricsPayload(
        synced=True,
        source="manual-sync",
        lines=[
            LyricLine(
                time=2.0,
                text="Un dia",
                words=[pickup, LyricWord(time=3.4, end=3.9, text="dia")],
            )
        ],
        manual=True,
    )
    save_aligned_cached(aligned_root, TRACK_KEY, payload)

    loaded = load_aligned_cached(aligned_root, TRACK_KEY)

    assert loaded is not None
    assert loaded.lines[0].words[0].time == pytest.approx(2.0)
    assert loaded.lines[0].time == pytest.approx(2.0)


def test_manual_payload_is_not_re_aligned_or_re_split() -> None:
    lines = [
        LyricLine(
            time=1.0,
            text="Brindar",
            words=[LyricWord(time=1.0, end=2.0, text="Brindar")],
        )
    ]
    payload = LyricsPayload(synced=True, source="manual-sync", lines=lines, manual=True)

    assert party_app._with_audio_syllables(TRACK_KEY, payload) is payload
    served = party_app._lines_for_client(lines, manual=True)
    assert [word["text"] for word in served[0]["words"]] == ["Brindar"]


def test_whisper_payload_without_glue_is_still_split_for_the_client() -> None:
    lines = [
        LyricLine(
            time=1.0,
            text="Brindar",
            words=[LyricWord(time=1.0, end=2.0, text="Brindar")],
        )
    ]

    served = party_app._lines_for_client(lines)

    assert len(served[0]["words"]) > 1
