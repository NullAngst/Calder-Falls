#!/usr/bin/env bash
# Assemble the Android app's web content into android/web-out/.
#
#   bash android/build-web.sh                 # render the music too (about 5 minutes)
#   bash android/build-web.sh --music DIR     # use music already rendered into DIR
#
# What ends up in android/web-out/assets/www/:
#   the front end from android/www/, the compiled story, the fonts, the icon,
#   inkjs (latest from npm), and the pre-rendered music with its manifest.
# Gradle puts that folder into the APK as assets/www/, and the launcher icon
# from android/web-out/res/.
#
# Needs: node and npm (for inkjs), plus, to render the music, everything the
# desktop smoke test needs (requirements.txt and libfluidsynth3).

set -euo pipefail
export LC_ALL=C

here=$(cd -- "$(dirname -- "$0")" && pwd -P) || exit 1
root=$(dirname -- "$here")
cd -- "$root" || exit 1

music_dir=""
while [ $# -gt 0 ]; do
    case "$1" in
        --music)
            [ $# -ge 2 ] || { printf 'build-web: --music needs a folder\n' >&2; exit 1; }
            music_dir=$2
            shift 2
            ;;
        *)
            printf 'build-web: unknown argument %s\n' "$1" >&2
            exit 1
            ;;
    esac
done

missing=""
for cmd in node npm cp mkdir; do
    command -v "$cmd" >/dev/null 2>&1 || missing="$missing $cmd"
done
if [ -z "$music_dir" ]; then
    command -v python3 >/dev/null 2>&1 || missing="$missing python3"
fi
if [ -n "$missing" ]; then
    printf 'build-web: missing required commands:%s\n' "$missing" >&2
    exit 1
fi

if [ ! -f story/build/main.json ]; then
    printf 'build-web: story/build/main.json is missing, run python3 -m calder_falls.storytest first\n' >&2
    exit 1
fi

out="$here/web-out"
www="$out/assets/www"
rm -rf -- "$out"
mkdir -p "$www/story" "$www/fonts" "$www/img" "$www/music" "$out/res/drawable-nodpi"

printf '== Front end\n'
cp -R -- "$here/www/." "$www/"
cp -- story/build/main.json "$www/story/main.json"
cp -- fonts/*.ttf "$www/fonts/"
cp -- assets/icon/calder-falls.svg "$www/img/"
cp -- assets/icon/calder-falls-256.png "$out/res/drawable-nodpi/ic_launcher.png"

printf '== inkjs (latest from npm)\n'
npm_dir=$(mktemp -d "${TMPDIR:-/tmp}/calder-inkjs.XXXXXX")
trap 'rm -rf -- "$npm_dir"' EXIT
(
    cd -- "$npm_dir" || exit 1
    npm init -y >/dev/null
    npm install --no-audit --no-fund --silent inkjs
)
ink="$npm_dir/node_modules/inkjs/dist/ink.js"
if [ ! -f "$ink" ]; then
    printf 'build-web: inkjs no longer ships dist/ink.js; look in %s/node_modules/inkjs/dist for the browser build\n' "$npm_dir" >&2
    exit 1
fi
cp -- "$ink" "$www/js/ink.js"
version=$(node -p 'require(process.argv[1]).version' "$npm_dir/node_modules/inkjs/package.json" 2>/dev/null || printf 'unknown')
printf 'inkjs %s\n' "$version"

printf '== Music\n'
if [ -n "$music_dir" ]; then
    if [ ! -f "$music_dir/manifest.json" ]; then
        printf 'build-web: %s has no manifest.json\n' "$music_dir" >&2
        exit 1
    fi
    cp -- "$music_dir"/*.ogg "$music_dir/manifest.json" "$www/music/"
else
    python3 -m calder_falls.audio.variants --out "$www/music" 2>&1 | grep -v '^fluidsynth: warning' || true
    if [ ! -f "$www/music/manifest.json" ]; then
        printf 'build-web: rendering the music failed (see above)\n' >&2
        exit 1
    fi
fi

printf '== Story checks against inkjs\n'
node "$here/test/storytest.js" "$www/js/ink.js"

printf 'build-web: done, %s\n' "$www"
