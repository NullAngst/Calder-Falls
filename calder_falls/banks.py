"""The optional GeneralUser GS download.

It is not bundled: Debian flagged that its sample origins are not fully
documented. The player can fetch it with one click in Settings. This pulls
the latest release of the author's GitHub repo, keeps the .sf2 and its
license text, and points the engine at it through the base_bank file.
Switching back to FluidR3 Mono just removes that file.
"""

import io
import json
import os
import urllib.request
import zipfile

from . import paths

REPO = "mrbumpy409/GeneralUser-GS"
API = f"https://api.github.com/repos/{REPO}/releases/latest"
PREF = "base_bank"


def pref_path():
    return os.path.join(paths.user_dir(), PREF)


def current_choice():
    try:
        with open(pref_path(), encoding="utf-8") as fh:
            p = fh.read().strip()
        return p if os.path.isfile(p) else ""
    except OSError:
        return ""


def use_bundled():
    try:
        os.remove(pref_path())
    except FileNotFoundError:
        pass


def download_generaluser(progress=None):
    """Blocking. Run it off the GUI thread. Returns the .sf2 path."""
    def say(msg):
        if progress:
            progress(msg)

    say("Asking GitHub for the latest GeneralUser GS release")
    req = urllib.request.Request(API, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "calder-falls"})
    with urllib.request.urlopen(req, timeout=30) as r:
        release = json.load(r)
    url = None
    for asset in release.get("assets", []):
        if asset.get("name", "").lower().endswith((".sf2", ".zip")):
            url = asset["browser_download_url"]
            break
    if url is None:
        url = release["zipball_url"]
    tag = release.get("tag_name", "latest")
    say(f"Downloading {tag}")
    req = urllib.request.Request(url, headers={"User-Agent": "calder-falls"})
    with urllib.request.urlopen(req, timeout=300) as r:
        blob = r.read()
    out_dir = paths.user_soundfont_dir()
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "GeneralUser-GS.sf2")
    if url.lower().endswith(".sf2"):
        with open(target, "wb") as fh:
            fh.write(blob)
    else:
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            names = z.namelist()
            sf2 = [n for n in names if n.lower().endswith(".sf2")]
            if not sf2:
                raise RuntimeError("the release has no .sf2 file in it")
            with open(target, "wb") as fh:
                fh.write(z.read(sorted(sf2, key=len)[0]))
            for n in names:
                base = os.path.basename(n).lower()
                if base.startswith("license") or base.startswith("readme"):
                    with open(os.path.join(out_dir, "GeneralUser-GS-" + os.path.basename(n)), "wb") as fh:
                        fh.write(z.read(n))
    with open(pref_path(), "w", encoding="utf-8") as fh:
        fh.write(target)
    say(f"Installed {tag}. Restart the game to hear it.")
    return target
