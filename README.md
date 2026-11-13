# Calder Falls

Calder Falls is a text-based psychological horror game for Linux, Windows and Android, for anyone who wanted the full game P.T. was teasing and never got it. You are a state police detective sent to a house where a father killed his family, and the hallway loops.

It plays with buttons under the text. The story is written in Ink, the music is sequenced live through FluidSynth on the desktop, and GitHub Actions builds a Linux AppImage, a Windows zip and installer, and an Android APK.

## What's in here

- `story/`: the whole game in Ink, 13 chapters, five endings. `story/build/main.json` is the compiled story the game runs.
- `calder_falls/`: the desktop game. Window, story wrapper, notebook and radio, theme warps, saves, settings.
- `calder_falls/audio/`, `music/`, `soundfonts/`, `renders/`: the music. `calder_falls/audio/variants.py` pre-renders it for Android.
- `calder_falls/jukebox.py`: the step 1 listening tool. Source only now, no AppImage.
- `android/`: the Android version. A thin front end in `android/www/` (HTML, CSS, JavaScript) that plays the same compiled story on inkjs inside a WebView, plus the Gradle project that wraps it in an APK.
- `fonts/`: Courier Prime, Caveat, Cedarville Cursive, Source Serif 4, all SIL Open Font License, licenses next to them.
- `assets/icon/`: the water tower, SVG and PNGs.
- `build/`: AppImage build, Windows build (`build-exe.py`, `windows/calder-falls.iss`), smoke test, icon renderer.

## Prerequisites

- To play: the AppImage on any glibc Linux, the zip or installer on 64-bit Windows 10 or 11, the APK on Android 8 or newer. Nothing else.
- To run from source: Linux, glibc-based. I'm on Kubuntu, so the package names below are Ubuntu's. Other distros have the same libraries under their own names.
- Also for source: Python 3.10 or newer with venv, plus `sudo apt install python3-venv libfluidsynth3 libportaudio2`.
- To change the story: inklecate, from inkle's GitHub releases (`inklecate_linux.zip`). Put it in `build/tools/`, since that's where the game looks first, or on your PATH.

## Playing

### The AppImage

1. Grab `Calder-Falls-x86_64.AppImage` from the repo's Releases page, or from an Actions run's artifacts.
2. `chmod +x Calder-Falls-x86_64.AppImage`, since downloads don't keep the executable bit.
3. Run it.

The first launch asks about flashing effects before anything flashes. Pick one. You can change it later in Settings.

### Windows

1. Grab `Calder-Falls-Setup-x64.exe` from Releases and run it. It installs for your user only, so no admin prompt.
2. Or grab `Calder-Falls-windows-x64.zip`, unzip it anywhere, and run `Calder Falls.exe` inside. Same game, nothing installed.

Windows SmartScreen will warn about both, since they aren't code-signed. "More info", then "Run anyway". Saves live in `%APPDATA%\calder-falls\saves\`.

### Android

1. Grab `Calder-Falls-android.apk` from Releases on the phone.
2. Open it. Android asks to allow installs from your browser or file manager the first time, allow it.
3. Play. The story is the full game. The notebook, evidence, map and radio are tabs along the bottom on a phone, and beside the story on a tablet in landscape.

The back button closes a dialog, then switches back to the story, then opens the menu. On the title screen it leaves. In dark scenes the flashlight follows your finger and stays where you lift it. Turning choices change under your finger as you press, and what they say then is what you pick.

Every APK the workflow builds gets a signed build provenance attestation, listed under the repo's Actions tab, Attestations. Anyone with the gh CLI can check a download against it with `gh attestation verify Calder-Falls-android.apk --repo NullAngst/Calder-Falls`.

### From source

1. `cd calder-falls`
2. `python3 -m venv .venv`, since that keeps these packages out of your system Python.
3. `. .venv/bin/activate`
4. `pip install -r requirements.txt`
5. `python3 -m calder_falls`

## How it plays

Read, then pick what Brennick does from the buttons under the text. Click the text to skip ahead while it types.

- **The notebook.** What you find goes into the tabs on the right: notes, Polaroids and statements, a county map marked up in pen. When the case lets you, you file a theory: who, what, when, why. The options only show up once you've found what supports them. A right theory moves you on. A wrong one resets the loop and the house gets worse. Partial credit still counts toward the truth you built.
- **Nerve** is the meter in the top strip. It drops in bad moments and comes back when you rest or smoke. Low Nerve pushes the window one stage further gone and makes the buttons hard to click.
- **The radio** tab has an AM dial you drag and a police band knob. Sometimes something is on a frequency. 1610 tells you true things. Acting on it changes you.
- **Hint**, top right, always works and never lies.

The game autosaves at every loop and chapter start. Save to one of three slots from the menu (Esc also opens it). Saves live in `~/.local/share/calder-falls/saves/` on Linux, `%APPDATA%\calder-falls\saves\` on Windows, and in the app's own data on Android.

## Settings

- Flicker and flashes: no flicker, gentle (the default), or full. No flicker is a still picture: no flashes or scanlines, the film grain and fog frozen in place, the low-battery flashlight steady, the drifting letters in Act IV held where they drifted, and the title screen light always on. Gentle keeps the effects but slides the grain instead of jumping it and softens the flicker.
- Honest controls: turns off the choices that change what they say on hover and the buttons that slide away from the mouse. Every other effect stays.
- Flashlight cone: off dims dark scenes evenly instead.
- Timed choices: off by default.
- Fourth-wall effects: the fake crash, the fake corrupted save, the title screen that changes between launches, the How to Play page that gets rewritten.
- Text size, story font, reveal speed, music volume.
- Sound bank (desktop only): FluidR3 Mono is bundled. GeneralUser GS sounds better and is a one-click download from its author's GitHub; it isn't bundled because Debian flagged that some of its sample origins aren't documented. Restart the game after switching.

## The music

The jukebox from step 1 is still here, from source: `python3 -m calder_falls.jukebox`. It plays every cue live with the controls the story drives: tempo, detune, layers, the PS2 filter, static bleed. `renders/*.ogg` has every cue rendered once through.

Android has no FluidSynth, so the music there is pre-rendered. `python3 -m calder_falls.audio.variants` plays the story with the autoplayer, notes every combination of cue, layers, tempo and detune it reaches (43 right now), and renders each one through the real engine to a seamless loop. The phone crossfades between those files at the same point in the cue when a layer drops or the tempo changes, and runs the static bleed live. The build does this on the runner, so none of it is committed.

## Changing things

EDIT THE SOURCE FILES, NOT THE GENERATED ONES. `story/build/main.json`, `music/cues/*.mid`, `soundfonts/Calder.sf2` and `renders/*.ogg` all get overwritten.

- The story: edit the `.ink` files under `story/` (Inky, inkle's free editor, works fine), then run `python3 -m calder_falls.storytest`. That compiles it, fails on any warning, checks every tag, and plays routes to all five endings in a couple of seconds. `story/README-ink.md` lists every tag and choice prefix the game understands.
- A new tag, warp or game rule: change `calder_falls/story.py` and its port `android/www/js/story.js` together, and the matching window code in `calder_falls/app.py` and `android/www/js/app.js`. The JavaScript files follow the Python ones function by function, so the counterpart is easy to find. `node android/test/storytest.js` plays the same routes on the Android side.
- A music cue: edit its function in `music/generate.py`, run `python3 music/generate.py cue_name`, then `python3 -m calder_falls.audio.render cue_name`.
- A sound in Calder.sf2: edit `soundfonts/build_calder.py` and run it.

## Building

GitHub does it for you, see Making a release below. Every push to main and every pull request runs the checks: the smoke test, and the same story routes on inkjs for Android. The builds only run when you start the workflow by hand.

To build the AppImage locally on Ubuntu or whichever glibc distro:

1. `sudo apt install libfluidsynth3 libportaudio2 curl`
2. `pip install -r requirements.txt pyinstaller`
3. Put inklecate in `build/tools/`.
4. `bash build/smoke-test.sh`, since that also compiles the story the build needs.
5. `bash build/build-appimage.sh`
6. `bash build/smoke-test.sh dist/Calder-Falls-x86_64.AppImage`

The Windows build only runs on Windows, since PyInstaller can't cross-build. On a Windows machine with Python: `pip install -r requirements.txt pyinstaller pillow`, download a `win10-x64` zip from FluidSynth's GitHub releases into a folder, then `python build/build-exe.py --fluidsynth thatfolder`. Add `--installer` if Inno Setup 6 is installed.

The Android build, on Linux with Node, Gradle and the Android SDK:

1. `bash android/build-web.sh`, which renders the music (about 5 minutes) and assembles the web content in `android/web-out/`.
2. `pip install playwright`, `python3 -m playwright install chromium`, then `python3 android/test/webtest.py` to play it in a headless browser at phone and tablet sizes.
3. `ANDROID_HOME=~/Android/Sdk bash android/build-android.sh`, or wherever your SDK is. Without the signing variables below the APK comes out unsigned.

The biggest file in the repo is `soundfonts/FluidR3Mono_GM.sf3` at 23.6 MB, under the 25 MB web upload limit. The AppImage is about 140 MB, the Windows zip about the same, the APK about 45 MB.

## Making a release

1. Bump `__version__` in `calder_falls/__init__.py`, since the APK's version comes from it too. Add an entry to `changes.md`.
2. Upload everything through the web UI as usual. The workflow calls every script with `bash`, so the dropped executable bit doesn't matter.
3. Go to Releases, Draft a new release, create a new tag there (like `v0.3.0`), and publish it.
4. Go to Actions, click "Build and release", click Run workflow, pick that tag under "Use workflow from", and run it.
5. Wait about 25 minutes. The workflow builds from that tag and attaches `Calder-Falls-x86_64.AppImage`, `Calder-Falls-windows-x64.zip`, `Calder-Falls-Setup-x64.exe` and `Calder-Falls-android.apk` to that release.

If you run it on a branch, the builds still finish and sit under the run's artifacts, but the "Release target" job fails and says why. Same if the tag has no release yet. Nothing gets attached unless all three builds pass.

## Signing the Android app

Android only installs signed APKs, and every update has to be signed with the same key, so make the key once and keep it somewhere safe. If you already have one for Isobar, you can use that same keystore here, since the secret names match.

1. Make a keystore, if you don't have one: `keytool -genkeypair -v -keystore calder-release.jks -alias calder -keyalg RSA -keysize 4096 -validity 10000`. It asks for a password and a few name fields.
2. `base64 -w 0 calder-release.jks > calder-release.jks.b64`
3. In the repo on GitHub: Settings, Secrets and variables, Actions, New repository secret. Add four:
   - `ANDROID_KEYSTORE_BASE64`: the contents of `calder-release.jks.b64`
   - `ANDROID_KEYSTORE_PASSWORD`: the keystore password
   - `ANDROID_KEY_ALIAS`: `calder`, or whichever alias you picked
   - `ANDROID_KEY_PASSWORD`: the key password (the same as the keystore password unless you set a different one)
4. Delete `calder-release.jks.b64`. Keep `calder-release.jks` and its password backed up. LOSE IT AND NOBODY CAN UPDATE THE APP WITHOUT UNINSTALLING IT FIRST, WHICH DELETES THEIR SAVES.

Without the secrets the Android job stops with a message pointing here.

## Where this differs from the spec

Step 1 (music):
- The base bank is FluidR3 Mono instead of FluidR3_GM: same instruments, mono samples like the PS2 actually had, 23.6 MB instead of 148 MB.
- "Mono-sum per voice" is partly approximated, since FluidSynth mixes voices before the engine sees them.
- Switching cues fades out and waits out the reverb tail. There's no crossfade.

Step 2 (everything else):
- **Length.** The story is 31,600 words of Ink across all 13 chapters, not the 90,000 to 110,000 the spec planned. Every chapter, loop, house and ending is written and playable, but the chapters are shorter than planned. I haven't timed a playthrough. At a normal reading pace, plus Act I's repeated hallway, the word count suggests roughly two to three hours, not five to eight.
- **The Ink runtime is bink, not inkcpp_py.** inkcpp_py loses and duplicates tags when an Ink function runs while a tag is waiting for its line, and this story does that constantly. The inkjs fallback won't load in Qt's JS engine; it throws on its own class constructors. bink is the Python binding for Blade Ink, a Rust port of the official runtime, Apache 2.0, and it ships as a prebuilt wheel, so the build no longer compiles anything. It's still a small project with one main maintainer, so it's the new weak spot. Swapping runtimes again touches `calder_falls/story.py` only.
- Saves are Ink's own JSON state plus a small JSON of window state, so `slot-1.ink.json` and `slot-1.json` rather than a binary snapshot.
- Test Pattern is reached by starting a second playthrough. The game sets `second_run` once any ending is on your profile. The smoke test sets that flag directly instead of finishing a whole first run.
- The step 1 jukebox no longer builds as its own AppImage. It still runs from source.

Android:
- The music is pre-rendered, not sequenced live. Every state the story reached in 45 autoplayed runs has its own file, plus the Spindle's slower record on later visits, which the autoplayer never goes back for. A state no run reached falls back to the closest file for that cue and makes up the tempo and pitch with playback speed, so the record slows down a little lower in pitch, like tape. Static bleed is live and the same as the desktop's.
- The changing window title ("one six one zero, four") has no window to go in, so it replaces the inventory line in the top strip.
- No sound bank choice. The renders use FluidR3 Mono.
- Saves don't move between the desktop and Android. The format is the same, but Android keeps them in the app's own storage.

## What I could not check

I can't hear audio, and I can't watch the window move. Everything below was checked headless:

- The story compiles with zero warnings, and every tag maps to code.
- Scripted routes reach all five endings. Wandering runs that file wrong theories on purpose still reach an ending.
- Every right theory answer can actually be found before you file it.
- Saves load back to the same place.
- The window plays the Prologue with music, toggles every setting, fakes the crash and loads a save.
- Both AppImages pass their own selftest.

Windows and Android were added later, and the same limits apply harder there:

- The Windows build has never run on Windows. Its build script and bundle layout were checked by running the same PyInstaller steps on Linux, and that bundle passes the selftest. The workflow runs the real Windows bundle's selftest on the runner, which is the first true test of FluidSynth's DLLs loading.
- The Android front end plays the full story in Node on inkjs (all five endings, the theory checks, saves), and plays into Chapter 2 in headless Chromium at phone and tablet sizes with music, every tab and dialog, and save and load. It has never run in a real WebView on a real phone, and the Java wrapper and Gradle files have never compiled, since there's no Android SDK where I built this. The first workflow run is their first build.

What that doesn't cover: the GeneralUser GS download (GitHub's API is blocked from where I built this, so it has never run), whether the writing is scary, whether the effects look right on a real screen, whether the theme hex values need tuning (the spec said they would), and live sound through PortAudio to your speakers.
