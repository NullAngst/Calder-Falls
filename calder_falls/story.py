"""The Ink story, and everything the game remembers around it.

story.py is the only file that talks to the Ink runtime, bink (Python
bindings for Blade Ink, a Rust port of the official runtime). The spec
picked inkcpp_py first; it was dropped because it shifts tags when a
function runs while a tag is pending (see changes.md). Swapping runtimes
again means changing this file and nothing else.

Session drives the story one choice point at a time and turns Ink output
into a flat list of events the window (or the headless smoke test) applies.
The window never reads Ink directly, which is why the smoke test can play
the whole game without a display and still exercise the same logic.

Ink conventions this game uses (see story/README-ink.md for the writer's
side):

  Tags on content lines      # name:args        (vocabulary in TAGS below)
  Choice prefixes            RADIO:1610: text   hidden, played from the radio dial
                             POLICE: text       hidden, played from the police knob
                             FILE: text         opens the theory dialog first
  Turning choice             [Shown text @@ What it really does]
  Variables the GUI reads    nerve, rounds, second_run, theory_score
"""

import json
import os
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass, field

from . import paths

try:
    from bink.story import story_from_file
except ImportError:  # the smoke test says this plainly; the GUI shows it
    story_from_file = None

THEME_STAGES = ("midnight", "fog", "bleed", "static", "dead_signal")
ITEMS = ("flashlight", "notebook", "camera", "pistol", "radio", "keys")
ENDINGS = ("dawn", "dead_air", "broadcast", "quiet_house", "test_pattern")

# Every tag the story may use. Anything else is an error in strict mode,
# so a typo in Act III fails the build instead of doing nothing.
TAGS = {
    "chapter", "autosave", "clear", "time", "hint", "evidence", "note",
    "theory", "slot", "map", "item", "item_lose", "ending", "pause", "timed",
    "dark", "battery", "shadow", "theme", "warp", "fourth", "music",
    "music_layer", "music_detune", "music_tempo", "music_static", "music_ps2",
    "speaker",
}
WARPS = {
    "scrollback", "tabs_rename", "tabs_normal", "radio_drift", "radio_still",
    "title_count", "title_normal", "cursor_needle", "cursor_normal", "swap",
    "swap_clear", "flinch", "flinch_off",
}
FOURTH = {"crash", "corrupt_save", "howto"}


class StoryError(Exception):
    pass


# ------------------------------------------------------------ files

def story_dir():
    return os.path.join(paths.data_dir(), "story")


def compiled_path():
    return os.path.join(story_dir(), "build", "main.json")


def find_inklecate():
    env = os.environ.get("INKLECATE")
    if env and os.path.isfile(env):
        return env
    local = os.path.join(paths.data_dir(), "build", "tools", "inklecate")
    if os.path.isfile(local):
        return local
    return shutil.which("inklecate")


def ink_sources():
    out = []
    for root, _dirs, files in os.walk(story_dir()):
        if os.sep + "build" in root:
            continue
        out += [os.path.join(root, f) for f in files if f.endswith(".ink")]
    return sorted(out)


def compile_story(strict=True):
    """main.ink -> build/main.json with inklecate.
    Returns the list of inklecate warnings. strict raises on any warning."""
    tool = find_inklecate()
    if not tool:
        raise StoryError("inklecate not found. Put it in build/tools/ or on PATH, or set INKLECATE.")
    src = os.path.join(story_dir(), "main.ink")
    out_dir = os.path.join(story_dir(), "build")
    os.makedirs(out_dir, exist_ok=True)
    js = os.path.join(out_dir, "main.json")
    proc = subprocess.run([tool, "-o", js, src], capture_output=True, text=True)
    text = (proc.stdout + proc.stderr).strip()
    lines = [ln for ln in text.splitlines() if ln.strip()]
    errors = [ln for ln in lines if ln.startswith("ERROR")]
    warnings = [ln for ln in lines if ln.startswith("WARNING")]
    if proc.returncode != 0 or errors:
        raise StoryError("inklecate failed:\n" + text)
    if strict and warnings:
        raise StoryError("inklecate warnings (the build treats them as errors):\n" + "\n".join(warnings))
    return warnings


def ensure_compiled():
    """From a source checkout, recompile when any .ink file is newer."""
    target = compiled_path()
    newest = max((os.path.getmtime(p) for p in ink_sources()), default=0)
    if os.path.isfile(target) and os.path.getmtime(target) >= newest:
        return target
    if find_inklecate():
        compile_story(strict=False)
    if not os.path.isfile(target):
        raise StoryError("story/build/main.json is missing and inklecate is not available to build it.")
    return target


# ------------------------------------------------------------ parsing

def parse_tag(raw):
    raw = raw.strip().lstrip("#").strip()
    name, _, arg = raw.partition(":")
    return name.strip(), arg.strip(), raw


@dataclass
class Choice:
    index: int          # Ink's index
    text: str           # what the button shows
    hover: str = ""     # what it says on hover (turning choice)
    kind: str = "normal"   # normal, radio, police, file
    freq: int = 0

    @property
    def truth(self):
        return self.hover or self.text


def parse_choice(index, raw):
    text = raw.strip()
    kind = "normal"
    freq = 0
    if text.startswith("RADIO:"):
        rest = text[6:]
        num, _, text = rest.partition(":")
        kind = "radio"
        freq = int(num.strip())
    elif text.startswith("POLICE:"):
        kind = "police"
        text = text[7:]
    elif text.startswith("FILE:"):
        kind = "file"
        text = text[5:]
    text = text.strip()
    hover = ""
    if "@@" in text:
        text, hover = (p.strip() for p in text.split("@@", 1))
    return Choice(index, text, hover, kind, freq)


@dataclass
class TheorySlot:
    name: str
    options: list       # [(text, correct, needs_evidence_or_empty)]


@dataclass
class Theory:
    id: str
    title: str
    slots: list = field(default_factory=list)

    def available(self, collected):
        out = []
        for slot in self.slots:
            opts = [o for o in slot.options if not o[2] or o[2] in collected]
            out.append((slot.name, opts))
        return out

    def score(self, answers):
        total = 0
        for slot in self.slots:
            pick = answers.get(slot.name)
            for text, correct, _need in slot.options:
                if text == pick and correct:
                    total += 1
        return total

    def correct_answers(self):
        return {s.name: next(o[0] for o in s.options if o[1]) for s in self.slots}


def parse_slot(arg):
    name, *opts = [p.strip() for p in arg.split(";")]
    options = []
    for o in opts:
        need = ""
        if "@" in o:
            o, need = (p.strip() for p in o.split("@", 1))
        correct = o.endswith("*")
        options.append((o.rstrip("*").strip(), correct, need))
    if not any(c for _t, c, _n in options):
        raise StoryError(f"theory slot '{name}' has no correct option")
    return TheorySlot(name, options)


# ------------------------------------------------------------ state

@dataclass
class GameState:
    chapter_no: int = 0
    chapter_title: str = ""
    theme: str = "midnight"
    evidence: dict = field(default_factory=dict)    # id -> {kind,title,caption}
    evidence_order: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    map_marks: list = field(default_factory=list)
    items: list = field(default_factory=list)
    hint: str = "Read everything. Then look again."
    time: str = "--:--"
    tabs_renamed: bool = False
    radio_drift: bool = False
    title_count: str = ""
    cursor_needle: bool = False
    flinch: bool = False
    swaps: dict = field(default_factory=dict)
    dark: bool = False
    battery_low: bool = False
    transcript: list = field(default_factory=list)  # recent paragraphs for a loaded save
    theory: dict = field(default_factory=dict)       # pending theory as plain data
    howto_rewritten: bool = False
    ending: str = ""
    second_run: bool = False
    speaker: str = ""


def theory_to_dict(t):
    return {"id": t.id, "title": t.title,
            "slots": [{"name": s.name, "options": [list(o) for o in s.options]} for s in t.slots]}


def theory_from_dict(d):
    if not d:
        return None
    return Theory(d["id"], d["title"],
                  [TheorySlot(s["name"], [tuple(o) for o in s["options"]]) for s in d["slots"]])


# ------------------------------------------------------------ session

class Session:
    """One playthrough. step() runs Ink to the next choice point."""

    TRANSCRIPT_KEEP = 80

    def __init__(self, audio=None, strict=False, save_dir=None):
        if story_from_file is None:
            raise StoryError("bink (the Ink runtime) is not installed: pip install bink")
        self.audio = audio
        self.strict = strict
        self.save_dir = save_dir or os.path.join(paths.user_dir(), "saves")
        self.path = ensure_compiled()
        self.ink = None
        self.state = GameState()
        self.choices = []
        self.ended = False
        self.autosave_pending = False
        self.tags_seen = set()
        self.unknown_tags = []

    # -------------------------------------------------- setup
    def new_game(self, second_run=False):
        self.ink = story_from_file(self.path)
        self.state = GameState(second_run=second_run)
        self.set_var("second_run", bool(second_run))
        self.ended = False
        self.choices = []

    # -------------------------------------------------- variables
    def get_var(self, name, default=None):
        try:
            v = self.ink.get_variable(name)
        except Exception:
            return default
        return default if v is None else v

    def set_var(self, name, value):
        try:
            self.ink.get_variable(name)
            self.ink.set_variable(name, value)
        except Exception:
            return False
        return True

    @property
    def nerve(self):
        return self.get_var("nerve", 10)

    # -------------------------------------------------- running
    def step(self):
        """Run to the next choice point or the end. Returns events."""
        events = []
        guard = 0
        while self.ink.can_continue():
            guard += 1
            if guard > 5000:
                raise StoryError("story ran 5000 lines without a choice; probably a loop with no choice")
            line = self.ink.cont()
            tags = list(self.ink.get_current_tags())
            for t in tags:
                events += self._tag(t)
            text = line.strip()
            if text:
                text = self._apply_swaps(text)
                self.state.transcript.append(text)
                del self.state.transcript[:-self.TRANSCRIPT_KEEP]
                events.append(("text", text, self.state.speaker))
                self.state.speaker = ""   # a speaker tag styles one line only
        self.choices = [parse_choice(i, t) for i, t in enumerate(self.ink.get_current_choices())]
        if not self.choices:
            self.ended = True
            events.append(("end",))
        elif self.autosave_pending:
            self.autosave_pending = False
            self.save("auto")
            events.append(("autosaved",))
        return events

    def _apply_swaps(self, text):
        for a, b in self.state.swaps.items():
            text = text.replace(a, b)
        return text

    def visible_choices(self):
        return [c for c in self.choices if c.kind in ("normal", "file")]

    def radio_offers(self):
        return [c for c in self.choices if c.kind in ("radio", "police")]

    def pending_theory(self):
        return theory_from_dict(self.state.theory)

    def choose(self, choice, answers=None):
        if choice.kind == "file":
            theory = self.pending_theory()
            score = theory.score(answers or {}) if theory else 0
            self.set_var("theory_score", score)
            self.state.theory = {}
        self.state.transcript.append("> " + choice.truth)
        self.ink.choose_choice_index(choice.index)
        self.choices = []

    # -------------------------------------------------- tags
    def _tag(self, raw):
        name, arg, full = parse_tag(raw)
        self.tags_seen.add(name if name not in ("warp", "fourth") else f"{name}:{arg.split(':')[0]}")
        st = self.state
        ev = []
        if name not in TAGS:
            self.unknown_tags.append(full)
            if self.strict:
                raise StoryError(f"unknown tag: # {full}")
            return ev
        if name.startswith("music"):
            if self.audio is not None:
                try:
                    self.audio.apply_tag(full)
                except ValueError as exc:
                    if self.strict:
                        raise StoryError(str(exc)) from None
            ev.append(("music", full))
        elif name == "chapter":
            num, _, title = arg.partition(":")
            st.chapter_no = int(num)
            st.chapter_title = title.strip()
            self.autosave_pending = True
            ev.append(("chapter", st.chapter_no, st.chapter_title))
        elif name == "autosave":
            self.autosave_pending = True
        elif name == "clear":
            st.transcript.clear()
            ev.append(("clear",))
        elif name == "time":
            st.time = arg
            ev.append(("time", arg))
        elif name == "hint":
            st.hint = arg
            ev.append(("hint", arg))
        elif name == "speaker":
            st.speaker = arg
        elif name == "evidence":
            parts = [p.strip() for p in arg.split(";")]
            if len(parts) < 3:
                raise StoryError(f"evidence tag needs id;kind;title[;caption]: {full}")
            eid, kind, title = parts[:3]
            caption = parts[3] if len(parts) > 3 else ""
            if eid not in st.evidence:
                st.evidence[eid] = {"kind": kind, "title": title, "caption": caption}
                st.evidence_order.append(eid)
                ev.append(("evidence", eid))
        elif name == "note":
            st.notes.append(arg)
            ev.append(("note", arg))
        elif name == "theory":
            tid, _, title = arg.partition(";")
            st.theory = theory_to_dict(Theory(tid.strip(), title.strip()))
        elif name == "slot":
            if not st.theory:
                raise StoryError(f"# slot with no # theory before it: {full}")
            t = theory_from_dict(st.theory)
            t.slots.append(parse_slot(arg))
            st.theory = theory_to_dict(t)
        elif name == "map":
            if arg not in st.map_marks:
                st.map_marks.append(arg)
            ev.append(("map", arg))
        elif name == "item":
            if arg not in ITEMS:
                raise StoryError(f"unknown item: {arg}")
            if arg not in st.items:
                st.items.append(arg)
            ev.append(("items",))
        elif name == "item_lose":
            if arg in st.items:
                st.items.remove(arg)
            ev.append(("items",))
        elif name == "ending":
            if arg not in ENDINGS:
                raise StoryError(f"unknown ending: {arg}")
            st.ending = arg
            ev.append(("ending", arg))
        elif name == "pause":
            ev.append(("pause", float(arg or 1)))
        elif name == "timed":
            secs, _, idx = arg.partition(":")
            ev.append(("timed", float(secs), int(idx or 0)))
        elif name == "dark":
            st.dark = arg == "on"
            ev.append(("dark", st.dark))
        elif name == "battery":
            st.battery_low = arg == "low"
            ev.append(("battery", st.battery_low))
        elif name == "shadow":
            ev.append(("shadow", arg))
        elif name == "theme":
            if arg not in THEME_STAGES:
                raise StoryError(f"unknown theme stage: {arg}")
            st.theme = arg
            ev.append(("theme", arg))
        elif name == "warp":
            kind, _, rest = arg.partition(":")
            if kind not in WARPS:
                raise StoryError(f"unknown warp: {kind}")
            if kind == "tabs_rename":
                st.tabs_renamed = True
            elif kind == "tabs_normal":
                st.tabs_renamed = False
            elif kind == "radio_drift":
                st.radio_drift = True
            elif kind == "radio_still":
                st.radio_drift = False
            elif kind == "title_count":
                st.title_count = rest
            elif kind == "title_normal":
                st.title_count = ""
            elif kind == "cursor_needle":
                st.cursor_needle = True
            elif kind == "cursor_normal":
                st.cursor_needle = False
            elif kind == "flinch":
                st.flinch = True
            elif kind == "flinch_off":
                st.flinch = False
            elif kind == "swap":
                a, _, b = rest.partition("=>")
                st.swaps[a.strip()] = b.strip()
            elif kind == "swap_clear":
                st.swaps.clear()
            elif kind == "scrollback":
                a, _, b = rest.partition("=>")
                a, b = a.strip(), b.strip()
                for i in range(len(st.transcript) - 1, -1, -1):
                    if a in st.transcript[i]:
                        st.transcript[i] = st.transcript[i].replace(a, b)
                        break
                ev.append(("warp", "scrollback", (a, b)))
                return ev
            ev.append(("warp", kind, rest))
        elif name == "fourth":
            if arg not in FOURTH:
                raise StoryError(f"unknown fourth-wall effect: {arg}")
            if arg == "howto":
                st.howto_rewritten = True
            ev.append(("fourth", arg))
        return ev

    # -------------------------------------------------- saves
    def _slot_paths(self, slot):
        os.makedirs(self.save_dir, exist_ok=True)
        base = os.path.join(self.save_dir, f"slot-{slot}")
        return base + ".ink.json", base + ".json"

    def save(self, slot):
        snap_path, meta_path = self._slot_paths(slot)
        with open(snap_path + ".tmp", "w", encoding="utf-8") as fh:
            fh.write(self.ink.save_state())
        os.replace(snap_path + ".tmp", snap_path)
        meta = {"saved": time.strftime("%Y-%m-%d %H:%M"), "chapter_no": self.state.chapter_no,
                "chapter_title": self.state.chapter_title, "state": asdict(self.state)}
        with open(meta_path + ".tmp", "w", encoding="utf-8") as fh:
            json.dump(meta, fh)
        os.replace(meta_path + ".tmp", meta_path)

    def slot_info(self, slot):
        _snap, meta_path = self._slot_paths(slot)
        if not os.path.isfile(meta_path):
            return None
        try:
            with open(meta_path, encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, ValueError):
            return None

    def load(self, slot):
        snap_path, meta_path = self._slot_paths(slot)
        meta = self.slot_info(slot)
        if meta is None or not os.path.isfile(snap_path):
            raise StoryError(f"save slot {slot} is empty or damaged")
        with open(snap_path, encoding="utf-8") as fh:
            saved = fh.read()
        self.ink = story_from_file(self.path)
        self.ink.load_state(saved)
        st = GameState()
        for k, v in meta["state"].items():
            if hasattr(st, k):
                setattr(st, k, v)
        self.state = st
        self.ended = False
        self.choices = [parse_choice(i, t) for i, t in enumerate(self.ink.get_current_choices())]
        return meta
