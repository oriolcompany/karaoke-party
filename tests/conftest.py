from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_cache_root(tmp_path_factory, monkeypatch) -> Path:
    """Keep every test out of the real per-user cache.

    Helpers such as ``_reload_library`` write to ``app_cache_root()``, which
    otherwise wipes the music folder the user last opened.
    """
    root = tmp_path_factory.mktemp("karaoke-cache")
    monkeypatch.setenv("KARAOKE_CACHE_DIR", str(root))
    return root
