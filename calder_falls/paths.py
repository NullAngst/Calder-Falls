"""Where things live.

data_dir() is the folder holding music/, soundfonts/ and fonts/. From a
source checkout that is the repo root. Inside the AppImage it is the
PyInstaller bundle. CALDER_DATA overrides both.

user_dir() is ~/.local/share/calder-falls (or $XDG_DATA_HOME/calder-falls),
where saves and downloaded sound banks go.
"""

import os
import sys


def data_dir():
    env = os.environ.get("CALDER_DATA")
    if env:
        return env
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def user_dir():
    base = os.environ.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(base, "calder-falls")


def cue_dir():
    return os.path.join(data_dir(), "music", "cues")


def soundfont_dir():
    return os.path.join(data_dir(), "soundfonts")


def user_soundfont_dir():
    return os.path.join(user_dir(), "soundfonts")
