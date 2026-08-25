from __future__ import annotations

from pathlib import Path

from karaoke_party.config import (
    default_music_root,
    load_last_music_root,
    save_last_music_root,
)


def test_save_and_load_last_music_root(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("KARAOKE_CACHE_DIR", str(tmp_path / "cache"))
    music = tmp_path / "songs"
    music.mkdir()
    save_last_music_root(music)
    loaded = load_last_music_root()
    assert loaded is not None
    assert loaded.resolve() == music.resolve()


def test_load_last_music_root_ignores_missing_folder(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("KARAOKE_CACHE_DIR", str(tmp_path / "cache"))
    gone = tmp_path / "gone"
    gone.mkdir()
    save_last_music_root(gone)
    gone.rmdir()
    assert load_last_music_root() is None


def test_default_music_root_prefers_cached_folder(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("KARAOKE_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.delenv("KARAOKE_MUSIC_ROOT", raising=False)
    music = tmp_path / "my-songs"
    music.mkdir()
    save_last_music_root(music)
    assert default_music_root().resolve() == music.resolve()


def test_default_music_root_prefers_env_over_cache(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("KARAOKE_CACHE_DIR", str(tmp_path / "cache"))
    cached = tmp_path / "cached-songs"
    cached.mkdir()
    save_last_music_root(cached)
    env_music = tmp_path / "env-songs"
    env_music.mkdir()
    monkeypatch.setenv("KARAOKE_MUSIC_ROOT", str(env_music))
    assert Path(default_music_root()) == env_music
