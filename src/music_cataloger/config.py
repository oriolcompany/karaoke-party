from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class StructureProfile:
    """Describes how to interpret the library tree before consulting MusicBrainz."""

    name: str
    artist_from_level: int | None = 0
    album_from_level: int | None = 1
    infer_year_from_folders: bool = True
    mixed_artist_files: bool = False
    skip_dir_names: set[str] = field(
        default_factory=lambda: {
            "images",
            "fotos",
            "covers",
            "artwork",
            "scans",
            "extra",
            "extras",
            "videos",
        }
    )


@dataclass(slots=True)
class CatalogerConfig:
    root: Path
    write: bool = False
    rename_files: bool = False
    use_musicbrainz: bool = True
    use_acoustid: bool = False
    acoustid_api_key: str = ""
    acoustid_score_threshold: float = 0.3
    only_incomplete: bool = False
    ignore_existing_tags: bool = False
    limit: int = 0
    artist_filter: str | None = None
    report_path: Path | None = None
    audio_extensions: set[str] = field(
        default_factory=lambda: {".mp3", ".wma", ".m4a", ".flac", ".ogg", ".wav", ".aac", ".opus"}
    )
    artist_aliases: dict[str, str] = field(default_factory=dict)
    profiles: list[StructureProfile] = field(
        default_factory=lambda: [
            StructureProfile(name="artist/album/file", artist_from_level=0, album_from_level=1),
            StructureProfile(name="artist/file", artist_from_level=0, album_from_level=None),
            StructureProfile(name="album/file", artist_from_level=None, album_from_level=0),
            StructureProfile(
                name="mixed-file-pool",
                artist_from_level=None,
                album_from_level=None,
                mixed_artist_files=True,
            ),
        ]
    )

