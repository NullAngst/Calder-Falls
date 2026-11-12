"""Headless story checks. Exit code 0 means every check passed.

    python3 -m calder_falls.storytest

1. Every tag written in the .ink source is one the game handles, and every
   music tag names a real cue or layer.
2. Scripted routes play the whole game, Prologue to credits, and reach all
   five endings. A route is a set of starting values for the hidden stats
   plus the final choice to pick; everything in between is played by an
   autoplayer that looks at what it has not tried yet.
3. On every route, each theory's right answers were actually findable by
   the time it was filed (the evidence they need had been collected).
4. Wandering walks with a seed and a habit of filing wrong theories still
   reach an ending: no dead ends, no loop without a way out.
5. Saving mid-game and loading into a fresh session comes back to the same
   choices and the same variables.
"""

import os
import random
import re
import sys
import tempfile

from . import story
from .audio import cues as cue_table

FAILS = []
TAG_RE = re.compile(r"(?:^|\s)#\s*([^#\n]+)")


def check(ok, what):
    print(("  ok   " if ok else "  FAIL ") + what, flush=True)
    if not ok:
        FAILS.append(what)


# ------------------------------------------------------------ source scan
def scan_tags():
    print("tags in the .ink source", flush=True)
    bad = []
    count = 0
    for path in story.ink_sources():
        with open(path, encoding="utf-8") as fh:
            for no, line in enumerate(fh, 1):
                code = line.split("//", 1)[0] if "//" in line and "://" not in line else line
                for m in TAG_RE.finditer(code):
                    raw = m.group(1).strip()
                    if not raw:
                        continue
                    count += 1
                    name, _, arg = raw.partition(":")
                    where = f"{os.path.relpath(path, story.story_dir())}:{no}"
                    if name not in story.TAGS:
                        bad.append(f"{where} unknown tag # {raw}")
                        continue
                    if name == "warp" and arg.split(":")[0] not in story.WARPS:
                        bad.append(f"{where} unknown warp # {raw}")
                    if name == "fourth" and arg not in story.FOURTH:
                        bad.append(f"{where} unknown fourth-wall effect # {raw}")
                    if name == "theme" and arg not in story.THEME_STAGES:
                        bad.append(f"{where} unknown theme stage # {raw}")
                    if name == "music" and arg != "stop" and arg not in cue_table.BY_NAME:
                        bad.append(f"{where} unknown music cue # {raw}")
                    if name == "music_layer":
                        parts = arg.split()
                        if len(parts) != 2 or parts[0] not in cue_table.LAYERS or parts[1] not in ("on", "off"):
                            bad.append(f"{where} bad layer tag # {raw}")
                    if name in ("evidence", "theory", "slot") and "|" in arg:
                        bad.append(f"{where} uses | inside a tag; fields are separated by ;")
    for b in bad:
        print("    " + b)
    check(not bad, f"all {count} tags in the source are known to the game")


# ------------------------------------------------------------ autoplayer
class Player:
    def __init__(self, seed, presets=None, final=None, wrong=0.0, second_run=False,
                 take_radio=0.5, save_dir=None):
        self.rng = random.Random(seed)
        self.presets = presets or {}
        self.final = final
        self.wrong = wrong
        self.second_run = second_run
        self.take_radio = take_radio
        self.s = story.Session(strict=True, save_dir=save_dir)
        self.used = {}
        self.unfindable = []
        self.stalled = 0

    def start(self):
        self.s.new_game(second_run=self.second_run)
        for k, v in self.presets.items():
            if not self.s.set_var(k, v):
                raise story.StoryError(f"route preset names an unknown variable: {k}")

    def pick(self):
        ch = self.s.choices
        if self.final:
            for c in ch:
                if self.final in c.truth:
                    return c
        if self.second_run:
            for c in ch:
                if "Stay on 1610" in c.truth:
                    return c

        t = self.s.pending_theory()
        missing = []
        if t is not None:
            have = set(self.s.state.evidence)
            missing = [need for sl in t.slots for _t, ok, need in sl.options if ok and need and need not in have]
        if missing:
            self.stalled += 1
            if self.stalled > 400:
                self.unfindable.append(f"{t.id}: never found {sorted(set(missing))}")
                self.stalled = 0
                missing = []
        else:
            self.stalled = 0

        def key(c):
            w = self.used.get(c.truth, 0)
            if missing and c.kind == "file":
                w += 1000
            if missing and c.truth.startswith(("Leave the house", "Go round again")):
                w -= 0.5
            if c.kind in ("radio", "police") and self.rng.random() > self.take_radio:
                w += 3
            if c.truth.startswith(("Walk to the kitchen", "Go back out", "Go round again")):
                w += 0.6
            if c.truth.startswith(("Keep looking", "Not yet")):
                w += 4
            if c.kind == "file":
                w -= 0.2
            return (w, self.rng.random())
        return min(ch, key=key)

    def answers(self):
        t = self.s.pending_theory()
        if t is None:
            return None
        if self.rng.random() < self.wrong:
            return {s.name: s.options[-1][0] for s in t.slots}
        return t.correct_answers()

    def play(self, limit=6000, save_at=None, on_save=None):
        self.start()
        steps = 0
        while True:
            self.s.step()
            if self.s.ended:
                return steps
            steps += 1
            if steps > limit:
                raise story.StoryError(f"no ending after {limit} choices (chapter {self.s.state.chapter_no})")
            if save_at is not None and steps == save_at and on_save:
                on_save(self)
            c = self.pick()
            self.used[c.truth] = self.used.get(c.truth, 0) + 1
            if c.kind == "file" or c.truth.startswith(("Walk to the kitchen", "Go back out", "Drive")):
                self.used = {k: v for k, v in self.used.items() if k.startswith(("Smoke", "Sit"))}
            self.s.choose(c, self.answers() if c.kind == "file" else None)


ROUTES = [
    ("dawn", dict(presets={"resolve": 40, "mercy": 40, "attunement": -40}, final="Hold on to the people")),
    ("dead_air", dict(presets={"resolve": 20, "attunement": -200}, final="Refuse them")),
    ("broadcast", dict(presets={"attunement": 200, "resolve": 5, "mercy": -100}, final="Let them in")),
    ("quiet_house", dict(presets={"resolve": -300}, final="Try to hold on")),
    ("test_pattern", dict(second_run=True)),
]


def routes(tmp):
    print("routes to every ending", flush=True)
    seen_tags = set()
    for want, kw in ROUTES:
        # A fixed seed per route. hash() would differ between runs, since
        # Python randomizes string hashes per process.
        p = Player(seed=sum(map(ord, want)), save_dir=tmp, **kw)
        try:
            steps = p.play()
            got = p.s.state.ending
            check(got == want, f"route '{want}' reaches the {got or 'no'} ending in {steps} choices")
            check(not p.s.unknown_tags, f"route '{want}': no unknown tags")
            uniq = sorted(set(p.unfindable))
            for u in uniq:
                print("    " + u)
            check(not uniq, f"route '{want}': every right theory answer can be found before filing")
            seen_tags |= p.s.tags_seen
        except story.StoryError as exc:
            check(False, f"route '{want}': {exc}")
    print(f"    tags exercised: {len(seen_tags)}")
    return seen_tags


def wander(tmp, seeds=6):
    print("wandering walks", flush=True)
    for seed in range(seeds):
        p = Player(seed=1000 + seed, wrong=0.35, take_radio=0.8, save_dir=tmp)
        try:
            steps = p.play(limit=9000)
            check(bool(p.s.state.ending), f"walk {seed} ends ({p.s.state.ending}) after {steps} choices")
        except story.StoryError as exc:
            check(False, f"walk {seed}: {exc}")


def save_load(tmp):
    print("save and load", flush=True)
    result = {}

    def snap(player):
        player.s.save("smoke")
        fresh = story.Session(strict=True, save_dir=tmp)
        fresh.load("smoke")
        keys = ("nerve", "resolve", "attunement", "mercy", "evidence", "loop")
        result["choices"] = ([c.text for c in fresh.choices], [c.text for c in player.s.choices])
        result["vars"] = ({k: fresh.get_var(k) for k in keys}, {k: player.s.get_var(k) for k in keys})
        result["state"] = (fresh.state.chapter_title, player.s.state.chapter_title)

    p = Player(seed=7, save_dir=tmp, presets={"resolve": 40, "mercy": 40}, final="Hold on to the people")
    p.play(save_at=120, on_save=snap)
    check(result.get("choices", (1, 2))[0] == result.get("choices", (1, 2))[1], "loaded save has the same choices")
    check(result.get("vars", (1, 2))[0] == result.get("vars", (1, 2))[1], "loaded save has the same variables")
    check(result.get("state", (1, 2))[0] == result.get("state", (1, 2))[1], "loaded save is in the same chapter")


def main():
    try:
        warnings = story.compile_story(strict=True)
        check(not warnings, "inklecate compiles story/main.ink with zero warnings")
    except story.StoryError as exc:
        check(False, str(exc))
        print(f"\n{len(FAILS)} check(s) failed")
        return 1
    scan_tags()
    with tempfile.TemporaryDirectory() as tmp:
        seen = routes(tmp)
        wander(tmp)
        save_load(tmp)
    used_warps = {t for t in seen if t.startswith("warp:")}
    check(len(used_warps) >= 6, f"routes exercise the window tricks ({len(used_warps)} warp kinds)")
    print()
    if FAILS:
        print(f"{len(FAILS)} check(s) failed:")
        for f in FAILS:
            print(f"  {f}")
        return 1
    print("all story checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
