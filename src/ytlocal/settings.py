"""Persistent app settings (portable-aware)."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

import yt_dlp

from ytlocal.paths import data_dir

_lock = threading.Lock()

DEFAULT_SETTINGS: dict[str, Any] = {
    # none | chrome | edge | firefox | brave | opera | file
    "cookies_browser": "none",
    "cookies_file": "",
}

SUPPORTED_BROWSERS = ("none", "chrome", "edge", "firefox", "brave", "opera", "file")


def settings_file() -> Path:
    return data_dir() / "settings.json"


def default_cookies_txt() -> Path:
    return data_dir() / "cookies.txt"


def _read() -> dict[str, Any]:
    path = settings_file()
    if not path.is_file():
        return dict(DEFAULT_SETTINGS)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return dict(DEFAULT_SETTINGS)
    if not isinstance(data, dict):
        return dict(DEFAULT_SETTINGS)
    merged = dict(DEFAULT_SETTINGS)
    merged.update({k: v for k, v in data.items() if k in DEFAULT_SETTINGS})
    return merged


def _write(data: dict[str, Any]) -> None:
    path = settings_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_settings() -> dict[str, Any]:
    with _lock:
        current = _read()
    current["cookies_txt_path"] = str(default_cookies_txt())
    current["cookies_txt_exists"] = default_cookies_txt().is_file()
    return current


def update_settings(patch: dict[str, Any]) -> dict[str, Any]:
    with _lock:
        current = _read()
        if "cookies_browser" in patch:
            browser = str(patch["cookies_browser"] or "none").lower().strip()
            if browser not in SUPPORTED_BROWSERS:
                raise ValueError(f"Unsupported browser: {browser}")
            current["cookies_browser"] = browser
        if "cookies_file" in patch:
            current["cookies_file"] = str(patch["cookies_file"] or "").strip()
        _write(current)
    return get_settings()


def cookie_ydl_opts() -> dict[str, Any]:
    """Return yt-dlp options for browser/file cookies, if configured."""
    settings = get_settings()
    browser = str(settings.get("cookies_browser") or "none").lower()

    if browser == "file":
        path = default_cookies_txt()
        custom = str(settings.get("cookies_file") or "").strip()
        if custom:
            path = Path(custom).expanduser()
        if path.is_file():
            return {"cookiefile": str(path.resolve())}
        return {}

    if browser and browser != "none":
        return {"cookiesfrombrowser": (browser,)}

    cookie_file = str(settings.get("cookies_file") or "").strip()
    if cookie_file:
        path = Path(cookie_file).expanduser()
        if path.is_file():
            return {"cookiefile": str(path.resolve())}
    # Auto-use cookies.txt if present next to the app data folder.
    auto = default_cookies_txt()
    if auto.is_file():
        return {"cookiefile": str(auto.resolve())}
    return {}


def _friendly_cookie_error(exc: Exception) -> str:
    text = str(exc)
    lower = text.lower()
    if "could not copy chrome cookie database" in lower or "could not copy" in lower and "cookie" in lower:
        return (
            "No s'han pogut llegir les cookies de Chrome/Edge. Tanca Chrome/Edge del tot i torna-ho a provar, "
            "o exporta cookies.txt (recomanat)."
        )
    if "could not find firefox cookies" in lower:
        return "No s'han trobat perfils de Firefox. Instal·la Firefox o fes servir cookies.txt."
    if "please sign in" in lower or "private video" in lower:
        return (
            "S'han carregat cookies, però YouTube encara demana iniciar sessió. "
            "Exporta cookies noves mentre tinguis la sessió iniciada a youtube.com."
        )
    return f"La comprovació de cookies ha fallat: {text}"


def probe_cookies() -> dict[str, Any]:
    """Test whether the configured cookies can be used by yt-dlp."""
    settings = get_settings()
    mode = str(settings.get("cookies_browser") or "none")
    opts = cookie_ydl_opts()
    if mode == "none" and not opts:
        return {
            "ok": False,
            "configured": False,
            "mode": mode,
            "message": "No hi ha cookies configurades.",
        }
    if mode == "file" and not opts:
        return {
            "ok": False,
            "configured": True,
            "mode": mode,
            "message": f"Falta el fitxer de cookies. Posa cookies Netscape a: {default_cookies_txt()}",
            "cookies_txt_path": str(default_cookies_txt()),
        }
    if not opts:
        return {
            "ok": False,
            "configured": True,
            "mode": mode,
            "message": "L'opció de cookies està activada, però no s'ha trobat cap font de cookies.",
        }

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noprogress": True,
        **opts,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info("https://www.youtube.com/watch?v=jNQXAC9IVRw", download=False)
        return {
            "ok": True,
            "configured": True,
            "mode": mode,
            "message": "Les cookies semblen vàlides.",
            "cookies_txt_path": str(default_cookies_txt()),
            "using": opts,
        }
    except Exception as exc:
        return {
            "ok": False,
            "configured": True,
            "mode": mode,
            "message": _friendly_cookie_error(exc),
            "cookies_txt_path": str(default_cookies_txt()),
            "detail": str(exc),
        }
