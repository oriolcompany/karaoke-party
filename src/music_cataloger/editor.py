"""Helpers for the Manual Edit GUI tab."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .tagger import TagCandidate

EDITABLE_FIELDS = ("track", "title", "artist", "album", "date", "albumartist", "file")
_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*]')


@dataclass
class EditorRow:
    path: Path
    tags: dict[str, str]
    original: dict[str, str] = field(default_factory=dict)
    dirty: bool = False
    error: str = ""
    cover_data: bytes | None = None
    cover_mime: str = ""
    cover_original_data: bytes | None = None
    cover_original_mime: str = ""
    # "" = unchanged, "set" = replace with cover_data, "remove" = strip cover
    cover_action: str = ""

    def __post_init__(self) -> None:
        self.tags.setdefault("file", self.path.name)
        if not self.original:
            self.original = dict(self.tags)
        if self.cover_original_data is None and self.cover_data is not None:
            self.cover_original_data = self.cover_data
            self.cover_original_mime = self.cover_mime

    def tags_changed(self) -> bool:
        return any(self.tags.get(key, "") != self.original.get(key, "") for key in EDITABLE_FIELDS)

    def cover_changed(self) -> bool:
        return self.cover_action in {"set", "remove"}

    def set_cover(self, data: bytes, mime: str) -> None:
        self.cover_data = data
        self.cover_mime = mime
        self.cover_action = "set"
        self.dirty = True

    def clear_cover(self) -> None:
        self.cover_data = None
        self.cover_mime = ""
        self.cover_action = "remove"
        self.dirty = True

    def revert_changes(self) -> None:
        self.tags = dict(self.original)
        self.cover_data = self.cover_original_data
        self.cover_mime = self.cover_original_mime
        self.cover_action = ""
        self.dirty = False
        self.error = ""

    def commit_baseline(self) -> None:
        """After a successful save, treat current state as the new original."""
        self.original = dict(self.tags)
        self.cover_original_data = self.cover_data
        self.cover_original_mime = self.cover_mime
        self.cover_action = ""
        self.dirty = False
        self.error = ""


def apply_cover_to_rows(rows: list[EditorRow], data: bytes, mime: str) -> int:
    changed = 0
    for row in rows:
        row.set_cover(data, mime)
        changed += 1
    return changed


def remove_cover_from_rows(rows: list[EditorRow]) -> int:
    changed = 0
    for row in rows:
        row.clear_cover()
        changed += 1
    return changed



def is_incomplete(tags: dict[str, str]) -> bool:
    return not all(tags.get(key) for key in ("title", "artist", "album", "date"))


def row_matches_filter(row: EditorRow, query: str, incomplete_only: bool) -> bool:
    if incomplete_only and not is_incomplete(row.tags):
        return False
    if not query:
        return True
    needle = query.casefold()
    haystack = " ".join(
        [
            row.tags.get("title", ""),
            row.tags.get("artist", ""),
            row.tags.get("album", ""),
            row.tags.get("albumartist", ""),
            row.tags.get("file", ""),
            row.path.name,
        ]
    ).casefold()
    return needle in haystack


def tags_to_candidate(tags: dict[str, str]) -> TagCandidate:
    return TagCandidate(
        title=tags.get("title", "").strip(),
        artist=tags.get("artist", "").strip(),
        album=tags.get("album", "").strip(),
        date=(tags.get("date", "") or "")[:4].strip(),
        track=tags.get("track", "").strip(),
        albumartist=tags.get("albumartist", "").strip(),
        source="manual-edit",
    )


def sanitize_filename(name: str, *, fallback_suffix: str = "") -> str:
    cleaned = name.replace("\\", "/").split("/")[-1].strip()
    cleaned = _INVALID_FILENAME_CHARS.sub("_", cleaned).strip(" .")
    if not cleaned:
        raise ValueError("El nom de fitxer no pot estar buit")
    if fallback_suffix and not Path(cleaned).suffix:
        cleaned = f"{cleaned}{fallback_suffix}"
    return cleaned


def rename_to_filename(path: Path, new_name: str) -> Path:
    """Rename ``path`` to ``new_name`` in the same folder. Returns the new path."""
    cleaned = sanitize_filename(new_name, fallback_suffix=path.suffix)
    dest = path.with_name(cleaned)
    if dest == path:
        return path
    if dest.exists():
        raise RuntimeError(f"Ja existeix un fitxer amb aquest nom: {dest.name}")
    path.rename(dest)
    return dest


def apply_field(rows: list[EditorRow], field_name: str, value: str) -> int:
    if field_name not in EDITABLE_FIELDS:
        raise ValueError(f"unsupported field: {field_name}")
    cleaned = value.strip()
    if field_name == "date":
        cleaned = cleaned[:4]
    elif field_name == "file":
        # Keep user text as-typed for the cell; sanitize on save.
        cleaned = value.replace("\\", "/").split("/")[-1].strip()
        if not cleaned:
            raise ValueError("El nom de fitxer no pot estar buit")
    changed = 0
    for row in rows:
        if field_name == "file":
            name = cleaned
            if not Path(name).suffix and row.path.suffix:
                name = f"{name}{row.path.suffix}"
            if row.tags.get("file", "") == name:
                continue
            row.tags["file"] = name
        else:
            if row.tags.get(field_name, "") == cleaned:
                continue
            row.tags[field_name] = cleaned
        row.dirty = True
        changed += 1
    return changed


def apply_bulk_fields(rows: list[EditorRow], updates: dict[str, str]) -> int:
    """Apply several field updates to every row. Returns rows that changed."""
    if not updates:
        return 0
    unknown = set(updates) - set(EDITABLE_FIELDS)
    if unknown:
        raise ValueError(f"unsupported field(s): {', '.join(sorted(unknown))}")
    changed_rows = 0
    for row in rows:
        before = dict(row.tags)
        for field_name, value in updates.items():
            apply_field([row], field_name, value)
        if row.tags != before:
            changed_rows += 1
    return changed_rows


def number_tracks(rows: list[EditorRow], start: int = 1) -> int:
    """Set sequential track numbers on rows (in the given order)."""
    if start < 0:
        raise ValueError("track start must be >= 0")
    changed = 0
    for offset, row in enumerate(rows):
        value = str(start + offset)
        if row.tags.get("track", "") == value:
            continue
        row.tags["track"] = value
        row.dirty = True
        changed += 1
    return changed
