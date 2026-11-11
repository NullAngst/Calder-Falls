"""PyInstaller entry point for the jukebox AppImage."""

import sys

from calder_falls.jukebox import main

if __name__ == "__main__":
    sys.exit(main())
