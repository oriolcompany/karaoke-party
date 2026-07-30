"""PyInstaller entrypoint for Karaoke Party."""

from karaoke_party.app import main

if __name__ == "__main__":
    import sys

    if "--open" not in sys.argv:
        sys.argv.append("--open")
    main()
