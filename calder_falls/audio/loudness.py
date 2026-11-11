"""Measure how loud each cue comes out and suggest a gain_db for cues.py.

    pip install pyloudnorm
    python3 -m calder_falls.audio.loudness            # every cue
    python3 -m calder_falls.audio.loudness june       # one cue

Each cue is rendered once through the real engine (PS2 filter on) and
measured in LUFS, the loudness unit streaming services use. The suggestion
is the gain_db that would put the cue on its target_lufs. Copy the number
into calder_falls/audio/cues.py by hand, then re-render.
"""

import sys

from . import cues as cue_table
from .engine import AudioEngine


def measure(name):
    import pyloudnorm
    eng = AudioEngine(output=False)
    try:
        data = eng.load(name)
        eng.play(name, loop=False)
        audio = eng.render(data.length)
    finally:
        eng.close()
    return pyloudnorm.Meter(eng.sr).integrated_loudness(audio.astype("float64"))


def main(argv=None):
    import importlib.util
    if importlib.util.find_spec("pyloudnorm") is None:
        print("needs pyloudnorm: pip install pyloudnorm", file=sys.stderr)
        return 1
    names = (argv if argv is not None else sys.argv[1:]) or [c.name for c in cue_table.CUES]
    print(f"{'cue':16s} {'now':>7s} {'target':>7s} {'gain_db':>8s} {'suggest':>8s}")
    for name in names:
        cue = cue_table.get(name)
        lu = measure(name)
        suggest = round(cue.gain_db + (cue.target_lufs - lu), 1)
        print(f"{name:16s} {lu:7.1f} {cue.target_lufs:7.1f} {cue.gain_db:8.1f} {suggest:8.1f}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
