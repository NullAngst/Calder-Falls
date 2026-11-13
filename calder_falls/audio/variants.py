"""Pre-rendered music for the Android build.

The Android app has no FluidSynth, so it plays cues rendered ahead of time.
The desktop engine changes a cue while it plays (layers on and off, tempo,
detune, static), and the story leans on that. This module works out which
of those combinations the story can actually reach, renders each one
through the real engine, and writes a manifest the web player reads.
Static bleed is the one control left live: the web player has its own copy.

    python3 -m calder_falls.audio.variants --out DIR            # find + render
    python3 -m calder_falls.audio.variants --out DIR --list     # find only

How a combination is found: the story autoplayer from storytest plays every
scripted route and a batch of wandering walks, with a stand-in audio engine
that records (cue, layers off, tempo, detune) every time one of them changes.
The title screen state (calder_falls, everything on) is always included.
A combination the walks never hit falls back, in the player, to the closest
one rendered for the same cue.

Each looping cue is rendered for two passes and the second pass is kept, so
the file starts with the reverb tail of its own end and loops seamlessly.
"""

import argparse
import json
import os
import sys
import time

import numpy as np
from scipy import signal

from .. import __version__
from . import cues as cue_table

TITLE = ("calder_falls", (), 1.0, 0.0)

# Tempos the walks can't reach. spindle_tempo() in story/act3/spindle.ink
# slows the bar's record on the second visit and every one after, and the
# autoplayer only ever goes in once. Every state the walks find for the cue
# also gets rendered at these tempos.
EXTRA_TEMPOS = {"the_spindle": (0.85, 0.7)}


# ------------------------------------------------------------ discovery

class Recorder:
    """Stands in for AudioEngine.apply_tag and remembers every state."""

    def __init__(self, seen):
        self.seen = seen
        self.cue = None
        self.off = set()
        self.tempo = 1.0
        self.detune = 0.0
        self.reset()

    def reset(self):
        # What the title screen does before every new game
        self.off = set()
        self.tempo = 1.0
        self.detune = 0.0
        self.cue = "calder_falls"
        self._note()

    def _note(self):
        if self.cue:
            self.seen.add((self.cue, tuple(sorted(self.off)), round(self.tempo, 3), round(self.detune, 1)))

    def apply_tag(self, tag):
        key, _, value = tag.strip().lstrip("#").strip().partition(":")
        key, value = key.strip(), value.strip()
        if key == "music":
            self.cue = None if value == "stop" else value
        elif key == "music_layer":
            layer, state = value.split()
            if state == "on":
                self.off.discard(layer)
            else:
                self.off.add(layer)
        elif key == "music_tempo":
            self.tempo = max(0.25, min(2.0, float(value)))
        elif key == "music_detune":
            self.detune = max(-200.0, min(200.0, float(value)))
        elif key in ("music_static", "music_ps2"):
            return True
        else:
            raise ValueError(f"unknown music tag {tag}")
        self._note()
        return True


def discover(walks=40):
    """Every music state the story reaches on the scripted routes and walks."""
    import tempfile

    from .. import storytest

    seen = {TITLE}
    with tempfile.TemporaryDirectory() as tmp:
        runs = [(sum(map(ord, name)), kw) for name, kw in storytest.ROUTES]
        runs += [(1000 + i, dict(wrong=0.35, take_radio=0.8)) for i in range(walks)]
        for seed, kw in runs:
            p = storytest.Player(seed=seed, save_dir=tmp, **kw)
            rec = Recorder(seen)
            p.s.audio = rec
            p.play(limit=9000)
    for cue, off, _tempo, detune in list(seen):
        for t in EXTRA_TEMPOS.get(cue, ()):
            seen.add((cue, off, t, detune))
    out = []
    for cue, off, tempo, detune in sorted(seen):
        try:
            cue_table.get(cue)
        except KeyError:
            raise SystemExit(f"variants: the story plays an unknown cue: {cue}") from None
        out.append({"cue": cue, "off": list(off), "tempo": tempo, "detune": detune})
    return out


# ------------------------------------------------------------ rendering

def variant_name(v):
    parts = [v["cue"]]
    if v["off"]:
        parts.append("no-" + "-".join(v["off"]))
    if v["tempo"] != 1.0:
        parts.append("t%03d" % round(v["tempo"] * 100))
    if v["detune"]:
        parts.append("d%+d" % round(v["detune"]))
    return "_".join(parts)


def render_variant(v, rate, path):
    import soundfile as sf

    from .engine import AudioEngine

    eng = AudioEngine(output=False)
    try:
        data = eng.load(v["cue"])
        for layer in v["off"]:
            eng.set_layer(layer, False)
        eng.set_tempo(v["tempo"])
        eng.set_detune(v["detune"])
        loop = data.cue.loop
        eng.play(v["cue"], loop=loop)
        one = data.length / v["tempo"]
        if loop:
            audio = eng.render(one * 2)
            start = int(round(one * eng.sr))
            audio = audio[start:start + int(round(one * eng.sr))]
        else:
            audio = eng.render(one + 4.0)
        src_rate = eng.sr
    finally:
        eng.close()
    if rate != src_rate:
        g = np.gcd(int(rate), int(src_rate))
        audio = signal.resample_poly(audio, rate // g, src_rate // g, axis=0).astype(np.float32)
    # Written in chunks: libsndfile's Vorbis encoder can crash on one huge write.
    # compression_level 0.6 is roughly Vorbis q4: transparent for music that
    # already went through a 12-bit, 8.5 kHz PS2 filter
    with sf.SoundFile(path, "w", samplerate=rate, channels=2, format="OGG", subtype="VORBIS",
                      compression_level=0.6) as fh:
        for i in range(0, len(audio), 16384):
            fh.write(audio[i:i + 16384])
    return len(audio) / rate, loop


def static_filters(rates):
    """Butterworth sections for the web player's static bleed, the same
    filters engine.StaticBleed uses, for every sample rate it may run at."""
    out = {}
    for r in rates:
        out[str(r)] = {
            "noise": signal.butter(2, [250, 4200], "band", fs=r, output="sos").tolist(),
            "music": signal.butter(2, [380, min(3400, r * 0.45)], "band", fs=r, output="sos").tolist(),
            "crackle": signal.butter(2, [600, min(7000, r * 0.45)], "band", fs=r, output="sos").tolist(),
        }
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Pre-render Calder Falls music for the Android build.")
    ap.add_argument("--out", required=True, help="folder for the .ogg files and manifest.json")
    ap.add_argument("--rate", type=int, default=24000,
                    help="sample rate of the files (the PS2 filter tops out near 8.5 kHz, so 24000 loses nothing)")
    ap.add_argument("--walks", type=int, default=40, help="wandering walks on top of the scripted routes")
    ap.add_argument("--list", action="store_true", help="print the combinations and stop")
    args = ap.parse_args(argv)

    t0 = time.monotonic()
    found = discover(args.walks)
    print(f"variants: {len(found)} music states reachable "
          f"({time.monotonic() - t0:.1f} s of story play)", flush=True)
    for v in found:
        print(f"  {variant_name(v)}", flush=True)
    if args.list:
        return 0

    os.makedirs(args.out, exist_ok=True)
    manifest = {"version": __version__, "rate": args.rate, "cues": {}, "variants": [],
                "static": static_filters((22050, 24000, 44100, 48000))}
    for c in cue_table.CUES:
        manifest["cues"][c.name] = {"title": c.title, "loop": c.loop}
    total = 0
    for v in found:
        name = variant_name(v)
        path = os.path.join(args.out, name + ".ogg")
        t1 = time.monotonic()
        seconds, loop = render_variant(v, args.rate, path)
        size = os.path.getsize(path)
        total += size
        print(f"  {name:40s} {seconds:6.1f} s  {size / 1e6:5.2f} MB  ({time.monotonic() - t1:.1f} s)", flush=True)
        manifest["variants"].append({"file": name + ".ogg", "cue": v["cue"], "off": v["off"],
                                     "tempo": v["tempo"], "detune": v["detune"],
                                     "seconds": round(seconds, 4), "loop": loop})
    with open(os.path.join(args.out, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1)
    print(f"variants: {len(found)} files, {total / 1e6:.1f} MB, {time.monotonic() - t0:.0f} s in all")
    return 0


if __name__ == "__main__":
    sys.exit(main())
