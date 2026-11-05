#!/usr/bin/env bash
# PenguinAOSP: EdgeLighting SystemUI controller (C 类文件 + DozeServiceHost B 类接线).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"
SRC="$ROOT/vendor/penguin/files/frameworks/base/packages/SystemUI/src/com/android/systemui/edgelighting"
DST="$SOURCE_DIR/frameworks/base/packages/SystemUI/src/com/android/systemui/edgelighting"

if [ ! -d "$SOURCE_DIR/build" ]; then
    echo "[edgelighting] 错误: $SOURCE_DIR 不像 AOSP 树" >&2
    exit 1
fi
if [ ! -f "$SRC/EdgeLightingController.java" ]; then
    echo "[edgelighting] 错误: 缺 $SRC/EdgeLightingController.java" >&2
    exit 1
fi

mkdir -p "$DST"
rsync -a --delete "$SRC/" "$DST/"
echo "[edgelighting] files -> $DST"
python3 "$ROOT/vendor/penguin/patches/systemui_edgelighting_doze.py" --source-dir "$SOURCE_DIR"
