"""Calder Falls entry point.

    python3 -m calder_falls             # play
    python3 -m calder_falls --selftest  # headless: plays the Prologue with sound, toggles
                                        # every setting, saves and loads, then exits
"""

import argparse
import os
import sys

from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication

from . import __version__, paths
from .settings import load_profile, load_settings, save_profile, save_settings


def load_fonts():
    d = os.path.join(paths.data_dir(), "fonts")
    if not os.path.isdir(d):
        return
    for f in sorted(os.listdir(d)):
        if f.endswith((".ttf", ".otf")):
            QFontDatabase.addApplicationFont(os.path.join(d, f))


def make_audio(output):
    from .audio.engine import AudioEngine
    try:
        return AudioEngine(output=output)
    except Exception as exc:  # no bank, no FluidSynth: play silent rather than not at all
        print(f"calder-falls: no music: {exc}", file=sys.stderr)
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Calder Falls")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--version", action="store_true")
    args, qt_args = ap.parse_known_args(argv)
    if sys.stdout is None:
        # The Windows build is a windowed program with no console, so print()
        # goes nowhere. CALDER_LOG sends --version and --selftest output to a
        # file instead, which is how the build workflow reads them.
        log = os.environ.get("CALDER_LOG")
        if log:
            sys.stdout = sys.stderr = open(log, "w", encoding="utf-8", buffering=1)
    if args.version:
        print(__version__)
        return 0
    app = QApplication([sys.argv[0]] + qt_args)
    app.setApplicationName("Calder Falls")
    app.setDesktopFileName("calder-falls")
    load_fonts()

    profile = load_profile()
    profile.launches += 1
    save_profile(profile)

    settings = load_settings()
    if not settings.first_launch_done and not args.selftest:
        from .ui.dialogs import FirstLaunchDialog
        d = FirstLaunchDialog()
        d.exec()
        settings.flicker = d.choice()
        settings.first_launch_done = True
        save_settings(settings)

    audio = make_audio(output=not args.selftest)
    from .app import GameWindow
    win = GameWindow(audio=audio, headless=args.selftest)
    if args.selftest:
        from .selftest import run
        return run(app, win)
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
