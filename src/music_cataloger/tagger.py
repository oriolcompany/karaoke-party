from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from collections.abc import Callable, Sequence
from typing import Any

from mutagen import File as MutagenFile
from mutagen.asf import ASF
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4

from .acoustid_client import AcoustIDClient
from .config import CatalogerConfig, StructureProfile
from .covers import lookup_itunes_metadata

MULTI_SPACE_RE = re.compile(r"\s+")
YEAR_RE = re.compile(r"(19\d{2}|20\d{2})")
TRACK_PREFIX_RE = re.compile(
    r"^(?:(?P<disc>\d+)\s*[-.])?\s*(?P<track>\d{1,3})\s*[-./)\s]+\s*(?P<title>.+)$"
)
RANGE_YEAR_RE = re.compile(r"(?P<y1>19\d{2})\s*[-–—]\s*(?P<y2>19\d{2}|20\d{2})")
BRACKETY_JUNK_RE = re.compile(
    r"\s*[\(\[\{][^)\]\}]*(?:lp|ep|cd|album|disc|completo?|complet|live|remaster(?:ed)?|"
    r"explicit|deluxe|edition|version|single|oficial|official|videoclip|lyric\s*video|"
    r"official\s*(?:video|audio|lyric(?:s)?(?:\s*video)?)?|audio\s*oficial|"
    r"v[ií]deo\s*oficial|with\s*lyrics|sub(?:titulad[oa]s?)?|visualizer|"
    r"prod(?:uced)?\.?\s*by|bonus\s*track|radio\s*edit|tema\s*oficial|"
    r"\bhd\b|\bhq\b|\b4k\b|lyrics?)"
    r"[^)\]\}]*[\)\]\}]\s*",
    re.I,
)
# Free-standing download noise outside brackets: "Song Official Video", "Song | Lyrics"
TITLE_NOISE_FREE_RE = re.compile(
    r"(?i)(?:^|[\s\-_|/]+)"
    r"(?:official(?:\s*(?:music\s*)?(?:video|audio|lyric(?:s)?(?:\s*video)?))?|"
    r"videoclip|audio\s*oficial|v[ií]deo\s*oficial|lyric(?:s)?(?:\s*video)?|"
    r"with\s*lyrics|visualizer|tema\s*oficial|\bhd\b|\bhq\b|\b4k\b)"
    r"(?=[\s\-_|/]+|$)"
)
FEAT_TAIL_RE = re.compile(
    r"(?i)\s+(?:feat\.?|ft\.?|featuring)\s+.+$"
)
LEADING_TRACK_RE = re.compile(
    r"^(?:(?P<disc>\d+)\s*[-.])?\s*(?P<track>\d{1,3})\s*[-./)\s]+\s*(?P<title>.+)$"
)
BAD_ALBUM_RE = re.compile(r"^(unknown|misc|various|music|songs?|tracks?)$", re.I)

# Downloaders append the source video id and sometimes truncate the name mid-id.
VIDEO_ID_TAIL_RE = re.compile(r"\s*\[(?P<id>[A-Za-z0-9_\- ]{11})\]\s*$")
TRUNCATED_BRACKET_TAIL_RE = re.compile(r"\s*\[[A-Za-z0-9_\- ]{0,11}$")
TRUNCATED_PAREN_TAIL_RE = re.compile(r"\s*\([^)]*$")
QUOTED_ALBUM_RE = re.compile(r"^(?P<artist>[^_]{2,60}?)\s*_(?P<album>[^_]+)_\s*(?P<tail>.*)$")
ARTIST_ALBUM_SPLIT_RE = re.compile(r"^(?P<artist>.{2,60}?)\s+[-–—]\s+(?P<album>.+)$")
FORMAT_TAIL_RE = re.compile(r"\s*\b(?:lp|ep|cd|album|disc)\b\s*$", re.I)
MEANINGLESS_TITLE_RE = re.compile(r"^[\d\W_]+$")
YEAR_PAREN_RE = re.compile(r"\s*[\(\[\{]\s*(?:19\d{2}|20\d{2})\s*[\)\]\}]\s*")


def looks_like_video_id(value: str) -> bool:
    """Tell an 11-character video id apart from a genuine bracketed note.

    Downloaders replace some id characters with spaces, so a couple of spaces are allowed,
    but the more spaces there are the more the value has to look like an id to qualify.
    """
    spaces = value.count(" ")
    if spaces > 2:
        return False
    core = value.replace(" ", "")
    if not core:
        return False
    has_digit = any(char.isdigit() for char in core)
    mixed_case = any(char.islower() for char in core) and any(char.isupper() for char in core)
    if spaces == 2:
        return has_digit and mixed_case
    return has_digit or mixed_case


@dataclass(slots=True)
class TagCandidate:
    artist: str = ""
    title: str = ""
    album: str = ""
    date: str = ""
    track: str = ""
    albumartist: str = ""
    source: str = ""
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class FileResult:
    path: str
    artist: str = ""
    title: str = ""
    album: str = ""
    date: str = ""
    track: str = ""
    albumartist: str = ""
    source: str = ""
    changed: bool = False
    mb_matched: bool = False
    acoustid_matched: bool = False
    itunes_matched: bool = False
    renamed_to: str = ""
    notes: list[str] = field(default_factory=list)
    error: str = ""


class MusicBrainzClient:
    def __init__(self, user_agent: str = "music-cataloger/0.1", min_interval: float = 1.05) -> None:
        self.user_agent = user_agent
        self.min_interval = min_interval
        self._last = 0.0
        self.cache: dict[str, Any] = {}

    def _throttle(self) -> None:
        gap = self.min_interval - (time.time() - self._last)
        if gap > 0:
            time.sleep(gap)

    def _get_json(self, url: str) -> dict[str, Any] | None:
        if url in self.cache:
            return self.cache[url]
        self._throttle()
        req = urllib.request.Request(
            url, headers={"User-Agent": self.user_agent, "Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except Exception:
            payload = None
        self._last = time.time()
        self.cache[url] = payload
        return payload

    def search_recording(self, artist: str, title: str, album: str = "") -> dict[str, str] | None:
        if not title:
            return None
        if not artist:
            return self._search_recording_by_title(title, album=album)

        parts = [f'recording:"{title}"', f'artist:"{artist}"']
        if album:
            parts.append(f'release:"{album}"')
        query = " AND ".join(parts)
        url = (
            "https://musicbrainz.org/ws/2/recording"
            f"?query={urllib.parse.quote(query)}&fmt=json&limit=5"
        )
        data = self._get_json(url)
        recordings = (data or {}).get("recordings") or []
        if not recordings:
            return None

        best: dict[str, str] | None = None
        best_score = -1
        title_l = title.lower()
        artist_l = artist.lower()
        album_l = album.lower()
        for rec in recordings:
            score = int(rec.get("score") or 0)
            rec_title = (rec.get("title") or "").strip()
            if rec_title.lower() == title_l:
                score += 30
            names = " ".join(a.get("name", "") for a in rec.get("artist-credit") or []).strip()
            if artist_l and artist_l in names.lower():
                score += 20
            chosen_release = None
            for rel in rec.get("releases") or []:
                rel_title = (rel.get("title") or "").strip()
                if album_l and rel_title.lower() == album_l:
                    score += 40
                    chosen_release = rel
                    break
            if chosen_release is None and rec.get("releases"):
                chosen_release = rec["releases"][0]
            if score <= best_score:
                continue
            best_score = score
            best = {
                "title": rec_title or title,
                "artist": names or artist,
                "album": (chosen_release or {}).get("title", album).strip(),
                "date": ((chosen_release or {}).get("date") or "")[:4],
                "track": "",
                "score": str(score),
            }
        if best and int(best["score"]) >= 40:
            return best
        return None

    def _search_recording_by_title(
        self, title: str, album: str = ""
    ) -> dict[str, str] | None:
        """MusicBrainz lookup when the filename only carries a song title."""
        title = (title or "").strip()
        if not title:
            return None
        parts = [f'recording:"{title}"']
        if album:
            parts.append(f'release:"{album}"')
        query = " AND ".join(parts)
        url = (
            "https://musicbrainz.org/ws/2/recording"
            f"?query={urllib.parse.quote(query)}&fmt=json&limit=10"
        )
        data = self._get_json(url)
        recordings = (data or {}).get("recordings") or []
        if not recordings:
            return None

        title_l = title.casefold()
        album_l = album.casefold()
        candidates: list[tuple[int, str, dict[str, str]]] = []
        for rec in recordings:
            rec_title = (rec.get("title") or "").strip()
            if not rec_title:
                continue
            # Title-only must be an exact (case-insensitive) recording title.
            if rec_title.casefold() != title_l:
                continue
            score = int(rec.get("score") or 0)
            names = " ".join(
                a.get("name", "") for a in rec.get("artist-credit") or []
            ).strip()
            if not names:
                continue
            chosen_release = None
            for rel in rec.get("releases") or []:
                rel_title = (rel.get("title") or "").strip()
                if album_l and rel_title.casefold() == album_l:
                    score += 40
                    chosen_release = rel
                    break
            if chosen_release is None and rec.get("releases"):
                chosen_release = rec["releases"][0]
            candidates.append(
                (
                    score,
                    names.casefold(),
                    {
                        "title": rec_title,
                        "artist": names,
                        "album": (chosen_release or {}).get("title", album).strip(),
                        "date": ((chosen_release or {}).get("date") or "")[:4],
                        "track": "",
                        "score": str(score),
                    },
                )
            )

        if not candidates:
            return None

        candidates.sort(key=lambda item: item[0], reverse=True)
        # Clear artist consensus among exact-title hits.
        artist_counts = Counter(artist for _score, artist, _row in candidates)
        top_artist, top_count = artist_counts.most_common(1)[0]
        if len(artist_counts) > 1:
            second = artist_counts.most_common(2)[1][1]
            if top_count == second or top_count <= len(candidates) // 2:
                return None

        best = next(
            (row for _score, artist, row in candidates if artist == top_artist),
            None,
        )
        if best and int(best["score"]) >= 60:
            return best
        return None

    def get_recording(
        self, mbid: str, preferred_album: str = ""
    ) -> dict[str, str] | None:
        """Fetch recording metadata by MusicBrainz recording ID."""
        mbid = (mbid or "").strip()
        if not mbid:
            return None
        url = (
            "https://musicbrainz.org/ws/2/recording/"
            f"{urllib.parse.quote(mbid)}"
            "?inc=artists+releases+media&fmt=json"
        )
        data = self._get_json(url)
        if not data or not data.get("id"):
            return None
        title = (data.get("title") or "").strip()
        artist_parts: list[str] = []
        for credit in data.get("artist-credit") or []:
            if isinstance(credit, str):
                artist_parts.append(credit)
                continue
            if not isinstance(credit, dict):
                continue
            nested = credit.get("artist") or {}
            name = (nested.get("name") or credit.get("name") or "").strip()
            if name:
                artist_parts.append(name)
            joinphrase = credit.get("joinphrase") or ""
            if joinphrase:
                artist_parts.append(joinphrase)
        artist = "".join(artist_parts).strip()
        album, date, track = self._pick_release_fields(
            data.get("releases") or [], mbid, preferred_album
        )
        return {
            "title": title,
            "artist": artist,
            "album": album,
            "date": date,
            "track": track,
            "score": "mbid",
        }

    @staticmethod
    def _track_number_for_recording(release: dict[str, Any], mbid: str) -> str:
        """Return the track position of this recording on a release (not the first track)."""
        for medium in release.get("media") or []:
            for tr in medium.get("tracks") or []:
                rec = tr.get("recording") or {}
                if rec.get("id") != mbid:
                    continue
                pos = tr.get("position")
                if pos is None:
                    pos = tr.get("number")
                if pos is None:
                    return ""
                return str(pos).split("/")[0].strip()
        return ""

    @classmethod
    def _pick_release_fields(
        cls,
        releases: list[dict[str, Any]],
        mbid: str,
        preferred_album: str = "",
    ) -> tuple[str, str, str]:
        if not releases:
            return "", "", ""
        preferred_l = preferred_album.casefold().strip()
        best: tuple[int, dict[str, Any], str] | None = None
        for release in releases:
            track = cls._track_number_for_recording(release, mbid)
            album = (release.get("title") or "").strip()
            score = 0
            if track:
                score += 50
            if preferred_l and album.casefold() == preferred_l:
                score += 100
            elif preferred_l and preferred_l in album.casefold():
                score += 40
            if release.get("date"):
                score += 2
            status = (release.get("status") or "").casefold()
            if status == "official":
                score += 5
            if best is None or score > best[0]:
                best = (score, release, track)
        if best is None:
            return "", "", ""
        _, release, track = best
        album = (release.get("title") or "").strip()
        date = (release.get("date") or "")[:4]
        return album, date, track


class MusicCataloger:
    def __init__(self, config: CatalogerConfig) -> None:
        self.config = config
        self.mb = MusicBrainzClient() if config.use_musicbrainz else None
        self.acoustid: AcoustIDClient | None = None
        if config.use_acoustid and config.acoustid_api_key.strip():
            self.acoustid = AcoustIDClient(
                config.acoustid_api_key,
                score_threshold=config.acoustid_score_threshold,
            )
        # iTunes text lookup uses the same matcher as cover art (strong for commercial catalogs).
        self.use_itunes = bool(config.use_acoustid)
        self._itunes_client = None
        self._known_artists: dict[str, str] | None = None

    def run(
        self,
        on_progress: Callable[[int, int, FileResult | None], None] | None = None,
    ) -> list[FileResult]:
        results: list[FileResult] = []
        files = list(self.iter_audio())
        if self.config.limit:
            files = files[: self.config.limit]
        total = len(files)
        done = 0
        itunes_client = None
        if self.use_itunes:
            import httpx

            itunes_client = httpx.Client(
                timeout=20.0,
                headers={"User-Agent": "music-cataloger/0.1 (local music tagger)"},
                follow_redirects=True,
            )
            self._itunes_client = itunes_client
        try:
            for path in files:
                existing = self.read_existing(path)
                if self.config.only_incomplete:
                    missing = [
                        k for k in ("title", "artist", "album", "date") if not existing.get(k)
                    ]
                    if not missing and not self.looks_bad_title(
                        existing.get("title", ""),
                        existing.get("artist", ""),
                        existing.get("album", ""),
                    ):
                        done += 1
                        if on_progress:
                            on_progress(done, total, None)
                        continue
                result = self.process_file(path, existing)
                results.append(result)
                done += 1
                if on_progress:
                    on_progress(done, total, result)
        finally:
            self._itunes_client = None
            if itunes_client is not None:
                itunes_client.close()
        if self.config.report_path:
            self.config.report_path.parent.mkdir(parents=True, exist_ok=True)
            with self.config.report_path.open("w", encoding="utf-8") as fh:
                for row in results:
                    fh.write(json.dumps(asdict(row), ensure_ascii=False) + "\n")
        return results

    def iter_audio(self):
        root = self.config.root
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.name.startswith("._") or path.name in {".DS_Store", "Thumbs.db", "desktop.ini"}:
                continue
            if self.config.artist_filter:
                rel0 = path.relative_to(root).parts[0].lower() if path.relative_to(root).parts else ""
                if rel0 != self.config.artist_filter.lower():
                    continue
            if path.suffix.lower() in self.config.audio_extensions:
                yield path

    def process_file(self, path: Path, existing: dict[str, str]) -> FileResult:
        inferred = self.infer_from_path(path)
        folder_names = path.relative_to(self.config.root).parts[:-1]
        merged = self.merge_tags(inferred, existing, folder_names)
        core_title = self.extract_core_title(
            merged.title, artist=merged.artist, album=merged.album
        )
        if core_title and core_title != merged.title:
            merged.notes.append("title_prefiltered")
            merged.title = core_title
        mb_matched = False
        acoustid_matched = False
        itunes_matched = False

        acoustid_attempted = self.acoustid is not None
        if acoustid_attempted:
            assert self.acoustid is not None
            if self.acoustid.fingerprint_file(path) is None:
                merged.notes.append("acoustid_fp_failed")
                hit = None
            else:
                hit = self.acoustid.identify(
                    path,
                    hint_title=merged.title,
                    hint_artist=merged.artist,
                )
            if hit is not None:
                acoustid_matched = True
                # Fingerprint identity wins over path/tag guesses for title/artist.
                if hit.title:
                    merged.title = self.clean_text(hit.title)
                if hit.artist:
                    merged.artist = self.clean_text(hit.artist)
                    if not merged.albumartist:
                        merged.albumartist = merged.artist
                if hit.album:
                    merged.album = self.clean_text(hit.album)
                if hit.date:
                    merged.date = hit.date
                if hit.track:
                    merged.track = self._norm_track(hit.track)
                merged.source = "acoustid"
                merged.notes.append(f"acoustid_score={hit.score:.3f}")
                merged.notes.append(f"acoustid_recording={hit.recording_id}")
                if self.mb and hit.recording_id:
                    mb_hit = self.mb.get_recording(
                        hit.recording_id,
                        preferred_album=hit.album or merged.album,
                    )
                    if mb_hit:
                        mb_matched = True
                        if mb_hit.get("title"):
                            merged.title = self.clean_text(mb_hit["title"])
                        if mb_hit.get("artist"):
                            merged.artist = self.clean_text(mb_hit["artist"])
                        if mb_hit.get("album"):
                            merged.album = self.clean_text(mb_hit["album"])
                        if mb_hit.get("date"):
                            merged.date = mb_hit["date"]
                        if mb_hit.get("track"):
                            merged.track = self._norm_track(mb_hit["track"])
                        merged.notes.append("mb_enriched_by_mbid")
            elif "acoustid_fp_failed" not in merged.notes:
                merged.notes.append("acoustid_no_match")

        # Same text search that finds cover art — often better coverage than MusicBrainz.
        # Works with artist+title, or title alone (flat YouTube download folders).
        if not acoustid_matched and self.use_itunes and merged.title:
            title_only_lookup = not bool(merged.artist)
            try:
                itunes_hit = lookup_itunes_metadata(
                    merged.artist,
                    merged.title,
                    merged.album,
                    client=self._itunes_client,
                )
            except Exception:
                itunes_hit = None
            if itunes_hit:
                itunes_matched = True
                if itunes_hit.get("title"):
                    merged.title = self.clean_text(itunes_hit["title"])
                if itunes_hit.get("artist"):
                    merged.artist = self.clean_text(itunes_hit["artist"])
                    if not merged.albumartist:
                        merged.albumartist = merged.artist
                if itunes_hit.get("album"):
                    merged.album = self.clean_text(itunes_hit["album"])
                if itunes_hit.get("date"):
                    merged.date = itunes_hit["date"]
                if itunes_hit.get("track"):
                    merged.track = self._norm_track(itunes_hit["track"])
                merged.source = "itunes"
                if title_only_lookup:
                    merged.notes.append("itunes_title_only")
                merged.notes.append("itunes_matched")

        # MusicBrainz text search as another fallback.
        if not acoustid_matched and not itunes_matched and self.mb:
            should_search = acoustid_attempted or self.needs_musicbrainz(merged, existing)
            if should_search and merged.title:
                title_only_lookup = not bool(merged.artist)
                hit = self.mb.search_recording(
                    merged.artist, merged.title, merged.album
                )
                if hit is None and merged.album:
                    hit = self.mb.search_recording(merged.artist, merged.title, "")
                if hit:
                    mb_matched = True
                    merged.title = hit["title"] or merged.title
                    merged.artist = hit["artist"] or merged.artist
                    merged.album = hit["album"] or merged.album
                    merged.date = hit["date"] or merged.date
                    if not merged.albumartist and merged.artist:
                        merged.albumartist = merged.artist
                    merged.source = merged.source or "musicbrainz"
                    if hit.get("score"):
                        merged.notes.append(f"mb_score={hit['score']}")
                    if title_only_lookup:
                        merged.notes.append("mb_title_only")

        changed = any(
            [
                (existing.get("title") or "") != merged.title,
                (existing.get("artist") or "") != merged.artist,
                (existing.get("album") or "") != merged.album,
                (existing.get("date") or "")[:4] != merged.date,
                self._norm_track(existing.get("track", "")) != self._norm_track(merged.track),
            ]
        )
        result = FileResult(
            path=str(path),
            artist=merged.artist,
            title=merged.title,
            album=merged.album,
            date=merged.date,
            track=merged.track,
            albumartist=merged.albumartist,
            source=merged.source,
            changed=changed,
            mb_matched=mb_matched,
            acoustid_matched=acoustid_matched,
            itunes_matched=itunes_matched,
            notes=merged.notes[:],
        )
        if self.config.write and changed and merged.title and merged.artist:
            try:
                self.write_tags(path, merged)
                if self.config.rename_files:
                    renamed = self.maybe_rename(path, merged)
                    if renamed != path:
                        result.renamed_to = str(renamed)
            except Exception as exc:
                result.error = str(exc)
        return result

    def infer_from_path(self, path: Path) -> TagCandidate:
        rel = path.relative_to(self.config.root)
        parts = list(rel.parts[:-1])
        candidates = [self._candidate_for_profile(rel, profile) for profile in self.config.profiles]
        candidates = [candidate for candidate in candidates if candidate]
        if not candidates:
            stem = self.clean_text(self.strip_download_junk(path.stem))
            return TagCandidate(title=stem, source="fallback")
        best = max(candidates, key=self._candidate_score)
        best.title = self.clean_text(best.title)
        best.artist = self.clean_text(best.artist)
        best.album = self.clean_text(best.album)
        best.albumartist = best.albumartist or best.artist
        # A name truncated down to just the artist carries no recoverable title, unlike a
        # self-titled track, which still arrives with its full video id.
        truncated_to_artist = (
            best.artist
            and best.title.lower() == best.artist.lower()
            and not self.has_video_id(path.stem)
        )
        if self.is_meaningless_title(best.title) or truncated_to_artist:
            best.title = ""
            best.notes.append("title_unresolved")
        if not best.date:
            for part in parts:
                year = self.extract_year(part)
                if year:
                    best.date = year
                    break
        return best

    def _candidate_for_profile(self, rel: Path, profile: StructureProfile) -> TagCandidate | None:
        parts = list(rel.parts)
        parent_parts = parts[:-1]
        if any(part.lower() in profile.skip_dir_names for part in parent_parts):
            return None

        artist = ""
        album = ""
        date = ""
        if profile.artist_from_level is not None and profile.artist_from_level < len(parent_parts):
            folder = parent_parts[profile.artist_from_level]
            folder_artist, folder_album, folder_date = self.split_artist_album(folder)
            if not folder_artist:
                folder_artist, folder_album, folder_date = self.match_known_artist_prefix(folder)
            if folder_artist:
                artist = self.canon_artist(folder_artist)
                album = folder_album
                date = folder_date
            else:
                artist = self.canon_artist(folder)
        if profile.album_from_level is not None and profile.album_from_level < len(parent_parts):
            level_date, level_album = self.parse_album_folder(parent_parts[profile.album_from_level])
            album = level_album or album
            date = level_date or date

        track, title, title_artist = self.parse_filename(parts[-1], artist)
        if profile.mixed_artist_files and title_artist:
            artist = self.canon_artist(title_artist)
        if not album:
            for part in parent_parts:
                year_value, album_value = self.parse_album_folder(part)
                if not date and year_value:
                    date = year_value
                if album_value and album_value.lower() not in {artist.lower(), ""} and not BAD_ALBUM_RE.match(album_value):
                    album = album_value
        return TagCandidate(
            artist=artist,
            title=title,
            album=album,
            date=date,
            track=track,
            albumartist=artist,
            source=profile.name,
        )

    def parse_filename(self, filename: str, fallback_artist: str) -> tuple[str, str, str]:
        stem = self.clean_text(self.strip_download_junk(Path(filename).stem))
        track = ""
        title = stem
        artist_hint = ""

        match = TRACK_PREFIX_RE.match(stem)
        if match:
            track = str(int(match.group("track")))
            title = self.clean_text(match.group("title"))

        if fallback_artist:
            pat = re.compile(rf"^{re.escape(fallback_artist)}\s*[-–—]\s*(?P<title>.+)$", re.I)
            match = pat.match(title)
            if match:
                title = self.clean_text(match.group("title"))
                nested = re.match(
                    r"^(?:(?P<album>.+?)\s*-\s+)?(?P<track>\d{1,3})\s*-\s+(?P<title>.+)$",
                    title,
                )
                if nested:
                    track = track or str(int(nested.group("track")))
                    title = self.clean_text(nested.group("title"))
                return track, self.strip_junk(title), fallback_artist

            pat = re.compile(
                rf"^(?P<title>.+?)\s*[-–—_]\s*{re.escape(fallback_artist)}\s*(?:\([^)]*\))?$",
                re.I,
            )
            match = pat.match(title)
            if match:
                title = self.clean_text(match.group("title"))
                return track, self.strip_junk(title), fallback_artist

        if not fallback_artist:
            leading = re.match(r"^(?P<artist>.+?)\s*[-–—]\s*(?P<title>.+)$", title)
            if leading:
                candidate = self.known_artists.get(self.clean_text(leading.group("artist")).lower())
                if candidate:
                    title = self.clean_text(leading.group("title"))
                    return track, self.strip_junk(title), candidate

        suffix = re.match(r"^(?P<title>.+?)\s*[-–—_]\s*(?P<artist>[^-–—_]{2,80})$", stem)
        if suffix and not fallback_artist:
            artist_hint = self.clean_text(suffix.group("artist"))
            if self.looks_like_artist_name(artist_hint):
                title = self.clean_text(suffix.group("title"))
                return track, self.strip_junk(title), artist_hint
            artist_hint = ""

        mixed = re.match(r"^(?P<artist>.+?)\s*[-–—]\s*(?P<title>.+)$", title)
        if mixed and not fallback_artist:
            hint = self.clean_text(mixed.group("artist"))
            if self.looks_like_artist_name(hint):
                artist_hint = hint
                title = self.clean_text(mixed.group("title"))
                return track, self.strip_junk(title), artist_hint

        return track, self.strip_junk(title), artist_hint

    def read_existing(self, path: Path) -> dict[str, str]:
        out = {"title": "", "artist": "", "album": "", "date": "", "track": "", "albumartist": ""}
        try:
            if path.suffix.lower() == ".wma":
                audio = ASF(path)
                tags = audio.tags or {}

                def get_asf(*keys: str) -> str:
                    for key in keys:
                        if key in tags and tags[key]:
                            return str(tags[key][0]).strip()
                    return ""

                out["title"] = get_asf("Title", "WM/Title")
                out["artist"] = get_asf("Author", "WM/AlbumArtist")
                out["album"] = get_asf("WM/AlbumTitle")
                out["date"] = get_asf("WM/Year")[:4]
                out["track"] = get_asf("WM/TrackNumber", "WM/Track")
                out["albumartist"] = get_asf("WM/AlbumArtist")
                return out

            audio = MutagenFile(path, easy=True)
        except Exception:
            return out
        if audio is None:
            return out
        tags = audio.tags or {}

        def get_easy(*keys: str) -> str:
            for key in keys:
                value = tags.get(key)
                if not value:
                    continue
                if isinstance(value, list):
                    value = value[0] if value else ""
                text = str(value).strip()
                if text:
                    return text
            return ""

        out["title"] = get_easy("title", "Title", "©nam")
        out["artist"] = get_easy("artist", "Author", "©ART")
        out["album"] = get_easy("album", "Album", "©alb")
        out["date"] = get_easy("date", "year", "©day")[:4]
        out["track"] = self._norm_track(get_easy("tracknumber", "track"))
        out["albumartist"] = get_easy("albumartist", "album artist")
        return out

    def trusted_existing(
        self,
        existing: dict[str, str],
        folder_names: Sequence[str] = (),
    ) -> dict[str, str]:
        """Blank out existing values we should not trust, letting the path win instead.

        A previous run may have written leftovers of a source video id, or a whole
        "Artist - Album" folder name as the artist, and those must not look authoritative.
        """
        if self.config.ignore_existing_tags:
            return dict.fromkeys(existing, "")
        trusted = dict(existing)
        for key in ("artist", "albumartist"):
            if trusted[key] and self.looks_bad_artist(trusted[key], folder_names):
                trusted[key] = ""
        for key in ("title", "album"):
            if trusted[key] and (
                self.looks_like_garbage_value(trusted[key])
                or "[" in trusted[key]
                or self.matches_split_folder_name(trusted[key], folder_names)
            ):
                trusted[key] = ""
        return trusted

    def salvage_title(self, existing: dict[str, str], artist: str, album: str) -> str:
        """Recover a title from mangled tags when the path yields none.

        An earlier bad pass can leave the real title stranded in the artist field, and even
        a weak cleaned-up value beats keeping a video id in the file.
        """
        weak = ""
        for key in ("title", "artist", "albumartist"):
            candidate = self.strip_junk(
                self.clean_text(self.strip_download_junk(existing.get(key, "")))
            )
            if not candidate or candidate.lower() in {artist.lower(), album.lower()}:
                continue
            # An "Artist - Album" folder name stored as a tag is not a title.
            if artist and len(candidate) > len(artist) and candidate.lower().startswith(artist.lower()):
                continue
            if self.is_meaningless_title(candidate):
                weak = weak or candidate
                continue
            return candidate
        return weak

    def merge_tags(
        self,
        inferred: TagCandidate,
        existing: dict[str, str],
        folder_names: Sequence[str] = (),
    ) -> TagCandidate:
        raw_existing = existing
        existing = self.trusted_existing(existing, folder_names)

        title = existing["title"] or inferred.title
        if self.looks_bad_title(title, existing["artist"] or inferred.artist, existing["album"] or inferred.album):
            if inferred.title:
                title = inferred.title
                inferred.notes.append("title_from_path")
            else:
                title = ""

        artist = existing["artist"] or inferred.artist
        if not existing["artist"] and inferred.artist:
            inferred.notes.append("artist_from_path")

        album = existing["album"] or inferred.album
        if (not album or BAD_ALBUM_RE.match(album)) and inferred.album:
            album = inferred.album
            inferred.notes.append("album_from_path")

        if not title:
            salvaged = self.salvage_title(raw_existing, artist, album)
            if salvaged:
                title = salvaged
                inferred.notes.append("title_salvaged_from_tags")

        date = (existing["date"] or inferred.date or "")[:4]
        track = self._norm_track(inferred.track or existing["track"])
        albumartist = existing["albumartist"] or inferred.albumartist or artist

        artist = self.clean_text(artist)
        album = self.clean_text(album)
        title = self.extract_core_title(self.clean_text(title), artist=artist, album=album)
        inferred.title = title
        inferred.artist = artist
        inferred.album = album
        inferred.date = date
        inferred.track = track
        inferred.albumartist = self.clean_text(albumartist)
        return inferred

    def needs_musicbrainz(self, inferred: TagCandidate, existing: dict[str, str]) -> bool:
        if not inferred.title or not inferred.artist:
            return True
        if not inferred.album or not inferred.date:
            return True
        if existing.get("title") and len(existing["title"]) >= 28 and not existing["title"].endswith((".", "!", "?", "'", '"')):
            if inferred.title == existing["title"]:
                return True
        return False

    def write_tags(self, path: Path, tag: TagCandidate) -> None:
        ext = path.suffix.lower()
        if ext == ".mp3":
            try:
                audio = MP3(path, ID3=EasyID3)
            except ID3NoHeaderError:
                audio = MutagenFile(path, easy=True)
                if audio is None:
                    raise RuntimeError("unreadable mp3")
                audio.add_tags()
            audio["title"] = tag.title
            audio["artist"] = tag.artist
            if tag.album:
                audio["album"] = tag.album
            if tag.date:
                audio["date"] = tag.date
            if tag.albumartist:
                try:
                    audio["albumartist"] = tag.albumartist
                except Exception:
                    pass
            if tag.track:
                audio["tracknumber"] = tag.track
            audio.save()
            return

        if ext == ".m4a":
            audio = MP4(path)
            if audio.tags is None:
                audio.add_tags()
            audio.tags["\xa9nam"] = [tag.title]
            audio.tags["\xa9ART"] = [tag.artist]
            if tag.album:
                audio.tags["\xa9alb"] = [tag.album]
            if tag.date:
                audio.tags["\xa9day"] = [tag.date]
            if tag.albumartist:
                audio.tags["aART"] = [tag.albumartist]
            if tag.track:
                try:
                    track_no = int(str(tag.track).split("/")[0])
                    audio.tags["trkn"] = [(track_no, 0)]
                except ValueError:
                    pass
            audio.save()
            return

        if ext == ".wma":
            audio = ASF(path)
            audio.tags["Title"] = tag.title
            audio.tags["Author"] = tag.artist
            if tag.album:
                audio.tags["WM/AlbumTitle"] = tag.album
            if tag.date:
                audio.tags["WM/Year"] = tag.date
            if tag.albumartist:
                audio.tags["WM/AlbumArtist"] = tag.albumartist
            if tag.track:
                audio.tags["WM/TrackNumber"] = tag.track
            audio.save()
            return

        audio = MutagenFile(path, easy=True)
        if audio is None:
            raise RuntimeError("unsupported/unreadable")
        if audio.tags is None:
            audio.add_tags()
        audio["title"] = tag.title
        audio["artist"] = tag.artist
        if tag.album:
            audio["album"] = tag.album
        if tag.date:
            try:
                audio["date"] = tag.date
            except Exception:
                pass
        if tag.track:
            try:
                audio["tracknumber"] = tag.track
            except Exception:
                pass
        audio.save()

    def maybe_rename(self, path: Path, tag: TagCandidate) -> Path:
        if tag.track:
            new_name = f"{int(tag.track):02d} - {tag.title}{path.suffix.lower()}"
        else:
            new_name = f"{tag.title}{path.suffix.lower()}"
        new_name = re.sub(r'[<>:"/\\|?*]', "_", new_name).strip(" .")
        dest = path.with_name(new_name)
        if dest == path or dest.exists():
            return path
        path.rename(dest)
        return dest

    def canon_artist(self, name: str) -> str:
        return self.config.artist_aliases.get(name, name)

    @staticmethod
    def clean_text(value: str) -> str:
        value = value.replace("_", " ").replace("–", "-").replace("—", "-")
        return MULTI_SPACE_RE.sub(" ", value).strip(" .-_")

    @staticmethod
    def has_video_id(stem: str) -> bool:
        """A complete trailing id means the name reached us intact, not truncated."""
        match = VIDEO_ID_TAIL_RE.search(stem)
        return bool(match) and looks_like_video_id(match.group("id"))

    @staticmethod
    def strip_download_junk(value: str) -> str:
        """Drop the trailing video id, plus any bracket left half-written by a truncated name."""
        match = VIDEO_ID_TAIL_RE.search(value)
        if match and looks_like_video_id(match.group("id")):
            value = value[: match.start()]
        value = TRUNCATED_BRACKET_TAIL_RE.sub("", value)
        value = TRUNCATED_PAREN_TAIL_RE.sub("", value)
        return value.strip()

    @staticmethod
    def strip_junk(value: str) -> str:
        value = BRACKETY_JUNK_RE.sub(" ", value)
        value = YEAR_PAREN_RE.sub(" ", value)
        value = TITLE_NOISE_FREE_RE.sub(" ", value)
        return MULTI_SPACE_RE.sub(" ", value).strip(" .-_")

    def extract_core_title(
        self, title: str, artist: str = "", album: str = ""
    ) -> str:
        """Pull the likely real song title out of download / YouTube noise.

        Used before online lookups (iTunes / MusicBrainz) so searches are not
        poisoned by 'Official Video', lyric tags, track prefixes, etc.
        """
        value = (title or "").strip()
        if not value:
            return ""
        original = value
        value = self.strip_download_junk(value)
        value = self.clean_text(value)

        # "01 - Title", "01. Title", "1) Title", optionally repeated ("11 - 11. Title")
        for _ in range(2):
            match = LEADING_TRACK_RE.match(value)
            if not match:
                break
            value = self.clean_text(match.group("title"))

        # Drop dotted index leftovers: "1.Les Cosines" already handled elsewhere;
        # still strip a bare "NN." prefix.
        dotted = re.match(r"^\d{1,3}\s*[.]\s*(.+)$", value)
        if dotted:
            value = self.clean_text(dotted.group(1))

        prev = None
        while prev != value:
            prev = value
            value = BRACKETY_JUNK_RE.sub(" ", value)
            value = YEAR_PAREN_RE.sub(" ", value)
            value = TITLE_NOISE_FREE_RE.sub(" ", value)
            value = self.clean_text(value)

        value = TRUNCATED_BRACKET_TAIL_RE.sub("", value)
        value = TRUNCATED_PAREN_TAIL_RE.sub("", value)
        value = self.clean_text(value)

        # YouTube-style "Title | Official Audio" / "Title // Lyrics"
        for sep in (" | ", " // ", " / "):
            if sep in value:
                parts = [part.strip() for part in value.split(sep) if part.strip()]
                value = self._pick_title_segment(parts, artist=artist, album=album)
                break

        # Drop "(Album Name)" before peeling the artist, so "Title - Artist (Album)" works.
        if album:
            alb = album.casefold().strip()
            wrapped = re.match(
                r"^(?P<main>.+?)\s*[\(\[\{](?P<inner>[^)\]\}]+)[\)\]\}]\s*$",
                value,
            )
            if wrapped and wrapped.group("inner").casefold().strip() == alb:
                value = wrapped.group("main").strip()

        value = self._strip_artist_from_title(value, artist)

        # Featuring tails hurt search more than they help for matching.
        value = FEAT_TAIL_RE.sub("", value)
        value = value.strip(" \"'`«»“”")
        value = self.clean_text(value)

        if self.is_meaningless_title(value):
            # Don't destroy a title we failed to parse; return a light cleanup only.
            fallback = self.clean_text(self.strip_download_junk(original))
            return "" if self.is_meaningless_title(fallback) else fallback
        return value

    def _strip_artist_from_title(self, title: str, artist: str) -> str:
        """Remove the artist/author name when it is embedded in the title."""
        value = (title or "").strip()
        art = (artist or "").strip()
        if not value or not art:
            return value
        # Keep self-titled tracks ("Inadaptats" by Inadaptats).
        if value.casefold() == art.casefold():
            return value

        variants = [art]
        bare = re.sub(r"(?i)^(?:the|els|les|el|la|l')\s+", "", art).strip()
        if bare and bare.casefold() != art.casefold():
            variants.append(bare)
        for splitter in (" & ", " and ", " i ", ", ", " x ", " / "):
            if splitter in art:
                first = art.split(splitter, 1)[0].strip()
                if len(first) >= 2:
                    variants.append(first)
                break

        for variant in variants:
            if len(variant) < 2:
                continue
            if value.casefold() == variant.casefold():
                return title.strip()
            escaped = re.escape(variant)
            stripped = False

            def _side_is_artist(side: str) -> bool:
                text = side.casefold().strip()
                # Ignore a trailing parenthetical on that side.
                text = re.sub(r"\s*[\(\[\{][^)\]\}]*[\)\]\}]\s*$", "", text).strip()
                return text == variant.casefold()

            for sep in (" - ", " – ", " — ", " _ ", ": ", " · "):
                if sep not in value:
                    continue
                left, right = value.split(sep, 1)
                left, right = left.strip(), right.strip()
                if _side_is_artist(left):
                    value = right
                    stripped = True
                    break
                if _side_is_artist(right):
                    value = left
                    stripped = True
                    break
            if stripped:
                value = self.clean_text(value)
                continue

            next_value = re.sub(
                rf"\s*[\(\[\{{]\s*{escaped}\s*[\)\]\}}]\s*",
                " ",
                value,
                flags=re.IGNORECASE,
            )
            next_value = re.sub(
                rf"^{escaped}\s+",
                "",
                next_value,
                count=1,
                flags=re.IGNORECASE,
            )
            next_value = re.sub(
                rf"\s+{escaped}$",
                "",
                next_value,
                count=1,
                flags=re.IGNORECASE,
            )
            value = self.clean_text(next_value)

        cleaned = self.clean_text(value)
        if self.is_meaningless_title(cleaned):
            return title.strip()
        return cleaned

    def _pick_title_segment(
        self, parts: list[str], *, artist: str = "", album: str = ""
    ) -> str:
        """Choose the segment that looks most like a song title."""
        if not parts:
            return ""
        if len(parts) == 1:
            return parts[0]
        art = artist.casefold().strip()
        alb = album.casefold().strip()
        noise_words = (
            "official",
            "video",
            "audio",
            "lyrics",
            "lyric",
            "videoclip",
            "visualizer",
            "hd",
            "hq",
        )

        def score(part: str) -> tuple[int, int]:
            lower = part.casefold()
            points = len(part)
            if art and (lower == art or lower.startswith(art + " ")):
                points -= 40
            if alb and lower == alb:
                points -= 40
            if any(word in lower.split() for word in noise_words):
                points -= 30
            if self.is_meaningless_title(part):
                points -= 100
            return (points, len(part))

        return max(parts, key=score)

    @staticmethod
    def is_meaningless_title(value: str) -> bool:
        text = (value or "").strip()
        return not text or bool(MEANINGLESS_TITLE_RE.match(text))

    @staticmethod
    def looks_like_garbage_value(value: str) -> bool:
        text = (value or "").strip()
        if not text:
            return False
        return text.count("[") != text.count("]") or text.count("(") != text.count(")")

    def looks_like_artist_name(self, value: str) -> bool:
        text = (value or "").strip()
        if len(text) < 2:
            return False
        if "[" in text or "]" in text:
            return False
        return not self.looks_like_garbage_value(text)

    def matches_split_folder_name(self, value: str, folder_names: Sequence[str] = ()) -> bool:
        """True when the value is a whole folder name that itself splits into artist and album."""
        lower = (value or "").strip().lower()
        if not lower:
            return False
        return any(
            lower == self.clean_text(folder).lower() and bool(self.split_artist_album(folder)[0])
            for folder in folder_names
        )

    def looks_bad_artist(self, artist: str, folder_names: Sequence[str] = ()) -> bool:
        text = (artist or "").strip()
        if not text:
            return True
        if not self.looks_like_artist_name(text):
            return True
        if BRACKETY_JUNK_RE.search(text):
            return True
        return self.matches_split_folder_name(text, folder_names)

    @staticmethod
    def extract_year(value: str) -> str:
        match = YEAR_RE.search(value)
        return match.group(1) if match else ""

    def split_artist_album(self, folder_name: str) -> tuple[str, str, str]:
        """Split a one-level folder such as "Inadaptats - Critica Social (Full Album)".

        Returns (artist, album, year); artist is empty when the name carries no separator.
        Underscores are handled before clean_text, which would otherwise turn the quoting
        underscores of "Band _Album_ LP 2023" into plain spaces.
        """
        raw = MULTI_SPACE_RE.sub(" ", folder_name).strip()

        quoted = QUOTED_ALBUM_RE.match(raw)
        if quoted:
            artist = self.clean_text(quoted.group("artist"))
            album = self.clean_text(quoted.group("album"))
            year = self.extract_year(quoted.group("tail"))
            if artist and album:
                return artist, album, year

        split = ARTIST_ALBUM_SPLIT_RE.match(self.clean_text(raw))
        if not split:
            return "", "", ""
        artist = self.clean_text(split.group("artist"))
        remainder = split.group("album")
        year = self.extract_year(remainder)
        album = self.clean_text(FORMAT_TAIL_RE.sub("", self.strip_junk(remainder)))
        if not year:
            year, album = self.parse_album_folder(album)
        if not artist or not album:
            return "", "", ""
        return artist, album, year

    @property
    def known_artists(self) -> dict[str, str]:
        """Artists learnt from folders that do carry a separator, keyed by lowercase name."""
        if self._known_artists is None:
            self._known_artists = self._collect_known_artists()
        return self._known_artists

    def _collect_known_artists(self) -> dict[str, str]:
        found: dict[str, str] = {}
        try:
            entries = sorted(path for path in self.config.root.iterdir() if path.is_dir())
        except OSError:
            return found
        for entry in entries:
            artist = self.split_artist_album(entry.name)[0]
            if artist:
                found.setdefault(artist.lower(), artist)
        return found

    def match_known_artist_prefix(self, value: str) -> tuple[str, str, str]:
        """Resolve "Manel 10 milles per veure..." using artists seen elsewhere in the library."""
        text = self.clean_text(value)
        lower = text.lower()
        for key in sorted(self.known_artists, key=len, reverse=True):
            if not lower.startswith(key) or len(text) == len(key):
                continue
            remainder = text[len(key) :]
            year = self.extract_year(remainder)
            album = self.clean_text(FORMAT_TAIL_RE.sub("", self.strip_junk(remainder)))
            if not year:
                year, album = self.parse_album_folder(album)
            if album:
                return self.known_artists[key], album, year
        return "", "", ""

    def parse_album_folder(self, folder_name: str) -> tuple[str, str]:
        name = self.clean_text(folder_name)
        match = re.match(
            r"^\[?\s*(?P<year>19\d{2}|20\d{2})\s*\]?\s*[-–—_]?\s*(?P<album>.+)$",
            name,
        )
        if match:
            return match.group("year"), self.clean_text(match.group("album"))
        match = re.match(r"^(?P<album>.+?)\s*[\(\[](?P<year>19\d{2}|20\d{2})[\)\]]$", name)
        if match:
            return match.group("year"), self.clean_text(match.group("album"))
        match = re.match(r"^(?P<album>.+?)\s*[-–—_]?\s+(?P<year>19\d{2}|20\d{2})$", name)
        if match:
            return match.group("year"), self.clean_text(match.group("album"))
        match = RANGE_YEAR_RE.search(name)
        if match:
            album = self.clean_text(re.sub(r"\s*\([^)]*\)\s*", " ", name))
            return match.group("y1"), album
        return "", name

    def looks_bad_title(self, title: str, artist: str, album: str) -> bool:
        lower = title.lower().strip()
        if not lower:
            return True
        if lower in {"track", "audio", "unknown", "untitled"}:
            return True
        if artist and lower == artist.lower():
            return True
        if album and lower == album.lower():
            return True
        if "disc complet" in lower or "discografia" in lower:
            return True
        # A surviving bracket means a source video id was never cleaned off.
        if "[" in title or "]" in title:
            return True
        return self.is_meaningless_title(title)

    @staticmethod
    def _norm_track(value: str) -> str:
        value = str(value or "").split("/")[0].strip()
        return value.lstrip("0") or value

    @staticmethod
    def _candidate_score(candidate: TagCandidate) -> tuple[int, int, int, int]:
        return (
            1 if candidate.artist else 0,
            1 if candidate.title else 0,
            1 if candidate.album else 0,
            2 if candidate.date else (1 if candidate.track else 0),
        )

