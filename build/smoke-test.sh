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
#      bash build/smoke-test.sh dist/Calder-Falls-x86_64.AppImage
#
# Every stage runs even if an earlier one failed. If anything failed, the very
# end of the output names each failed stage and repeats its FAIL and error
# lines, so the cause is at the bottom of the log where you can always find it.
#
# Needs inklecate: build/tools/inklecate, on PATH, or $INKLECATE.

set -euo pipefail
export LC_ALL=C

here=$(cd -- "$(dirname -- "$0")" && pwd -P) || exit 1
root=$(dirname -- "$here")
cd -- "$root" || exit 1

missing=""
for cmd in python3 cmp grep env; do
    command -v "$cmd" >/dev/null 2>&1 || missing="$missing $cmd"
done
if [ -n "$missing" ]; then
    printf 'smoke-test: missing required commands:%s\n' "$missing" >&2
    exit 1
fi

work=$(mktemp -d "${TMPDIR:-/tmp}/calder-smoke.XXXXXX")
trap 'rm -rf -- "$work"' EXIT

summary="$work/summary"
: >"$summary"

# note_failure <stage name> <log file or empty>
note_failure() {
    {
        printf '\n[%s]\n' "$1"
        if [ -n "${2:-}" ] && [ -f "$2" ]; then
            # The lines that say what broke. FluidSynth's missing-driver warnings and
            # GLib's assertion chatter from a system library are noise, not causes.
            grep -E 'FAIL|[Ee]rror|Traceback|failed|not found|missing' -- "$2" \
                | grep -v -e '^fluidsynth: warning' -e 'GLib-GObject-CRITICAL' -e 'PortAudio loaded' \
                | head -n 60 || true
        fi
    } >>"$summary"
}

# stage <name> <command...>
# Runs a command, shows its output, and records it in the summary if it fails.
stage() {
    local name=$1
    shift
    local log="$work/stage.log"
    printf '== %s\n' "$name"
    local rc=0
    "$@" >"$log" 2>&1 || rc=$?
    grep -v '^fluidsynth: warning' -- "$log" || true
    if [ "$rc" -ne 0 ]; then
        printf 'smoke-test: stage "%s" exited with %s\n' "$name" "$rc"
        note_failure "$name (exit $rc)" "$log"
    fi
}

printf '== MIDI cues are current\n'
# A warning, not a failure: a new Python can change what random.randint
# returns for the same seed, which would flag every cue with no edit on our end.
if python3 music/generate.py --out "$work/cues" >"$work/generate.log" 2>&1; then
    stale=0
    for f in music/cues/*.mid; do
        name=$(basename -- "$f")
        if ! cmp -s -- "$f" "$work/cues/$name"; then
            printf 'smoke-test: warning: %s differs from what music/generate.py writes now\n' "$f"
            stale=1
        fi
    done
    for f in "$work"/cues/*.mid; do
        name=$(basename -- "$f")
        if [ ! -f "music/cues/$name" ]; then
            printf 'smoke-test: music/cues/%s is missing\n' "$name" | tee -a "$work/generate.log"
            note_failure "MIDI cues: music/cues/$name is missing" ""
        fi
    done
    if [ "$stale" -ne 0 ]; then
        printf 'smoke-test: warning: regenerate with python3 music/generate.py and listen again\n'
    fi
else
    cat -- "$work/generate.log"
    note_failure "MIDI cues: music/generate.py failed" "$work/generate.log"
fi

# Built fresh to prove the script still runs. Not compared byte for byte,
# since numpy and scipy updates can move the last bit of a sample.
stage "Calder.sf2 builds" python3 soundfonts/build_calder.py "$work/Calder.sf2"

stage "music checks" python3 -m calder_falls.audio.smoke

stage "story checks" python3 -m calder_falls.storytest

# Settings, saves and the profile go to a throwaway folder, not your real ones
export XDG_DATA_HOME="$work/xdg"

# Qt complains under LC_ALL=C and switches to C.UTF-8 itself; give it that up front.
# Nothing below parses command output, so the parsing rule above is unaffected.
qt_env="LC_ALL=C.UTF-8"

stage "game window selftest" env "$qt_env" QT_QPA_PLATFORM=offscreen python3 -m calder_falls --selftest

stage "jukebox selftest" env "$qt_env" QT_QPA_PLATFORM=offscreen python3 -m calder_falls.jukebox --selftest

for image in "$@"; do
    chmod +x -- "$image"
    # No FUSE on CI runners, so let the AppImage unpack itself instead of mounting
    stage "AppImage selftest: $image" env "$qt_env" APPIMAGE_EXTRACT_AND_RUN=1 QT_QPA_PLATFORM=offscreen "$image" --selftest
done

if [ -s "$summary" ]; then
    printf '\n==================== smoke-test: FAILED ====================\n'
    printf 'What failed, and the lines from it that say why:\n'
    cat -- "$summary"
    printf '\n=============================================================\n'
    exit 1
fi
printf '\nsmoke-test: everything passed\n'
