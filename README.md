# Karaoke Party

Local web karaoke: pick a folder of tagged MP3s, fetch synced lyrics from
[LRCLIB](https://lrclib.net), align words to the audio, and sing along in the browser.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pip install -e ".[align]"
```

The `[align]` extra installs `faster-whisper` (CPU, Whisper `small`). First song
alignment downloads the model and can take 1–3 minutes; results are cached under
`.cache/aligned`.

## Run

```bash
karaoke-party --music "C:\path\to\your\mp3\folder"
```

Then open http://127.0.0.1:8765

You can also set the folder in the UI after launch.

## How it works

1. The server scans the music folder and reads title/artist/album/duration from tags.
2. Synced lyrics (LRC) are fetched from LRCLIB and cached under `.cache/lyrics`.
3. On song open, estimated word timings play immediately; in the background Whisper word timestamps are matched to the known lyric text and cached under `.cache/aligned`.
4. When alignment finishes (or is already cached), the stage swaps to word-accurate timings.

## Notes

- Best results when files already have clean `title` and `artist` tags (e.g. after music-cataloger).
- Default alignment language is Catalan (`ca`). Change via `POST /api/align` body `language`.
- Not every song has synced lyrics on LRCLIB; plain lyrics are shown when only those exist.
- This is for personal/local use with music you own.
