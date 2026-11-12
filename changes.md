# Changes

2026.11.11 - Build fix

* The music check for "this control changes the cue" also passes when the change is at least 3e-4 RMS on its own, about -70 dBFS and three times the PS2 filter's 12-bit noise floor. The old rule, more than 1% of the whole mix, still applies alongside it
* The smoke test's failure summary leaves out GLib assertion warnings, which come from a system library and never caused a failure

Reasons for changes: "dawn: noise layer off changes it" failed on the runner. Dawn's noise layer is a deliberately quiet tape hiss under a full guitar. Locally it changed the mix by 1.1% against a 1% threshold, and the runner's newer libraries pushed it just under. Judging a quiet layer against the loudness of the whole mix was the wrong test. The new rule asks whether the layer stands clearly above the noise floor. A layer that really is silent still fails, since its difference is exactly zero.

2026.11.11 - Build fix

* The smoke test ends with a summary when anything fails: each failed stage by name, plus its FAIL and error lines
* Every stage's output, stderr included, now prints in the log, not only when the stage fails
* Story check routes use fixed seeds. They were seeded from hash(), which Python randomizes per run, so the runner played different routes than a local run did

Reasons for changes: the second failed run gave no visible reason. GitHub's log viewer only draws the lines on screen, so a copied log loses the middle, and that is where the failing stage was. The summary puts the cause at the bottom. The seed change makes a failing route reproducible locally. All 300 seeded routes and 40 wandering runs pass here, under both Python 3.13 and 3.14, so the seed was probably not the cause.

2026.11.11 - Build fix

* The PortAudio check in the jukebox and game selftests now fails only when the library is missing or can't be loaded. PortAudio refusing to start because there is no sound server counts as loaded
* The game window selftest runs the same PortAudio check as the jukebox
* Qt runs under C.UTF-8 in the smoke test and the AppImage selftest step, which removes the locale warning from the log

Reasons for changes: the GitHub runner's PortAudio is built with PulseAudio support and there is no PulseAudio server on the runner, so PortAudio loaded and then refused to initialize. The old check treated that the same as a missing library and failed the build. The container I built in had no PulseAudio support, so it never hit this.

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
