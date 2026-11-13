"""Where things live.

data_dir() is the folder holding music/, soundfonts/ and fonts/. From a
source checkout that is the repo root. Inside the AppImage or the Windows
build it is the PyInstaller bundle. CALDER_DATA overrides both.

user_dir() is where saves and downloaded sound banks go:
~/.local/share/calder-falls on Linux, %APPDATA%\\calder-falls on Windows.
$XDG_DATA_HOME/calder-falls wins on either, which is how the selftests
keep their files out of your real ones.
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
    base = os.environ.get("XDG_DATA_HOME")
    if not base and sys.platform == "win32":
        base = os.environ.get("APPDATA")
    if not base:
        base = os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(base, "calder-falls")


def cue_dir():
    return os.path.join(data_dir(), "music", "cues")


def soundfont_dir():
    return os.path.join(data_dir(), "soundfonts")


def user_soundfont_dir():
    return os.path.join(user_dir(), "soundfonts")
