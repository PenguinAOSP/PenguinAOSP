#!/usr/bin/env bash
# PenguinAOSP: Recents FrequentApps row (C 类文件 + Launcher3 B 类接线).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"
SRC_BASE="$ROOT/vendor/penguin/files/packages/apps/Launcher3"
DST_BASE="$SOURCE_DIR/packages/apps/Launcher3"

if [ ! -d "$SOURCE_DIR/build" ]; then
    echo "[frequent-apps] 错误: $SOURCE_DIR 不像 AOSP 树" >&2
    exit 1
fi

mkdir -p "$DST_BASE/quickstep/src/com/android/quickstep/views"
mkdir -p "$DST_BASE/quickstep/res/drawable"
mkdir -p "$DST_BASE/res/values"

cp -a "$SRC_BASE/quickstep/src/com/android/quickstep/views/FrequentAppsView.java" \
    "$DST_BASE/quickstep/src/com/android/quickstep/views/"
cp -a "$SRC_BASE/quickstep/res/drawable/frequent_app_ripple.xml" \
    "$DST_BASE/quickstep/res/drawable/"
cp -a "$SRC_BASE/res/values/penguin_frequent_apps_dimens.xml" \
    "$DST_BASE/res/values/"
echo "[frequent-apps] files copied"

python3 "$ROOT/vendor/penguin/patches/launcher3_frequent_apps.py" --source-dir "$SOURCE_DIR"
