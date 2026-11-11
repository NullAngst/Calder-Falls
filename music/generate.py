"""Write every Calder Falls music cue as a standard MIDI file.

Each cue is a function below that sets its rules: tempo, chord loop, motif,
drum pattern, instruments, and where it varies. Every rule is plain Python
so a cue can be changed and regenerated in seconds:

    python3 music/generate.py            # all cues
    python3 music/generate.py june       # one cue
    python3 music/generate.py --out DIR  # somewhere else

Channel layout is the same in every cue, because the engine mutes layers
by channel:
    lead  : 0, 1, 10     pad   : 2, 11, 12     bass : 3
    noise : 4, 5, 6      drums : 9 (GM kit), 7, 8 (Calder metal)

Banks: 0 is General MIDI from the base bank, 128 is GM drums, 20 is Calder.sf2.
Every melody, chord loop and pattern here was written for this game.
"""

import math
import os
import random
import sys

import mido

TPB = 480
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cues")

CALDER = 20
GM = 0
DRUMS = 128

# Calder.sf2 programs
TREM_MANDOLIN, MANDOLIN, EPIANO, REV_PIANO, DIST_BASS, TAPE_PAD, SUB_DRONE = 0, 1, 2, 3, 4, 5, 6
METAL_KIT, SCRAPE, HISS, STATIC, HOUSE = 8, 9, 10, 11, 12

# General MIDI programs we use from the base bank
GM_PIANO, GM_HONKY, GM_DRAWBAR, GM_CHURCH_ORGAN = 0, 3, 16, 19
GM_NYLON, GM_STEEL, GM_CLEAN_GTR = 24, 25, 27
GM_ACOUSTIC_BASS, GM_FINGER_BASS = 32, 33
GM_CHOIR, GM_VOICE_OOHS, GM_SYNTH_VOICE = 52, 53, 54

# GM drum keys
KICK, STICK, SNARE, CLAP, HAT, PEDAL_HAT, OPEN_HAT = 36, 37, 38, 39, 42, 44, 46
CRASH, RIDE, TAMB, LOW_TOM, MID_TOM = 49, 51, 54, 45, 47
BRUSH_TAP, BRUSH_SWIRL = 38, 40

NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def n(name):
    """'F#4' -> 66. Octave 4 holds middle C (60)."""
    if isinstance(name, int):
        return name
    pc = NAMES[name[0]]
    rest = name[1:]
    while rest and rest[0] in "#b":
        pc += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    return pc + 12 * (int(rest) + 1)


class Song:
    def __init__(self, name, bpm, beats, seed=None, timesig=(4, 4)):
        self.name = name
        self.bpm = bpm
        self.length = beats
        self.rng = random.Random(seed if seed is not None else name)
        self.events = {}       # channel -> list of (tick, order, msg)
        self.meta = [(0, 0, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm))),
                     (0, 1, mido.MetaMessage("time_signature", numerator=timesig[0],
                                             denominator=timesig[1])),
                     (0, 2, mido.MetaMessage("track_name", name=name))]
        self.used = set()

    # timing ----------------------------------------------------------
    def tick(self, beat):
        return int(round(beat * TPB))

    def ms(self, ms):
        """Milliseconds in beats at this tempo."""
        return ms / 1000.0 * self.bpm / 60.0

    def sec(self, seconds):
        return seconds * self.bpm / 60.0

    def _add(self, ch, beat, msg, order=5):
        beat = max(0.0, beat)
        self.events.setdefault(ch, []).append((self.tick(beat), order, msg))

    # messages --------------------------------------------------------
    def setup(self, ch, bank, prog, vol=100, pan=64, rev=40, cho=0, expr=127):
        self._add(ch, 0, mido.Message("control_change", channel=ch, control=0, value=bank % 128), 0)
        self._add(ch, 0, mido.Message("program_change", channel=ch, program=prog), 1)
        for cc, v in ((7, vol), (10, pan), (91, rev), (93, cho), (11, expr),
                      (101, 0), (100, 0), (6, 2), (38, 0)):
            self._add(ch, 0, mido.Message("control_change", channel=ch, control=cc, value=v), 2)
        self.used.add(ch)

    def note(self, ch, pitch, start, dur, vel, jitter=8.0):
        if start >= self.length:
            return
        pitch = n(pitch)
        if not 0 <= pitch <= 127:
            return
        j = self.ms(self.rng.uniform(-jitter, jitter)) if jitter else 0.0
        s = max(0.0, start + j)
        e = min(start + dur + j * 0.5, self.length - 0.02)
        if e <= s + 0.01:
            e = min(s + 0.05, self.length - 0.01)
        v = int(max(1, min(127, vel)))
        self._add(ch, s, mido.Message("note_on", channel=ch, note=pitch, velocity=v), 6)
        self._add(ch, e, mido.Message("note_off", channel=ch, note=pitch, velocity=0), 4)

    def chord(self, ch, pitches, start, dur, vel, spread=0.0, jitter=6.0):
        for i, p in enumerate(pitches):
            self.note(ch, p, start + i * spread, dur - i * spread, vel + self.rng.randint(-5, 5), jitter)

    def cc(self, ch, control, value, at):
        self._add(ch, at, mido.Message("control_change", channel=ch, control=control,
                                       value=int(max(0, min(127, value)))), 3)

    def ramp(self, ch, control, v0, v1, start, end, step=0.25):
        b = start
        while b <= end:
            f = (b - start) / max(end - start, 1e-6)
            self.cc(ch, control, v0 + (v1 - v0) * f, b)
            b += step

    def bend(self, ch, cents, at):
        val = int(max(-8192, min(8191, cents / 200.0 * 8192)))
        self._add(ch, at, mido.Message("pitchwheel", channel=ch, pitch=val), 3)

    def marker(self, text, at):
        self.meta.append((self.tick(at), 3, mido.MetaMessage("marker", text=text)))

    def all_off(self, at):
        for ch in sorted(self.used):
            self.cc(ch, 120, 0, at)

    # output ----------------------------------------------------------
    def save(self, path):
        mid = mido.MidiFile(type=1, ticks_per_beat=TPB)
        end_tick = self.tick(self.length)

        def track(items, name=None):
            tr = mido.MidiTrack()
            if name:
                tr.append(mido.MetaMessage("track_name", name=name, time=0))
            last = 0
            for tk, _, msg in sorted(items, key=lambda x: (x[0], x[1])):
                tk = min(tk, end_tick)
                tr.append(msg.copy(time=tk - last))
                last = tk
            tr.append(mido.MetaMessage("end_of_track", time=end_tick - last))
            return tr

        mid.tracks.append(track(self.meta))
        for ch in sorted(self.events):
            mid.tracks.append(track(self.events[ch], f"ch{ch}"))
        mid.save(path)
        return mid


# ------------------------------------------------------------ shared material

# Chords: name -> (bass note, upper voicing)
CH = {
    "Em9": ("E2", ["E3", "G3", "B3", "F#4"]),
    "Em": ("E2", ["E3", "G3", "B3", "E4"]),
    "Em/D": ("D2", ["E3", "G3", "B3", "E4"]),
    "Cmaj7#11": ("C2", ["C3", "E3", "B3", "F#4"]),
    "Am7": ("A1", ["A2", "E3", "G3", "C4"]),
    "B7sus4": ("B1", ["B2", "E3", "A3", "F#4"]),
    "B7": ("B1", ["B2", "D#3", "A3", "F#4"]),
    "Em/G": ("G1", ["G2", "E3", "B3", "F#4"]),
    "Fmaj7#11": ("F1", ["F3", "A3", "B3", "E4"]),
    "D": ("D2", ["D3", "F#3", "A3", "D4"]),
    "Cmaj7": ("C2", ["C3", "E3", "G3", "B3"]),
    "Emaj9": ("E2", ["E3", "G#3", "B3", "F#4"]),
}

# The Calder Falls theme. 8 bars of 4/4 in E minor, one chord per bar:
# Em9 Em9 Cmaj7#11 Cmaj7#11 Am7 Am7 B7sus4 B7
THEME_CHORDS = ["Em9", "Em9", "Cmaj7#11", "Cmaj7#11", "Am7", "Am7", "B7sus4", "B7"]
THEME = [
    ("B4", 0, 1.5), ("A4", 1.5, .5), ("G4", 2, 1), ("F#4", 3, 1),
    ("E4", 4, 2), ("G4", 6, .5), ("A4", 6.5, .5), ("B4", 7, 1),
    ("C5", 8, 1.5), ("B4", 9.5, .5), ("A4", 10, 1), ("F#4", 11, 1),
    ("G4", 12, 3),
    ("A4", 16, 1), ("C5", 17, 1), ("E5", 18, 1.5), ("D5", 19.5, .5),
    ("C5", 20, 1), ("B4", 21, 1), ("A4", 22, 2),
    ("E5", 24, 1), ("D5", 25, .5), ("B4", 25.5, 1.5), ("A4", 27, 1),
    ("D#5", 28, 2), ("B4", 30, 2),
]
# The answering phrase: same first six bars, last two come home to E.
THEME_ANSWER = THEME[:-6] + [
    ("E5", 24, 1), ("D5", 25, .5), ("B4", 25.5, 1), ("G4", 26.5, .5), ("A4", 27, 1),
    ("B4", 28, 1), ("E4", 29, 3),
]
ANSWER_CHORDS = ["Em9", "Em9", "Cmaj7#11", "Cmaj7#11", "Am7", "Am7", "B7sus4", "Em9"]


def play_phrase(s, ch, phrase, start, vel=90, transpose=0, jitter=10, legato=0.95):
    for p, b, d in phrase:
        accent = 8 if b % 4 == 0 else 0
        s.note(ch, n(p) + transpose, start + b, d * legato, vel + accent + s.rng.randint(-6, 6), jitter)


def pad_chords(s, ch, chords, start, vel=55, bar=4, octave=0):
    for i, c in enumerate(chords):
        _, voi = CH[c]
        s.chord(ch, [n(x) + 12 * octave for x in voi], start + i * bar, bar, vel, jitter=15)


def arp(s, ch, chords, start, vel=60, pattern=(0, 2, 1, 3, 2, 4, 3, 2), step=0.5, bar=4,
        swing=0.0, octave=0, skip=0.0):
    for i, c in enumerate(chords):
        bass, voi = CH[c]
        tones = [n(bass) + 12] + [n(x) for x in voi]
        steps = int(bar / step)
        for k in range(steps):
            if skip and s.rng.random() < skip:
                continue
            tone = tones[pattern[k % len(pattern)] % len(tones)] + 12 * octave
            pos = start + i * bar + k * step
            if swing and k % 2 == 1:
                pos += swing * step
            v = vel + (6 if k % 4 == 0 else 0) + s.rng.randint(-7, 4)
            s.note(ch, tone, pos, step * 2.2, v, jitter=7)


def triphop_bar(s, start, var=0, vel=1.0, ch=9, swing=0.12, layback_ms=22):
    """One bar of slow trip-hop: heavy kick, laid-back snare on 2 and 4,
    swung hats, ghost notes. var picks a kick pattern."""
    kicks = [(0, 0.75, 2.5), (0, 0.75, 2.25, 2.5), (0, 1.75, 2.5, 3.25), (0, 2.5, 2.75)][var % 4]
    for k in kicks:
        s.note(ch, KICK, start + k, 0.25, (108 if k == 0 else 92) * vel, jitter=4)
    lb = s.ms(layback_ms)
    for b in (1, 3):
        s.note(ch, SNARE, start + b + lb, 0.25, 100 * vel, jitter=5)
    for g in (1.75, 3.75):
        if s.rng.random() < 0.55:
            s.note(ch, SNARE, start + g + lb, 0.1, 26 * vel, jitter=8)
    for i in range(8):
        pos = start + i * 0.5 + (swing if i % 2 else 0)
        if i == 7 and s.rng.random() < 0.4:
            s.note(ch, OPEN_HAT, pos, 0.4, 62 * vel, jitter=6)
        else:
            s.note(ch, HAT, pos, 0.1, (70 if i % 2 == 0 else 48) * vel + s.rng.randint(-8, 8), jitter=6)


def triphop_fill(s, start, vel=1.0, ch=9):
    lb = s.ms(20)
    for i, b in enumerate((2, 2.5, 3, 3.25, 3.5, 3.75)):
        s.note(ch, SNARE, start + b + lb, 0.1, (50 + i * 10) * vel, jitter=5)
    s.note(ch, KICK, start, 0.25, 104 * vel)
    s.note(ch, KICK, start + 0.75, 0.25, 88 * vel)


def triphop_bass(s, ch, chords, start, vel=92, bar=4, figure=0):
    figs = [
        [(0, 1.4, 0), (1.75, .25, 0), (2.5, .9, 12), (3.5, .4, 10)],
        [(0, 2.4, 0), (2.5, .5, 0), (3.25, .6, 7)],
        [(0, .7, 0), (.75, .7, 0), (2.5, .5, 0), (3, .4, 12), (3.5, .4, 7)],
    ]
    for i, c in enumerate(chords):
        root = n(CH[c][0])
        for b, d, iv in figs[figure % len(figs)]:
            s.note(ch, root + iv, start + i * bar + b, d, vel + s.rng.randint(-6, 6), jitter=5)


# ------------------------------------------------------------ cues

def cue_calder_falls():
    """Title and the drive in. 78 bpm trip-hop, tremolo mandolin carries the
    theme. Intro 4, A 8, A' 8, bridge 8, A 8, outro 4."""
    s = Song("calder_falls", 78, 40 * 4)
    s.setup(0, CALDER, TREM_MANDOLIN, vol=104, pan=60, rev=60)
    s.setup(1, GM, GM_STEEL, vol=80, pan=78, rev=55)
    s.setup(2, CALDER, TAPE_PAD, vol=78, pan=64, rev=70)
    s.setup(3, GM, GM_FINGER_BASS, vol=100, pan=64, rev=15)
    s.setup(4, CALDER, HISS, vol=50, rev=0)
    s.setup(9, DRUMS, 0, vol=110, rev=35)
    B = 4
    intro = ["Em9", "Cmaj7#11", "Am7", "B7sus4"]
    bridge = ["Am7", "Em/G", "Fmaj7#11", "B7sus4", "Am7", "Em/G", "Fmaj7#11", "B7"]
    s.note(4, 60, 0, s.length - 0.1, 70, jitter=0)

    # intro: pad and guitar, mandolin hints at the first bar of the theme
    pad_chords(s, 2, intro, 0, vel=50)
    arp(s, 1, intro, 0, vel=50, skip=0.15)
    play_phrase(s, 0, [("B4", 0, 1.5), ("A4", 1.5, .5), ("G4", 2, 2)], 12 * 1, vel=70)

    # A
    a0 = 4 * B
    pad_chords(s, 2, THEME_CHORDS, a0, vel=52)
    triphop_bass(s, 3, THEME_CHORDS, a0, figure=0)
    play_phrase(s, 0, THEME, a0, vel=92)
    for i in range(8):
        triphop_bar(s, a0 + i * B, var=(0 if i % 4 != 3 else 1))
    triphop_fill(s, a0 + 7 * B)

    # A': guitar joins, the answer comes home
    a1 = 12 * B
    pad_chords(s, 2, ANSWER_CHORDS, a1, vel=52)
    arp(s, 1, ANSWER_CHORDS, a1, vel=56, swing=0.1)
    triphop_bass(s, 3, ANSWER_CHORDS, a1, figure=2)
    play_phrase(s, 0, THEME_ANSWER, a1, vel=94)
    for i in range(8):
        triphop_bar(s, a1 + i * B, var=(2 if i % 2 else 0))
    s.note(9, CRASH, a1, 2, 70)

    # bridge: drums thin out, mandolin answers the guitar
    b0 = 20 * B
    pad_chords(s, 2, bridge, b0, vel=58)
    arp(s, 1, bridge, b0, vel=60, pattern=(0, 3, 2, 4, 1, 3, 2, 4))
    triphop_bass(s, 3, bridge, b0, figure=1)
    counter = [("E5", 0, 3), ("D5", 3, 1), ("B4", 4, 4),
               ("C5", 8, 2), ("B4", 10, 1), ("A4", 11, 1), ("F#4", 12, 4),
               ("E5", 16, 3), ("F#5", 19, 1), ("G5", 20, 2), ("F#5", 22, 2),
               ("E5", 24, 2), ("C5", 26, 2), ("D#5", 28, 4)]
    play_phrase(s, 0, counter, b0, vel=86)
    for i in range(8):
        if i in (0, 1, 4, 5):
            for k in range(8):
                s.note(9, HAT, b0 + i * B + k * .5 + (.12 if k % 2 else 0), .1, 46, jitter=6)
            s.note(9, KICK, b0 + i * B, .25, 90)
        else:
            triphop_bar(s, b0 + i * B, var=3, vel=0.9)
    triphop_fill(s, b0 + 7 * B)

    # A again
    a2 = 28 * B
    pad_chords(s, 2, THEME_CHORDS, a2, vel=54)
    arp(s, 1, THEME_CHORDS, a2, vel=50, skip=0.3)
    triphop_bass(s, 3, THEME_CHORDS, a2, figure=0)
    play_phrase(s, 0, THEME, a2, vel=94)
    for i in range(8):
        triphop_bar(s, a2 + i * B, var=(1 if i % 2 else 0))
    s.note(9, CRASH, a2, 2, 64)

    # outro: back to the intro, the last chord just hangs
    o0 = 36 * B
    pad_chords(s, 2, ["Em9", "Cmaj7#11", "Am7", "Em9"], o0, vel=48)
    arp(s, 1, ["Em9", "Cmaj7#11"], o0, vel=44, skip=0.3)
    s.note(3, "E2", o0, 6, 80)
    play_phrase(s, 0, [("B4", 0, 1.5), ("A4", 1.5, .5), ("G4", 2, 1), ("F#4", 3, 1), ("E4", 4, 3.5)],
                o0 + 4, vel=72)
    return s


def cue_cobb_road():
    """The Harlan house, early loops. No tempo: the grid is one beat per
    second. Fridge hum, a clock, a pad you barely notice. Once per loop the
    fridge cuts out and the clock skips."""
    s = Song("cobb_road", 60, 150)
    s.setup(4, CALDER, HOUSE, vol=84, rev=10)   # fridge
    s.setup(5, CALDER, HOUSE, vol=76, pan=74, rev=35)  # clock
    s.setup(2, CALDER, TAPE_PAD, vol=62, rev=90)
    s.setup(7, CALDER, METAL_KIT, vol=60, rev=60)
    s.note(4, 60, 0.0, 108, 72, jitter=0)
    s.note(4, 60, 121, 28.9, 72, jitter=0)
    s.note(7, 36, 120.6, 2, 28, jitter=0)       # compressor clunk on restart
    skip = 87
    for sec in range(150):
        if sec == skip:
            continue
        s.note(5, 62 if sec % 2 == 0 else 64, sec, 0.2, 70 + s.rng.randint(-4, 4), jitter=2)
    # pad: low, slow, changes you notice late
    for at, notes, dur in ((2, ["E2", "B2"], 28), (32, ["F2", "C3"], 26), (60, ["D2", "A2", "E3"], 30),
                           (92, ["E2", "B2", "C3"], 26), (120, ["E2", "B2"], 28)):
        s.chord(2, notes, at, dur, 30, jitter=0)
        s.ramp(2, 11, 40, 100, at, at + dur * 0.5, step=1)
        s.ramp(2, 11, 100, 40, at + dur * 0.5, at + dur - 1, step=1)
    return s


def cue_june():
    """June is near. One detuned piano note on repeat over a low drone,
    sometimes doubled like a heartbeat, sometimes answered backwards."""
    s = Song("june", 60, 120)
    s.setup(2, CALDER, SUB_DRONE, vol=100, rev=30)
    s.setup(0, GM, GM_PIANO, vol=112, pan=58, rev=100)
    s.setup(1, CALDER, REV_PIANO, vol=80, pan=70, rev=110)
    s.bend(0, -38, 0)
    s.note(2, "E1", 0.0, 119.8, 96, jitter=0)
    s.note(2, "E2", 30, 40, 40, jitter=0)
    at = 1.5
    while at < 116:
        v = s.rng.randint(42, 70)
        s.note(0, "D#4", at, 2.5, v, jitter=0)
        if s.rng.random() < 0.22:
            s.note(0, "D#4", at + 0.42, 2.0, v - 16, jitter=0)
        at += s.rng.uniform(2.8, 4.6)
    for at in (24, 58, 97):
        s.note(1, "D#3", at, 3.15, 80, jitter=0)
    return s


def cue_the_hush():
    """Town exploration in the fog. 70 bpm, sparse nylon guitar with long
    gaps, a pad for the fog, the odd mandolin note far off."""
    s = Song("the_hush", 70, 32 * 4)
    s.setup(1, GM, GM_NYLON, vol=120, pan=60, rev=80)
    s.setup(0, CALDER, MANDOLIN, vol=70, pan=86, rev=110)
    s.setup(2, CALDER, TAPE_PAD, vol=58, rev=100)
    s.setup(4, CALDER, HISS, vol=44)
    ch_local = {
        "Am9": ("A1", ["A2", "E3", "B3", "C4"]),
        "Fmaj7": ("F1", ["F2", "C3", "E3", "A3"]),
        "Cmaj7/G": ("G1", ["G2", "C3", "E3", "B3"]),
        "Dm9": ("D2", ["D3", "F3", "C4", "E4"]),
    }
    CH.update(ch_local)
    prog = ["Am9", "Fmaj7", "Cmaj7/G", "Dm9"]
    s.note(4, 60, 0, s.length - 0.1, 60, jitter=0)
    for i in range(8):
        c = prog[i % 4]
        pad_chords(s, 2, [c, c], i * 16, vel=40, bar=8, octave=0)
    # guitar phrases: 2 bars of playing, 2 bars of nothing
    phrase_bars = [0, 4, 8, 12, 16, 20, 24, 28]
    for pb in phrase_bars:
        c = prog[(pb // 4) % 4]
        bass, voi = CH[c]
        tones = [n(bass) + 12] + [n(x) + 12 for x in voi]
        start = pb * 4
        s.note(1, tones[0], start, 4, 60)
        order = [2, 3, 4, 3] if pb % 8 == 0 else [4, 3, 2, 1]
        for k, idx in enumerate(order):
            s.note(1, tones[idx], start + 1 + k * 0.75, 3, 52 - k * 3, jitter=20)
        s.note(1, tones[1], start + 5.5, 2.5, 44, jitter=20)
    for at, p in ((22, "E5"), (55, "C6"), (88, "B5"), (114, "A5")):
        s.note(0, p, at, 2, 46, jitter=0)
    return s


def cue_substation():
    """Police substation, the safe room. 84 bpm, warm electric piano,
    brushes, upright bass. The closest thing to comfort in the game."""
    s = Song("substation", 84, 32 * 4)
    s.setup(2, CALDER, EPIANO, vol=92, pan=58, rev=55)
    s.setup(0, CALDER, EPIANO, vol=110, pan=72, rev=60)
    s.setup(3, GM, GM_ACOUSTIC_BASS, vol=84, rev=20)
    s.setup(9, DRUMS, 40, vol=78, rev=40)          # GM brush kit
    s.setup(4, CALDER, HISS, vol=36)
    CH.update({
        "Dmaj9": ("D2", ["F#3", "A3", "C#4", "E4"]),
        "Bm9": ("B1", ["D3", "A3", "C#4", "F#4"]),
        "Gmaj9": ("G1", ["F#3", "A3", "B3", "D4"]),
        "A7sus4": ("A1", ["G3", "A3", "D4", "E4"]),
        "Em9b": ("E2", ["G3", "B3", "D4", "F#4"]),
        "F#m7": ("F#2", ["E3", "A3", "C#4", "E4"]),
        "A13": ("A1", ["G3", "C#4", "F#4", "B4"]),
    })
    prog = ["Dmaj9", "Bm9", "Gmaj9", "A7sus4", "Em9b", "F#m7", "Gmaj9", "A13"]
    s.note(4, 60, 0, s.length - 0.1, 50, jitter=0)
    melody = [("F#5", 0, 1.5), ("E5", 1.5, .5), ("D5", 2, 2),
              ("C#5", 4, 1), ("D5", 5, 1), ("F#5", 6, 2),
              ("A5", 8, 1.5), ("G5", 9.5, .5), ("F#5", 10, 1), ("D5", 11, 1),
              ("E5", 12, 4),
              ("B4", 16, 1), ("D5", 17, 1), ("F#5", 18, 2),
              ("E5", 20, 1.5), ("C#5", 21.5, .5), ("A4", 22, 2),
              ("B4", 24, 1), ("D5", 25, 1), ("G5", 26, 2),
              ("F#5", 28, 2), ("E5", 30, 2)]
    for rep in range(4):
        base = rep * 32
        for i, c in enumerate(prog):
            bass, voi = CH[c]
            # comping: chord on 1, a softer push on the and of 2
            s.chord(2, voi, base + i * 4, 1.9, 58, spread=0.02)
            s.chord(2, voi, base + i * 4 + 2.5, 1.4, 44, spread=0.02)
            # walking-ish bass in half notes with a pickup
            r = n(bass)
            s.note(3, r, base + i * 4, 1.9, 86)
            s.note(3, r + 7, base + i * 4 + 2, 1.4, 74)
            s.note(3, r + (5 if i % 2 else 10), base + i * 4 + 3.5, 0.45, 64)
            # brushes
            for k in range(4):
                s.note(9, BRUSH_SWIRL, base + i * 4 + k, 0.9, 34, jitter=10)
            for b in (1, 3):
                s.note(9, BRUSH_TAP, base + i * 4 + b + s.ms(15), 0.2, 54, jitter=8)
            s.note(9, KICK, base + i * 4, 0.25, 58)
            if i % 2:
                s.note(9, KICK, base + i * 4 + 2.5, 0.25, 44)
        if rep in (1, 3):
            play_phrase(s, 0, melody, base, vel=64, jitter=14, legato=0.9)
        elif rep == 2:
            play_phrase(s, 0, melody[:10], base, vel=58, transpose=-12, jitter=14)
    return s


def cue_listening_room():
    """Any Bleed house. Metal being hit and dragged, static that swells
    and drains, drones that refuse a key. No tempo, no tonal centre."""
    s = Song("listening_room", 60, 120)
    s.setup(7, CALDER, METAL_KIT, vol=100, pan=50, rev=90)
    s.setup(8, CALDER, METAL_KIT, vol=90, pan=80, rev=110)
    s.setup(5, CALDER, SCRAPE, vol=90, pan=70, rev=100)
    s.setup(6, CALDER, STATIC, vol=96, rev=50)
    s.setup(2, CALDER, SUB_DRONE, vol=100, rev=40)
    # drones that move by tritones and semitones
    at = 0
    for p, d in (("C1", 24), ("F#1", 20), ("C#1", 26), ("G1", 22), ("C1", 27.8)):
        s.note(2, p, at, d, 90, jitter=0)
        if p in ("C#1", "G1"):
            s.note(2, n(p) + 6, at + 4, d - 6, 50, jitter=0)
        at += d
    # metal: clusters of hits with long silences between
    at = 2.0
    while at < 114:
        burst = s.rng.randint(1, 5)
        for k in range(burst):
            key = 36 + 2 * s.rng.randint(0, 5) + s.rng.randint(0, 1)
            ch = 7 if s.rng.random() < 0.6 else 8
            s.note(ch, key, at + k * s.rng.uniform(0.15, 0.7), 3, s.rng.randint(40, 110), jitter=0)
        at += s.rng.uniform(3.0, 9.0)
    for at, p in ((14, 52), (47, 58), (79, 49), (101, 61)):
        s.note(5, p, at, s.rng.uniform(3.0, 6.0), 90, jitter=0)
    # static swells
    s.note(6, 60, 0.5, 119, 100, jitter=0)
    s.cc(6, 11, 10, 0)
    for k, at in enumerate((6, 33, 61, 90)):
        peak = 110 if k % 2 else 85
        s.ramp(6, 11, 10, peak, at, at + 8, step=0.5)
        s.ramp(6, 11, peak, 10, at + 9, at + 16, step=0.5)
    return s


def cue_fellowship():
    """St. Adalbert's parish hall. 66 bpm, an upright piano nobody has
    tuned since the mill closed. Shaped like a hymn, harmony that goes
    one step wrong, phrases that run a bar short."""
    s = Song("fellowship", 66, 116)
    s.setup(0, GM, GM_HONKY, vol=96, pan=56, rev=70)
    s.setup(3, GM, GM_HONKY, vol=90, pan=50, rev=70)
    s.setup(4, CALDER, HISS, vol=40)
    s.note(4, 60, 0, s.length - 0.1, 50, jitter=0)
    # wow: the two hands drift against each other
    b = 0.0
    while b < s.length:
        s.bend(0, 14 * math.sin(b * 0.37), b)
        s.bend(3, -10 * math.sin(b * 0.29 + 1.0), b)
        b += 0.5
    # (melody, chord) per beat. F major, 4-bar and 3-bar phrases.
    F, Bb, C, Dm, Gm, Db, E = (["A3", "C4", "F4"], ["Bb3", "D4", "F4"], ["G3", "C4", "E4"],
                               ["A3", "D4", "F4"], ["Bb3", "D4", "G4"], ["Ab3", "Db4", "F4"],
                               ["G#3", "B3", "E4"])
    BASS = {id(F): "F2", id(Bb): "Bb1", id(C): "C2", id(Dm): "D2", id(Gm): "G1", id(Db): "Db2", id(E): "E2"}
    hymn = [
        # phrase 1, 4 bars
        ("A4", F, 1), ("A4", F, 1), ("Bb4", Bb, 1), ("C5", F, 1),
        ("C5", Dm, 1), ("Bb4", Gm, 1), ("A4", F, 2),
        ("G4", C, 1), ("A4", F, 1), ("Bb4", Gm, 1), ("A4", Dm, 1),
        ("G4", C, 3), (None, None, 1),
        # phrase 2, 3 bars, ends on a chord that is not in the key
        ("C5", F, 1), ("D5", Bb, 1), ("C5", F, 1), ("Bb4", Gm, 1),
        ("A4", F, 1), ("Ab4", Db, 1), ("F4", Db, 2),
        ("G4", C, 3), (None, None, 1),
        # phrase 3, 4 bars
        ("A4", F, 1), ("C5", F, 1), ("F5", Dm, 1), ("E5", C, 1),
        ("D5", Bb, 1), ("C5", F, 1), ("Bb4", Gm, 2),
        ("A4", F, 1), ("G4", C, 1), ("F4", Dm, 1), ("E4", C, 1),
        ("F4", F, 3), (None, None, 1),
        # phrase 4, 3 bars, the amen lands on E major and stays there
        ("C5", F, 1), ("Bb4", Bb, 1), ("A4", F, 1), ("G4", C, 1),
        ("G#4", E, 2), ("B4", E, 2),
        ("G#4", E, 4),
    ]
    beat = 0.0
    for rep in range(2):
        for mel, chord, d in hymn:
            if mel is not None:
                s.note(0, mel, beat, d * 0.95, 78, jitter=25)
                s.chord(0, [n(x) for x in chord], beat, d * 0.92, 56, spread=0.015, jitter=25)
                bass = BASS[id(chord)]
                s.note(3, bass, beat, d * 0.95, 70, jitter=25)
                s.note(3, n(bass) - 12, beat, d * 0.95, 52, jitter=25)
            beat += d
        beat += 2  # a breath between verses
    s.length = beat
    return s


def cue_the_spindle():
    """The bar. 90 bpm, a jukebox record in a minor blues shape. The game
    slows it on each visit with # music_tempo, the file stays at 90."""
    s = Song("the_spindle", 90, 24 * 4)
    s.setup(0, GM, GM_CLEAN_GTR, vol=110, pan=70, rev=45)
    s.setup(2, GM, GM_DRAWBAR, vol=82, pan=50, rev=40)
    s.setup(3, GM, GM_FINGER_BASS, vol=88, rev=15)
    s.setup(9, DRUMS, 0, vol=84, rev=30)
    s.setup(4, CALDER, HISS, vol=52)
    s.note(4, 60, 0, s.length - 0.1, 60, jitter=0)
    CH.update({
        "Am7b": ("A1", ["G3", "C4", "E4"]),
        "Dm7b": ("D2", ["F3", "A3", "C4"]),
        "E7b": ("E2", ["G#3", "B3", "D4"]),
        "F7b": ("F2", ["A3", "C4", "Eb4"]),
    })
    form = ["Am7b"] * 4 + ["Dm7b"] * 2 + ["Am7b"] * 2 + ["E7b", "F7b", "Am7b", "E7b"]
    sw = 1 / 3  # shuffle: the second eighth sits on the last triplet
    lick = [("E5", 0, .5), ("G5", .67, .3), ("A5", 1, 1.5), ("G5", 2.67, .3), ("E5", 3, 1),
            ("D5", 4, .5), ("E5", 4.67, .3), ("C5", 5, 2.5), ("A4", 7.67, .3),
            ("C5", 8, 1), ("D5", 9, .5), ("E5", 9.67, 1.3), ("G4", 11, 1),
            ("A4", 12, 3.5)]
    for rep in range(2):
        base = rep * 48
        for i, c in enumerate(form):
            bar = base + i * 4
            bass, voi = CH[c]
            r = n(bass)
            for k, iv in enumerate((0, 7, 9, 7)):
                s.note(3, r + iv, bar + k, 0.6, 88 - (k % 2) * 10)
                s.note(3, r + iv + (12 if k == 3 else 0), bar + k + 0.5 + sw * 0.5, 0.3, 60)
            s.chord(2, voi, bar, 3.9, 46, jitter=10)
            for k in (1, 3):
                s.chord(0, [x + 12 for x in map(n, voi)], bar + k, 0.35, 58, spread=0.01)
            for k in range(4):
                s.note(9, RIDE if rep else HAT, bar + k, 0.2, 64)
                s.note(9, HAT, bar + k + 0.5 + sw * 0.5, 0.1, 44)
            s.note(9, KICK, bar, 0.25, 92)
            s.note(9, KICK, bar + 2, 0.25, 84)
            s.note(9, SNARE, bar + 1 + s.ms(12), 0.25, 84)
            s.note(9, SNARE, bar + 3 + s.ms(12), 0.25, 88)
        # the lick over bars 1-4 and 9-12 of each chorus
        play_phrase(s, 0, lick, base, vel=86, transpose=0)
        play_phrase(s, 0, lick[:9], base + 32, vel=82, transpose=-2 if rep else 0)
    return s


def cue_precentor():
    """Margaret Lusk. 72 bpm, an organ pad and a voice-like synth, warm
    major chords on top, a D drone a tritone underneath. Kind on the
    surface. Cold all the way down."""
    s = Song("precentor", 72, 32 * 4)
    s.setup(2, GM, GM_CHURCH_ORGAN, vol=84, pan=60, rev=90)
    s.setup(0, GM, GM_SYNTH_VOICE, vol=114, pan=66, rev=100)
    s.setup(3, CALDER, SUB_DRONE, vol=96, rev=20)
    s.setup(11, CALDER, TAPE_PAD, vol=70, rev=80)
    s.setup(9, DRUMS, 0, vol=60, rev=60)
    s.setup(4, CALDER, HISS, vol=40)
    s.note(4, 60, 0, s.length - 0.1, 50, jitter=0)
    top = [["Ab4", "C5", "Eb5"], ["F4", "Ab4", "C5"], ["F4", "Ab4", "Db5"], ["G4", "Bb4", "Eb5"]]
    for i in range(16):
        s.chord(2, top[i % 4], i * 8, 8, 52, jitter=12)
    for i in range(4):
        s.note(3, "D1", i * 32, 32, 96, jitter=0)
        s.chord(11, ["D2", "A2"], i * 32, 32, 44, jitter=0)
    voice = [("Eb5", 0, 3), ("C5", 3, 1), ("Ab4", 4, 4),
             ("C5", 8, 2), ("Db5", 10, 2), ("C5", 12, 4),
             ("Bb4", 16, 3), ("Ab4", 19, 1), ("F4", 20, 4),
             ("G4", 24, 2), ("Ab4", 26, 2), ("Bb4", 28, 4)]
    for rep in (1, 2, 3):
        play_phrase(s, 0, voice, rep * 32, vel=70, jitter=12, legato=1.0)
    # a pulse like a slow heart, almost not there
    b = 0
    while b < s.length - 1:
        s.note(9, KICK, b, 0.25, 34, jitter=6)
        s.note(9, KICK, b + 0.5, 0.25, 22, jitter=6)
        b += 2
    return s


def cue_water_tower():
    """Act IV, the climb. 88 bpm, the full beat, distorted bass, metal on
    the accents, and the mandolin brings the theme back up the ladder."""
    s = Song("water_tower", 88, 40 * 4)
    s.setup(0, CALDER, TREM_MANDOLIN, vol=108, pan=60, rev=55)
    s.setup(1, GM, GM_STEEL, vol=78, pan=80, rev=50)
    s.setup(2, CALDER, TAPE_PAD, vol=78, rev=70)
    s.setup(3, CALDER, DIST_BASS, vol=102, rev=10)
    s.setup(7, CALDER, METAL_KIT, vol=88, pan=44, rev=80)
    s.setup(9, DRUMS, 0, vol=104, rev=30)
    s.setup(4, CALDER, HISS, vol=50)
    s.setup(6, CALDER, STATIC, vol=80, rev=40)
    B = 4
    s.note(4, 60, 0, s.length - 0.1, 64, jitter=0)
    climb = ["Cmaj7", "D", "Em", "Em/D", "Cmaj7", "D", "B7sus4", "B7"]
    sections = [
        (0, ["Em9", "Cmaj7#11", "Am7", "B7sus4"] * 2, "intro"),
        (8, climb, "climb"),
        (16, THEME_CHORDS, "theme"),
        (24, climb, "climb2"),
        (32, ANSWER_CHORDS, "answer"),
    ]
    for bar0, chords, kind in sections:
        b0 = bar0 * B
        pad_chords(s, 2, chords, b0, vel=50 if kind == "intro" else 56)
        triphop_bass(s, 3, chords, b0, vel=96, figure=2 if kind.startswith("climb") else 0)
        arp(s, 1, chords, b0, vel=50, step=0.25,
            pattern=(0, 2, 4, 3, 1, 3, 2, 4), skip=0.2 if kind == "intro" else 0.05)
        for i in range(8):
            if kind == "intro" and i < 4:
                for k in range(8):
                    s.note(9, HAT, b0 + i * B + k * .5 + (.1 if k % 2 else 0), .1, 52)
                s.note(9, KICK, b0 + i * B, .25, 96)
            else:
                triphop_bar(s, b0 + i * B, var=(1 if i % 2 else 2), vel=1.08, swing=0.08)
                if i % 2 == 0:
                    s.note(7, 38 + s.rng.randint(0, 1), b0 + i * B + 1 + s.ms(20), 2, 70)
        triphop_fill(s, b0 + 7 * B, vel=1.1)
        s.note(9, CRASH, b0, 2, 84)
        s.note(7, 36, b0, 3, 96)
        # static swells into each new section
        s.note(6, 60, b0 + 6 * B, 2 * B - 0.2, 90, jitter=0)
        s.ramp(6, 11, 0, 110, b0 + 6 * B, b0 + 8 * B - 0.5, step=0.25)
        if kind == "climb":
            play_phrase(s, 0, [("E5", 0, 4), ("F#5", 4, 4), ("G5", 8, 4), ("F#5", 12, 2), ("E5", 14, 2),
                               ("E5", 16, 3), ("D5", 19, 1), ("F#5", 20, 4), ("D#5", 24, 4), ("B4", 28, 4)],
                        b0, vel=84)
        elif kind == "theme":
            play_phrase(s, 0, THEME, b0, vel=96)
            play_phrase(s, 0, THEME, b0, vel=60, transpose=-12)
        elif kind == "climb2":
            play_phrase(s, 0, [("G5", 0, 4), ("A5", 4, 4), ("B5", 8, 4), ("A5", 12, 2), ("G5", 14, 2),
                               ("G5", 16, 3), ("F#5", 19, 1), ("A5", 20, 4), ("F#5", 24, 4), ("D#5", 28, 4)],
                        b0, vel=90)
        elif kind == "answer":
            play_phrase(s, 0, THEME_ANSWER, b0, vel=100, transpose=12)
            play_phrase(s, 0, THEME_ANSWER, b0, vel=70)
    return s


def cue_mill_floor():
    """The Ledger at full voice. Everything from earlier cues comes in
    one layer at a time, out of step with each other, then the whole
    thing cuts to silence. Plays once. The grid is one beat per second."""
    s = Song("mill_floor", 60, 160)
    s.setup(12, CALDER, SUB_DRONE, vol=104, rev=30)
    s.setup(6, CALDER, STATIC, vol=96, rev=40)
    s.setup(7, CALDER, METAL_KIT, vol=100, pan=40, rev=90)
    s.setup(8, CALDER, METAL_KIT, vol=96, pan=88, rev=90)
    s.setup(2, GM, GM_CHURCH_ORGAN, vol=78, rev=90)
    s.setup(0, CALDER, TREM_MANDOLIN, vol=100, pan=60, rev=70)
    s.setup(3, CALDER, DIST_BASS, vol=104, rev=10)
    s.setup(1, GM, GM_PIANO, vol=90, pan=72, rev=100)
    s.setup(9, DRUMS, 0, vol=104, rev=40)
    s.setup(11, GM, GM_CHOIR, vol=96, rev=110)
    s.setup(5, CALDER, SCRAPE, vol=90, rev=90)
    s.bend(1, -38, 0)
    cut = 148.0

    def at88(beat):
        return beat * 60 / 88

    # 0: drone and static
    s.note(12, "E1", 0, cut, 96, jitter=0)
    s.note(12, "F1", 40, cut - 40, 60, jitter=0)
    s.note(6, 60, 0.5, cut - 0.5, 100, jitter=0)
    s.ramp(6, 11, 20, 70, 0, 60, step=1)
    s.ramp(6, 11, 70, 127, 100, cut, step=0.5)
    # 15: metal, getting denser
    at = 15.0
    while at < cut:
        density = 0.3 + 2.5 * (at - 15) / (cut - 15)
        key = 36 + 2 * s.rng.randint(0, 5)
        s.note(7 if s.rng.random() < 0.5 else 8, key, at, 3, s.rng.randint(60, 115), jitter=0)
        at += max(0.18, s.rng.expovariate(density))
    # 30: the hymn on the organ, slow, in F against an E drone
    hymn = [("A4", 3), ("A4", 3), ("Bb4", 3), ("C5", 3), ("C5", 3), ("Bb4", 3), ("A4", 6),
            ("G4", 3), ("A4", 3), ("Bb4", 3), ("A4", 3), ("G4", 9)]
    b = 30.0
    for rep in range(3):
        for p, d in hymn:
            if b >= cut:
                break
            s.note(2, p, b, d, 70, jitter=0)
            s.note(2, n(p) - 9, b, d, 56, jitter=0)
            b += d
    # 45: the theme on mandolin at its own tempo
    for k, start in enumerate((45, 82, 118)):
        for p, tb, d in THEME:
            pos = start + tb * 60 / 70
            if pos < cut:
                s.note(0, n(p) + (12 if k == 2 else 0), pos, d * 60 / 70, 90 + 8 * k, jitter=0)
    # 60: distorted bass pulse
    b = 60.0
    while b < cut:
        s.note(3, "E1" if int(b) % 16 < 12 else "F1", b, 0.5, 100, jitter=0)
        b += 1.0
    # 75: June's piano note
    b = 75.0
    while b < cut:
        s.note(1, "D#4", b, 2, s.rng.randint(55, 85), jitter=0)
        b += s.rng.uniform(1.4, 3.0)
    # 90: the water tower beat at 88
    beat = 0.0
    while 90 + at88(beat) < cut - 0.5:
        bar_start = 90 + at88(beat)
        for k in (0, 0.75, 2.5):
            s.note(9, KICK, bar_start + at88(k), 0.25, 110, jitter=0)
        for k in (1, 3):
            s.note(9, SNARE, bar_start + at88(k), 0.25, 104, jitter=0)
        for k in range(8):
            s.note(9, HAT, bar_start + at88(k * 0.5), 0.1, 70, jitter=0)
        beat += 4
    # 100: choir clusters
    for start, notes in ((100, ["E3", "F3", "B3"]), (112, ["E3", "F3", "Bb3", "B3"]),
                         (124, ["D3", "E3", "F3", "Bb3", "B3"]), (136, ["E3", "F3", "Bb3", "B3", "C4"])):
        s.chord(11, notes, start, min(12, cut - start), 90, jitter=0)
    s.ramp(11, 11, 50, 127, 100, cut, step=1)
    # scrapes
    for at in (52, 88, 121, 139):
        s.note(5, 50 + s.rng.randint(0, 12), at, 5, 100, jitter=0)
    s.marker("calder:cut", cut)
    s.all_off(cut)
    return s


def cue_dawn():
    """The true ending. 76 bpm, the main theme with nothing left but a
    guitar. The last chord is the first major chord the theme has ever had."""
    s = Song("dawn", 76, 34 * 4)
    s.setup(1, GM, GM_STEEL, vol=96, pan=56, rev=70)
    s.setup(0, GM, GM_NYLON, vol=116, pan=70, rev=75)
    s.setup(4, CALDER, HISS, vol=30)
    s.note(4, 60, 0, s.length - 0.1, 40, jitter=0)
    arp(s, 1, THEME_CHORDS, 0, vel=54, pattern=(0, 2, 1, 3, 2, 4, 3, 2))
    play_phrase(s, 0, THEME, 0, vel=78, transpose=-12, jitter=18)
    arp(s, 1, ANSWER_CHORDS, 32, vel=54, pattern=(0, 3, 2, 4, 1, 4, 3, 2))
    play_phrase(s, 0, THEME_ANSWER, 32, vel=80, transpose=-12, jitter=18)
    arp(s, 1, ["Am7", "Em/G", "Fmaj7#11", "B7sus4", "Am7", "Em/G", "Cmaj7", "B7sus4"], 64, vel=48,
        pattern=(0, 2, 3, 4, 3, 2), step=0.5, skip=0.25)
    arp(s, 1, THEME_CHORDS, 96, vel=50)
    play_phrase(s, 0, THEME[:13], 96, vel=74, transpose=-12, jitter=18)
    # coda: Emaj9, let ring
    _, voi = CH["Emaj9"]
    s.note(1, "E2", 128, 7.5, 60)
    s.chord(1, voi, 128, 7.5, 50, spread=0.12)
    s.note(0, "G#4", 129, 6.5, 56)
    return s


CUES = {
    "calder_falls": cue_calder_falls,
    "cobb_road": cue_cobb_road,
    "june": cue_june,
    "the_hush": cue_the_hush,
    "substation": cue_substation,
    "listening_room": cue_listening_room,
    "fellowship": cue_fellowship,
    "the_spindle": cue_the_spindle,
    "precentor": cue_precentor,
    "water_tower": cue_water_tower,
    "mill_floor": cue_mill_floor,
    "dawn": cue_dawn,
}


def main(argv):
    args = argv[1:]
    out = OUT
    if "--out" in args:
        i = args.index("--out")
        out = args[i + 1]
        del args[i:i + 2]
    os.makedirs(out, exist_ok=True)
    names = args or list(CUES)
    for name in names:
        if name not in CUES:
            print(f"unknown cue: {name}", file=sys.stderr)
            return 1
        song = CUES[name]()
        path = os.path.join(out, f"{name}.mid")
        mid = song.save(path)
        print(f"{name:15s} {mid.length:7.1f} s  {song.bpm} bpm  channels {sorted(song.used)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
