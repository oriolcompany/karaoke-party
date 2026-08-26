"""Mux a browser capture of the live karaoke stage with original audio.

The YouTube iframe cannot be recorded, and album art is never used.
ffmpeg is required to mux the stage recording into an MP4.
"""

from __future__ import annotations

import json
import math
import os
import random
import re
import shutil
import subprocess
import threading
from collections.abc import Callable
from pathlib import Path

from .lyrics import LyricLine, LyricWord, LyricsPayload
from .stems import ffmpeg_available
from .syllables import expand_syllable_tokens, has_syllable_glue
from .track_cache import (
    aligned_path,
    ensure_track_dir,
    karaoke_meta_path,
    karaoke_path,
)

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
KARAOKE_RENDER_VERSION = 11
YOUTUBE_AUDIO_RATE = 48000
YOUTUBE_AUDIO_BITRATE = "384k"
# Stage palette (styles.css): ink, gold, cyan, bg.
_INK = "&H00EAF6FF"
_GOLD = "&H004AE1FF"
_CYAN = "&H00FFE73D"
_BG = "0x07060b"
_AURA_BG = (3, 2, 8)
_AURA_RIBBONS = (
    (255, 45, 106, 0.12, 1.15, 0.32, 0.2, 0.18),
    (255, 225, 74, 0.10, 0.82, -0.24, 1.7, 0.80),
    (61, 231, 255, 0.11, 1.40, 0.41, 3.1, 0.14),
    (255, 120, 60, 0.09, 0.62, -0.18, 4.4, 0.86),
)
_AURA_PARTICLE_RGB = ((255, 45, 106), (255, 225, 74), (61, 231, 255))


class VideoRenderError(RuntimeError):
    pass


def download_filename(artist: str, title: str) -> str:
    raw = f"{artist} - {title}".strip(" -") or "karaoke"
    safe = re.sub(r'[<>:"/\\|?*]', "_", raw)
    safe = re.sub(r"\s+", " ", safe).strip(" .")[:120] or "karaoke"
    return f"{safe}.mp4"


def karaoke_is_current(tracks_root: Path, key: str) -> Path | None:
    """Return the cached MP4 when it matches the current alignment and look."""
    path = karaoke_path(tracks_root, key)
    if not path.is_file() or path.stat().st_size <= 0:
        return None
    aligned = aligned_path(tracks_root, key)
    if not aligned.is_file():
        return None
    if path.stat().st_mtime + 0.01 < aligned.stat().st_mtime:
        return None
    meta = _read_karaoke_meta(tracks_root, key)
    if int(meta.get("version") or 0) != KARAOKE_RENDER_VERSION:
        return None
    if str(meta.get("background") or "") != choose_background(tracks_root, key):
        return None
    if str(meta.get("audio") or "") != "original":
        return None
    if str(meta.get("source") or "") != "stage":
        return None
    return path


def choose_background(tracks_root: Path, key: str) -> str:
    """Always Aura — covers are never used in the exported MP4."""
    del tracks_root, key
    return "aura"


def _read_karaoke_meta(tracks_root: Path, key: str) -> dict:
    path = karaoke_meta_path(tracks_root, key)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_karaoke_meta(tracks_root: Path, key: str, background: str) -> None:
    path = karaoke_meta_path(tracks_root, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "version": KARAOKE_RENDER_VERSION,
                "background": background,
                "audio": "original",
                "source": "stage",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def mark_karaoke_exported(tracks_root: Path, key: str) -> None:
    _write_karaoke_meta(tracks_root, key, "aura")


def lines_for_render(payload: LyricsPayload) -> list[LyricLine]:
    if has_syllable_glue(payload.lines):
        return payload.lines
    return expand_syllable_tokens(payload.lines)


def choose_audio(track_path: Path, tracks_root: Path, key: str) -> Path:
    """Use the original mix (with vocals), not the instrumental stem."""
    del tracks_root, key
    return Path(track_path)


def ass_timestamp(seconds: float) -> str:
    cs = max(0, int(round(float(seconds) * 100.0)))
    hours, cs = divmod(cs, 360_000)
    minutes, cs = divmod(cs, 6_000)
    secs, cs = divmod(cs, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"


def _escape_ass(text: str) -> str:
    return (
        (text or "")
        .replace("\\", r"\\")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("\n", r"\N")
    )


def _line_words(line: LyricLine) -> list[LyricWord]:
    if line.words:
        return list(line.words)
    start = float(line.time)
    return [LyricWord(time=start, end=start + 1.5, text=line.text or "")]


def _line_span(
    line: LyricLine, next_line: LyricLine | None, audio_end: float
) -> tuple[float, float]:
    words = _line_words(line)
    start = min(float(word.time) for word in words)
    end = max(float(word.end) for word in words)
    if next_line is not None:
        nxt = _line_words(next_line)
        next_start = min(float(word.time) for word in nxt)
        if next_start > start:
            end = max(end, min(next_start, audio_end))
    else:
        end = max(end, audio_end)
    return start, max(end, start + 0.05)


def _karaoke_text(words: list[LyricWord]) -> str:
    parts: list[str] = []
    for index, word in enumerate(words):
        text = (word.text or "").replace("\n", " ").strip()
        if not text:
            continue
        duration = max(float(word.end), float(word.time)) - float(word.time)
        centis = max(1, int(round(duration * 100.0)))
        piece = _escape_ass(text)
        nxt = words[index + 1] if index + 1 < len(words) else None
        if nxt is not None and not word.glue:
            piece += " "
        parts.append(f"{{\\k{centis}}}{piece}")
    return "".join(parts)


def build_ass_document(
    *,
    lines: list[LyricLine],
    artist: str,
    title: str,
    duration: float,
    layout: str = "stack",
    background: str = "aura",
) -> str:
    """ASS script: title/artist + current karaoke line + upcoming preview."""
    audio_end = max(float(duration), 0.2)
    dual = layout == "dual"
    current_size = 64 if dual else 72
    next_size = 64 if dual else 36
    next_primary = _INK if dual else _CYAN
    outline = 4 if background == "aura" else 3
    shadow = 2 if background == "aura" else 0
    events: list[str] = [
        f"Dialogue: 0,0:00:00.00,{ass_timestamp(audio_end)},Title,,0,0,0,,{{\\pos(960,72)}}{_escape_ass(title)}",
        f"Dialogue: 0,0:00:00.00,{ass_timestamp(audio_end)},Artist,,0,0,0,,{{\\pos(960,138)}}{_escape_ass(artist.upper())}",
    ]
    for index, line in enumerate(lines):
        nxt = lines[index + 1] if index + 1 < len(lines) else None
        start, end = _line_span(line, nxt, audio_end)
        words = _line_words(line)
        fill = _karaoke_text(words) or _escape_ass(line.text)
        events.append(
            f"Dialogue: 1,{ass_timestamp(start)},{ass_timestamp(end)},Current,,0,0,0,,"
            f"{{\\pos(960,520)}}{fill}"
        )
        if nxt is not None:
            preview = _escape_ass("".join(
                (w.text or "") + ("" if w.glue else " ")
                for w in _line_words(nxt)
            ).strip() or nxt.text)
            events.append(
                f"Dialogue: 0,{ass_timestamp(start)},{ass_timestamp(end)},Next,,0,0,0,,"
                f"{{\\pos(960,700)}}{preview}"
            )

    header = f"""[Script Info]
Title: Karaoke Party
ScriptType: v4.00+
PlayResX: {VIDEO_WIDTH}
PlayResY: {VIDEO_HEIGHT}
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Arial,{52},&H00EAF6FF,&H00EAF6FF,&H00000000,&H64000000,-1,0,0,0,100,100,2,0,1,{outline},{shadow},5,80,80,40,1
Style: Artist,Arial,{28},{_GOLD},{_GOLD},&H00000000,&H64000000,-1,0,0,0,100,100,6,0,1,{outline},{shadow},5,80,80,40,1
Style: Current,Arial,{current_size},{_GOLD},{_INK},&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,{outline},{shadow},5,80,80,40,1
Style: Next,Arial,{next_size},{next_primary},{next_primary},&H00000000,&H64000000,0,0,0,0,100,100,2,0,1,{max(2, outline - 1)},{shadow},5,80,80,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    return header + "\n".join(events) + "\n"


def _ass_filter(ass_name: str, fonts_dir: Path | None) -> str:
    filt = ass_name.replace("\\", "/").replace("'", r"\'")
    if fonts_dir is None:
        return f"ass={filt}"
    # Relative path only: a Windows drive colon breaks the filtergraph parser.
    fonts = Path(fonts_dir).name if Path(fonts_dir).is_absolute() else str(fonts_dir).replace("\\", "/")
    if fonts in {"", "."}:
        return f"ass={filt}:fontsdir=."
    return f"ass={filt}:fontsdir={fonts}"


def default_fonts_dir() -> Path | None:
    if os.name == "nt":
        windir = os.environ.get("WINDIR") or r"C:\Windows"
        path = Path(windir) / "Fonts"
        return path if path.is_dir() else None
    for candidate in (Path("/usr/share/fonts"), Path("/usr/local/share/fonts")):
        if candidate.is_dir():
            return candidate
    return None


def _stage_fonts(work_dir: Path) -> Path | None:
    """Copy a system sans font next to the ASS file so ffmpeg needs no drive path."""
    source_dir = default_fonts_dir()
    if source_dir is None:
        return None
    names = (
        "arial.ttf",
        "Arial.ttf",
        "arialbd.ttf",
        "DejaVuSans.ttf",
        "LiberationSans-Regular.ttf",
        "FreeSans.ttf",
    )
    found: Path | None = None
    if source_dir.is_file():
        found = source_dir
    else:
        for name in names:
            candidate = source_dir / name
            if candidate.is_file():
                found = candidate
                break
        if found is None and os.name == "nt":
            for candidate in source_dir.glob("*.ttf"):
                if "arial" in candidate.name.lower():
                    found = candidate
                    break
    if found is None:
        return None
    dest = work_dir / found.name
    try:
        shutil.copy2(found, dest)
    except OSError:
        return None
    return work_dir


def build_ffmpeg_command(
    *,
    audio_name: str,
    output_name: str,
    ass_name: str,
    cover_name: str | None = None,
    aura_name: str | None = None,
    duration: float,
    fonts_dir: Path | None = None,
) -> list[str]:
    duration = max(float(duration), 0.2)
    ass = _ass_filter(ass_name, fonts_dir)
    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-progress",
        "pipe:1",
        "-nostats",
    ]
    still = False
    if aura_name:
        command += ["-stream_loop", "-1", "-i", aura_name]
        video = (
            f"[0:v]scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},setsar=1,{ass}[v]"
        )
    elif cover_name:
        still = True
        command += ["-loop", "1", "-framerate", str(VIDEO_FPS), "-i", cover_name]
        video = (
            f"[0:v]scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},setsar=1,eq=brightness=-0.22:saturation=0.72[fit];"
            f"[fit]{ass}[v]"
        )
    else:
        still = True
        command += [
            "-f",
            "lavfi",
            "-i",
            f"color=c={_BG}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:r={VIDEO_FPS}:d={duration:.3f}",
        ]
        video = f"[0:v]{ass}[v]"
    command += ["-i", audio_name, "-t", f"{duration:.3f}"]
    command += [
        "-filter_complex",
        video,
        "-map",
        "[v]",
        "-map",
        "1:a",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
    ]
    if still:
        command += ["-tune", "stillimage"]
    command += [
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        "-movflags",
        "+faststart",
        output_name,
    ]
    return command


def probe_duration(path: Path) -> float:
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return 0.0
    try:
        value = float((result.stdout or "").strip())
    except ValueError:
        return 0.0
    return value if value > 0 else 0.0


def _parse_progress_line(line: str, duration: float) -> float | None:
    text = line.strip()
    if duration <= 0:
        return None
    try:
        if text.startswith("out_time_ms="):
            raw = text.split("=", 1)[1]
            if raw.upper() == "N/A":
                return None
            return min(1.0, max(0.0, int(raw) / 1000.0 / duration))
        if text.startswith("out_time_us="):
            raw = text.split("=", 1)[1]
            if raw.upper() == "N/A":
                return None
            return min(1.0, max(0.0, int(raw) / 1_000_000.0 / duration))
    except ValueError:
        return None
    return None


def build_mux_command(
    *,
    video_name: str,
    audio_name: str,
    output_name: str,
    duration: float,
) -> list[str]:
    duration = max(float(duration), 0.2)
    gop = max(1, VIDEO_FPS // 2)
    return [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-progress",
        "pipe:1",
        "-nostats",
        "-i",
        video_name,
        "-i",
        audio_name,
        "-t",
        f"{duration:.3f}",
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-vf",
        (
            f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:flags=lanczos+accurate_rnd+full_chroma_int,"
            "setsar=1,format=yuv420p"
        ),
        "-r",
        str(VIDEO_FPS),
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-tune",
        "animation",
        "-profile:v",
        "high",
        "-level:v",
        "4.1",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "15",
        "-bf",
        "2",
        "-g",
        str(gop),
        "-x264-params",
        "aq-mode=3",
        "-tag:v",
        "avc1",
        "-colorspace",
        "bt709",
        "-color_primaries",
        "bt709",
        "-color_trc",
        "bt709",
        "-color_range",
        "tv",
        "-c:a",
        "aac",
        "-b:a",
        YOUTUBE_AUDIO_BITRATE,
        "-ar",
        str(YOUTUBE_AUDIO_RATE),
        "-ac",
        "2",
        "-shortest",
        "-movflags",
        "+faststart",
        output_name,
    ]


def build_copy_mux_command(
    *,
    video_name: str,
    audio_name: str,
    output_name: str,
    duration: float,
) -> list[str]:
    """Wrap an already encoded H.264 stream: no second generation of losses."""
    duration = max(float(duration), 0.2)
    return [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-progress",
        "pipe:1",
        "-nostats",
        "-fflags",
        "+genpts",
        "-r",
        str(VIDEO_FPS),
        "-f",
        "h264",
        "-i",
        video_name,
        "-i",
        audio_name,
        "-t",
        f"{duration:.3f}",
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        YOUTUBE_AUDIO_BITRATE,
        "-ar",
        str(YOUTUBE_AUDIO_RATE),
        "-ac",
        "2",
        # No -shortest here: with a copied raw H.264 stream ffmpeg considers the
        # video finished and drops the audio packets the encoder still had
        # buffered, leaving a silent file. -t already bounds the output.
        "-movflags",
        "+faststart",
        output_name,
    ]


def mux_stage_recording(
    *,
    video_path: Path,
    audio_path: Path,
    output_path: Path,
    duration: float,
    on_progress: Callable[[float], None] | None = None,
) -> Path:
    if not ffmpeg_available():
        raise VideoRenderError("Cal ffmpeg per crear el vídeo karaoke")
    if not Path(video_path).is_file():
        raise VideoRenderError("No s’ha rebut la gravació de l’escenari")
    if not Path(audio_path).is_file():
        raise VideoRenderError("No s’ha trobat l’àudio de la cançó")
    suffix = Path(video_path).suffix.lower()
    stream_copy = suffix == ".h264"
    duration = max(float(duration), 0.2)
    # The tagged duration can round down, and -t decides where the song is cut,
    # so always trust the audio file itself when it turns out to be longer.
    probed_audio = probe_duration(Path(audio_path))
    if probed_audio > duration:
        duration = probed_audio
    if duration < 1.0 and not stream_copy:
        probed_video = probe_duration(Path(video_path))
        if probed_video > duration:
            duration = probed_video
    work_dir = output_path.parent / f".video-{output_path.stem}"
    if work_dir.exists():
        shutil.rmtree(work_dir, ignore_errors=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    try:
        video_name = f"stage{suffix or '.webm'}"
        audio_name = f"audio{Path(audio_path).suffix.lower() or '.mp3'}"
        shutil.copy2(video_path, work_dir / video_name)
        shutil.copy2(audio_path, work_dir / audio_name)
        out_name = "out.mp4"
        build = build_copy_mux_command if stream_copy else build_mux_command
        command = build(
            video_name=video_name,
            audio_name=audio_name,
            output_name=out_name,
            duration=duration,
        )
        _run_ffmpeg(command, work_dir, duration, on_progress)
        produced = work_dir / out_name
        if not produced.is_file() or produced.stat().st_size <= 0:
            raise VideoRenderError("ffmpeg no ha generat el MP4")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            output_path.unlink()
        shutil.move(str(produced), str(output_path))
        return output_path
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def _stamp(buf: bytearray, width: int, height: int, cx: float, cy: float, radius: float, rgb: tuple[int, int, int], alpha: float) -> None:
    rad = max(1, int(radius) + 1)
    r2 = radius * radius
    x0 = max(0, int(cx) - rad)
    x1 = min(width - 1, int(cx) + rad)
    y0 = max(0, int(cy) - rad)
    y1 = min(height - 1, int(cy) + rad)
    cr, cg, cb = rgb
    for y in range(y0, y1 + 1):
        dy = y - cy
        row = y * width * 3
        for x in range(x0, x1 + 1):
            dx = x - cx
            dist = dx * dx + dy * dy
            if dist > r2:
                continue
            fall = 1.0 - dist / r2
            gain = alpha * fall * fall
            i = row + x * 3
            buf[i] = min(255, buf[i] + int(cr * gain))
            buf[i + 1] = min(255, buf[i + 1] + int(cg * gain))
            buf[i + 2] = min(255, buf[i + 2] + int(cb * gain))


def _aura_frame(
    width: int,
    height: int,
    t: float,
    particles: list[tuple[float, float, float, float, float, int]],
    vignette: list[float],
) -> bytes:
    buf = bytearray(bytes(_AURA_BG) * (width * height))
    for r, g, b, amp, freq, speed, phase, y0 in _AURA_RIBBONS:
        rgb = (r, g, b)
        steps = 36
        radius = 11.0
        for i in range(steps + 1):
            u = i / steps
            wave = math.sin(u * math.pi * 2 * freq + t * speed + phase) * amp
            wave += math.sin(u * math.pi * 5.2 + t * speed * 0.55) * amp * 0.35
            x = u * width
            y = height * (y0 + wave * 0.55)
            _stamp(buf, width, height, x, y, radius, rgb, 0.22)
    for x0, y0, z, vx, vy, hue in particles:
        x = (x0 + vx * t + math.sin(t * 0.6 + y0 * 12) * 0.02) % 1.08 - 0.04
        y = (y0 + vy * t) % 1.08 - 0.04
        rgb = _AURA_PARTICLE_RGB[hue]
        _stamp(buf, width, height, x * width, y * height, 1.2 + z * 1.6, rgb, 0.18 + z * 0.35)
    # Darken edges so lyrics stay readable.
    for i, factor in enumerate(vignette):
        if factor >= 0.999:
            continue
        base = i * 3
        buf[base] = int(buf[base] * factor)
        buf[base + 1] = int(buf[base + 1] * factor)
        buf[base + 2] = int(buf[base + 2] * factor)
    return bytes(buf)


def _aura_vignette(width: int, height: int) -> list[float]:
    table = [1.0] * (width * height)
    for y in range(height):
        ny = (y / max(height - 1, 1) - 0.5) * 2.0
        row = y * width
        for x in range(width):
            nx = (x / max(width - 1, 1) - 0.5) * 2.0
            table[row + x] = max(0.42, 1.0 - 0.48 * min(1.0, nx * nx * 0.7 + ny * ny))
    return table


def _seed_aura_particles(count: int) -> list[tuple[float, float, float, float, float, int]]:
    rng = random.Random(42)
    out: list[tuple[float, float, float, float, float, int]] = []
    for _ in range(count):
        out.append(
            (
                rng.random(),
                rng.random(),
                0.35 + rng.random() * 0.65,
                (rng.random() - 0.5) * 0.021,
                -0.007 - rng.random() * 0.017,
                rng.randrange(3),
            )
        )
    return out


def write_aura_clip(path: Path, *, seconds: float = 6.0, fps: int = 20, width: int = 640, height: int = 360) -> Path:
    """Encode a short looping Aura bed (stage ribbons + particles)."""
    seconds = max(float(seconds), 1.0)
    frames = max(1, int(round(seconds * fps)))
    particles = _seed_aura_particles(min(90, max(40, width * height // 9000 + 50)))
    vignette = _aura_vignette(width, height)
    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{width}x{height}",
        "-r",
        str(fps),
        "-i",
        "pipe:0",
        "-vf",
        f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:flags=bicubic,gblur=sigma=2.2,eq=saturation=1.12",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-crf",
        "26",
        "-pix_fmt",
        "yuv420p",
        str(path.name),
    ]
    proc = subprocess.Popen(
        command,
        cwd=str(path.parent),
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    err_chunks: list[bytes] = []

    def _drain_err() -> None:
        if proc.stderr is None:
            return
        err_chunks.append(proc.stderr.read() or b"")

    err_thread = threading.Thread(target=_drain_err, name="aura-ffmpeg-stderr", daemon=True)
    err_thread.start()
    try:
        assert proc.stdin is not None
        for index in range(frames):
            t = index / float(fps)
            proc.stdin.write(_aura_frame(width, height, t, particles, vignette))
        proc.stdin.close()
    except Exception:
        proc.kill()
        proc.wait()
        raise
    err_thread.join(timeout=8)
    code = proc.wait()
    err = b"".join(err_chunks)
    if code != 0 or not path.is_file() or path.stat().st_size <= 0:
        detail = err.decode("utf-8", "replace").strip()[:300]
        raise VideoRenderError(f"No s’ha pogut crear el fons Aura: {detail or f'codi {code}'}")
    return path


def _run_ffmpeg(
    command: list[str],
    work_dir: Path,
    duration: float,
    on_progress: Callable[[float], None] | None,
) -> None:
    proc = subprocess.Popen(
        command,
        cwd=str(work_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    err_chunks: list[str] = []

    def _drain_err() -> None:
        if proc.stderr is None:
            return
        err_chunks.append(proc.stderr.read() or "")

    err_thread = threading.Thread(target=_drain_err, name="ffmpeg-stderr", daemon=True)
    err_thread.start()
    last = -1.0
    if proc.stdout is not None:
        for line in proc.stdout:
            ratio = _parse_progress_line(line, duration)
            if ratio is None or on_progress is None:
                continue
            if ratio - last >= 0.02 or ratio >= 0.999:
                last = ratio
                on_progress(ratio)
    code = proc.wait()
    err_thread.join(timeout=5)
    if code != 0:
        detail = "".join(err_chunks).strip()[:400] or f"codi {code}"
        raise VideoRenderError(f"ffmpeg ha fallat: {detail}")


def render_karaoke_mp4(
    *,
    audio_path: Path,
    output_path: Path,
    payload: LyricsPayload,
    artist: str,
    title: str,
    duration: float,
    layout: str = "stack",
    background: str = "aura",
    on_progress: Callable[[float], None] | None = None,
) -> Path:
    if not ffmpeg_available():
        raise VideoRenderError("Cal ffmpeg per crear el vídeo karaoke")
    if not Path(audio_path).is_file():
        raise VideoRenderError("No s’ha trobat l’àudio de la cançó")

    lines = lines_for_render(payload)
    if not lines:
        raise VideoRenderError("No hi ha lletra sincronitzada per al vídeo")

    duration = max(float(duration), 0.0)
    if duration < 1.0:
        probed = probe_duration(Path(audio_path))
        if probed > duration:
            duration = probed
    duration = max(duration, 0.2)
    work_dir = output_path.parent / f".video-{output_path.stem}"
    if work_dir.exists():
        shutil.rmtree(work_dir, ignore_errors=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    try:
        audio_name = f"audio{Path(audio_path).suffix.lower() or '.mp3'}"
        shutil.copy2(audio_path, work_dir / audio_name)
        background = "aura"
        aura_path = work_dir / "aura.mp4"
        if duration >= 8:
            write_aura_clip(aura_path, seconds=6.0)
        else:
            write_aura_clip(aura_path, seconds=2.0, fps=16, width=480, height=270)
        aura_name = aura_path.name
        ass_name = "lyrics.ass"
        (work_dir / ass_name).write_text(
            build_ass_document(
                lines=lines,
                artist=artist,
                title=title,
                duration=duration,
                layout=layout,
                background=background,
            ),
            encoding="utf-8",
        )
        staged_fonts = _stage_fonts(work_dir)
        out_name = "out.mp4"
        command = build_ffmpeg_command(
            audio_name=audio_name,
            output_name=out_name,
            ass_name=ass_name,
            cover_name=None,
            aura_name=aura_name,
            duration=duration,
            fonts_dir=Path(".") if staged_fonts is not None else None,
        )
        _run_ffmpeg(command, work_dir, duration, on_progress)
        produced = work_dir / out_name
        if not produced.is_file() or produced.stat().st_size <= 0:
            raise VideoRenderError("ffmpeg no ha generat el MP4")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            output_path.unlink()
        shutil.move(str(produced), str(output_path))
        return output_path
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def export_track_karaoke(
    *,
    tracks_root: Path,
    key: str,
    audio_path: Path,
    payload: LyricsPayload,
    artist: str,
    title: str,
    duration: float,
    layout: str = "stack",
    on_progress: Callable[[float], None] | None = None,
) -> Path:
    ensure_track_dir(tracks_root, key)
    target = karaoke_path(tracks_root, key)
    background = choose_background(tracks_root, key)
    audio = choose_audio(audio_path, tracks_root, key)
    rendered = render_karaoke_mp4(
        audio_path=audio,
        output_path=target,
        payload=payload,
        artist=artist,
        title=title,
        duration=duration,
        layout=layout,
        background=background,
        on_progress=on_progress,
    )
    _write_karaoke_meta(tracks_root, key, background)
    return rendered
