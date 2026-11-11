"""Player settings and the profile that outlives a playthrough.

Both are small JSON files in ~/.local/share/calder-falls/. A broken or
missing file means defaults, never a crash.
"""

import json
import os
from dataclasses import asdict, dataclass, field

from . import paths


@dataclass
class Settings:
    flicker: str = "gentle"          # off, gentle, full
    honest_controls: bool = False
    flashlight_cone: bool = True
    text_size: int = 15
    reveal_speed: int = 55           # characters per second, 0 = instant
    timed_choices: bool = False
    fourth_wall: bool = True
    font: str = "Courier Prime"      # or Source Serif 4
    music_volume: int = 80
    first_launch_done: bool = False


@dataclass
class Profile:
    launches: int = 0
    playthroughs: int = 0
    endings_seen: list = field(default_factory=list)


def _path(name):
    return os.path.join(paths.user_dir(), name)


def _load(cls, name):
    obj = cls()
    try:
        with open(_path(name), encoding="utf-8") as fh:
            data = json.load(fh)
        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
    except (OSError, ValueError):
        pass
    return obj


def _save(obj, name):
    os.makedirs(paths.user_dir(), exist_ok=True)
    tmp = _path(name) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(asdict(obj), fh, indent=2)
    os.replace(tmp, _path(name))


def load_settings():
    s = _load(Settings, "settings.json")
    if s.flicker not in ("off", "gentle", "full"):
        s.flicker = "gentle"
    return s


def save_settings(s):
    _save(s, "settings.json")


def load_profile():
    return _load(Profile, "profile.json")


def save_profile(p):
    _save(p, "profile.json")
