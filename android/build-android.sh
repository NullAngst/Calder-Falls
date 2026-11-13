#!/usr/bin/env bash
# Build the Android APK from what build-web.sh assembled.
#
#   bash android/build-android.sh
#
# Uses the newest stable Android Gradle Plugin from Google's Maven repo and
# whatever Gradle is on the PATH (the workflow installs the current release).
# Nothing is pinned, so an upstream release can break this with no change on
# our end. maintenance.md says what to do when it does.
#
# Signing: set CF_KEYSTORE (path to the .jks), CF_KEYSTORE_PASSWORD,
# CF_KEY_ALIAS and CF_KEY_PASSWORD. Without them the release APK is built
# unsigned, which is fine for a look but will not install.
#
# Output: android/app/build/outputs/apk/release/app-release(-unsigned).apk

set -euo pipefail
export LC_ALL=C

here=$(cd -- "$(dirname -- "$0")" && pwd -P) || exit 1
cd -- "$here" || exit 1

missing=""
for cmd in gradle curl grep sed sort tail; do
    command -v "$cmd" >/dev/null 2>&1 || missing="$missing $cmd"
done
if [ -n "$missing" ]; then
    printf 'build-android: missing required commands:%s\n' "$missing" >&2
    exit 1
fi
if [ -z "${ANDROID_HOME:-}${ANDROID_SDK_ROOT:-}" ]; then
    printf 'build-android: set ANDROID_HOME to your Android SDK\n' >&2
    exit 1
fi
if [ ! -f web-out/assets/www/index.html ] || [ ! -f web-out/assets/www/music/manifest.json ]; then
    printf 'build-android: run bash android/build-web.sh first\n' >&2
    exit 1
fi

# The newest AGP that isn't an alpha, beta or release candidate
meta=https://dl.google.com/android/maven2/com/android/tools/build/gradle/maven-metadata.xml
agp=$(curl -fsSL "$meta" | grep -o '<version>[0-9]*\.[0-9]*\.[0-9]*</version>' \
    | sed 's/<[^>]*>//g' | sort -t. -k1,1n -k2,2n -k3,3n | tail -n 1) || agp=""
if [ -z "$agp" ]; then
    printf 'build-android: could not read the latest Android Gradle Plugin version from %s\n' "$meta" >&2
    exit 1
fi
printf 'build-android: Android Gradle Plugin %s, %s\n' "$agp" "$(gradle --version 2>/dev/null | grep '^Gradle' || printf 'Gradle unknown')"

if [ -n "${CF_KEYSTORE:-}" ] && [ ! -f "$CF_KEYSTORE" ]; then
    printf 'build-android: CF_KEYSTORE points at %s, which does not exist\n' "$CF_KEYSTORE" >&2
    exit 1
fi

gradle --no-daemon --stacktrace -PagpVersion="$agp" assembleRelease
