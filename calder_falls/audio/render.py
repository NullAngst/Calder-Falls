"""Render cues to audio files through the real engine.

    python3 -m calder_falls.audio.render                 # every cue to renders/*.ogg
    python3 -m calder_falls.audio.render june dawn       # just these
    python3 -m calder_falls.audio.render --out /tmp/x --format wav --no-ps2 june

Looping cues are rendered once through plus a few seconds of tail, so the
file ends where the loop would start again.
"""

import argparse
import os
import sys

from .. import paths
from . import cues as cue_table
from .engine import render_cue_to_file


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render Calder Falls cues to audio files.")
    ap.add_argument("cues", nargs="*", help="cue names (default: all)")
    ap.add_argument("--out", default=os.path.join(paths.data_dir(), "renders"))
    ap.add_argument("--format", default="ogg", choices=("ogg", "wav", "flac"))
    ap.add_argument("--no-ps2", action="store_true", help="render without the PS2 filter")
    ap.add_argument("--static", type=float, default=0.0, help="static bleed 0..1")
    args = ap.parse_args(argv)
    names = args.cues or [c.name for c in cue_table.CUES]
    os.makedirs(args.out, exist_ok=True)
    for name in names:
        cue_table.get(name)
        path = os.path.join(args.out, f"{name}.{args.format}")
        audio = render_cue_to_file(name, path, ps2=not args.no_ps2, static=args.static)
        print(f"{name:15s} {len(audio) / 48000:6.1f} s -> {path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
