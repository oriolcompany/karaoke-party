# Karaoke Party

Local web karaoke: pick a folder of tagged MP3s, fetch synced lyrics from
[LRCLIB](https://lrclib.net), align words to the audio, and sing along in the browser.

## Quick start (Windows)

Double-click:

```text
KaraokeParty.bat
```

This will:

1. Create `.venv` if needed
2. Install dependencies (including Whisper alignment when possible)
3. Start the server at http://127.0.0.1:8765
4. Open the browser

Close the console window to stop the app.

## Setup (manual)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pip install -e ".[align]"
```

The `[align]` extra installs `faster-whisper`. Defaults to Whisper `medium` on
CUDA when a GPU is available, otherwise CPU. The model is downloaded/loaded in
the background when the server starts (not on the first song). Results are
cached under `.cache/aligned`. When stem separation is installed, alignment
isolates the vocal track first for better accuracy. If CUDA libraries do not
match, Whisper falls back to CPU automatically.

### Karaoke (instrumental) tracks

```bash
pip install -e ".[stems]"      # NVIDIA GPU
pip install -e ".[stems-cpu]"  # CPU only
```

This installs [`audio-separator`](https://github.com/nomadkaraoke/python-audio-separator),
which wraps the UVR model zoo (Demucs, MDX-Net, RoFormer). Model weights download on
first use. Generated tracks are cached as MP3 under the app cache in `stems/`, and the
vocal stem is reused to make Whisper alignment more accurate. **ffmpeg must be on PATH.**

| Variable | Default | Notes |
| --- | --- | --- |
| `KARAOKE_STEMS_MODEL` | `htdemucs.yaml` | Any filename from `audio-separator --list_models`; RoFormer checkpoints separate better but are slower |
| `KARAOKE_STEMS_BITRATE` | `192k` | MP3 bitrate of the cached tracks |
| `KARAOKE_STEMS_AUTOCAST` | off | Set to `1` for faster GPU inference |

### Tuning alignment accuracy

| Variable | Default | Notes |
| --- | --- | --- |
| `KARAOKE_WHISPER_MODEL` | `medium` | `small` is faster; `large-v3` is slower and heavier on VRAM |
| `KARAOKE_WHISPER_BEAM` | `3` | Higher (up to `5`) can help a bit more; `1` is fastest |
| `KARAOKE_WHISPER_DEVICE` | auto (`cuda` if available, else `cpu`) | Force with `cpu` / `cuda` |
| `KARAOKE_WHISPER_COMPUTE` | `float16` on CUDA, `int8` on CPU | CTranslate2 compute type |

## Run

```bash
karaoke-party --open --music "C:\path\to\your\mp3\folder"
```

Then open http://127.0.0.1:8765 if you did not pass `--open`.

You can also set the folder in the UI after launch.

## Build standalone EXE (optional)

```text
build_exe.bat
```

Creates `dist\KaraokeParty.exe`. The EXE bundles the web UI and base server.
For full Whisper alignment support, prefer `KaraokeParty.bat`.

## How it works

1. The server scans the music folder and reads title/artist/album/duration from tags.
2. Synced lyrics (LRC) are fetched from LRCLIB and cached under `.cache/lyrics`.
3. On song open, estimated word timings play immediately; in the background Whisper word timestamps are matched to the known lyric text and cached under `.cache/aligned`.
   If stem separation is available, the vocal track is isolated first. Matching walks a single monotonic best path over the whole song, so repeated choruses cannot steal each other's timings, and it can merge tokens in both directions (`l'amor` vs `l'` + `amor`).
4. When alignment finishes (or is already cached), the stage swaps to word-accurate timings.
5. Covers are resolved from embedded tags, then folder art, then iTunes (and embedded back into the file).
6. On request (or as part of Whisper align), the song is split into vocal and instrumental stems so it can be sung karaoke style; both are cached.

## Notes

- Best results when files already have clean `title` and `artist` tags (e.g. after music-cataloger).
- Default alignment language is Catalan (`ca`). Change via `POST /api/align` body `language`.
- Improving the aligner bumps `ALIGNED_CACHE_VERSION`, so songs aligned by an older version are recomputed on demand.
- Not every song has synced lyrics on LRCLIB; plain lyrics are shown when only those exist.
- This is for personal/local use with music you own.
