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

The `[align]` extra installs `faster-whisper` (CPU, Whisper `small`). First song
alignment downloads the model and can take 1–3 minutes; results are cached under
`.cache/aligned`.

### Tuning alignment accuracy

| Variable | Default | Notes |
| --- | --- | --- |
| `KARAOKE_WHISPER_MODEL` | `small` | `medium` / `large-v3` transcribe sung Catalan better but are several times slower on CPU |
| `KARAOKE_WHISPER_BEAM` | `1` | `3`–`5` improves transcription, roughly doubling alignment time |
| `KARAOKE_WHISPER_DEVICE` | `cpu` | `cuda` when a GPU with CUDA is available |
| `KARAOKE_WHISPER_COMPUTE` | `int8` on CPU, `float16` otherwise | CTranslate2 compute type |

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
   Matching walks a single monotonic best path over the whole song, so repeated choruses cannot steal each other's timings, and it can merge tokens in both directions (`l'amor` vs `l'` + `amor`).
4. When alignment finishes (or is already cached), the stage swaps to word-accurate timings.
5. Covers are resolved from embedded tags, then folder art, then iTunes (and embedded back into the file).

## Notes

- Best results when files already have clean `title` and `artist` tags (e.g. after music-cataloger).
- Default alignment language is Catalan (`ca`). Change via `POST /api/align` body `language`.
- Improving the aligner bumps `ALIGNED_CACHE_VERSION`, so songs aligned by an older version are recomputed on demand.
- Not every song has synced lyrics on LRCLIB; plain lyrics are shown when only those exist.
- This is for personal/local use with music you own.
