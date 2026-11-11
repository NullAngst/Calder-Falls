# Changes

2026.11.11 - Initial release (step 2: the game)

* All 13 chapters in Ink, about 31,600 words: the Prologue, the twelve Act I loops in three chapters, the Act II hub with the Pruitt and Dorsey houses and 9 Mill Street, Act III at St. Adalbert's, the Spindle and the library, Act IV at the water tower and the mill floor, five endings
* Game window in PyQt6: typewriter story pane, two-column choices, top strip with chapter, inventory, LCD wristwatch and Nerve, sidebar tabs for notebook, Polaroid evidence board, county map and AM radio with police knob
* Case notebook and theory filing, with options that only appear once the supporting evidence is found, and partial credit on a reset
* Midnight theme with five stages (Midnight, Fog, Bleed, Static, Dead Signal) that blend into each other; low Nerve pushes one stage further
* Painted overlay for grain, fog, flicker, scanlines and CRT edges; flashlight cone in dark scenes with low-battery flicker and things standing just outside it
* Window tricks driven by Ink tags: scrollback that changes off screen, turning choices, flinching buttons, renamed tabs, a radio needle that drifts to 1610, a household count in the title bar, a radio-needle cursor in the Bleed
* Fourth-wall effects: fake crash, fake corrupted save, a title screen that changes between launches, How to Play rewritten in Act IV, all behind one setting
* Settings: flicker level asked on first launch, honest controls, flashlight cone, timed choices (off by default), fourth-wall effects, text size, story font, reveal speed, music volume, one-click GeneralUser GS download
* Autosave at every loop and chapter start, three manual slots, saves in ~/.local/share/calder-falls/saves/
* Story checks: zero-warning compile, every tag known, scripted routes to all five endings, wandering runs with wrong theories, every right answer findable, save round trip
* Game window selftest: plays the Prologue with sound, toggles every setting, fakes the crash, saves and loads
* The workflow downloads the latest inklecate, and builds and releases both the game and jukebox AppImages
* Ink runtime switched from inkcpp_py to bink

Reasons for changes: step 2 of the Calder Falls build spec. The Ink runtime changed because inkcpp_py drops and duplicates tags when an Ink function runs while a tag is waiting for its line: the first tag in the next group came back twice and the last one went missing. inkjs, the spec's fallback, throws on load in Qt's JS engine. bink handles every case that broke inkcpp_py and installs as a prebuilt wheel, so the build no longer compiles a runtime. The story is shorter than the spec's 90,000 to 110,000 words; every chapter is there, at roughly a third of the planned length.

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
