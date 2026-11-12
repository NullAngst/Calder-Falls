# Calder Falls

Calder Falls is a text-based psychological horror game for Linux, in a desktop window, for anyone who wanted the full game P.T. was teasing and never got it. You are a state police detective sent to a house where a father killed his family, and the hallway loops.

It plays with buttons under the text. The story is written in Ink, the music is sequenced live through FluidSynth, and GitHub Actions builds it into an AppImage.

## What's in here

- `story/`: the whole game in Ink, 13 chapters, five endings. `story/build/main.json` is the compiled story the game runs.
- `calder_falls/`: the game. Window, story wrapper, notebook and radio, theme warps, saves, settings.
- `calder_falls/audio/`, `music/`, `soundfonts/`, `renders/`: the music from step 1, unchanged except for the version number.
- `calder_falls/jukebox.py`: the step 1 listening tool, still built alongside the game.
- `fonts/`: Courier Prime, Caveat, Cedarville Cursive, Source Serif 4, all SIL Open Font License, licenses next to them.
- `assets/icon/`: the water tower, SVG and PNGs.
- `build/`: AppImage build, smoke test, icon renderer.

## Prerequisites

- Linux, glibc-based. I'm on Kubuntu, so the package names below are Ubuntu's. Other distros have the same libraries under their own names.
- To play the AppImage: nothing else.
- To run from source: Python 3.10 or newer with venv, plus `sudo apt install python3-venv libfluidsynth3 libportaudio2`.
- To change the story: inklecate, from inkle's GitHub releases (`inklecate_linux.zip`). Put it in `build/tools/`, since that's where the game looks first, or on your PATH.

## Playing

### The AppImage

1. Grab `Calder-Falls-x86_64.AppImage` from the repo's Releases page, or from an Actions run's artifacts.
2. `chmod +x Calder-Falls-x86_64.AppImage`, since downloads don't keep the executable bit.
3. Run it.

The first launch asks about flashing effects before anything flashes. Pick one. You can change it later in Settings.

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

The game autosaves at every loop and chapter start. Save to one of three slots from the menu (Esc also opens it). Saves live in `~/.local/share/calder-falls/saves/`.

## Settings

- Flicker and flashes: no flicker, gentle (the default), or full. No flicker is a still picture: no flashes or scanlines, the film grain and fog frozen in place, the low-battery flashlight steady, the drifting letters in Act IV held where they drifted, and the title screen light always on. Gentle keeps the effects but slides the grain instead of jumping it and softens the flicker.
- Honest controls: turns off the choices that change what they say on hover and the buttons that slide away from the mouse. Every other effect stays.
- Flashlight cone: off dims dark scenes evenly instead.
- Timed choices: off by default.
- Fourth-wall effects: the fake crash, the fake corrupted save, the title screen that changes between launches, the How to Play page that gets rewritten.
- Text size, story font, reveal speed, music volume.
- Sound bank: FluidR3 Mono is bundled. GeneralUser GS sounds better and is a one-click download from its author's GitHub; it isn't bundled because Debian flagged that some of its sample origins aren't documented. Restart the game after switching.

## The music

The jukebox from step 1 is still here: `python3 -m calder_falls.jukebox`, or the `Calder-Falls-Jukebox-x86_64.AppImage` release. It plays every cue live with the controls the story drives: tempo, detune, layers, the PS2 filter, static bleed. `renders/*.ogg` has every cue rendered once through.

## Changing things

EDIT THE SOURCE FILES, NOT THE GENERATED ONES. `story/build/main.json`, `music/cues/*.mid`, `soundfonts/Calder.sf2` and `renders/*.ogg` all get overwritten.

- The story: edit the `.ink` files under `story/` (Inky, inkle's free editor, works fine), then run `python3 -m calder_falls.storytest`. That compiles it, fails on any warning, checks every tag, and plays routes to all five endings in a couple of seconds. `story/README-ink.md` lists every tag and choice prefix the game understands.
- A music cue: edit its function in `music/generate.py`, run `python3 music/generate.py cue_name`, then `python3 -m calder_falls.audio.render cue_name`.
- A sound in Calder.sf2: edit `soundfonts/build_calder.py` and run it.

## Building

GitHub does it for you.

1. Upload everything through the web UI as usual. The workflow calls every script with `bash`, so the dropped executable bit doesn't matter.
2. Go to Releases, Draft a new release, create a tag like `v0.2.0`, and publish. That starts the workflow. It fetches the latest inklecate, runs the smoke test, builds both AppImages, runs each one's selftest, and attaches them to the release.
3. Or go to Actions, pick "Build and release", Run workflow. Same build, with the AppImages kept under the run's artifacts.

To build locally on Ubuntu or whichever glibc distro:

1. `sudo apt install libfluidsynth3 libportaudio2 curl`
2. `pip install -r requirements.txt pyinstaller`
3. Put inklecate in `build/tools/`.
4. `bash build/smoke-test.sh`, since that also compiles the story the build needs.
5. `bash build/build-appimage.sh`
6. `bash build/smoke-test.sh dist/Calder-Falls-x86_64.AppImage dist/Calder-Falls-Jukebox-x86_64.AppImage`

The biggest file in the repo is `soundfonts/FluidR3Mono_GM.sf3` at 23.6 MB, under the 25 MB web upload limit. Each AppImage is about 140 MB.

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
- The step 1 jukebox still builds as its own AppImage next to the game.

## What I could not check

I can't hear audio, and I can't watch the window move. Everything below was checked headless:

- The story compiles with zero warnings, and every tag maps to code.
- Scripted routes reach all five endings. Wandering runs that file wrong theories on purpose still reach an ending.
- Every right theory answer can actually be found before you file it.
- Saves load back to the same place.
- The window plays the Prologue with music, toggles every setting, fakes the crash and loads a save.
- Both AppImages pass their own selftest.

What that doesn't cover: the GeneralUser GS download (GitHub's API is blocked from where I built this, so it has never run), whether the writing is scary, whether the effects look right on a real screen, whether the theme hex values need tuning (the spec said they would), and live sound through PortAudio to your speakers.
