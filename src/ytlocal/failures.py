"""Persistent log of failed downloads."""

from __future__ import annotations

import json
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from ytlocal.error_messages import (
    clean_error,
    display_title,
    enrich_failure,
    format_error_with_title,
    youtube_watch_url,
)
from ytlocal.paths import data_dir


_lock = threading.Lock()


def failures_file() -> Path:
    return data_dir() / "failed.json"


def _read() -> list[dict[str, Any]]:
    path = failures_file()
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def _write(items: list[dict[str, Any]]) -> None:
    path = failures_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def list_failures() -> list[dict[str, Any]]:
    with _lock:
        items = _read()
    items.sort(key=lambda x: x.get("created_at") or 0, reverse=True)
    return [enrich_failure(item) for item in items]


def add_failure(
    *,
    title: str,
    url: str,
    error: str,
    mode: str = "audio",
    quality: str = "best",
    kind: str = "single",
    playlist_title: str | None = None,
) -> dict[str, Any]:
    cleaned = clean_error(error)
    watch = youtube_watch_url(url, title) or url
    record = {
        "id": uuid.uuid4().hex,
        "title": display_title(title, watch, playlist_title),
        "url": watch or url,
        "error": cleaned,
        "reason": format_error_with_title(cleaned, title, watch, playlist_title),
        "mode": mode,
        "quality": quality,
        "kind": kind,
        "playlist_title": playlist_title,
        "created_at": time.time(),
    }
    with _lock:
        items = _read()
        # Keep newest first, cap history.
        items.insert(0, record)
        _write(items[:500])
    return enrich_failure(record)


def remove_failure(failure_id: str) -> bool:
    with _lock:
        items = _read()
        next_items = [item for item in items if item.get("id") != failure_id]
        if len(next_items) == len(items):
            return False
        _write(next_items)
        return True


def clear_failures() -> int:
    with _lock:
        items = _read()
        _write([])
        return len(items)


def get_failure(failure_id: str) -> dict[str, Any] | None:
    with _lock:
        for item in _read():
            if item.get("id") == failure_id:
                return enrich_failure(item)
    return None
