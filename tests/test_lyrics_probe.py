"""Regression: lyrics probe must not restart forever when fetches fail."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import AsyncMock, patch

from karaoke_party.library import TrackInfo
from karaoke_party import app as party_app
from karaoke_party.lyrics import LyricsUnavailable, cache_key, load_cached


def _track(track_id: str, title: str = "Song") -> TrackInfo:
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
        "a": _track("a", "One"),
        "b": _track("b", "Two"),
    }
    party_app._probe_thread = None
    party_app._reset_probe_state()


def test_probe_marks_failed_tracks_so_library_stops_restarting(tmp_path: Path, monkeypatch) -> None:
    lyrics = tmp_path / "lyrics"
    aligned = tmp_path / "aligned"
    lyrics.mkdir()
    aligned.mkdir()
    monkeypatch.setattr(party_app, "cache_dir", lambda _root=None: lyrics)
    monkeypatch.setattr(party_app, "aligned_cache_dir", lambda _root=None: aligned)

    with patch(
        "karaoke_party.app.fetch_lyrics",
        new=AsyncMock(side_effect=RuntimeError("lrclib down")),
    ):
        party_app._probe_state.update({"running": True, "done": 0, "total": 2, "found": 0})
        gen = party_app._probe_generation
        party_app._probe_attempted.update({"a", "b"})
        party_app._run_lyrics_probe(["a", "b"], gen)

    assert party_app._probe_state["running"] is False
    assert party_app._probe_pass_complete is True
    assert party_app._probe_attempted == {"a", "b"}

    for title in ("One", "Two"):
        key = cache_key("Artist", title, 180.0)
        cached = load_cached(lyrics, key)
        assert cached is not None
        assert cached.lines == []
        assert cached.source == "probe-error"

    snap = party_app._library_snapshot()
    assert snap["pending"] == 0
    assert snap["hidden"] == 2

    party_app._ensure_lyrics_probe()
    assert party_app._probe_state["running"] is False
    assert party_app._probe_state["total"] == 2


def test_ensure_claims_running_under_lock(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(party_app, "cache_dir", lambda _root=None: tmp_path / "lyrics")
    monkeypatch.setattr(party_app, "aligned_cache_dir", lambda _root=None: tmp_path / "aligned")
    (tmp_path / "lyrics").mkdir()
    (tmp_path / "aligned").mkdir()

    started = []

    class FakeThread:
        def __init__(self, target, args=(), daemon=None, name=None):
            self.target = target
            self.args = args
            self._alive = False

        def start(self):
            self._alive = True
            started.append(self.args[0])

        def is_alive(self):
            return self._alive

    monkeypatch.setattr(party_app.threading, "Thread", FakeThread)

    party_app._ensure_lyrics_probe()
    assert party_app._probe_state["running"] is True
    assert party_app._probe_state["total"] == 2
    assert len(started) == 1
    assert set(started[0]) == {"a", "b"}
    # Claimed up-front so pending cannot retrigger another pass.
    assert party_app._probe_attempted == {"a", "b"}

    party_app._ensure_lyrics_probe()
    assert len(started) == 1


def test_rescan_without_root_change_keeps_probe_progress(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "music"
    root.mkdir()
    monkeypatch.setattr(party_app, "scan_library", lambda _root: [_track("a"), _track("b")])

    party_app._music_root = root
    party_app._tracks = {"a": _track("a"), "b": _track("b")}
    with party_app._probe_lock:
        party_app._probe_attempted.update({"a", "b"})
        party_app._probe_pass_complete = True
        party_app._probe_state.update({"running": False, "done": 2, "total": 2, "found": 0})

    party_app._reload_library(root, reset_probe=False)
    assert party_app._probe_pass_complete is True
    assert party_app._probe_attempted == {"a", "b"}
    assert party_app._probe_state["done"] == 2

    party_app._ensure_lyrics_probe()
    assert party_app._probe_state["running"] is False


def test_offline_streak_finishes_pass_without_hammering_lrclib(tmp_path: Path, monkeypatch) -> None:
    lyrics = tmp_path / "lyrics"
    aligned = tmp_path / "aligned"
    lyrics.mkdir()
    aligned.mkdir()
    monkeypatch.setattr(party_app, "cache_dir", lambda _root=None: lyrics)
    monkeypatch.setattr(party_app, "aligned_cache_dir", lambda _root=None: aligned)
    monkeypatch.setattr(party_app, "OFFLINE_FAILURE_STREAK", 2)
    monkeypatch.setattr(party_app, "PROBE_CONCURRENCY", 1)

    party_app._tracks = {f"t{i}": _track(f"t{i}", f"Song {i}") for i in range(10)}
    calls = {"n": 0}

    async def always_down(**_kwargs):
        calls["n"] += 1
        raise LyricsUnavailable("down")

    track_ids = list(party_app._tracks)
    party_app._probe_state.update({"running": True, "done": 0, "total": len(track_ids), "found": 0})
    with patch("karaoke_party.app.fetch_lyrics", new=AsyncMock(side_effect=always_down)):
        party_app._run_lyrics_probe(track_ids, party_app._probe_generation)

    assert party_app._probe_state["done"] == len(track_ids)
    assert party_app._probe_state["offline"] is True
    # Stops calling out after the streak instead of timing out on every song.
    assert calls["n"] == 2

    snap = party_app._library_snapshot()
    assert snap["pending"] == 0
    assert snap["errors"] == len(track_ids)


def test_stale_generation_does_not_inflate_done(tmp_path: Path, monkeypatch) -> None:
    lyrics = tmp_path / "lyrics"
    aligned = tmp_path / "aligned"
    lyrics.mkdir()
    aligned.mkdir()
    monkeypatch.setattr(party_app, "cache_dir", lambda _root=None: lyrics)
    monkeypatch.setattr(party_app, "aligned_cache_dir", lambda _root=None: aligned)

    async def slow_fetch(**_kwargs):
        time.sleep(0.05)
        raise RuntimeError("boom")

    party_app._probe_state.update({"running": True, "done": 0, "total": 2, "found": 0})
    stale_gen = party_app._probe_generation
    party_app._reset_probe_state()  # invalidates stale_gen

    with patch("karaoke_party.app.fetch_lyrics", new=AsyncMock(side_effect=slow_fetch)):
        party_app._run_lyrics_probe(["a", "b"], stale_gen)

    assert party_app._probe_state["done"] == 0
    assert party_app._probe_pass_complete is False
