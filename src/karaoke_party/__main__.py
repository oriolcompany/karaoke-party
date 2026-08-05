"""Allow `python -m karaoke_party`.

GPU / CUDA repair runs in a separate step first so a broken CPU-only torch can
be replaced before ``app`` (and Whisper) import it.
"""

from __future__ import annotations

import sys

_BOOTSTRAP_FLAGS = ("--skip-gpu-setup",)


def _bootstrap_gpu() -> None:
    if "--skip-deps" in sys.argv or "--skip-gpu-setup" in sys.argv:
        return
    # Frozen builds cannot pip-install; KaraokeParty.bat already ran the repair.
    if getattr(sys, "frozen", False):
        return
    from karaoke_party.gpu_setup import ensure_gpu

    status = ensure_gpu(install=True)
    if status.has_nvidia and not status.ok:
        print(
            "Karaoke Party: GPU detectada però CUDA no està a punt.\n"
            "  Torna a executar KaraokeParty.bat o:\n"
            "  python -m karaoke_party.gpu_setup",
            file=sys.stderr,
        )
        raise SystemExit(1)


def _strip_bootstrap_flags() -> None:
    sys.argv = [arg for arg in sys.argv if arg not in _BOOTSTRAP_FLAGS]


if __name__ == "__main__":
    _bootstrap_gpu()
    _strip_bootstrap_flags()
    from karaoke_party.app import main

    main()
