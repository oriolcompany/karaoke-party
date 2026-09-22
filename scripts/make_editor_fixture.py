"""Build a throwaway library + cache so the syllable editor can be tried locally.

Run it with KARAOKE_CACHE_DIR pointing somewhere disposable, then start the
server with the same cache dir and --music <printed folder>.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

from karaoke_party.lyrics import cache_key

ARTIST = "Prova Karaoke"
TITLE = "Cançó de prova"
ALBUM = "Demo"
SYLLABLES = [
    ("A", 0.60, 0.90, True),
    ("vui", 0.90, 1.35, False),
    ("can", 1.60, 1.95, True),
    ("tem", 1.95, 2.45, False),
    ("junts", 2.70, 3.30, False),
    ("fins", 3.90, 4.30, False),
    ("que", 4.30, 4.60, False),
    ("sur", 4.80, 5.15, True),
    ("ti", 5.15, 5.50, False),
    ("el", 5.60, 5.80, False),
    ("sol", 5.95, 6.70, False),
]
LINES = [(0, 5), (5, 11)]
LINE_TEXTS = ["Avui cantem junts", "fins que surti el sol"]


def build_audio(path: Path) -> None:
    """Short tone burst per syllable so the waveform has visible onsets."""
    beeps = []
    for index, (_text, start, end, _glue) in enumerate(SYLLABLES):
        freq = 220 + (index % 5) * 80
        beeps.append(
            f"sine=frequency={freq}:duration={end - start:.3f}:sample_rate=44100,"
            f"adelay={int(start * 1000)}:all=1[a{index}]"
        )
    inputs = "[0:a]" + "".join(f"[a{i}]" for i in range(len(SYLLABLES)))
    graph = (
        ";".join(beeps)
        + f";{inputs}amix=inputs={len(SYLLABLES) + 1}:duration=first:normalize=0[out]"
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-filter_complex", graph, "-map", "[out]",
            "-t", "10", "-codec:a", "libmp3lame", "-q:a", "4",
            str(path),
        ],
        check=True,
    )


def main() -> int:
    from karaoke_party.config import aligned_cache_dir

    root = Path(sys.argv[1]).resolve()
    music = root / "music"
    music.mkdir(parents=True, exist_ok=True)
    song = music / "prova.mp3"
    build_audio(song)

    tags = EasyID3()
    tags["artist"] = ARTIST
    tags["title"] = TITLE
    tags["album"] = ALBUM
    tags.save(song)

    duration = MP3(song).info.length
    key = cache_key(ARTIST, TITLE, duration)
    track_dir = aligned_cache_dir() / key
    track_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(song, track_dir / "vocals.mp3")
    shutil.copy(song, track_dir / "instrumental.mp3")

    lines = []
    for (start, stop), text in zip(LINES, LINE_TEXTS):
        words = [
            {"time": w_start, "end": w_end, "text": w_text, "glue": glue}
            for w_text, w_start, w_end, glue in SYLLABLES[start:stop]
        ]
        lines.append({"time": words[0]["time"], "text": text, "words": words})

    (track_dir / "meta.json").write_text(
        json.dumps(
            {"key": key, "artist": ARTIST, "title": TITLE, "album": ALBUM, "duration": duration},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (track_dir / "aligned.json").write_text(
        json.dumps(
            {
                "synced": True,
                "source": "whisper-align",
                "plain": "\n".join(LINE_TEXTS),
                "lines": lines,
                "align_version": 5,
                "manual_edit": False,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(music)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
