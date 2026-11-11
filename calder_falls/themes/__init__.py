"""Midnight and the four stages it decays through.

The window has one theme. Ink tags (# theme:bleed) move it between stages,
and low Nerve pushes it one stage further for as long as Nerve stays low.
Colors interpolate over a couple of seconds, so a change reads as the room
going wrong rather than a skin swap.

The hex values are a starting point, to be tuned on a real screen.
"""

import os
from dataclasses import dataclass, replace

ORDER = ("midnight", "fog", "bleed", "static", "dead_signal")


@dataclass(frozen=True)
class Stage:
    name: str
    bg: str
    text: str
    accent: str
    grain: float = 0.05       # film grain strength 0..1
    haze: float = 0.0         # drifting fog over the text
    flicker: float = 0.0      # light flicker
    swap: float = 0.0         # chance per second that a word briefly swaps
    scanlines: float = 0.0
    split: float = 0.0        # color split on text edges, in pixels
    stutter: float = 0.0      # typewriter stutter chance
    drift: float = 0.0        # letters drifting off their line


STAGES = {
    "midnight": Stage("midnight", "#0B0F1A", "#C8CDD8", "#4A6FA5", grain=0.05),
    "fog": Stage("fog", "#1A1C1F", "#D0D0CC", "#8A9099", grain=0.06, haze=0.5),
    "bleed": Stage("bleed", "#1A0D0A", "#D9C2B0", "#8C2F1B", grain=0.08, haze=0.15,
                   flicker=0.35, swap=0.35),
    "static": Stage("static", "#0E0E10", "#C4C4C4", "#5E8C8C", grain=0.1,
                    scanlines=0.35, split=1.2, flicker=0.15),
    "dead_signal": Stage("dead_signal", "#050505", "#9E9A94", "#7A1414", grain=0.12,
                         scanlines=0.2, split=0.6, flicker=0.2, stutter=0.12, drift=0.25),
}


def push(name, steps=1):
    i = ORDER.index(name) if name in ORDER else 0
    return ORDER[min(len(ORDER) - 1, i + steps)]


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(c):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(v)))) for v in c)


def mix(a, b, t):
    ca, cb = _rgb(a), _rgb(b)
    return _hex([x + (y - x) * t for x, y in zip(ca, cb)])


def interpolate(a, b, t):
    """A stage somewhere between a and b."""
    if t <= 0:
        return a
    if t >= 1:
        return b
    nums = {}
    for f in ("grain", "haze", "flicker", "swap", "scanlines", "split", "stutter", "drift"):
        nums[f] = getattr(a, f) + (getattr(b, f) - getattr(a, f)) * t
    return replace(a, name=b.name, bg=mix(a.bg, b.bg, t), text=mix(a.text, b.text, t),
                   accent=mix(a.accent, b.accent, t), **nums)


def calm(stage, flicker_setting):
    """Apply the accessibility setting. off kills every flash and scanline,
    gentle halves them, full leaves them alone."""
    if flicker_setting == "off":
        return replace(stage, flicker=0.0, scanlines=0.0, split=0.0, swap=0.0)
    if flicker_setting == "gentle":
        return replace(stage, flicker=stage.flicker * 0.4, scanlines=stage.scanlines * 0.6)
    return stage


def stylesheet(stage, base_px=15):
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "midnight.qss"), encoding="utf-8") as fh:
        qss = fh.read()
    values = {
        "bg": stage.bg,
        "text": stage.text,
        "accent": stage.accent,
        "panel": mix(stage.bg, stage.text, 0.05),
        "panel2": mix(stage.bg, stage.text, 0.09),
        "border": mix(stage.bg, stage.text, 0.16),
        "dim": mix(stage.bg, stage.text, 0.55),
        "hover": mix(stage.bg, stage.accent, 0.25),
        "px": str(base_px),
        "small": str(max(11, base_px - 3)),
    }
    for k, v in values.items():
        qss = qss.replace("@" + k + "@", v)
    return qss
