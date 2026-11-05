#!/usr/bin/env bash
# PenguinAOSP: Launcher3 LiquidGlass (folder open/preview) — TabBar glass is framework ViewRootImpl.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"
SRC="$ROOT/vendor/penguin/files/packages/apps/Launcher3"
DST="$SOURCE_DIR/packages/apps/Launcher3"

if [ ! -d "$SOURCE_DIR/build" ]; then
    echo "[launcher-glass] 错误: $SOURCE_DIR 不像 AOSP 树" >&2
    exit 1
fi

mkdir -p "$DST/src/com/android/launcher3/util" "$DST/src/com/android/launcher3/folder"
cp -a "$SRC/src/com/android/launcher3/util/LiquidGlass.kt" "$DST/src/com/android/launcher3/util/"
# LargeFolderPreview is penguin-only; only copy if we also wire call sites (skip bare copy for now)

echo "[launcher-glass] LiquidGlass.kt copied"
python3 "$ROOT/vendor/penguin/patches/launcher3_liquid_glass.py" --source-dir "$SOURCE_DIR"
