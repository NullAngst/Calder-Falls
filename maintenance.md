# Maintenance

A check to run every couple of months, so the build keeps working while every dependency floats at its latest version. Nothing here is pinned on purpose. The cost is that an upstream release can break a build with no change on our end, and the smoke test is there to catch that before it ships.

Plan on 30 minutes if everything passes.

## 1. Run the build on GitHub

1. Go to the repo's Actions tab, pick "Build and release", hit Run workflow on main. The "Release target" job fails on a branch, on purpose; ignore it for a check.
2. Wait for it to finish, about 25 minutes. The Android music render is the slow part.
3. Green means the latest Python, PyQt6, scipy, numpy, pyfluidsynth, bink, sounddevice, mido, inklecate, PyInstaller, appimagetool, FluidSynth for Windows, Inno Setup, inkjs, Playwright, Gradle and the Android Gradle Plugin all still work together. Download the artifacts and open each one once, since a green build that won't open is still broken: the AppImage on your desktop, the Windows zip on a Windows machine if you have one, the APK on your phone. Play the Prologue, with sound, as far as the front door.

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

### Story checks against inkjs

`node android/test/storytest.js` plays the Android port of the story code on the latest inkjs. If it fails and the Python story checks pass, either inkjs changed or `android/www/js/story.js` fell behind `calder_falls/story.py`. Compare the two; they go function by function in the same order. The port uses `Story`, `canContinue`, `Continue`, `currentTags`, `currentChoices`, `ChooseChoiceIndex`, `variablesState`, `state.toJson` and `state.LoadJson` from inkjs.

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

`PortAudio failed to load` means `calder_falls/_libs.py` isn't finding the bundled `libportaudio.so.2`. Extract the AppImage (`./Calder-Falls-x86_64.AppImage --appimage-extract`) and check that `squashfs-root/usr/lib/calder-falls/_internal/` still holds `libportaudio.so*` and `libfluidsynth.so*`. PyInstaller has moved that folder once before.

### Windows build

- "Latest FluidSynth for Windows" failing with no matching assets: FluidSynth renamed its release zips. Look at the latest release on github.com/FluidSynth/fluidsynth, find the 64-bit Windows zip, and change the `--pattern` in `release.yml` to match it. The build log prints which zip and which DLLs it used.
- The selftest failing with `Couldn't find the FluidSynth library` or a DLL load error: FluidSynth renamed its DLL again (`libfluidsynth-3.dll` became `fluidsynth-3.dll` in 2.4.5). Add the new name to the Windows patterns in `calder_falls/_libs.py` and to `fluidsynth_dir()` in `build/build-exe.py`.
- "no selftest log was written": the EXE didn't get far enough to open the log, usually a missing DLL. Unzip the artifact on a Windows machine and run `Calder Falls.exe` from a terminal, or use Dependencies (github.com/lucasg/Dependencies) on `_internal\fluidsynth-3.dll` to see what it can't find.
- Inno Setup: the step installs it with Chocolatey if the runner image doesn't have it. If the installer step fails on a script error, Inno Setup changed something; its compiler message names the line in `build/windows/calder-falls.iss`. Never change the `AppId` line, since that's how Windows matches upgrades to the installed copy.

### Android build

Each step in the Android job, and what its failure usually means:

- "Assemble the web content": `calder_falls.audio.variants` failed (the same engine as the music checks, so the smoke test usually fails first), or npm couldn't install inkjs, or inkjs moved its browser build out of `dist/ink.js`. The script says which.
- "Front end checks in Chromium": `android/test/webtest.py` plays the front end at phone and tablet sizes. A failure names the check, and JavaScript errors print in full. Run it locally after `bash android/build-web.sh --music /some/folder/with/renders` to skip the five-minute render.
- "Build the signed APK": the newest Android Gradle Plugin and the current Gradle didn't agree, or the plugin changed its build DSL. The error names the line in `android/app/build.gradle.kts`. A brand-new major plugin version is the usual cause; if the fix isn't obvious, check the plugin's release notes for removed properties.
- "Check the signature": a secret is missing or wrong. See "Signing the Android app" in the README.

Two things in the Android build are fixed numbers on purpose:

- `compileSdk` and `targetSdk` (37, Android 17) in `android/app/build.gradle.kts`. Once a year, after a new Android release, raise both, run the workflow, and play the APK on a phone. A new target can change how Android treats the app (edge-to-edge drawing, the back gesture), which a green build won't show. Google Play isn't involved, so there's no deadline, but don't let it fall years behind.
- `minSdk` 26 (Android 8). No reason to change it.

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

`release.yml` uses `actions/checkout@v5`, `actions/setup-python@v6`, `actions/upload-artifact@v4`, `actions/download-artifact@v4`, `gradle/actions/setup-gradle@v4` and `actions/attest-build-provenance@v2`. GitHub warns in the run log when a major version is being retired. If you see that warning, bump the number to whatever the action's README says is current. Bump upload-artifact and download-artifact together.

## 7. The Android keystore

Check you still have `calder-release.jks` and its password somewhere that isn't this computer. Nothing breaks without it until the day you need it, and then there is no fix.

## 8. Write it down

Add an entry to `changes.md` for anything you changed, even a one-line fix, so the next check knows what moved.
