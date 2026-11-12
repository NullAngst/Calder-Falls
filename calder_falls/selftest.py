"""Headless check of the game window. Run with --selftest, no display needed
(QT_QPA_PLATFORM=offscreen). It plays the Prologue through the real window
with music rendered offline, toggles every setting, fakes the crash, files
theories, saves and loads, opens every dialog, and exits 0 if nothing broke.
"""

import sys
import time
import traceback

import numpy as np

from . import story
from .settings import Settings
from .ui.dialogs import FirstLaunchDialog, HowToDialog, SaveDialog, SettingsDialog, TheoryDialog
from .ui.title import subtitle_for

FAILS = []


def check(ok, what):
    print(("  ok   " if ok else "  FAIL ") + what, flush=True)
    if not ok:
        FAILS.append(what)


def pump(app, seconds=0.0):
    end = time.monotonic() + seconds
    while True:
        app.processEvents()
        if time.monotonic() >= end:
            break
        time.sleep(0.01)


def settle(app, win):
    """Let the typewriter finish (by skipping) and the choices appear."""
    for _ in range(50):
        pump(app)
        if win.view.is_revealing():
            win.view.skip()
        if win.crash.isVisible():
            win.crash._restart()
            pump(app, 1.3)
        if win.choices.buttons or win.ended:
            return True
    return bool(win.choices.buttons) or win.ended


def pick(win, used):
    buttons = [b for b in win.choices.buttons if hasattr(b, "choice")]
    if not buttons:
        return None

    def key(b):
        t = b.choice.truth
        w = used.get(t, 0)
        if t.startswith("Walk to the kitchen"):
            w += 0.5
        if t.startswith("Keep looking"):
            w += 5
        return w
    return min(buttons, key=key).choice


def play_until(app, win, done, limit=400):
    used = {}
    for _ in range(limit):
        if not settle(app, win):
            return False
        if win.ended or done():
            return True
        c = pick(win, used)
        if c is None:
            return False
        used[c.truth] = used.get(c.truth, 0) + 1
        if c.kind == "file" or c.truth.startswith("Walk to the kitchen"):
            used.clear()
        win.on_choice(c)
    return done()


def run(app, win):
    errors = []

    def hook(etype, value, tb):
        errors.append("".join(traceback.format_exception(etype, value, tb)))
    sys.excepthook = hook

    win.show()
    pump(app, 0.2)
    print("title screen", flush=True)
    check(win.stack.currentWidget() is win.title, "starts on the title screen")
    from .settings import Profile
    subs = {subtitle_for(Profile(launches=n, endings_seen=e), True)
            for n, e in ((1, []), (2, []), (5, []), (8, []), (2, ["quiet_house"]), (3, ["dawn"]), (1, ["broadcast"]))}
    check(len(subs) >= 5, f"title screen changes between launches ({len(subs)} variants)")
    check(subtitle_for(Profile(launches=9), False) == "Ostrander County, October 1986",
          "title screen stays put with fourth-wall effects off")

    print("audio library", flush=True)
    from ._libs import check_portaudio
    ok, msg = check_portaudio()
    print("    " + msg, flush=True)
    check(ok, "PortAudio loads")

    print("prologue with sound", flush=True)
    win.new_game()
    check(win.session is not None, "a new game starts")
    sound = 0.0
    if win.audio is not None:
        block = win.audio.render(3.0)
        sound = float(np.sqrt(np.mean(np.square(block, dtype=np.float64))))
    check(win.audio is not None and sound > 0.003, f"music plays during the Prologue (rms {sound:.4f})")
    reached = play_until(app, win, lambda: win.session.state.chapter_no >= 2)
    check(reached, "plays through the Prologue to Cobb Road")
    if win.audio is not None:
        block = win.audio.render(2.0)
        check(np.isfinite(block).all(), "audio stays finite in Act I")

    print("settings", flush=True)
    base = Settings(**vars(win.settings))
    variants = [
        {"flicker": "off"}, {"flicker": "full"}, {"flicker": "gentle"},
        {"honest_controls": True}, {"honest_controls": False},
        {"flashlight_cone": False}, {"flashlight_cone": True},
        {"timed_choices": True}, {"timed_choices": False},
        {"fourth_wall": False}, {"fourth_wall": True},
        {"text_size": 22}, {"text_size": 15},
        {"font": "Source Serif 4"}, {"font": "Courier Prime"},
        {"reveal_speed": 0}, {"reveal_speed": 55},
        {"music_volume": 0}, {"music_volume": 80},
    ]
    for v in variants:
        for k, val in v.items():
            setattr(win.settings, k, val)
        win.apply_settings()
        pump(app)
        if win.choices.buttons:
            pass
        check(True, f"setting {list(v)[0]} = {list(v.values())[0]}")
    for k, val in vars(base).items():
        setattr(win.settings, k, val)
    win.apply_settings()

    print("no flicker means a still picture", flush=True)
    settle(app, win)
    for mode in ("off", "full"):
        win.settings.flicker = mode
        win.apply_settings()
        for stage in ("midnight", "fog", "bleed", "static", "dead_signal"):
            win.set_stage(stage, instant=True)
            pump(app, 0.2)
            a = win.overlay.grab().toImage()
            pump(app, 0.6)
            b = win.overlay.grab().toImage()
            if mode == "off":
                check(a == b, f"no flicker: the {stage} overlay draws the same frame twice")
            elif stage == "static":
                check(a != b, "full flicker: the overlay does change between frames (the check can see motion)")
        # the dark flashlight scene with a dying battery
        win.set_stage("midnight", instant=True)
        win.view.set_dark(True)
        win.view.battery_low = True
        from PyQt6.QtCore import QPointF
        win.view.mouse = QPointF(300, 200)
        pump(app, 0.2)
        a = win.view.grab().toImage()
        pump(app, 0.6)
        b = win.view.grab().toImage()
        if mode == "off":
            check(a == b, "no flicker: the low-battery flashlight holds steady")
            check(not win.overlay.timer.isActive(), "no flicker: the overlay stops repainting")
        win.view.set_dark(False)
        win.view.battery_low = False
    for k, val in vars(base).items():
        setattr(win.settings, k, val)
    win.apply_settings()
    win.set_stage(win.session.state.theme, instant=True)

    print("timed choice", flush=True)
    settle(app, win)
    win.settings.timed_choices = True
    win.pending_timed = (0.5, 0)
    win._show_choices()
    before = list(win.session.state.transcript)
    pump(app, 0.9)
    settle(app, win)
    after = list(win.session.state.transcript)
    check(before != after, "a timed choice picks its default when the timer runs out")
    win.settings.timed_choices = False

    print("honest controls and turning choices", flush=True)
    ch = story.parse_choice(0, "Open the door @@ Close the door")
    check(ch.text == "Open the door" and ch.truth == "Close the door", "turning choice text parses")

    print("fourth wall", flush=True)
    win.apply_events([("fourth", "crash")])
    win._revealed()
    check(win.crash.isVisible(), "fake crash shows")
    win.crash._restart()
    pump(app, 1.3)
    check(not win.crash.isVisible(), "fake crash restarts back into the game")
    win.apply_events([("fourth", "corrupt_save")])
    check(win.corrupt_once, "fake corrupted save is armed")
    d = SaveDialog(win.session, "load", corrupt=True, parent=win)
    d.show()
    pump(app)
    d.close()
    win.settings.fourth_wall = False
    win.pending_crash = False
    win.apply_events([("fourth", "crash")])
    check(not win.pending_crash, "fake crash is skipped with fourth-wall effects off")
    win.settings.fourth_wall = True

    print("warps", flush=True)
    for ev in (("warp", "tabs_rename", ""), ("warp", "title_count", "4")):
        win.session.state.tabs_renamed = True
        win.session.state.title_count = "4"
        win.apply_events([ev])
    check(win.tabs.tabText(0) == "Ledger" and win.tabs.tabText(1) == "Family", "tabs rename themselves")
    check("one six one zero" in win.windowTitle(), "window title picks up a household count")
    win.session.state.tabs_renamed = False
    win.session.state.title_count = ""
    win.apply_events([])
    for stage in ("fog", "bleed", "static", "dead_signal", "midnight"):
        win.set_stage(stage, instant=True)
        pump(app, 0.15)
    check(True, "every theme stage renders")

    print("saves", flush=True)
    settle(app, win)
    win.session.save("1")
    texts = [c.text for c in win.session.choices]
    win._load("1")
    settle(app, win)
    check([c.text for c in win.session.choices] == texts, "save and load come back to the same choices")

    print("dialogs", flush=True)
    for dlg in (SettingsDialog(win.settings, win), HowToDialog(False, win), HowToDialog(True, win),
                SaveDialog(win.session, "save", parent=win), FirstLaunchDialog(win)):
        dlg.show()
        pump(app)
        dlg.close()
    th = story.Theory("x", "Test", [story.parse_slot("who;A*;B@ev_none;C")])
    td = TheoryDialog(th, set(), win)
    td.show()
    pump(app)
    check(td.boxes["who"].count() == 2, "theory options without their evidence stay hidden")
    td.close()

    print("act I loops", flush=True)
    reached = play_until(app, win, lambda: win.session.get_var("loop", 0) >= 3, limit=300)
    check(reached, "plays into the Act I loops through the window")

    for e in errors:
        print(e, flush=True)
    check(not errors, "no exceptions in the window")
    win.close()
    print()
    if FAILS:
        print(f"selftest: {len(FAILS)} check(s) failed", flush=True)
        return 1
    print("selftest passed", flush=True)
    return 0
