"""Per-album karaoke stage backdrops (1920×1080 stills)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .config import app_cache_root
from .library import album_group_key

BACKDROP_PREFIX = "backdrop"
META_NAME = "meta.json"
MAX_BYTES = 12 * 1024 * 1024
ALLOWED_MIME = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def album_backdrop_key(artist: str, album: str) -> str:
    return album_group_key(artist or "Artista desconegut", album or "Sense àlbum")


def album_backdrop_id(album_key: str) -> str:
    return hashlib.sha1((album_key or "").encode("utf-8")).hexdigest()


def album_backdrops_dir() -> Path:
    path = app_cache_root() / "album-backdrops"
    path.mkdir(parents=True, exist_ok=True)
    return path


def album_backdrop_folder(album_key: str) -> Path:
    return album_backdrops_dir() / album_backdrop_id(album_key)


def sniff_image_mime(data: bytes) -> str:
    if len(data) >= 8 and data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if len(data) >= 3 and data.startswith(b"\xff\xd8"):
        return "image/jpeg"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return ""


def find_album_backdrop(album_key: str) -> Path | None:
    folder = album_backdrop_folder(album_key)
    if not folder.is_dir():
        return None
    matches = sorted(folder.glob(f"{BACKDROP_PREFIX}.*"))
    if not matches:
        return None
    path = matches[0]
    return path if path.is_file() else None


def album_has_backdrop(album_key: str) -> bool:
    path = find_album_backdrop(album_key)
    return path is not None and path.stat().st_size > 0


def list_album_backdrop_keys() -> set[str]:
    keys: set[str] = set()
    root = album_backdrops_dir()
    if not root.is_dir():
        return keys
    for meta_path in root.glob(f"*/{META_NAME}"):
        try:
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        key = str(payload.get("album_key") or "").strip()
        if key and find_album_backdrop(key):
            keys.add(key)
    return keys


def save_album_backdrop(
    album_key: str,
    data: bytes,
    *,
    artist: str = "",
    album: str = "",
    mime: str = "",
) -> Path:
    if not album_key.strip():
        raise ValueError("Cal una clau d’àlbum")
    if not data:
        raise ValueError("La imatge és buida")
    if len(data) > MAX_BYTES:
        raise ValueError("La imatge és massa gran (màxim 12 MB)")
    sniffed = sniff_image_mime(data)
    if not sniffed:
        raise ValueError("Cal una imatge JPG, PNG o WebP")
    declared = (mime or "").lower()
    if declared in {"image/jpg", "image/jpeg"}:
        declared = "image/jpeg"
    if declared in ALLOWED_MIME and declared != sniffed:
        raise ValueError("El fitxer no coincideix amb el tipus d’imatge")
    suffix = ALLOWED_MIME[sniffed]
    folder = album_backdrop_folder(album_key)
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob(f"{BACKDROP_PREFIX}.*"):
        try:
            old.unlink()
        except OSError:
            continue
    path = folder / f"{BACKDROP_PREFIX}{suffix}"
    path.write_bytes(data)
    meta = {
        "album_key": album_key,
        "artist": artist or "",
        "album": album or "",
        "mime": sniffed,
    }
    (folder / META_NAME).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def delete_album_backdrop(album_key: str) -> bool:
    folder = album_backdrop_folder(album_key)
    if not folder.is_dir():
        return False
    removed = False
    for child in folder.iterdir():
        try:
            child.unlink()
            removed = True
        except OSError:
            continue
    try:
        folder.rmdir()
    except OSError:
        pass
    return removed
