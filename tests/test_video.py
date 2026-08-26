"""Karaoke MP4 export: ASS lyrics and ffmpeg command."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from karaoke_party.lyrics import LyricLine, LyricWord, LyricsPayload, cache_key
from karaoke_party.stems import ffmpeg_available
from karaoke_party.track_cache import (
    aligned_path,
    clear_track_files,
    karaoke_meta_path,
    karaoke_path,
    write_meta,
)
from karaoke_party.video import (
    KARAOKE_RENDER_VERSION,
    ass_timestamp,
    build_ass_document,
    build_ffmpeg_command,
    build_mux_command,
    choose_audio,
    choose_background,
    download_filename,
    karaoke_is_current,
    render_karaoke_mp4,
)


def _line(text: str, t0: float, words: list[LyricWord]) -> LyricLine:
    return LyricLine(time=t0, text=text, words=words)


def test_ass_timestamp_format() -> None:
    assert ass_timestamp(0) == "0:00:00.00"
    assert ass_timestamp(72.5) == "0:01:12.50"
    assert ass_timestamp(3661.03) == "1:01:01.03"


def test_download_filename_strips_illegal_chars() -> None:
    name = download_filename('Art:ist', 'Títol? "x"')
    assert name.endswith(".mp4")
    assert ":" not in name
    assert "?" not in name
    assert '"' not in name


def test_ass_karaoke_fill_and_glue() -> None:
    lines = [
        _line(
            "brindar amb mi",
            1.0,
            [
                LyricWord(1.0, 1.2, "brin", glue=True),
                LyricWord(1.2, 1.5, "dar", glue=False),
                LyricWord(1.5, 1.8, "amb"),
                LyricWord(1.8, 2.1, "mi"),
            ],
        ),
        _line(
            "una altra",
            2.1,
            [
                LyricWord(2.1, 2.4, "una"),
                LyricWord(2.4, 2.8, "altra"),
            ],
        ),
    ]
    script = build_ass_document(
        lines=lines,
        artist="Sopa de Cabra",
        title="El far del sud",
        duration=10.0,
        layout="stack",
    )
    assert "Style: Current" in script
    assert "SOPA DE CABRA" in script
    assert "El far del sud" in script
    assert r"{\k20}brin{\k30}dar {\k30}amb {\k30}mi" in script
    assert "una altra" in script
    assert "Style: Next" in script
    # Current line stays on screen until the next phrase starts.
    assert "0:00:01.00,0:00:02.10,Current" in script
    assert "0:00:01.00,0:00:02.10,Next" in script


def test_ass_escapes_override_braces() -> None:
    lines = [_line("{hola}", 0.0, [LyricWord(0.0, 0.4, "{hola}")])]
    script = build_ass_document(lines=lines, artist="A", title="B", duration=1.0)
    assert r"\{hola\}" in script
    assert "{hola}" not in script.split("[Events]", 1)[1]


def test_ffmpeg_command_uses_cover_and_ass() -> None:
    command = build_ffmpeg_command(
        audio_name="audio.mp3",
        output_name="out.mp4",
        ass_name="lyrics.ass",
        cover_name="cover.jpg",
        duration=12.5,
        fonts_dir=None,
    )
    joined = " ".join(command)
    assert command[0] == "ffmpeg"
    assert "-i" in command
    assert "cover.jpg" in command
    assert "audio.mp3" in command
    assert "lyrics.ass" in joined
    assert "libx264" in command
    assert "out.mp4" in command


def test_ffmpeg_command_relative_fontsdir() -> None:
    command = build_ffmpeg_command(
        audio_name="audio.mp3",
        output_name="out.mp4",
        ass_name="lyrics.ass",
        cover_name=None,
        duration=3.0,
        fonts_dir=Path("."),
    )
    joined = " ".join(command)
    assert "fontsdir=." in joined
    assert "C:" not in joined


def test_ffmpeg_command_aura_loops_without_stillimage() -> None:
    command = build_ffmpeg_command(
        audio_name="audio.mp3",
        output_name="out.mp4",
        ass_name="lyrics.ass",
        aura_name="aura.mp4",
        duration=12.5,
        fonts_dir=None,
    )
    joined = " ".join(command)
    assert "-stream_loop" in command
    assert "aura.mp4" in command
    assert "stillimage" not in joined
    assert "lyrics.ass" in joined


def test_ffmpeg_command_color_fallback_without_cover() -> None:
    command = build_ffmpeg_command(
        audio_name="audio.mp3",
        output_name="out.mp4",
        ass_name="lyrics.ass",
        cover_name=None,
        duration=3.0,
    )
    assert "lavfi" in command
    assert any(item.startswith("color=c=") for item in command)


def test_mux_command_maps_stage_video_and_original_audio() -> None:
    command = build_mux_command(
        video_name="stage.webm",
        audio_name="audio.mp3",
        output_name="out.mp4",
        duration=12.5,
    )
    joined = " ".join(command)
    assert command[0] == "ffmpeg"
    assert "stage.webm" in command
    assert "audio.mp3" in command
    assert "0:v:0" in command
    assert "1:a:0" in command
    assert "libx264" in command
    assert "1920:1080" in joined
    assert command[command.index("-profile:v") + 1] == "high"
    assert command[command.index("-tune") + 1] == "animation"
    assert command[command.index("-crf") + 1] == "15"
    assert command[command.index("-r") + 1] == "30"
    assert "384k" in command
    assert "48000" in command
    assert "+faststart" in command


def test_choose_audio_uses_original_even_with_instrumental(tmp_path: Path) -> None:
    key = "abc"
    folder = tmp_path / key
    folder.mkdir()
    original = tmp_path / "song.mp3"
    original.write_bytes(b"orig")
    inst = folder / "instrumental.mp3"
    inst.write_bytes(b"inst")
    assert choose_audio(original, tmp_path, key) == original


def test_choose_background_always_aura(tmp_path: Path) -> None:
    from karaoke_party.youtube import save_cached

    key = cache_key("A", "B", 10.0)
    write_meta(tmp_path, key, artist="A", title="B", duration=10.0)
    (tmp_path / key / "cover.jpg").write_bytes(b"art")
    assert choose_background(tmp_path, key) == "aura"
    save_cached(
        tmp_path,
        key,
        {"found": True, "video_id": "dQw4w9WgXcQ"},
        artist="A",
        title="B",
        duration=10.0,
    )
    assert choose_background(tmp_path, key) == "aura"


def test_karaoke_is_current_requires_newer_than_align(tmp_path: Path) -> None:
    key = cache_key("A", "B", 10.0)
    write_meta(tmp_path, key, artist="A", title="B", duration=10.0)
    video = karaoke_path(tmp_path, key)
    aligned = aligned_path(tmp_path, key)
    video.parent.mkdir(parents=True, exist_ok=True)
    aligned.write_text("{}", encoding="utf-8")
    video.write_bytes(b"mp4")
    karaoke_meta_path(tmp_path, key).write_text(
        f'{{"version": {KARAOKE_RENDER_VERSION}, "background": "aura", "audio": "original", "source": "stage"}}',
        encoding="utf-8",
    )
    os.utime(aligned, (1_000_000, 1_000_000))
    os.utime(video, (2_000_000, 2_000_000))
    assert karaoke_is_current(tmp_path, key) == video
    os.utime(aligned, (3_000_000, 3_000_000))
    assert karaoke_is_current(tmp_path, key) is None


def test_karaoke_is_current_rejects_old_cover_export(tmp_path: Path) -> None:
    key = cache_key("A", "B", 10.0)
    write_meta(tmp_path, key, artist="A", title="B", duration=10.0)
    aligned_path(tmp_path, key).write_text("{}", encoding="utf-8")
    karaoke_path(tmp_path, key).write_bytes(b"mp4")
    os.utime(aligned_path(tmp_path, key), (1_000_000, 1_000_000))
    os.utime(karaoke_path(tmp_path, key), (2_000_000, 2_000_000))
    assert karaoke_is_current(tmp_path, key) is None


def test_karaoke_is_current_rejects_python_render_without_stage_source(tmp_path: Path) -> None:
    key = cache_key("A", "B", 10.0)
    write_meta(tmp_path, key, artist="A", title="B", duration=10.0)
    aligned_path(tmp_path, key).write_text("{}", encoding="utf-8")
    karaoke_path(tmp_path, key).write_bytes(b"mp4")
    karaoke_meta_path(tmp_path, key).write_text(
        f'{{"version": {KARAOKE_RENDER_VERSION}, "background": "aura", "audio": "original"}}',
        encoding="utf-8",
    )
    os.utime(aligned_path(tmp_path, key), (1_000_000, 1_000_000))
    os.utime(karaoke_path(tmp_path, key), (2_000_000, 2_000_000))
    assert karaoke_is_current(tmp_path, key) is None


def test_clear_aligned_removes_karaoke_mp4(tmp_path: Path) -> None:
    key = cache_key("A", "B", 10.0)
    write_meta(tmp_path, key, artist="A", title="B", duration=10.0)
    aligned_path(tmp_path, key).write_text("{}", encoding="utf-8")
    karaoke_path(tmp_path, key).write_bytes(b"mp4")
    karaoke_meta_path(tmp_path, key).write_text("{}", encoding="utf-8")
    removed = clear_track_files(tmp_path, key, {"aligned"})
    assert removed["aligned"] == 1
    assert not karaoke_path(tmp_path, key).is_file()
    assert not karaoke_meta_path(tmp_path, key).is_file()


@pytest.mark.skipif(not ffmpeg_available(), reason="ffmpeg missing")
def test_render_short_karaoke_mp4(tmp_path: Path) -> None:
    import subprocess

    audio = tmp_path / "song.mp3"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=44100:cl=stereo",
            "-t",
            "0.8",
            "-c:a",
            "libmp3lame",
            "-q:a",
            "9",
            str(audio),
        ],
        check=True,
        capture_output=True,
    )
    payload = LyricsPayload(
        synced=True,
        source="whisper-align",
        lines=[
            LyricLine(
                time=0.0,
                text="hola",
                words=[LyricWord(0.05, 0.4, "hola")],
            )
        ],
        plain="hola",
    )
    out = tmp_path / "karaoke.mp4"
    render_karaoke_mp4(
        audio_path=audio,
        output_path=out,
        payload=payload,
        artist="Artista",
        title="Cançó",
        duration=0.8,
        layout="stack",
    )
    assert out.is_file()
    assert out.stat().st_size > 500
