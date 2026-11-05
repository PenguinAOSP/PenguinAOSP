#!/usr/bin/env bash
# PenguinAOSP: Power menu Styles (C 类文件 + GlobalActions/SystemUIModule B 类).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"
SRC="$ROOT/vendor/penguin/files/frameworks/base/packages/SystemUI"
DST="$SOURCE_DIR/frameworks/base/packages/SystemUI"

if [ ! -d "$SOURCE_DIR/build" ]; then
    echo "[power-menu] 错误: $SOURCE_DIR 不像 AOSP 树" >&2
    exit 1
fi

mkdir -p "$DST/src/com/android/systemui/penguin" \
         "$DST/src/com/android/systemui/globalactions" \
         "$DST/res/layout" "$DST/res/drawable" "$DST/res/values"

cp -a "$SRC/src/com/android/systemui/penguin/PowerMenuLayout.java" "$DST/src/com/android/systemui/penguin/"
cp -a "$SRC/src/com/android/systemui/penguin/PenguinHooksModule.kt" "$DST/src/com/android/systemui/penguin/"
cp -a "$SRC/src/com/android/systemui/globalactions/"*.java "$DST/src/com/android/systemui/globalactions/"
cp -a "$SRC/res/layout/"*.xml "$DST/res/layout/"
cp -a "$SRC/res/drawable/"*.xml "$DST/res/drawable/"
cp -a "$SRC/res/values/"*.xml "$DST/res/values/"
echo "[power-menu] files copied"
python3 "$ROOT/vendor/penguin/patches/systemui_power_menu_style.py" --source-dir "$SOURCE_DIR"
