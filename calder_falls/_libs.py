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
