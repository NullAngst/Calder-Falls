"""The cue table and the layer map.

Every cue in the spec's cue list is here. The story refers to cues by
name (# music:cobb_road), so a name never changes once the story uses it.
"""

import os
from dataclasses import dataclass

from .. import paths

# Layer name -> MIDI channels. Same in every cue (see music/generate.py).
LAYERS = {
    "drums": (9, 7, 8),
    "bass": (3,),
    "lead": (0, 1, 10),
    "pad": (2, 11, 12),
    "noise": (4, 5, 6),
}
LAYER_ORDER = ("drums", "bass", "lead", "pad", "noise")


def layer_of(channel):
    for name, chans in LAYERS.items():
        if channel in chans:
            return name
    return None


@dataclass(frozen=True)
class Cue:
    name: str
    title: str
    where: str
    tempo: str
    feel: str
    loop: bool = True
    gain_db: float = 0.0       # loudness trim, set by python3 -m calder_falls.audio.loudness
    target_lufs: float = -20.0  # how loud the cue should sit in the game

    @property
    def path(self):
        return os.path.join(paths.cue_dir(), f"{self.name}.mid")


CUES = [
    Cue("calder_falls", "Calder Falls", "Title, drive in", "78 bpm",
        "Trip-hop, mandolin lead, the main theme", gain_db=0.0, target_lufs=-18.0),
    Cue("cobb_road", "Cobb Road", "Harlan house, early loops", "none",
        "Fridge hum, a clock, a pad you barely notice", gain_db=5.0, target_lufs=-26.0),
    Cue("june", "June", "Stalker nearby", "none",
        "Low drone, one detuned piano note on repeat", gain_db=3.9, target_lufs=-22.0),
    Cue("the_hush", "The Hush", "Town exploration", "70 bpm",
        "Sparse guitar, long gaps, fog", gain_db=9.8, target_lufs=-23.0),
    Cue("substation", "Substation", "Police substation, safe room", "84 bpm",
        "Warm electric piano, the closest thing to comfort", gain_db=6.4, target_lufs=-20.0),
    Cue("listening_room", "Listening Room", "Any Bleed house", "none",
        "Metal percussion, static swells, no tonal center", gain_db=3.2, target_lufs=-20.0),
    Cue("fellowship", "Fellowship", "St. Adalbert's parish hall", "66 bpm",
        "Out-of-tune upright piano, a hymn shape that isn't a real hymn", gain_db=9.4, target_lufs=-22.0),
    Cue("the_spindle", "The Spindle", "The bar", "90 bpm",
        "Jukebox-ish, gets slower each visit", gain_db=4.2, target_lufs=-19.0),
    Cue("precentor", "Precentor", "Margaret Lusk", "72 bpm",
        "Organ pad, voice-like synth, warm on top, cold underneath", gain_db=3.4, target_lufs=-20.0),
    Cue("water_tower", "Water Tower", "Act IV climb", "88 bpm",
        "Full beat, distorted bass, mandolin returns", gain_db=-0.4, target_lufs=-17.0),
    Cue("mill_floor", "Mill Floor", "The Ledger at full voice", "none",
        "Everything from earlier cues layered, then cut to silence", loop=False, gain_db=1.0, target_lufs=-16.0),
    Cue("dawn", "Dawn", "Ending", "76 bpm",
        "The main theme, stripped to guitar", gain_db=6.0, target_lufs=-21.0),
]

BY_NAME = {c.name: c for c in CUES}


def get(name):
    try:
        return BY_NAME[name]
    except KeyError:
        raise KeyError(f"unknown music cue: {name}") from None
