"""Point pyfluidsynth and sounddevice at the libraries bundled with the game.

Both find their C library with ctypes.util.find_library, which asks
ldconfig (or, on Windows, PATH) and never looks inside the bundle. When
frozen, we answer that question ourselves for the names that matter. From
a source checkout this does nothing and the system libraries are used.

On Windows only FluidSynth is redirected. sounddevice finds its own
PortAudio DLL inside its package when find_library comes up empty, and
PyInstaller bundles that package whole.

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
    if sys.platform == "win32":
        # FluidSynth's DLLs (glib, libsndfile and the rest) sit next to it in
        # the bundle; let Windows find them there when it loads the library.
        os.add_dll_directory(base)
        # libfluidsynth-3.dll up to 2.4.4, fluidsynth-3.dll from 2.4.5 on
        wanted = {"fluidsynth": ("libfluidsynth*.dll", "fluidsynth*.dll")}
    else:
        wanted = {
            "fluidsynth": ("libfluidsynth.so*",),
            "portaudio": ("libportaudio.so*",),
        }
    found = {}
    for key, patterns in wanted.items():
        for pattern in patterns:
            hits = sorted(glob.glob(os.path.join(base, pattern)))
            if hits:
                found[key] = hits[0]
                break
    if not found:
        return
    original = ctypes.util.find_library

    def find_library(name):
        if name in found:
            return found[name]
        return original(name)

    ctypes.util.find_library = find_library


def check_portaudio():
    """For the selftests. Returns (ok, message).

    Only a missing or unloadable library is a failure. PortAudio refusing
    to start because there is no sound server (a CI runner has none) means
    the library loaded fine, which is all the AppImage has to prove.
    """
    prepare()
    try:
        import sounddevice
    except OSError as exc:  # library not found, or found and could not be loaded
        return False, f"PortAudio failed to load: {exc}"
    except Exception as exc:  # sounddevice.PortAudioError: loaded, but no audio server
        return True, f"PortAudio loaded, no audio server here ({str(exc).splitlines()[0][:120]})"
    return True, (f"PortAudio {sounddevice.get_portaudio_version()[1]}, "
                  f"{len(sounddevice.query_devices())} audio device(s)")
