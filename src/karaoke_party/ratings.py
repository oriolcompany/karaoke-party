"""User star ratings for songs.

Stored at the app cache root (not inside ``tracks/<key>/``) so clearing lyrics,
Whisper, stems, covers, or YouTube cache does not wipe scores.
Keys are the same ``cache_key(artist, title, duration)`` used for song folders.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

from .config import app_cache_root

RATINGS_NAME = "ratings.json"
MIN_RATING = 0
MAX_RATING = 5

_lock = threading.Lock()


def ratings_path() -> Path:
    return app_cache_root() / RATINGS_NAME


def normalize_rating(value: object) -> int:
    try:
        rating = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise ValueError("La puntuació ha de ser un enter") from None
    if isinstance(value, bool) or rating < MIN_RATING or rating > MAX_RATING:
        raise ValueError(f"La puntuació ha de ser entre {MIN_RATING} i {MAX_RATING}")
    return rating


def load_ratings() -> dict[str, int]:
    path = ratings_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    out: dict[str, int] = {}
    for raw_key, raw_value in data.items():
        key = str(raw_key).strip()
        if not key:
            continue
        try:
            rating = normalize_rating(raw_value)
        except ValueError:
            continue
        if rating > MIN_RATING:
            out[key] = rating
    return out


def get_rating(key: str, ratings: dict[str, int] | None = None) -> int:
    table = ratings if ratings is not None else load_ratings()
    try:
        return normalize_rating(table.get(str(key).strip(), 0))
    except ValueError:
        return 0


def set_rating(key: str, rating: int) -> int:
    key = str(key).strip()
    if not key:
        raise ValueError("Falta la clau de la cançó")
    value = normalize_rating(rating)
    with _lock:
        table = load_ratings()
        if value == MIN_RATING:
            table.pop(key, None)
        else:
            table[key] = value
        path = ratings_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(table, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        tmp.replace(path)
    return value
