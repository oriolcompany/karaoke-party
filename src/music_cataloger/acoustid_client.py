from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import acoustid

# AcoustID scores are often modest on messy/compressed rips; keep this low.
DEFAULT_SCORE_THRESHOLD = 0.3
LOOKUP_META = ["recordings", "releases", "tracks", "compress"]
MAX_FINGERPRINT_SECONDS = 120


def _hidden_subprocess_kwargs() -> dict[str, Any]:
    """Avoid flashing a console window when spawning fpcalc on Windows."""
    if os.name != "nt":
        return {}
    kwargs: dict[str, Any] = {}
    # Python 3.7+
    create_no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    if create_no_window:
        kwargs["creationflags"] = create_no_window
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    kwargs["startupinfo"] = startupinfo
    return kwargs


def run_fpcalc(path: Path, *, maxlength: int = MAX_FINGERPRINT_SECONDS) -> tuple[float, str]:
    """Run Chromaprint fpcalc without showing a terminal window."""
    fpcalc = configure_fpcalc()
    if fpcalc is None:
        raise FileNotFoundError("fpcalc not found")
    command = [str(fpcalc), "-length", str(maxlength), str(path)]
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        **_hidden_subprocess_kwargs(),
    )
    if completed.returncode != 0:
        raise RuntimeError(f"fpcalc exited with status {completed.returncode}")

    duration: float | None = None
    fingerprint: str | None = None
    for line in completed.stdout.splitlines():
        if b"=" not in line:
            continue
        key, value = line.split(b"=", 1)
        if key == b"DURATION":
            duration = float(value)
        elif key == b"FINGERPRINT":
            fingerprint = value.decode("ascii", errors="ignore")
    if duration is None or not fingerprint:
        raise RuntimeError("missing fpcalc output")
    return duration, fingerprint


@dataclass(slots=True)
class AcoustIDMatch:
    score: float
    recording_id: str
    title: str = ""
    artist: str = ""
    album: str = ""
    date: str = ""
    track: str = ""


def resolve_fpcalc() -> Path | None:
    """Locate fpcalc.exe for Chromaprint fingerprinting."""
    env = os.environ.get(acoustid.FPCALC_ENVVAR, "").strip()
    if env:
        candidate = Path(env)
        if candidate.is_file():
            return candidate

    candidates: list[Path] = []
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        candidates.append(exe_dir / "fpcalc.exe")
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            base = Path(meipass)
            candidates.append(base / "fpcalc.exe")
            candidates.append(base / "vendor" / "fpcalc" / "fpcalc.exe")

    # src/music_cataloger/acoustid_client.py -> repo root
    repo_root = Path(__file__).resolve().parents[2]
    candidates.append(repo_root / "vendor" / "fpcalc" / "fpcalc.exe")
    candidates.append(Path.cwd() / "vendor" / "fpcalc" / "fpcalc.exe")
    candidates.append(Path.cwd() / "fpcalc.exe")

    which = os.environ.get("PATH", "")
    for folder in which.split(os.pathsep):
        if not folder:
            continue
        name = "fpcalc.exe" if os.name == "nt" else "fpcalc"
        candidates.append(Path(folder) / name)

    seen: set[Path] = set()
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.is_file():
            return resolved
    return None


def configure_fpcalc() -> Path | None:
    path = resolve_fpcalc()
    if path is not None:
        os.environ[acoustid.FPCALC_ENVVAR] = str(path)
    return path


class AcoustIDClient:
    def __init__(
        self,
        api_key: str,
        *,
        score_threshold: float = DEFAULT_SCORE_THRESHOLD,
        min_interval: float = 0.35,
    ) -> None:
        self.api_key = api_key.strip()
        self.score_threshold = score_threshold
        self.min_interval = min_interval
        self._last = 0.0
        self._fp_cache: dict[str, tuple[float, str] | None] = {}
        self._lookup_cache: dict[tuple[Any, ...], AcoustIDMatch | None] = {}
        self.fpcalc_path = configure_fpcalc()

    def _throttle(self) -> None:
        gap = self.min_interval - (time.time() - self._last)
        if gap > 0:
            time.sleep(gap)

    def fingerprint_file(self, path: Path) -> tuple[float, str] | None:
        key = f"{path.resolve()}::{path.stat().st_mtime_ns}"
        if key in self._fp_cache:
            return self._fp_cache[key]
        if self.fpcalc_path is None and configure_fpcalc() is None:
            self._fp_cache[key] = None
            return None
        try:
            result = run_fpcalc(path)
        except Exception:
            self._fp_cache[key] = None
            return None
        self._fp_cache[key] = result
        return result

    def identify(
        self,
        path: Path,
        *,
        hint_title: str = "",
        hint_artist: str = "",
    ) -> AcoustIDMatch | None:
        fp = self.fingerprint_file(path)
        if fp is None:
            return None
        duration, fingerprint = fp
        match = self.lookup_fingerprint(
            fingerprint,
            duration,
            hint_title=hint_title,
            hint_artist=hint_artist,
        )
        if match is None:
            return None
        if match.score >= self.score_threshold:
            return match
        # Even weaker scores are OK when path/tag hints roughly agree.
        similarity = self._hint_similarity(
            match, hint_title=hint_title, hint_artist=hint_artist
        )
        if match.score >= 0.18 and similarity >= 0.75:
            return match
        # Last resort: accept a sole low-confidence hit rather than discarding it.
        if match.score >= 0.22:
            return match
        return None

    def lookup_fingerprint(
        self,
        fingerprint: str,
        duration: float,
        *,
        hint_title: str = "",
        hint_artist: str = "",
    ) -> AcoustIDMatch | None:
        cache_key = (fingerprint, int(duration), hint_title.casefold(), hint_artist.casefold())
        if cache_key in self._lookup_cache:
            return self._lookup_cache[cache_key]
        if not self.api_key:
            self._lookup_cache[cache_key] = None
            return None
        self._throttle()
        try:
            data = acoustid.lookup(
                self.api_key,
                fingerprint,
                duration,
                meta=LOOKUP_META,
            )
            match = self._best_match(
                data, hint_title=hint_title, hint_artist=hint_artist
            )
        except Exception:
            match = None
        self._last = time.time()
        self._lookup_cache[cache_key] = match
        return match

    def _best_match(
        self,
        data: dict[str, Any],
        *,
        hint_title: str = "",
        hint_artist: str = "",
    ) -> AcoustIDMatch | None:
        if not data or data.get("status") != "ok":
            return None
        best: AcoustIDMatch | None = None
        best_key: tuple[float, float, int] | None = None
        for result in data.get("results") or []:
            try:
                score = float(result.get("score") or 0.0)
            except (TypeError, ValueError):
                continue
            for recording in result.get("recordings") or []:
                recording_id = (recording.get("id") or "").strip()
                if not recording_id:
                    continue
                title = (recording.get("title") or "").strip()
                artists = recording.get("artists") or []
                artist = "".join(
                    a.get("name", "") + a.get("joinphrase", "") for a in artists
                ).strip()
                album, date, track = self._release_fields(recording)
                if not title:
                    continue
                candidate = AcoustIDMatch(
                    score=score,
                    recording_id=recording_id,
                    title=title,
                    artist=artist,
                    album=album,
                    date=date,
                    track=track,
                )
                similarity = self._hint_similarity(
                    candidate, hint_title=hint_title, hint_artist=hint_artist
                )
                completeness = (
                    (2 if candidate.artist else 0)
                    + (2 if candidate.album else 0)
                    + (2 if candidate.track else 0)
                    + (1 if candidate.date else 0)
                )
                key = (score, similarity, completeness)
                if best_key is None or key > best_key:
                    best = candidate
                    best_key = key
        return best

    @staticmethod
    def _hint_similarity(
        candidate: AcoustIDMatch,
        *,
        hint_title: str = "",
        hint_artist: str = "",
    ) -> float:
        score = 0.0
        if hint_title and candidate.title:
            score += SequenceMatcher(
                None, hint_title.casefold(), candidate.title.casefold()
            ).ratio()
        if hint_artist and candidate.artist:
            score += SequenceMatcher(
                None, hint_artist.casefold(), candidate.artist.casefold()
            ).ratio()
        return score

    @staticmethod
    def _release_fields(recording: dict[str, Any]) -> tuple[str, str, str]:
        releases = recording.get("releases") or []
        if not releases:
            return "", "", ""
        best: tuple[int, str, str, str] | None = None
        for release in releases:
            album = (release.get("title") or "").strip()
            date = (release.get("date") or "")[:4]
            track = ""
            for medium in release.get("mediums") or []:
                tracks = medium.get("tracks") or []
                # AcoustID usually returns only the matched track(s) for this recording.
                for tr in tracks:
                    position = tr.get("position")
                    if position is None:
                        position = tr.get("number")
                    if position is not None:
                        track = str(position).split("/")[0].strip()
                        break
                if track:
                    break
            rank = (3 if track else 0) + (2 if album else 0) + (1 if date else 0)
            if best is None or rank > best[0]:
                best = (rank, album, date, track)
        if best is None:
            return "", "", ""
        return best[1], best[2], best[3]
