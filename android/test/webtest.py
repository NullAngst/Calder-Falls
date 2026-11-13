"""Headless check of the Android front end in Chromium, the engine Android's
WebView runs on. Exit code 0 means every check passed.

    python3 android/test/webtest.py            # after bash android/build-web.sh
    python3 android/test/webtest.py --shots DIR    # also save screenshots

Serves android/web-out/assets/www on localhost (a secure origin, like the
app's https://appassets.androidplatform.net), then at phone and tablet sizes:
plays into the game with music, opens every tab and dialog, files a theory
if one comes up, saves and loads, and fails on any JavaScript error.

Needs: pip install playwright, then python3 -m playwright install chromium
"""

import argparse
import functools
import http.server
import os
import sys
import threading

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
WWW = os.path.join(os.path.dirname(HERE), "web-out", "assets", "www")
FAILS = []


def check(ok, what):
    print(("  ok   " if ok else "  FAIL ") + what, flush=True)
    if not ok:
        FAILS.append(what)


class Quiet(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".js": "text/javascript", ".ogg": "audio/ogg", ".svg": "image/svg+xml"}

    def log_message(self, *_args):
        pass


def serve():
    handler = functools.partial(Quiet, directory=WWW)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def settle(page, rounds=40):
    """Skip the typing until choice buttons (or the end) show up."""
    for _ in range(rounds):
        page.evaluate("CF.game.view.isRevealing() && CF.game.view.skip()")
        if page.evaluate("!document.getElementById('crash').classList.contains('hidden')"):
            page.click("#crash-restart")
            page.wait_for_timeout(1400)
        n = page.locator("#choice-grid button").count()
        if n:
            return n
        page.wait_for_timeout(100)
    return 0


def pick(page, used):
    """Least-used visible choice, avoiding the ones that loop back."""
    labels = page.eval_on_selector_all("#choice-grid button", "bs => bs.map(b => b.textContent)")
    best = min(range(len(labels)), key=lambda i: (used.get(labels[i], 0) + (5 if labels[i].startswith("Keep looking") else 0), i))
    used[labels[best]] = used.get(labels[best], 0) + 1
    return best


def run(page, size_name, shots):
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

    page.goto(page.base + "/index.html")
    # First launch asks about flicker before anything flashes
    page.wait_for_selector(".dialog", timeout=15000)
    check(page.locator(".dialog input[value=gentle]").is_checked(), f"{size_name}: first launch asks about flicker, gentle preselected")
    page.click(".dialog button")
    try:
        page.wait_for_function("document.getElementById('subtitle').textContent !== ''", timeout=15000)
        check(True, f"{size_name}: title screen has its subtitle")
    except Exception:
        check(False, f"{size_name}: title screen has its subtitle")
    if shots:
        page.screenshot(path=os.path.join(shots, f"{size_name}-title.png"))

    page.wait_for_function("CF.game.music.voice !== null", timeout=20000)
    state = page.evaluate("CF.game.music.ctx.state")
    check(state == "running", f"{size_name}: title music is playing (AudioContext {state})")
    check(page.evaluate("!!CF.game.music.staticNode"), f"{size_name}: the static bleed worklet loaded")

    page.click("[data-act=new]")
    page.wait_for_selector("#game:not(.hidden)")
    used = {}
    choices_made = 0
    filed = False
    for _ in range(60):
        n = settle(page)
        if not n:
            break
        if page.evaluate("CF.game.session.pendingTheory() !== null") and not filed:
            # file the theory with whatever is in the boxes
            buttons = page.eval_on_selector_all("#choice-grid button", "bs => bs.map(b => b.textContent)")
            files = [i for i, _ in enumerate(buttons)
                     if page.evaluate(f"CF.game.session.visibleChoices()[{i}].kind") == "file"]
            if files:
                page.locator("#choice-grid button").nth(files[0]).click()
                page.wait_for_selector(".dialog .theory-title")
                if shots:
                    page.screenshot(path=os.path.join(shots, f"{size_name}-theory.png"))
                page.click(".dialog button:has-text('File it')")
                filed = True
                choices_made += 1
                continue
        page.locator("#choice-grid button").nth(pick(page, used)).click()
        choices_made += 1
        if page.evaluate("CF.game.session.state.chapter_no") >= 2:
            break
    check(choices_made >= 10, f"{size_name}: played {choices_made} choices into chapter "
          f"{page.evaluate('CF.game.session.state.chapter_no')}")
    check(page.evaluate("CF.game.music.state.cue") is not None, f"{size_name}: the story switched music cues "
          f"(now {page.evaluate('CF.game.music.state.cue')})")
    if shots:
        page.screenshot(path=os.path.join(shots, f"{size_name}-story.png"))

    for tab in ("notebook", "evidence", "map", "radio"):
        page.click(f"#tabs [data-tab={tab}]")
        page.wait_for_timeout(150)
        visible = page.evaluate(f"document.querySelector('#side .pane[data-pane={tab}]').offsetParent !== null")
        check(visible, f"{size_name}: the {tab} tab opens")
        if shots:
            page.screenshot(path=os.path.join(shots, f"{size_name}-{tab}.png"))
    if page.locator("#tabs [data-tab=story]").is_visible():
        page.click("#tabs [data-tab=story]")

    # Every theme stage, and the dark flashlight scene
    for stage in ("fog", "bleed", "static", "dead_signal", "midnight"):
        page.evaluate(f"CF.game.setStage('{stage}', true)")
        page.wait_for_timeout(120)
        if shots:
            page.screenshot(path=os.path.join(shots, f"{size_name}-stage-{stage}.png"))
    page.evaluate("CF.game.view.setDark(true)")
    page.wait_for_timeout(200)
    if shots:
        page.screenshot(path=os.path.join(shots, f"{size_name}-dark.png"))
    page.evaluate("CF.game.view.setDark(CF.game.session.state.dark)")

    # Music tags the story uses, straight at the player
    for tag in ("music_layer:drums off", "music_tempo:0.85", "music_detune:-25", "music_static:0.5",
                "music:the_spindle", "music_static:0"):
        page.evaluate(f"CF.game.music.applyTag({tag!r})")
        page.wait_for_timeout(250)
    page.wait_for_function("CF.game.music.voice && CF.game.music.voice.variant.cue === 'the_spindle'", timeout=20000)
    check(True, f"{size_name}: music follows layer, tempo, detune and static tags")

    # Menu, save, load
    page.click("#menu-btn")
    page.click(".dialog button:has-text('Save')")
    page.click(".dialog .slots button:has-text('Slot 1')")
    before = page.evaluate("CF.game.session.choices.map(c => c.text).join('|')")
    page.click("#menu-btn")
    page.click(".dialog button:has-text('Load')")
    page.click(".dialog .slots button:has-text('Slot 1')")
    page.wait_for_timeout(200)
    after = page.evaluate("CF.game.session.choices.map(c => c.text).join('|')")
    check(before == after and before != "", f"{size_name}: a save loads back to the same choices")

    # Settings and How to Play open and close; the back button walks out
    page.click("#menu-btn")
    page.click(".dialog button:has-text('Settings')")
    page.select_option("#s-flicker", "off")
    page.click(".dialog button:has-text('Save')")
    check(page.evaluate("CF.game.settings.flicker") == "off", f"{size_name}: settings save")
    page.click("#menu-btn")
    page.click(".dialog button:has-text('How to Play')")
    check(page.evaluate("CF.back()") == "handled", f"{size_name}: back closes a dialog")
    check(page.evaluate("CF.back()") == "handled", f"{size_name}: back in the game opens the menu")
    page.evaluate("CF.back()")
    page.evaluate("CF.game.showTitle()")
    check(page.evaluate("CF.back()") == "exit", f"{size_name}: back on the title screen leaves the app")
    check(page.evaluate("!document.querySelector('[data-act=continue]').disabled"), f"{size_name}: Continue is offered after a save")

    for e in errors:
        print("    " + e)
    check(not errors, f"{size_name}: no JavaScript errors")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", help="folder for screenshots")
    args = ap.parse_args()
    if not os.path.isfile(os.path.join(WWW, "index.html")):
        print("webtest: run bash android/build-web.sh first", file=sys.stderr)
        return 1
    if args.shots:
        os.makedirs(args.shots, exist_ok=True)
    srv = serve()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    sizes = [("phone", 412, 915, True), ("tablet", 1280, 800, True)]
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        for name, w, h, touch in sizes:
            print(f"{name} ({w}x{h})", flush=True)
            ctx = browser.new_context(viewport={"width": w, "height": h}, has_touch=touch, device_scale_factor=2)
            page = ctx.new_page()
            page.base = base
            try:
                run(page, name, args.shots)
            except Exception as exc:  # a timeout or a missing element is a failure, not a crash
                check(False, f"{name}: {str(exc).splitlines()[0]}")
            ctx.close()
        browser.close()
    srv.shutdown()
    print()
    if FAILS:
        print(f"{len(FAILS)} check(s) failed:")
        for f in FAILS:
            print(f"  {f}")
        return 1
    print("all Android web checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
