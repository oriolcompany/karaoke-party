"""Hand-tuned syllable times must be validated on save and never re-estimated."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi import HTTPException

from karaoke_party import app as party_app
from karaoke_party.app import (
    ResyncFromBody,
    ResyncLineBody,
    ResyncWordBody,
    RetimeLineBody,
    SaveTimingBody,
    TimingLineBody,
    TimingWordBody,
)
from karaoke_party.library import TrackInfo
from karaoke_party.lyrics import (
    ALIGNED_CACHE_VERSION,
    LyricLine,
    LyricsPayload,
    LyricWord,
    cache_key,
    load_aligned_cached,
    load_cached,
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


def _resync_body(from_line: int, lines: list[ResyncLineBody]) -> ResyncFromBody:
    return ResyncFromBody(track_id=TRACK.id, from_line=from_line, lines=lines)


def test_resync_requires_a_following_line(aligned_root: Path) -> None:
    body = _resync_body(
        0,
        [ResyncLineBody(text="Només", words=[ResyncWordBody(time=1.0, end=1.4, text="Només")])],
    )
    with pytest.raises(HTTPException) as exc:
        party_app.start_align_from(body)
    assert exc.value.status_code == 400


def test_resync_requires_the_anchor_to_be_placed(aligned_root: Path) -> None:
    body = _resync_body(
        0,
        [
            ResyncLineBody(text="Avui", words=[ResyncWordBody(text="Avui")]),
            ResyncLineBody(text="Després", words=[ResyncWordBody(text="Després")]),
        ],
    )
    with pytest.raises(HTTPException) as exc:
        party_app.start_align_from(body)
    assert exc.value.status_code == 400


def test_resync_enqueues_from_the_corrected_line(aligned_root: Path, monkeypatch) -> None:
    party_app._align_jobs.clear()
    monkeypatch.setattr(party_app, "alignment_available", lambda: True)
    monkeypatch.setattr(party_app, "separation_available", lambda: True)
    monkeypatch.setattr(party_app, "whisper_model_status", lambda: {"ready": True, "error": ""})
    captured: dict = {}

    def fake_enqueue(job_id, track, language, *, from_line=None, lines=None):
        captured["job_id"] = job_id
        captured["language"] = language
        captured["from_line"] = from_line
        captured["lines"] = lines

    monkeypatch.setattr(party_app, "_enqueue_align_job", fake_enqueue)
    body = _resync_body(
        0,
        [
            ResyncLineBody(
                text="Avui",
                words=[
                    ResyncWordBody(time=1.0, end=1.4, text="A", glue=True),
                    ResyncWordBody(time=1.4, end=2.0, text="vui"),
                ],
            ),
            ResyncLineBody(text="Després ve la resta", words=[ResyncWordBody(text="Després")]),
        ],
    )

    response = party_app.start_align_from(body)

    assert response["status"] == "queued"
    assert response["job_id"] == captured["job_id"]
    assert captured["from_line"] == 0
    assert captured["language"] == "ca"
    assert captured["lines"][0].words[0].time == pytest.approx(1.0)
    assert captured["lines"][0].words[0].glue is True
    assert captured["lines"][1].text == "Després ve la resta"
    assert captured["lines"][1].words == []


def test_retime_endpoint_keeps_unchanged_syllables() -> None:
    body = RetimeLineBody(
        text="casa,",
        floor=0.0,
        ceiling=4.0,
        words=[
            ResyncWordBody(time=1.0, end=1.4, text="ca", glue=True),
            ResyncWordBody(time=1.4, end=1.8, text="sa"),
        ],
    )
    payload = party_app.retime_lyric_line(body)
    assert payload["fit"] == "kept"
    assert payload["lines"][0]["words"][0]["time"] == pytest.approx(1.0)
    assert payload["lines"][0]["words"][1]["text"] == "sa,"


def test_retime_endpoint_inserts_unplaced_phrases() -> None:
    body = RetimeLineBody(text="una frase nova\ni una altra")
    payload = party_app.retime_lyric_line(body)
    assert payload["fit"] == "unplaced"
    assert len(payload["lines"]) == 2
    assert all(word["time"] is None for line in payload["lines"] for word in line["words"])


def test_retime_endpoint_rejects_blank_text() -> None:
    with pytest.raises(HTTPException) as exc:
        party_app.retime_lyric_line(RetimeLineBody(text="  \n"))
    assert exc.value.status_code == 400


def test_saving_edited_text_updates_lyrics_without_dropping_alignment(aligned_root: Path) -> None:
    party_app.save_lyrics_timing(
        _body(
            [
                TimingLineBody(
                    text="Brindar",
                    words=[_word(4.2, 4.5, "brin", glue=True), _word(4.5, 5.0, "dar")],
                )
            ]
        )
    )
    party_app.save_lyrics_timing(
        _body(
            [
                TimingLineBody(
                    text="Brindar fort",
                    words=[
                        _word(4.2, 4.5, "brin", glue=True),
                        _word(4.5, 5.0, "dar"),
                        _word(5.0, 5.4, "fort"),
                    ],
                )
            ]
        )
    )
    aligned = load_aligned_cached(aligned_root, TRACK_KEY)
    assert aligned is not None
    assert aligned.lines[0].text == "Brindar fort"
    cached = load_cached(party_app.cache_dir(), TRACK_KEY)
    assert cached is not None
    assert "Brindar fort" in cached.plain
