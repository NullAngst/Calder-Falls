# Maintenance

A check to run every couple of months, so the build keeps working while every dependency floats at its latest version. Nothing here is pinned on purpose. The cost is that an upstream release can break a build with no change on our end, and the smoke test is there to catch that before it ships.

Plan on 30 minutes if everything passes.

## 1. Run the build on GitHub

1. Go to the repo's Actions tab, pick "Build and release", hit Run workflow.
2. Wait for it to finish. The smoke test alone takes about 3 minutes.
3. Green means the latest Python, PyQt6, scipy, numpy, pyfluidsynth, bink, sounddevice, mido, inklecate, PyInstaller and appimagetool all still work together. Download the artifacts and open both AppImages once, since a green build that won't open on your desktop is still broken. Play the Prologue in the game, with sound, as far as the front door.

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

### Latest inklecate

The workflow downloads `inklecate_linux.zip` from inkle's latest GitHub release. If that step fails, inkle has renamed the asset. Look at the release page for the Linux zip and update the URL in `release.yml`.

If the smoke test says inklecate has warnings after an upgrade, a newer compiler got stricter. The warning names the file and line. Fix the Ink, not the check.

### Story checks

`python3 -m calder_falls.storytest` runs in about two seconds, so run it locally first. What its failures mean:

- `unknown tag`: a tag in the `.ink` source the game doesn't handle. A typo, or a new tag that needs adding to `TAGS` in `calder_falls/story.py` and handling in `Session._tag`.
- `route 'x' reaches the y ending`: an ending's conditions in `story/act4/endings.ink` changed, or a route's presets in `calder_falls/storytest.py` no longer push the stats far enough.
- `never found [...]`: a theory's right answer needs evidence the autoplayer could not find in 400 tries. Usually that means the evidence is now unreachable from where the theory is filed. That's a real bug for players too.
- `no ending after N choices`: a loop with no way out.

### bink (the Ink runtime)

bink is a small project with one main maintainer. If a new release breaks the story checks, the error will come from `calder_falls/story.py`, the only file that touches it. The game uses `story_from_file`, `can_continue`, `cont`, `get_current_tags`, `get_current_choices`, `choose_choice_index`, `get_variable`, `set_variable`, `save_state` and `load_state`. Check its changelog for whichever one broke. If bink dies outright, inkcpp_py is the other Python runtime. It needs the tag workaround described in `changes.md`, and the swap stays inside `story.py`.

### AppImage build

- PyInstaller errors about a missing module: add `--hidden-import thatmodule` to `build/build-appimage.sh`.
- The game AppImage collects bink's bundled library with `--collect-all bink`. If bink moves its library file, that flag still finds it. If the game AppImage says bink can't load, extract it and look for the shared library under `_internal/bink/native/`.
- An error from `pyi_rth_pkgres` means setuptools crept back in. The build already excludes `pkg_resources` and `setuptools`; check they're still in the exclude list.
- appimagetool is pulled from its `continuous` release. If its command line changes, its README on GitHub has the new flags.
- The excludelist comes from AppImageCommunity/pkg2appimage. If that URL dies, the script falls back to a short built-in list and says so. Find the new location and update the URL.

### AppImage selftest

`PortAudio failed to load` means `calder_falls/_libs.py` isn't finding the bundled `libportaudio.so.2`. Extract the AppImage (`./Calder-Falls-x86_64.AppImage --appimage-extract`) and check that `squashfs-root/usr/lib/calder-falls/_internal/` still holds `libportaudio.so*` and `libfluidsynth.so*` (for the jukebox, `usr/lib/calder-falls-jukebox/`). PyInstaller has moved that folder once before.

`music plays during the Prologue` failing in the game selftest means the engine came up but rendered silence. Run the music checks on their own (`python3 -m calder_falls.audio.smoke`) to see which part.

## 4. Licenses

- GeneralUser GS (the optional download in Settings, `calder_falls/banks.py`): older versions of its license asked sites not to hotlink the download files. Read the license in the latest release on its author's GitHub and confirm a one-click download from the game is still fine. Debian flagged the provenance of its samples, which is why it isn't bundled.
- FluidR3 Mono: MIT. The license is `soundfonts/LICENSE-FluidR3Mono.txt`. Nothing to check unless the bank gets swapped.
- Calder.sf2: ours, generated. Nothing to check.
- Fonts: all SIL Open Font License, licenses in `fonts/`. They come from the google/fonts repo; nothing to check unless a font is swapped.
- bink: Apache 2.0. Check it hasn't changed license if you bump it by hand.

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
