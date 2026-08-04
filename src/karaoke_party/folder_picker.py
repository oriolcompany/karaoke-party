from __future__ import annotations

from pathlib import Path


def pick_music_folder(initial: str | None = None) -> str | None:
    """Open a native folder dialog and return the chosen absolute path.

    Returns None when the user cancels or the dialog cannot be shown.
    """
    start = None
    if initial:
        candidate = Path(initial).expanduser()
        if candidate.is_dir():
            start = str(candidate)
        elif candidate.parent.is_dir():
            start = str(candidate.parent)

    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return None

    root = tk.Tk()
    root.withdraw()
    try:
        root.attributes("-topmost", True)
    except Exception:
        pass
    try:
        root.update()
        chosen = filedialog.askdirectory(
            parent=root,
            initialdir=start,
            mustexist=True,
            title="Tria la carpeta de música",
        )
    except Exception:
        return None
    finally:
        try:
            root.destroy()
        except Exception:
            pass

    if not chosen:
        return None
    path = Path(chosen).expanduser()
    if not path.is_dir():
        return None
    return str(path.resolve())
