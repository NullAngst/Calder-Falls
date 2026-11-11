#!/usr/bin/env bash
# Headless checks for Calder Falls.
#
#   bash build/smoke-test.sh
#
# 1. The committed MIDI cues match what music/generate.py writes now (warning only).
# 2. soundfonts/build_calder.py still builds a bank.
# 3. Every cue plays through FluidSynth, and every control changes it.
# 4. The story compiles with zero inklecate warnings, every tag is known,
#    and scripted routes reach all five endings.
# 5. The game window opens with no display, plays the Prologue with sound,
#    and toggles every setting. The jukebox does the same for its controls.
# 6. Any AppImage paths given run their own selftest too:
#      bash build/smoke-test.sh dist/Calder-Falls-x86_64.AppImage dist/Calder-Falls-Jukebox-x86_64.AppImage
#
# Needs inklecate: build/tools/inklecate, on PATH, or $INKLECATE.

set -euo pipefail
export LC_ALL=C

here=$(cd -- "$(dirname -- "$0")" && pwd -P) || exit 1
root=$(dirname -- "$here")
cd -- "$root" || exit 1

missing=""
for cmd in python3 cmp; do
    command -v "$cmd" >/dev/null 2>&1 || missing="$missing $cmd"
done
if [ -n "$missing" ]; then
    printf 'smoke-test: missing required commands:%s\n' "$missing" >&2
    exit 1
fi

work=$(mktemp -d "${TMPDIR:-/tmp}/calder-smoke.XXXXXX")
trap 'rm -rf -- "$work"' EXIT

fail=0

printf '== MIDI cues are current\n'
# A warning, not a failure: a new Python can change what random.randint
# returns for the same seed, which would flag every cue with no edit on our end.
python3 music/generate.py --out "$work/cues" >/dev/null
stale=0
for f in music/cues/*.mid; do
    name=$(basename -- "$f")
    if ! cmp -s -- "$f" "$work/cues/$name"; then
        printf 'smoke-test: warning: %s differs from what music/generate.py writes now\n' "$f" >&2
        stale=1
    fi
done
for f in "$work"/cues/*.mid; do
    name=$(basename -- "$f")
    if [ ! -f "music/cues/$name" ]; then
        printf 'smoke-test: music/cues/%s is missing\n' "$name" >&2
        fail=1
    fi
done
if [ "$stale" -ne 0 ]; then
    printf 'smoke-test: warning: regenerate with python3 music/generate.py and listen again\n' >&2
fi

printf '== Calder.sf2 builds\n'
# Built fresh to prove the script still runs. Not compared byte for byte,
# since numpy and scipy updates can move the last bit of a sample.
if ! python3 soundfonts/build_calder.py "$work/Calder.sf2" >/dev/null; then
    printf 'smoke-test: soundfonts/build_calder.py failed\n' >&2
    fail=1
fi

printf '== music checks\n'
# FluidSynth warns about missing audio drivers on a headless runner; that is noise here.
if ! python3 -m calder_falls.audio.smoke 2>"$work/smoke.err"; then
    grep -v '^fluidsynth: warning' "$work/smoke.err" >&2 || true
    fail=1
fi

printf '== story checks\n'
if ! python3 -m calder_falls.storytest; then
    fail=1
fi

# Settings, saves and the profile go to a throwaway folder, not your real ones
export XDG_DATA_HOME="$work/xdg"

printf '== game window selftest\n'
if ! QT_QPA_PLATFORM=offscreen python3 -m calder_falls --selftest 2>"$work/game.err"; then
    grep -v '^fluidsynth: warning' "$work/game.err" >&2 || true
    fail=1
fi

printf '== jukebox selftest\n'
if ! QT_QPA_PLATFORM=offscreen python3 -m calder_falls.jukebox --selftest 2>"$work/jukebox.err"; then
    grep -v '^fluidsynth: warning' "$work/jukebox.err" >&2 || true
    fail=1
fi

for image in "$@"; do
    printf '== AppImage selftest: %s\n' "$image"
    chmod +x -- "$image"
    # No FUSE on CI runners, so let the AppImage unpack itself instead of mounting
    if ! APPIMAGE_EXTRACT_AND_RUN=1 QT_QPA_PLATFORM=offscreen "$image" --selftest 2>"$work/appimage.err"; then
        grep -v '^fluidsynth: warning' "$work/appimage.err" >&2 || true
        fail=1
    fi
done

if [ "$fail" -ne 0 ]; then
    printf '\nsmoke-test: FAILED\n' >&2
    exit 1
fi
printf '\nsmoke-test: everything passed\n'
