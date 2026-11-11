#!/usr/bin/env bash
# Build Calder Falls as Linux AppImages.
#
#   bash build/build-appimage.sh            # both
#   bash build/build-appimage.sh game       # dist/Calder-Falls-x86_64.AppImage
#   bash build/build-appimage.sh jukebox    # dist/Calder-Falls-Jukebox-x86_64.AppImage
#
# Needs the Python deps from requirements.txt plus pyinstaller, the system
# libraries libfluidsynth3 and libportaudio2 (both get bundled), and for the
# game a compiled story: story/build/main.json (python3 -m calder_falls.storytest
# builds it with inklecate).
#
# This script targets glibc Linux (GitHub's Ubuntu runner). It finds the two
# libraries with ldconfig -p, which is glibc-only. Set LIBFLUIDSYNTH and
# LIBPORTAUDIO to full paths to skip that.

set -euo pipefail
export LC_ALL=C

here=$(cd -- "$(dirname -- "$0")" && pwd -P) || exit 1
root=$(dirname -- "$here")
cd -- "$root" || exit 1

which_apps=${1:-both}
case "$which_apps" in
    both | game | jukebox) ;;
    *)
        printf 'build-appimage: unknown target %s (use game, jukebox or both)\n' "$which_apps" >&2
        exit 1
        ;;
esac

missing=""
for cmd in python3 pyinstaller curl find awk; do
    command -v "$cmd" >/dev/null 2>&1 || missing="$missing $cmd"
done
if [ -z "${LIBFLUIDSYNTH:-}" ] || [ -z "${LIBPORTAUDIO:-}" ]; then
    command -v ldconfig >/dev/null 2>&1 || missing="$missing ldconfig"
fi
if [ -n "$missing" ]; then
    printf 'build-appimage: missing required commands:%s\n' "$missing" >&2
    exit 1
fi

version=$(python3 -c 'import calder_falls; print(calder_falls.__version__)')

work=$(mktemp -d "${TMPDIR:-/tmp}/calder-appimage.XXXXXX")
trap 'rm -rf -- "$work"' EXIT

find_lib() {
    # glibc only: ldconfig -p lists "libfoo.so.3 (libc6,x86-64) => /path"
    ldconfig -p | awk -v want="$1" '$1 ~ "^"want"\\.so" && /x86-64/ { print $NF; exit }'
}

fluid=${LIBFLUIDSYNTH:-$(find_lib libfluidsynth)}
porta=${LIBPORTAUDIO:-$(find_lib libportaudio)}
for lib in "$fluid" "$porta"; do
    if [ -z "$lib" ] || [ ! -f "$lib" ]; then
        printf 'build-appimage: could not find libfluidsynth or libportaudio (install libfluidsynth3 and libportaudio2)\n' >&2
        exit 1
    fi
done

# The base General MIDI bank: the repo copy, else the Ubuntu package
bank="$root/soundfonts/FluidR3Mono_GM.sf3"
if [ ! -f "$bank" ]; then
    bank=/usr/share/sounds/sf3/FluidR3Mono_GM.sf3
fi
if [ ! -f "$bank" ]; then
    printf 'build-appimage: FluidR3Mono_GM.sf3 not found (install fluidr3mono-gm-soundfont)\n' >&2
    exit 1
fi

for f in soundfonts/Calder.sf2 assets/icon/calder-falls-256.png; do
    if [ ! -f "$f" ]; then
        printf 'build-appimage: %s is missing\n' "$f" >&2
        exit 1
    fi
done
if [ "$which_apps" != jukebox ] && [ ! -f story/build/main.json ]; then
    printf 'build-appimage: story/build/main.json is missing, run python3 -m calder_falls.storytest first\n' >&2
    exit 1
fi

printf '== Fetching the AppImage tools\n'
excl="$work/excludelist"
if ! curl -fsSL -o "$excl" https://raw.githubusercontent.com/AppImageCommunity/pkg2appimage/master/excludelist; then
    printf 'build-appimage: could not fetch the excludelist, using a short built-in one\n' >&2
    printf '%s\n' libasound.so.2 libGL.so.1 libEGL.so.1 libGLX.so.0 libOpenGL.so.0 \
        libdrm.so.2 libgbm.so.1 libfontconfig.so.1 libfreetype.so.6 libharfbuzz.so.0 \
        libX11.so.6 libxcb.so.1 libwayland-client.so.0 libc.so.6 libm.so.6 \
        libdl.so.2 libpthread.so.0 librt.so.1 libz.so.1 >"$excl"
fi
tool="$work/appimagetool"
curl -fsSL -o "$tool" https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x -- "$tool"
mkdir -p dist

# build_one <exe name> <entry script> <AppImage file> <menu name> <comment> <extra pyinstaller args...>
build_one() {
    local app=$1 entry=$2 out_name=$3 label=$4 comment=$5
    shift 5
    local bundle="$work/dist/$app"
    local appdir="$work/AppDir-$app"

    printf '== PyInstaller: %s\n' "$app"
    pyinstaller --noconfirm --clean --onedir --log-level WARN \
        --name "$app" \
        --distpath "$work/dist" --workpath "$work/build-$app" --specpath "$work" \
        --paths "$root" \
        --add-binary "$fluid:." \
        --add-binary "$porta:." \
        --add-data "$root/music/cues:music/cues" \
        --add-data "$root/soundfonts/Calder.sf2:soundfonts" \
        --add-data "$bank:soundfonts" \
        --add-data "$root/soundfonts/LICENSE-FluidR3Mono.txt:soundfonts" \
        --add-data "$root/assets/icon:assets/icon" \
        --exclude-module tkinter --exclude-module matplotlib --exclude-module soundfile \
        --exclude-module pkg_resources --exclude-module setuptools \
        "$@" \
        "$root/build/$entry"

    printf '== Dropping libraries the host must provide\n'
    # The AppImage project's excludelist names libraries that break when
    # bundled (libasound has to match the host's ALSA plugins, libGL the
    # host driver). Two exceptions: libfluidsynth links libjack and
    # libpipewire directly and fails to load without them. We never use
    # FluidSynth's own audio drivers, so bundled copies of those two are
    # never asked to talk to a server.
    local line name
    while IFS= read -r line; do
        name=${line%%#*}
        name=$(printf '%s' "$name" | awk '{ print $1 }')
        case "$name" in
            "" | libjack.so.0 | libpipewire-0.3.so.0) continue ;;
        esac
        find "$bundle" -name "$name" -exec rm -f -- {} +
    done <"$excl"

    printf '== AppDir: %s\n' "$app"
    mkdir -p "$appdir/usr/lib" "$appdir/usr/share/applications" \
        "$appdir/usr/share/icons/hicolor/256x256/apps"
    mv -- "$bundle" "$appdir/usr/lib/$app"

    # One app per AppDir, so AppRun just runs the one executable under usr/lib
    cat >"$appdir/AppRun" <<'EOF'
#!/bin/sh
here=${APPDIR:-$(cd -- "$(dirname -- "$0")" && pwd -P)}
for exe in "$here"/usr/lib/*/calder-falls*; do
    if [ -f "$exe" ] && [ -x "$exe" ]; then
        exec "$exe" "$@"
    fi
done
printf 'AppRun: no executable found under %s/usr/lib\n' "$here" >&2
exit 1
EOF
    chmod +x -- "$appdir/AppRun"

    {
        printf '[Desktop Entry]\n'
        printf 'Type=Application\n'
        printf 'Name=%s\n' "$label"
        printf 'Comment=%s\n' "$comment"
        printf 'Exec=%s\n' "$app"
        printf 'Icon=%s\n' "$app"
        printf 'Categories=Game;AdventureGame;\n'
        printf 'Terminal=false\n'
        printf 'X-AppImage-Version=%s\n' "$version"
    } >"$appdir/$app.desktop"
    cp -- "$appdir/$app.desktop" "$appdir/usr/share/applications/"
    cp -- assets/icon/calder-falls-256.png "$appdir/$app.png"
    cp -- assets/icon/calder-falls-256.png "$appdir/.DirIcon"
    cp -- assets/icon/calder-falls-256.png "$appdir/usr/share/icons/hicolor/256x256/apps/$app.png"

    printf '== appimagetool: %s\n' "$out_name"
    # No FUSE on CI runners, so appimagetool unpacks itself instead of mounting
    ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 "$tool" --no-appstream "$appdir" "dist/$out_name"
    printf 'built dist/%s\n' "$out_name"
}

if [ "$which_apps" != jukebox ]; then
    build_one calder-falls game-entry.py Calder-Falls-x86_64.AppImage \
        "Calder Falls" "A text-based psychological horror game" \
        --collect-all bink \
        --add-data "$root/story/build/main.json:story/build" \
        --add-data "$root/fonts:fonts" \
        --add-data "$root/calder_falls/themes/midnight.qss:calder_falls/themes"
fi
if [ "$which_apps" != game ]; then
    build_one calder-falls-jukebox jukebox-entry.py Calder-Falls-Jukebox-x86_64.AppImage \
        "Calder Falls Jukebox" "Listen to and shape every Calder Falls music cue"
fi
