"""Bulk instrumental generation must include songs without lyrics."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from karaoke_party import app as party_app
from karaoke_party.library import TrackInfo


def _track(track_id: str, title: str) -> TrackInfo:
    return TrackInfo(
        id=track_id,
        path=f"/tmp/{track_id}.mp3",
        relpath=f"{track_id}.mp3",
        title=title,
        artist="Artist",
        album="Album",
        duration=180.0,
    )


def setup_function() -> None:
    party_app._music_root = Path("/tmp/music")
    party_app._tracks = {
        "with-lyrics": _track("with-lyrics", "Has Lyrics"),
        "no-lyrics": _track("no-lyrics", "No Lyrics"),
    }
    party_app._stem_jobs.clear()
    party_app._stem_queue.clear()
    party_app._stem_bulk_state.update(
        {
            "running": False,
            "done": 0,
            "total": 0,
            "failed": 0,
            "current": "",
            "error": "",
        }
    )


def test_generate_library_stems_includes_songs_without_lyrics() -> None:
    queued: list[str] = []

    def _fake_enqueue(job_id, track, *, front=False):
        queued.append(track.id)

    with (
        patch.object(party_app, "separation_available", return_value=True),
        patch.object(party_app, "has_instrumental", return_value=False),
        patch.object(party_app, "_enqueue_stem_job", side_effect=_fake_enqueue),
        patch.object(
            party_app,
            "_library_snapshot",
            return_value={"tracks": [{"id": "with-lyrics"}]},
        ),
    ):
        result = party_app.generate_library_stems()

    assert result["queued"] == 2
    assert result["running"] is True
    assert queued == ["with-lyrics", "no-lyrics"]
