#!/usr/bin/env bash
# PenguinAOSP: Recents MemInfoView (RAM line) from penguinOS Launcher3.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"
SRC="$ROOT/vendor/penguin/files/packages/apps/Launcher3"
DST="$SOURCE_DIR/packages/apps/Launcher3"

if [ ! -d "$SOURCE_DIR/build" ]; then
    echo "[launcher-meminfo] 错误: $SOURCE_DIR 不像 AOSP 树" >&2
    exit 1
fi

mkdir -p \
  "$DST/quickstep/src/com/android/quickstep/views" \
  "$DST/quickstep/res/layout" \
  "$DST/res/values"

cp -a "$SRC/quickstep/src/com/android/quickstep/views/MemInfoView.java" \
  "$DST/quickstep/src/com/android/quickstep/views/"
cp -a "$SRC/quickstep/res/layout/meminfo.xml" "$DST/quickstep/res/layout/"
cp -a "$SRC/res/values/penguin_launcher_meminfo.xml" "$DST/res/values/"

echo "[launcher-meminfo] files copied"
python3 "$ROOT/vendor/penguin/patches/launcher3_meminfo.py" --source-dir "$SOURCE_DIR"
