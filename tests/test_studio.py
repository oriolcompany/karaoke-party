from __future__ import annotations

import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from karaoke_party.studio import bind_library, router


def _client(root: Path | None = None) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    bind_library(root_getter=lambda: root, reload_library=lambda _path: None)
    return TestClient(app)


def test_catalog_lists_the_karaoke_folder(tmp_path: Path) -> None:
    song = tmp_path / "Artist" / "Album" / "Song.mp3"
    song.parent.mkdir(parents=True)
    song.write_bytes(b"not-a-real-mp3")
    other = tmp_path / "other"
    other.mkdir()
    response = _client(tmp_path).get("/api/studio/catalog/tracks", params={"root": str(other)})
    assert response.status_code == 200
    body = response.json()
    assert body["root"] == str(tmp_path.resolve())
    assert body["count"] == 1
    assert body["tracks"][0]["rel"] == "Artist/Album/Song.mp3"
    assert body["tracks"][0]["title"] == "Song"


def test_catalog_rejects_path_escape(tmp_path: Path) -> None:
    response = _client(tmp_path).get(
        "/api/studio/catalog/cover",
        params={"rel": "../outside.mp3"},
    )
    assert response.status_code == 400


def test_catalog_run_on_empty_folder(tmp_path: Path) -> None:
    client = _client(tmp_path)
    started = client.post(
        "/api/studio/catalog/run",
        json={
            "write": False,
            "use_musicbrainz": False,
            "use_acoustid": False,
        },
    )
    assert started.status_code == 200
    job_id = started.json()["job_id"]
    status = {"status": "running"}
    for _ in range(50):
        status = client.get(f"/api/studio/catalog/run/{job_id}").json()
        if status["status"] in {"done", "error"}:
            break
        time.sleep(0.05)
    assert status["status"] == "done"
    assert status["error"] == ""


def test_download_rejects_unknown_quality() -> None:
    response = _client().post(
        "/api/studio/yt/download",
        json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "quality": "4k"},
    )
    assert response.status_code == 400


def test_catalog_settings_do_not_require_a_library(tmp_path: Path, monkeypatch) -> None:
    import music_cataloger.settings as settings

    monkeypatch.setattr(settings, "settings_path", lambda: tmp_path / "settings.json")
    response = _client().get("/api/studio/catalog/settings")
    assert response.status_code == 200
    body = response.json()
    assert body["acoustid_configured"] is False
    assert body["fpcalc_ready"] is True
