"""Point pyfluidsynth and sounddevice at the libraries bundled in the AppImage.

Both find their C library with ctypes.util.find_library, which asks
ldconfig and never looks inside the bundle. When frozen, we answer that
question ourselves for the two names that matter. From a source checkout
this does nothing and the system libraries are used.

Must run before fluidsynth or sounddevice is imported.
"""

import ctypes.util
import glob
import os
import sys

_done = False


def prepare():
    global _done
    if _done:
        return
    _done = True
    if not getattr(sys, "frozen", False):
        return
    base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    wanted = {
        "fluidsynth": "libfluidsynth.so*",
        "portaudio": "libportaudio.so*",
    }
    found = {}
    for key, pattern in wanted.items():
        hits = sorted(glob.glob(os.path.join(base, pattern)))
        if hits:
            found[key] = hits[0]
    if not found:
        return
    original = ctypes.util.find_library

    def find_library(name):
        if name in found:
            return found[name]
        return original(name)

    ctypes.util.find_library = find_library
