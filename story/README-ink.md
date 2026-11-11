# Writing for Calder Falls in Ink

This is the writer's side of the story files: how a line of Ink turns into something on screen. The engine side is in `calder_falls/story.py`.

## Files

`main.ink` holds the variables and includes every chapter. One file per chapter, under `act1/` to `act4/`. Inky (inkle's free editor) opens `main.ink` and plays the whole thing, tags and all, if you want to read through it without the game window.

## Tags

A tag on its own line attaches to the next line of text. A tag at the end of a line attaches to that line. Both are fine.

| Tag | What it does |
|---|---|
| `# chapter:5:The Hush` | Chapter number and title in the top strip, plus an autosave |
| `# autosave` | Autosave at the next choice point |
| `# clear` | Clears the story pane (the Act I loops use this) |
| `# time:16:20` | Sets Brennick's wristwatch |
| `# hint:Text` | What the Hint button says from here on |
| `# evidence:id;kind;title;caption` | Adds a card to the Evidence tab. kind is photo, statement, object or time |
| `# note:Text` | Adds a line to the notebook |
| `# theory:id;Title` then `# slot:name;Option*@ev_id;Option;Option` | Sets up the next FILE choice. `*` marks the right option, `@ev_id` hides an option until that evidence is found |
| `# map:place` | Pen mark on the county map (places are in `ui/sidebar.py`) |
| `# item:flashlight` / `# item_lose:...` | Inventory |
| `# pause:2` | Typewriter waits this many seconds |
| `# timed:7:2` | The next choices get a 7 second timer, defaulting to the third choice. Only when timed choices are on |
| `# dark:on` / `# dark:off`, `# battery:low`, `# shadow:text` | Flashlight scenes |
| `# theme:fog` | Theme stage: midnight, fog, bleed, static, dead_signal |
| `# speaker:1610` | The next line is a radio voice (also `police`) |
| `# warp:...` | Window tricks, see below |
| `# fourth:crash`, `# fourth:corrupt_save`, `# fourth:howto` | Fourth-wall effects |
| `# music:cue`, `# music_layer:drums off`, `# music_detune:30`, `# music_tempo:0.8`, `# music_static:0.4`, `# music_ps2:off`, `# music:stop` | Music |
| `# ending:dawn` | Records the ending on the player's profile |

Fields inside a tag are separated with `;`. NEVER use `|` inside a tag. Ink reads it as alternatives and the compile fails.

Warps: `scrollback:old text=>new text` (changes an earlier paragraph once it is off screen), `tabs_rename`, `tabs_normal`, `radio_drift`, `radio_still`, `title_count:4`, `title_normal`, `cursor_needle`, `cursor_normal`, `swap:word=>word`, `swap_clear`, `flinch`, `flinch_off`.

Any tag not on this list fails the smoke test. That is on purpose.

## Choices

- `+ [Text]` is sticky, `* [Text]` shows once ever. Inside anything that can repeat (a loop, a hub), use `+`, or the options run out and the story ends early.
- `+ [RADIO:1610: Text]` is hidden from the buttons and played from the radio dial when the player tunes near 1610.
- `+ [POLICE: Text]` is hidden and played from the police knob.
- `+ [FILE: Text]` opens the theory dialog before it is taken. The score lands in `theory_score`.
- `+ [What it says @@ What it does]` is a turning choice. The button reads the first part, turns into the second on hover, and clicking does the second. Honest controls in Settings shows only the second part.

## Variables the window reads

`nerve` (0 to 10, the meter), `rounds` (shown with the pistol), `second_run` (set by the game on a second playthrough), `theory_score` (set by the game when a theory is filed).

## Checking your work

    python3 -m calder_falls.storytest

That compiles with inklecate (any warning fails), checks every tag, plays routes to all five endings, wanders the story with seeds that file wrong theories on purpose, and round-trips a save. It takes a couple of seconds.
