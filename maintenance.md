# Maintenance

A check to run every couple of months, so the build keeps working while every dependency floats at its latest version. Nothing here is pinned on purpose. The cost is that an upstream release can break a build with no change on our end, and the smoke test is there to catch that before it ships.

Plan on 20 minutes if everything passes.

## 1. Run the build on GitHub

1. Go to the repo's Actions tab, pick "Build and release", hit Run workflow.
2. Wait for it to finish. The smoke test alone takes about 3 minutes.
3. Green means the latest Python, PyQt6, scipy, numpy, pyfluidsynth, sounddevice, mido, PyInstaller and appimagetool all still work together. Download the artifact and open it once, since a green build that won't open on your desktop is still broken.

If it's red, read which step failed and go to the matching section below.

## 2. Read the smoke test output

Even on a green run, open the "Smoke test" step's log and look for lines starting with `smoke-test: warning:`.

- `music/cues/x.mid differs from what music/generate.py writes now`: either someone edited `generate.py` without regenerating, or a new Python changed what `random` returns for the same seed. Run `python3 music/generate.py`, render with `python3 -m calder_falls.audio.render`, and listen to the changed cues before committing them. A changed seed means changed notes.

## 3. When a step fails

### System packages

`ubuntu-latest` moves to a new Ubuntu release every couple of years. If apt can't find a package:

- `libfluidsynth3` will become `libfluidsynth4` whenever FluidSynth bumps its soname. Search packages.ubuntu.com for `libfluidsynth`, swap the name in `release.yml`.
- Same for `libportaudio2`.
- `fluidr3mono-gm-soundfont` only matters if `soundfonts/FluidR3Mono_GM.sf3` is missing from the repo.

### Python packages

If `pip install` fails, the newest Python on the runner probably came out before one of the packages shipped wheels for it. Usually that fixes itself within a few weeks. If it can't wait, set `python-version` in `release.yml` to the previous release, like `"3.13"`, and put it back to `"3.x"` next check.

If the smoke test fails right after an upgrade:

- An error from `fluidsynth.py` usually means pyfluidsynth renamed something. The engine only uses `Synth`, `sfload`, `noteon`, `noteoff`, `cc`, `program_change`, `pitch_bend`, `all_sounds_off`, `program_reset`, `set_reverb`, `set_chorus` and the raw `_fl.fluid_synth_write_float`. Check pyfluidsynth's changelog for whichever one broke.
- An error from `scipy.signal` means a filter function changed. The engine uses `butter`, `sosfilt` and nothing else at runtime.
- A `jukebox` failure with a Qt message usually means PyQt6 moved an enum. The fix is the new name, one line.

### AppImage build

- PyInstaller errors about a missing module: add `--hidden-import thatmodule` to `build/build-appimage.sh`.
- An error from `pyi_rth_pkgres` means setuptools crept back in. The build already excludes `pkg_resources` and `setuptools`; check they're still in the exclude list.
- appimagetool is pulled from its `continuous` release. If its command line changes, its README on GitHub has the new flags.
- The excludelist comes from AppImageCommunity/pkg2appimage. If that URL dies, the script falls back to a short built-in list and says so. Find the new location and update the URL.

### AppImage selftest

`PortAudio failed to load` means `calder_falls/_libs.py` isn't finding the bundled `libportaudio.so.2`. Extract the AppImage (`./Calder-Falls-Jukebox-x86_64.AppImage --appimage-extract`) and check that `squashfs-root/usr/lib/calder-falls-jukebox/_internal/` still holds `libportaudio.so*` and `libfluidsynth.so*`. PyInstaller has moved that folder once before.

## 4. Licenses

- GeneralUser GS (step 2's optional download): older versions of its license asked sites not to hotlink the download files. Read the license in the latest release on its author's GitHub and confirm a one-click download from the game is still fine. Debian flagged the provenance of its samples, which is why it isn't bundled.
- FluidR3 Mono: MIT. The license is `soundfonts/LICENSE-FluidR3Mono.txt`. Nothing to check unless the bank gets swapped.
- Calder.sf2: ours, generated. Nothing to check.

## 5. Loudness

If any cue changed since the last check:

1. `pip install pyloudnorm`
2. `python3 -m calder_falls.audio.loudness`
3. Anywhere the suggested `gain_db` is more than 1 dB off the current one, copy the suggestion into `calder_falls/audio/cues.py`.
4. `python3 -m calder_falls.audio.render` to refresh the `.ogg` files.

## 6. GitHub Actions versions

`release.yml` uses `actions/checkout@v5`, `actions/setup-python@v6` and `actions/upload-artifact@v4`. GitHub warns in the run log when a major version is being retired. If you see that warning, bump the number to whatever the action's README says is current.

## 7. Write it down

Add an entry to `changes.md` for anything you changed, even a one-line fix, so the next check knows what moved.
