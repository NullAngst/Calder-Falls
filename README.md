# Calder Falls: step 1, the music

This is the music for Calder Falls, a text-based psychological horror game, plus a jukebox that plays every cue live through the same engine the game will use. Step 1 exists so you can listen and push back before any story gets built on top of the sound.

## What's in here

- `renders/*.ogg`: every cue rendered once through, PS2 filter on. Open them in any player, this is the fastest way to listen.
- `calder_falls/jukebox.py`: the jukebox app. Plays each cue live, with the controls the story will drive: tempo, detune, each layer on or off, PS2 filter, static bleed.
- `music/generate.py`: the cue generator. Every melody, chord loop, drum pattern and instrument choice is a few lines of Python per cue.
- `music/cues/*.mid`: the 12 cues as standard MIDI files.
- `soundfonts/Calder.sf2`: our own sound bank, every sample generated with numpy. `soundfonts/build_calder.py` builds it.
- `soundfonts/FluidR3Mono_GM.sf3`: the General MIDI bank under it (MIT, license next to it).
- `calder_falls/audio/engine.py`: the audio engine. FluidSynth render loop, PS2 filter, reverb, layers, detune, tempo, static. Step 2 uses this same file.
- `build/`: the AppImage build, the smoke test, the icon renderer.
- `.github/workflows/release.yml`: builds the jukebox AppImage on GitHub.

## Prerequisites

- Linux. I'm on Kubuntu, so the package names below are Ubuntu's. Other distros have the same libraries under their own names.
- Python 3.10 or newer, with venv.
- FluidSynth 2.x and PortAudio: `sudo apt install python3-venv libfluidsynth3 libportaudio2`.

You only need those to run from source. The AppImage carries everything.

## Listening

### The quick way

Open the files in `renders/`. Each one is one pass through the cue plus a few seconds of tail, so a looping cue ends right where it would start over.

### The AppImage

1. Grab `Calder-Falls-Jukebox-x86_64.AppImage` from the repo's Releases page, or from the Actions run's artifacts.
2. `chmod +x Calder-Falls-Jukebox-x86_64.AppImage`, since downloads don't keep the executable bit.
3. Run it. Double-click a cue to play it.

### From source

1. `cd calder-falls`
2. `python3 -m venv .venv`, since that keeps these packages out of your system Python.
3. `. .venv/bin/activate`
4. `pip install -r requirements.txt`
5. `python3 -m calder_falls.jukebox`

## Using the jukebox

Pick a cue on the left, hit Play. Everything on the right changes the cue while it plays, the same way the story will:

- Tempo, 50% to 150%. The notes get slower or faster, the pitch stays put, since the engine sequences the MIDI live.
- Detune, plus or minus 100 cents. Everything but the drums drifts out of tune.
- Static bleed. The music narrows to AM radio, fades like a station at the edge of its range, and static sits on top.
- Layers: drums, bass, lead, pad, noise. A greyed-out layer isn't used by that cue.
- PS2 filter. Off gives you the clean FluidSynth output, so you can hear what the filter is doing.

The Ink tags the story will use map one to one onto these: `# music:cobb_road`, `# music_layer:drums off`, `# music_detune:30`, `# music_tempo:0.8`, `# music_static:0.4`, `# music_ps2:off`, `# music:stop`.

## Changing a cue

EDIT `music/generate.py`, NOT THE `.mid` FILES. The `.mid` files get overwritten every time the generator runs.

1. Change the cue's function in `music/generate.py`. Each one has a comment saying what it's going for.
2. `python3 music/generate.py june`, or with no name to rebuild all of them.
3. `python3 -m calder_falls.audio.render june`, since that refreshes `renders/june.ogg`.
4. Listen again in the jukebox.

If a change makes a cue louder or quieter than it should sit, `pip install pyloudnorm` and run `python3 -m calder_falls.audio.loudness june`. It prints a suggested `gain_db` for that cue in `calder_falls/audio/cues.py`.

Changing a sound in Calder.sf2 works the same way: edit `soundfonts/build_calder.py`, run it, re-render.

## Building the AppImage

GitHub does this for you. On the repo:

1. Upload everything through the web UI as usual. The workflow calls every script with `bash`, so the dropped executable bit doesn't matter.
2. Go to Releases, Draft a new release, create a tag like `v0.1.0`, publish. That tag starts the workflow, which runs the smoke test, builds the AppImage, runs the AppImage's own selftest, and attaches it to the release.
3. Or go to Actions, pick "Build and release", Run workflow. Same build, and the AppImage lands under that run's artifacts instead of a release.

The repo upload limit through the web UI is 25 MB per file. The biggest file here is `soundfonts/FluidR3Mono_GM.sf3` at 23.6 MB, so it fits.

To build locally, on Ubuntu or whichever glibc distro:

1. `sudo apt install libfluidsynth3 libportaudio2 curl`
2. `pip install -r requirements.txt pyinstaller`
3. `bash build/build-appimage.sh`
4. `bash build/smoke-test.sh dist/Calder-Falls-Jukebox-x86_64.AppImage`, since that runs the full check and then the AppImage's selftest.

## How the music works

Same idea as Silent Hill 2 on the PS2, with modern parts. Each cue is a MIDI file. The engine reads its events and plays them into FluidSynth at the right sample, using two SoundFonts: FluidR3 Mono for the General MIDI instruments, Calder.sf2 for everything that carries the game's sound (tremolo mandolin, detuned electric piano, reversed piano, distorted bass, tape pad, sub drone, sheet metal, metal scrape, tape hiss, radio static, fridge hum and clock). FluidSynth's reverb runs big and dark. Then numpy and scipy do the PS2 part: narrow the mix toward mono, hold it on a 32 kHz grid, lowpass it dark, crunch it to 12 bits. sounddevice plays it.

Because nothing is prerecorded, the game can change a cue while it plays. That's the whole reason to do it this way.

Every cue has a fixed seed, so the generator writes the same MIDI every run.
