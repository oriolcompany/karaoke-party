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
cached per song under `tracks/<key>/aligned.json`. Alignment always isolates the
vocal track first (generating stems on demand when missing); the `[stems]` extra
is required for Whisper. If CUDA libraries do not match, Whisper falls back to CPU
automatically.

### Karaoke (instrumental) tracks

```bash
pip install -e ".[stems]"      # NVIDIA GPU
pip install -e ".[stems-cpu]"  # CPU only
```

This installs [`audio-separator`](https://github.com/nomadkaraoke/python-audio-separator),
which wraps the UVR model zoo (Demucs, MDX-Net, RoFormer). Model weights download on
first use. Generated tracks are cached as MP3 inside each song folder
(`tracks/<key>/instrumental.mp3` and `vocals.mp3`); the vocal stem is reused to make
Whisper alignment more accurate. **ffmpeg must be on PATH.**

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

1. The server scans the music folder and reads title/artist/album/duration from tags. Basic LRCLIB sync does **not** run on startup.
2. Synced lyrics (LRC) are fetched from LRCLIB when you open a song, run Whisper sync, or use Settings → “Resincronitzar sense lletra”, and cached under `tracks/<key>/lyrics.json`.
3. Whisper sync always runs the chain **basic lyrics → stem separation → Whisper**. Word timings are cached under `tracks/<key>/aligned.json`. Matching walks a single monotonic best path over the whole song, so repeated choruses cannot steal each other's timings, and it can merge tokens in both directions (`l'amor` vs `l'` + `amor`).
4. When alignment finishes (or is already cached), the stage swaps to word-accurate timings.
5. Covers are resolved from embedded tags, then folder art, then iTunes (and embedded back into the file); a copy also lives at `tracks/<key>/cover.<ext>`.
6. Stems are also generated on demand from the instrumental toggle / bulk settings action; Whisper reuses the same cache.
7. Settings → Memòria cau can clear/resync one song, wipe all caches, or export/import a per-song zip between PCs.

### Per-song cache layout

App cache root (Windows: `%LOCALAPPDATA%\KaraokeParty`, override with `KARAOKE_CACHE_DIR`):

```text
tracks/<key>/
  meta.json
  lyrics.json
  aligned.json
  instrumental.mp3
  vocals.mp3
  cover.<ext>
```

`key` is `sha1(artist.lower|title.lower|int(duration))`. Demucs scratch files go to
`stems-work/`; downloaded models stay in `stem-models/` and `whisper` caches.

## Notes

- Best results when files already have clean `title` and `artist` tags (e.g. after music-cataloger).
- Default alignment language is Catalan (`ca`). Change via `POST /api/align` body `language`.
- Improving the aligner bumps `ALIGNED_CACHE_VERSION`, so songs aligned by an older version are recomputed on demand.
- Not every song has synced lyrics on LRCLIB; plain lyrics are shown when only those exist.
- This is for personal/local use with music you own.
