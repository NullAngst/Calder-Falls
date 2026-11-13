"""Build Calder Falls for Windows: a portable zip and an installer.

    python build/build-exe.py --fluidsynth DIR [--installer]

DIR holds FluidSynth's Windows release zips (the workflow downloads the
latest win10-x64 ones from FluidSynth's GitHub releases), or an already
unpacked FluidSynth folder. Every DLL next to FluidSynth's own goes into
the bundle, since it needs them (glib, libsndfile and the rest).

Writes:
    dist/Calder-Falls/Calder Falls.exe        the game, one folder
    dist/Calder-Falls-windows-x64.zip         that folder, zipped
    dist/Calder-Falls-Setup-x64.exe           with --installer (needs Inno Setup)

Needs the Python deps from requirements.txt plus pyinstaller and pillow,
and story/build/main.json (python -m calder_falls.storytest builds it).
Runs on Windows only: PyInstaller can't cross-build.
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = "Calder Falls"


def fail(msg):
    print(f"build-exe: {msg}", file=sys.stderr)
    sys.exit(1)


def fluidsynth_dir(src, work):
    """The folder holding FluidSynth's DLL, unpacked from a zip if need be."""
    def find(folder):
        for pattern in ("libfluidsynth*.dll", "fluidsynth*.dll"):
            hits = sorted(glob.glob(os.path.join(folder, "**", pattern), recursive=True))
            if hits:
                return hits[0]
        return None

    dll = find(src)
    if dll:
        return os.path.dirname(dll), dll
    zips = sorted(glob.glob(os.path.join(src, "*.zip")))
    # A glib build first when there's a choice: the long-standing one, with
    # every driver and file format in it
    zips.sort(key=lambda z: (0 if "glib" in os.path.basename(z).lower() else 1, z))
    for z in zips:
        out = os.path.join(work, "fluidsynth", os.path.splitext(os.path.basename(z))[0])
        with zipfile.ZipFile(z) as fh:
            fh.extractall(out)
        dll = find(out)
        if dll:
            print(f"build-exe: FluidSynth from {os.path.basename(z)}")
            return os.path.dirname(dll), dll
    fail(f"no FluidSynth DLL in {src} or any zip in it")


def make_icon(work):
    from PIL import Image

    png = os.path.join(ROOT, "assets", "icon", "calder-falls-256.png")
    ico = os.path.join(work, "calder-falls.ico")
    Image.open(png).save(ico, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    return ico


def data(src, dest):
    return f"{src}{os.pathsep}{dest}"


def main():
    ap = argparse.ArgumentParser(description="Build Calder Falls for Windows.")
    ap.add_argument("--fluidsynth", required=True, help="FluidSynth release zips, or an unpacked FluidSynth")
    ap.add_argument("--installer", action="store_true", help="also build the Inno Setup installer")
    args = ap.parse_args()

    if sys.platform != "win32":
        fail("this builds the Windows version and has to run on Windows")
    for f in ("story/build/main.json", "soundfonts/Calder.sf2", "soundfonts/FluidR3Mono_GM.sf3"):
        if not os.path.isfile(os.path.join(ROOT, f)):
            fail(f"{f} is missing")

    sys.path.insert(0, ROOT)
    from calder_falls import __version__

    work = tempfile.mkdtemp(prefix="calder-exe-")
    try:
        fs_dir, fs_dll = fluidsynth_dir(os.path.abspath(args.fluidsynth), work)
        dlls = sorted(glob.glob(os.path.join(fs_dir, "*.dll")))
        print(f"build-exe: bundling {len(dlls)} DLLs from FluidSynth: {', '.join(os.path.basename(d) for d in dlls)}")
        icon = make_icon(work)

        import PyInstaller.__main__

        dist = os.path.join(ROOT, "dist")
        os.makedirs(dist, exist_ok=True)
        cmd = [
            "--noconfirm", "--clean", "--onedir", "--windowed", "--log-level", "WARN",
            "--name", APP,
            "--icon", icon,
            "--distpath", os.path.join(work, "dist"),
            "--workpath", os.path.join(work, "build"),
            "--specpath", work,
            "--paths", ROOT,
            "--collect-all", "bink",
            "--add-data", data(os.path.join(ROOT, "story", "build", "main.json"), "story/build"),
            "--add-data", data(os.path.join(ROOT, "fonts"), "fonts"),
            "--add-data", data(os.path.join(ROOT, "calder_falls", "themes", "midnight.qss"), "calder_falls/themes"),
            "--add-data", data(os.path.join(ROOT, "music", "cues"), "music/cues"),
            "--add-data", data(os.path.join(ROOT, "soundfonts", "Calder.sf2"), "soundfonts"),
            "--add-data", data(os.path.join(ROOT, "soundfonts", "FluidR3Mono_GM.sf3"), "soundfonts"),
            "--add-data", data(os.path.join(ROOT, "soundfonts", "LICENSE-FluidR3Mono.txt"), "soundfonts"),
            "--add-data", data(os.path.join(ROOT, "assets", "icon"), "assets/icon"),
            "--exclude-module", "tkinter", "--exclude-module", "matplotlib", "--exclude-module", "soundfile",
            "--exclude-module", "pkg_resources", "--exclude-module", "setuptools",
        ]
        for d in dlls:
            cmd += ["--add-binary", data(d, ".")]
        cmd.append(os.path.join(ROOT, "build", "game-entry.py"))
        PyInstaller.__main__.run(cmd)

        folder = os.path.join(dist, "Calder-Falls")
        shutil.rmtree(folder, ignore_errors=True)
        shutil.move(os.path.join(work, "dist", APP), folder)
        print(f"build-exe: built {folder}")

        zpath = os.path.join(dist, "Calder-Falls-windows-x64.zip")
        if os.path.exists(zpath):
            os.remove(zpath)
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
            for base, _dirs, files in os.walk(folder):
                for f in files:
                    full = os.path.join(base, f)
                    zf.write(full, os.path.join("Calder-Falls", os.path.relpath(full, folder)))
        print(f"build-exe: built {zpath}")

        if args.installer:
            iscc = shutil.which("iscc") or shutil.which("ISCC")
            if not iscc:
                for p in (r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe", r"C:\Program Files\Inno Setup 6\ISCC.exe"):
                    if os.path.isfile(p):
                        iscc = p
                        break
            if not iscc:
                fail("Inno Setup (ISCC.exe) not found; install it, or leave out --installer")
            subprocess.run([
                iscc, "/Q",
                f"/DAppVersion={__version__}",
                f"/DSourceDir={folder}",
                f"/DIconFile={icon}",
                f"/DOutDir={dist}",
                os.path.join(ROOT, "build", "windows", "calder-falls.iss"),
            ], check=True)
            print(f"build-exe: built {os.path.join(dist, 'Calder-Falls-Setup-x64.exe')}")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
