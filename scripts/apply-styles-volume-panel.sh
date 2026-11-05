#!/usr/bin/env bash
# PenguinAOSP: Volume panel Styles (C files into SystemUI).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"
SRC="$ROOT/vendor/penguin/files/frameworks/base/packages/SystemUI"
DST="$SOURCE_DIR/frameworks/base/packages/SystemUI"

if [ ! -d "$SOURCE_DIR/build" ]; then
    echo "[volume-panel] 错误: $SOURCE_DIR 不像 AOSP 树" >&2
    exit 1
fi

mkdir -p "$DST/src/com/android/systemui/penguin" \
         "$DST/src/com/android/systemui/volume/dialog/domain/interactor" \
         "$DST/src/com/android/systemui/volume/dialog/sliders/ui" \
         "$DST/src/com/android/systemui/volume/dialog/sliders/domain/interactor" \
         "$DST/src/com/android/systemui/volume/dialog/ui/binder" \
         "$DST/src/com/android/systemui/volume/dialog/ringer/ui/binder" \
         "$DST/src/com/android/systemui/volume/dialog/captions/ui/binder" \
         "$DST/src/com/android/systemui/volume/dialog/settings/ui/binder" \
         "$DST/src/com/android/systemui/volume/dialog/settings/domain" \
         "$DST/res/layout" "$DST/res/drawable" "$DST/res/values" "$DST/res/values-night"

cp -a "$SRC/src/com/android/systemui/penguin/VolumePanelLook.kt" "$DST/src/com/android/systemui/penguin/"
cp -a "$SRC/src/com/android/systemui/penguin/PenguinHooksModule.kt" "$DST/src/com/android/systemui/penguin/"
cp -a "$SRC/src/com/android/systemui/volume/VolumePanelStyle.kt" "$DST/src/com/android/systemui/volume/"
cp -a "$SRC/src/com/android/systemui/volume/StyledVolumePanelLook.kt" "$DST/src/com/android/systemui/volume/"
cp -a "$SRC/src/com/android/systemui/volume/dialog" "$DST/src/com/android/systemui/volume/"
cp -a "$SRC/res/layout"/volume_dialog_*.xml "$DST/res/layout/"
cp -a "$SRC/res/drawable"/*volume* "$DST/res/drawable/" 2>/dev/null || true
cp -a "$SRC/res/drawable"/ic_volume_panel_*.xml "$DST/res/drawable/" 2>/dev/null || true
cp -a "$SRC/res/values"/volume_panel_*.xml "$DST/res/values/"
cp -a "$SRC/res/values-night"/volume_panel_*.xml "$DST/res/values-night/" 2>/dev/null || true

echo "[volume-panel] files copied"
