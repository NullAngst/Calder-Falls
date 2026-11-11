# Changes

2026.11.11 - Initial release (step 1: music)

* 12 music cues as MIDI, written by music/generate.py from per-cue rules
* Calder.sf2, 12 presets built from numpy-synthesized samples by soundfonts/build_calder.py
* FluidR3 Mono as the General MIDI base bank
* Audio engine: live MIDI sequencing through FluidSynth, PS2 filter, big dark reverb, layer muting, detune, tempo, static bleed, Ink music tag parsing, the Mill Floor hard cut
* Every cue rendered to renders/*.ogg
* Per-cue loudness trims measured in LUFS, plus a tool to re-measure them
* Jukebox app with every control the story will use, in the Midnight colors
* Water tower icon as SVG and PNGs
* Smoke test covering every cue and control, plus the jukebox and AppImage selftests
* GitHub Actions workflow that builds the jukebox AppImage

Reasons for changes: step 1 of the Calder Falls build spec. The music ships alone first so it can be listened to and fixed before the story is built around it.
