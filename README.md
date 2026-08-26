# Karaoke Party

Local web karaoke: pick a folder of tagged MP3s, fetch synced lyrics from
[LRCLIB](https://lrclib.net), align words to the audio, and sing along in the browser.

## Quick start (Windows)

Double-click **Karaoke Party** on the Desktop (created on first launch, with the app icon), or:

```text
KaraokeParty.bat
```

This will:

1. Create `.venv` if needed
2. Install required dependencies (base + Whisper + stems) and verify `ffmpeg` is on PATH
3. If an NVIDIA GPU is present, verify PyTorch CUDA + CUDA 12 libs for Whisper and
   install/repair them automatically when needed
4. Abort with a clear error if anything required is missing
5. Start the server at http://127.0.0.1:8765
6. Open the browser

Close the console window to stop the app.

## Setup (manual)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pip install -e ".[align]"
pip install -e ".[stems]"      # or ".[stems-cpu]" without NVIDIA GPU
```

`ffmpeg` must also be on PATH. On start, `karaoke-party` checks base packages, Whisper,
stems, torchaudio (MMS), and ffmpeg, and exits if any are missing (use `--skip-deps` only for development).
With an NVIDIA GPU, `KaraokeParty.bat` (and `python -m karaoke_party`) also runs
`python -m karaoke_party.gpu_setup`, which installs a CUDA PyTorch wheel matching the
driver and the CUDA 12 libraries Whisper needs when they are missing.

The `[align]` extra installs `faster-whisper`. Defaults to Whisper `medium` on
CUDA when a GPU is available, otherwise CPU. The model is downloaded/loaded in
the background when the server starts (not on the first song). Results are
cached per song under `tracks/<key>/aligned.json`. Alignment always isolates the
vocal track first (generating stems on demand when missing); the `[stems]` extra
is required for Whisper. After Whisper locates each phrase, **Meta MMS**
force-aligns the known lyric letters on the vocal stem and groups them into
Catalan syllables. `torchaudio` (pulled in with `[stems]`) downloads the MMS
weights on first use (~1.2 GB, cached under the app cache `torch/` folder).
MMS is licensed CC-BY-NC; this app is for personal/local use. If CUDA libraries
do not match, Whisper falls back to CPU automatically. Set `KARAOKE_MMS=0` to
skip MMS and keep energy-based syllable splits.

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
| `KARAOKE_WHISPER_MODEL` | `large-v3` on CUDA, else `medium` | `small` is faster; override if VRAM is tight |
| `KARAOKE_WHISPER_BEAM` | `5` on CUDA, else `3` | Higher can help a bit more; `1` is fastest |
| `KARAOKE_WHISPER_DEVICE` | auto (`cuda` if available, else `cpu`) | Force with `cpu` / `cuda` |
| `KARAOKE_WHISPER_COMPUTE` | `float16` on CUDA, `int8` on CPU | CTranslate2 compute type |
| `KARAOKE_MMS` | `1` | `0` disables Meta MMS syllable alignment |
| `KARAOKE_MMS_DEVICE` | auto (`cuda` if Torch sees a GPU) | Force with `cpu` / `cuda` |

When LRCLIB already provides synced line times, each line is located as a
phrase near those cues (so choruses do not steal each other’s timings). Without
LRC times it walks phrases through the song and can absorb a long instrumental
intro; if too little matches it falls back to a whole-song word path.

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
3. Whisper sync always runs the chain **basic lyrics → stem separation → Whisper → MMS syllables**. Word timings are cached under `tracks/<key>/aligned.json`. Matching locates each lyric line as a phrase in the ASR, then aligns words inside that span, so a misheard word cannot steal the next line. Repeated choruses stay monotonic, and tokens can merge in both directions (`l'amor` vs `l'` + `amor`). MMS then timestamps each letter of that known line on the vocal stem and the fill is grouped into Catalan syllables (`brin`+`dar`). If MMS is unavailable, syllable edges fall back to energy valleys inside the Whisper word window.
4. When alignment finishes (or is already cached), the stage swaps to syllable-accurate timings.
5. Covers are resolved from embedded tags, then folder art, then iTunes (and embedded back into the file); a copy also lives at `tracks/<key>/cover.<ext>`.
6. When you open a song, the server looks up a YouTube music video (`yt-dlp` search, or a tagged/filename video id) and caches only `tracks/<key>/youtube.json` (the video id, not the file). The stage can play that clip **muted** in a YouTube iframe as the background; local audio keeps the lyric clock. Toggle **Vídeo / Portada / Aura / Escenari** on the stage: Portada is a Ken Burns animation of the album cover; Aura is a generative particle field. Spotify Canvas is not used — the public Spotify API does not expose those clips.
7. Stems are also generated on demand from the instrumental toggle / bulk settings action; Whisper reuses the same cache.
8. Settings → Memòria cau can clear/resync one song, wipe all caches, or export/import a per-song zip between PCs.

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
  youtube.json
```

`key` is `sha1(artist.lower|title.lower|int(duration))`. Demucs scratch files go to
`stems-work/`; downloaded models stay in `stem-models/`, `whisper`, and `torch` (MMS).

## Notes

- Best results when files already have clean `title` and `artist` tags (e.g. after music-cataloger).
- Default alignment language is Catalan (`ca`). Change via `POST /api/align` body `language`.
- Improving the aligner bumps `ALIGNED_CACHE_VERSION`, so songs aligned by an older version are recomputed on demand.
- Not every song has synced lyrics on LRCLIB; plain lyrics are shown when only those exist.
- Stage video search needs network access and `yt-dlp` (installed with the base package). Set `KARAOKE_YOUTUBE=0` to skip search. Tagged YouTube URLs or a yt-dlp `[id]` in the filename still count.
- This is for personal/local use with music you own.
