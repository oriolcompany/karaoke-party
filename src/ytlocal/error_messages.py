"""Human-friendly formatting for yt-dlp / download errors."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse


_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_VIDEO_ID_RE = re.compile(r"^[\w-]{11}$")


def strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text or "").strip()


def clean_error(text: str) -> str:
    cleaned = strip_ansi(text)
    cleaned = cleaned.replace("ERROR:", "").strip()
    cleaned = re.sub(r"^\[youtube\]\s*[\w-]{11}:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def extract_video_id(url: str, title: str | None = None) -> str | None:
    if title and _VIDEO_ID_RE.match(title.strip()):
        return title.strip()
    if not url:
        return None
    raw = url.strip()
    if _VIDEO_ID_RE.match(raw):
        return raw
    try:
        parsed = urlparse(raw)
        if parsed.hostname and "youtu.be" in parsed.hostname:
            vid = parsed.path.strip("/").split("/")[0]
            return vid if _VIDEO_ID_RE.match(vid) else None
        qs = parse_qs(parsed.query)
        if "v" in qs and qs["v"]:
            vid = qs["v"][0]
            return vid if _VIDEO_ID_RE.match(vid) else None
        parts = [p for p in parsed.path.split("/") if p]
        if "shorts" in parts or "embed" in parts or "live" in parts:
            for i, part in enumerate(parts):
                if part in {"shorts", "embed", "live"} and i + 1 < len(parts):
                    cand = parts[i + 1]
                    if _VIDEO_ID_RE.match(cand):
                        return cand
        if parts and _VIDEO_ID_RE.match(parts[-1]):
            return parts[-1]
    except Exception:
        return None
    return None


def youtube_watch_url(url: str, title: str | None = None) -> str | None:
    vid = extract_video_id(url, title)
    if vid:
        return f"https://www.youtube.com/watch?v={vid}"
    if url and url.startswith("http"):
        return url
    return None


def is_usable_title(title: str | None) -> bool:
    """True when ``title`` looks like a real video name, not a URL or ID."""
    raw = (title or "").strip()
    if not raw:
        return False
    if raw.startswith("Pista desconeguda"):
        return False
    if _VIDEO_ID_RE.match(raw):
        return False
    lower = raw.lower()
    if lower.startswith("http://") or lower.startswith("https://"):
        return False
    if re.fullmatch(r"item\s+\d+", lower):
        return False
    return True


def display_title(title: str | None, url: str = "", playlist_title: str | None = None) -> str:
    raw = (title or "").strip()
    vid = extract_video_id(url, raw)
    if is_usable_title(raw):
        return raw
    if vid:
        return f"Pista desconeguda (ID de YouTube: {vid})"
    if playlist_title:
        return f"Pista desconeguda de “{playlist_title}”"
    return url or "Pista desconeguda"


def friendly_reason(error: str) -> str:
    text = clean_error(error).lower()

    if "could not copy chrome cookie database" in text or ("could not copy" in text and "cookie" in text):
        return "No s'han pogut llegir les cookies de Chrome/Edge. Tanca el navegador o fes servir cookies.txt (recomanat)."
    if "private video" in text:
        return "Vídeo privat: cal accés o inici de sessió. Fes servir un cookies.txt exportat amb la sessió iniciada."
    if "please sign in" in text or "sign in to confirm" in text:
        return "YouTube demana iniciar sessió. Les cookies de Chrome sovint fallen a Windows: fes servir cookies.txt."
    if "members-only" in text or "members only" in text:
        return "Vídeo només per a membres."
    if "requested format is not available" in text or "no video formats found" in text:
        return (
            "YouTube no ha ofert cap àudio o vídeo descarregable. "
            "Torna a obrir Karaoke Party i intenta-ho una altra vegada."
        )
    if "http error 403" in text or "403: forbidden" in text:
        return (
            "Bloquejat per YouTube (HTTP 403). Cal Node.js o Deno instal·lat, "
            "i sovint cookies.txt amb la sessió iniciada a YouTube."
        )
    if "http error 404" in text or "404: not found" in text:
        return "Vídeo no trobat (HTTP 404)."
    if "video unavailable" in text:
        return "Vídeo no disponible."
    if "has been removed" in text or "been deleted" in text:
        return "El vídeo s'ha eliminat."
    if "copyright" in text:
        return "Bloquejat per drets d'autor."
    if "geo" in text and ("restrict" in text or "not available" in text):
        return "No disponible en aquest país."
    if "confirm your age" in text or "age-restricted" in text:
        return "Vídeo amb límit d'edat (cal iniciar sessió)."
    if "ffmpeg" in text:
        return "Problema amb ffmpeg en convertir l'àudio/vídeo."
    if "timed out" in text or "timeout" in text:
        return "Temps d'espera de xarxa esgotat."
    if "urlopen error" in text or "network is unreachable" in text:
        return "Error de xarxa."
    if "missing url" in text or "falta l'url" in text:
        return "Falta l'URL del vídeo."
    if not text:
        return "La descàrrega ha fallat."
    short = clean_error(error)
    if len(short) > 160:
        short = short[:157] + "..."
    return short


def format_error_with_title(
    error: str,
    title: str | None = None,
    url: str = "",
    playlist_title: str | None = None,
) -> str:
    """Catalan error text, prefixed with the video title when known."""
    reason = friendly_reason(error)
    label = (title or "").strip()
    if not is_usable_title(label):
        return reason
    if label in reason:
        return reason
    return f"«{label}»: {reason}"


def enrich_failure(record: dict) -> dict:
    """Add display fields for API/UI without mutating storage shape permanently."""
    out = dict(record)
    title = str(out.get("title") or "")
    url = str(out.get("url") or "")
    error = str(out.get("error") or "")
    playlist = out.get("playlist_title")
    out["display_title"] = display_title(title, url, str(playlist) if playlist else None)
    # Always recompute reason in Catalan for UI consistency.
    out["reason"] = format_error_with_title(
        error,
        title,
        url,
        str(playlist) if playlist else None,
    )
    out["error_clean"] = clean_error(error)
    out["watch_url"] = youtube_watch_url(url, title)
    out["video_id"] = extract_video_id(url, title)
    return out
