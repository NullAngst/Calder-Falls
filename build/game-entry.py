"""PyInstaller entry point for the game AppImage."""

import sys

from calder_falls.main import main

if __name__ == "__main__":
    sys.exit(main())
