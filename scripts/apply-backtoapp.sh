#!/usr/bin/env bash
# PenguinAOSP: BackToApp status-bar indicator (C 类文件 + StatusBarRoot B 类接线).
# 依赖: PENGUIN_SETTINGS_KEYS（BACK_TO_APP_INDICATOR 常量）.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"
SRC="$ROOT/vendor/penguin/files/frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/backtoapp"
DST="$SOURCE_DIR/frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/backtoapp"

if [ ! -d "$SOURCE_DIR/build" ]; then
    echo "[backtoapp] 错误: $SOURCE_DIR 不像 AOSP 树" >&2
    exit 1
fi
if [ ! -f "$SRC/BackToAppTracker.kt" ]; then
    echo "[backtoapp] 错误: 缺 $SRC/BackToAppTracker.kt" >&2
    exit 1
fi

mkdir -p "$DST"
rsync -a --delete "$SRC/" "$DST/"
echo "[backtoapp] files -> $DST"
python3 "$ROOT/vendor/penguin/patches/systemui_backtoapp_statusbar.py" --source-dir "$SOURCE_DIR"
