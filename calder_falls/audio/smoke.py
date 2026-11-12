"""Headless checks for the music. Exit code 0 means every check passed.

    python3 -m calder_falls.audio.smoke

What it proves, for every cue in the cue table:
  - the MIDI file exists, loads, and plays through FluidSynth with sound
  - the output is finite and never clips past full scale
  - every control audibly changes it: tempo, detune, each layer the cue
    actually uses, the PS2 filter, static bleed
And once: every Ink music tag form parses, a bad one raises, and the
Mill Floor cut really goes silent.

"Audibly" here means that over a few seconds where the control has
something to act on, the samples change by more than 1% of the mix, or by
more than 3e-4 RMS on their own (about -70 dBFS, well above the 12-bit
floor of the PS2 filter). It is a measurement, not a listening test.
"""

import sys

import numpy as np

from . import cues as cue_table
from .engine import AudioEngine

WINDOW = 4.0
FAILS = []


def check(ok, what):
    if not ok:
        FAILS.append(what)
    print(("  ok   " if ok else "  FAIL ") + what, flush=True)


def rms(a):
    return float(np.sqrt(np.mean(np.square(a, dtype=np.float64))))


def first_note(data, channels=None):
    for t, m in zip(data.times, data.events):
        if isinstance(m, tuple):
            continue
        if m.type == "note_on" and m.velocity > 0 and (channels is None or m.channel in channels):
            return t
    return None


def window(name, at, setup=None, seconds=WINDOW):
    eng = AudioEngine(output=False)
    try:
        if setup:
            setup(eng)
        eng.play(name, fade=0)
        eng.seek(max(0.0, at - 0.25))
        return eng.render(seconds)
    finally:
        eng.close()


# The PS2 filter crunches to 12 bits with dither, so anything quieter than
# about 1e-4 RMS is lost in that noise floor. A control "audibly changes" a
# cue when the difference it makes is either more than 1% of the whole mix,
# or on its own at least 3e-4 RMS (about -70 dBFS), three times that floor.
# The second rule is what lets a deliberately quiet layer, like the tape hiss
# under Dawn's guitar, count as present without depending on how loud the
# rest of the mix is.
NOISE_FLOOR_RMS = 3e-4


def differs(a, b):
    d = rms(a - b)
    base = max(rms(a), 1e-6)
    return d / base > 0.01 or d > NOISE_FLOOR_RMS


def cue_checks(cue):
    print(f"{cue.name}", flush=True)
    eng = AudioEngine(output=False)
    try:
        data = eng.load(cue.name)
    finally:
        eng.close()
    check(bool(data.layers), f"{cue.name}: has notes on known layers {data.layers}")
    t0 = first_note(data) or 0.0
    base = window(cue.name, t0, seconds=8.0)
    check(np.isfinite(base).all(), f"{cue.name}: output is finite")
    check(np.abs(base).max() <= 1.0, f"{cue.name}: no samples past full scale")
    check(20 * np.log10(rms(base) + 1e-12) > -60, f"{cue.name}: plays with sound")
    again = window(cue.name, t0, seconds=8.0)
    check(np.array_equal(base, again), f"{cue.name}: renders the same twice")
    base = base[:int(WINDOW * 48000)]

    tonal = [c for c in data.channels if c != 9]
    tt = first_note(data, set(tonal)) if tonal else t0
    if tt is not None:
        ref = window(cue.name, tt)
        det = window(cue.name, tt, lambda e: e.set_detune(30))
        check(differs(ref, det), f"{cue.name}: detune changes it")
    slow = window(cue.name, t0, lambda e: e.set_tempo(0.8))
    check(differs(base, slow), f"{cue.name}: tempo changes it")
    dry = window(cue.name, t0, lambda e: e.set_ps2(False))
    check(differs(base, dry), f"{cue.name}: PS2 filter changes it")
    noisy = window(cue.name, t0, lambda e: e.set_static(0.5))
    check(differs(base, noisy), f"{cue.name}: static bleed changes it")
    for layer in data.layers:
        chans = set(cue_table.LAYERS[layer])
        tl = first_note(data, chans)
        ref = window(cue.name, tl)
        off = window(cue.name, tl, lambda e, lay=layer: e.set_layer(lay, False))
        check(differs(ref, off), f"{cue.name}: {layer} layer off changes it")


def tag_checks():
    print("tags", flush=True)
    eng = AudioEngine(output=False)
    try:
        good = ["music:cobb_road", "music:stop", "music_layer:drums off", "music_layer:pad on",
                "music_detune:30", "music_detune:-12.5", "music_tempo:0.8",
                "music_static:0.4", "music_ps2:off", "# music:dawn"]
        for tag in good:
            try:
                check(eng.apply_tag(tag) is True, f"tag '{tag}' handled")
            except ValueError as exc:
                check(False, f"tag '{tag}' handled ({exc})")
        check(eng.apply_tag("theme:bleed") is False, "non-music tag left alone")
        for tag in ("music:no_such_cue", "music_layer:drums maybe", "music_layer:kazoo off",
                    "music_tempo:fast", "music_volume:3"):
            try:
                eng.apply_tag(tag)
                check(False, f"bad tag '{tag}' rejected")
            except ValueError:
                check(True, f"bad tag '{tag}' rejected")
    finally:
        eng.close()


def cut_check():
    print("mill_floor cut", flush=True)
    eng = AudioEngine(output=False)
    try:
        data = eng.load("mill_floor")
        cut = next(t for t, m in zip(data.times, data.events)
                   if isinstance(m, tuple) and m[1] == "calder:cut")
        eng.play("mill_floor", fade=0)
        eng.seek(cut - 6)
        a = eng.render(9)
    finally:
        eng.close()
    sr = 48000
    loud = rms(a[2 * sr:5 * sr])
    after = rms(a[int(6.2 * sr):int(8.5 * sr)])
    check(loud > 0.01, "mill_floor is loud before the cut")
    check(after < 1e-3, "mill_floor is silent after the cut")


def main(argv=None):
    names = (argv if argv else sys.argv[1:]) or [c.name for c in cue_table.CUES]
    for name in names:
        cue_checks(cue_table.get(name))
    if not argv and len(sys.argv) <= 1:
        tag_checks()
        cut_check()
    print()
    if FAILS:
        print(f"{len(FAILS)} check(s) failed:")
        for f in FAILS:
            print(f"  {f}")
        return 1
    print("all music checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
