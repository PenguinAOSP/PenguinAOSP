#!/usr/bin/env bash
# PenguinAOSP: QS panel Styles (qs_panel_style) into main SystemUI — not PenguinSystemUI override.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"
SRC="$ROOT/vendor/penguin/files/frameworks/base/packages/SystemUI"
DST="$SOURCE_DIR/frameworks/base/packages/SystemUI"

if [ ! -d "$SOURCE_DIR/build" ]; then
    echo "[styles-qs] 错误: $SOURCE_DIR 不像 AOSP 树" >&2
    exit 1
fi

copy_tree() {
    local rel="$1"
    if [ -e "$SRC/$rel" ]; then
        mkdir -p "$DST/$(dirname "$rel")"
        cp -a "$SRC/$rel" "$DST/$rel"
    fi
}

# Interfaces + DI
copy_tree src/com/android/systemui/penguin/QsPanels.kt
copy_tree src/com/android/systemui/penguin/ShadeMotion.kt
copy_tree src/com/android/systemui/penguin/PenguinHooksModule.kt

# Impl
mkdir -p "$DST/src/com/penguin/systemui/qs"
cp -a "$SRC/src/com/penguin/systemui/qs/"*.kt "$DST/src/com/penguin/systemui/qs/"

# QS style tree
mkdir -p \
  "$DST/src/com/android/systemui/qs/composefragment" \
  "$DST/src/com/android/systemui/qs/panels/ui/compose/infinitegrid" \
  "$DST/src/com/android/systemui/qs/shared/style" \
  "$DST/src/com/android/systemui/qs/shared/ui/slider" \
  "$DST/src/com/android/systemui/qs/ui/composable" \
  "$DST/src/com/android/systemui/scene/ui/composable/transitions" \
  "$DST/src/com/android/systemui/shade/ui/composable" \
  "$DST/src/com/android/compose/gesture/effect" \
  "$DST/res/drawable" "$DST/res/values" "$DST/res/values-land"

cp -a "$SRC/src/com/android/systemui/qs/composefragment/"*.kt "$DST/src/com/android/systemui/qs/composefragment/"
cp -a "$SRC/src/com/android/systemui/qs/panels/ui/compose/"*.kt "$DST/src/com/android/systemui/qs/panels/ui/compose/" 2>/dev/null || true
cp -a "$SRC/src/com/android/systemui/qs/panels/ui/compose/infinitegrid/StyledQsTileStyle.kt" \
  "$DST/src/com/android/systemui/qs/panels/ui/compose/infinitegrid/"
# Keep LiquidGlass.kt; copy style companions without clobbering LiquidGlass if only style files present
for f in LocalQsPanelStyle.kt QsPanelStyle.kt QsPanelStyleRepository.kt StyleOfViewModels.kt; do
  cp -a "$SRC/src/com/android/systemui/qs/shared/style/$f" "$DST/src/com/android/systemui/qs/shared/style/"
done
cp -a "$SRC/src/com/android/systemui/qs/shared/ui/slider/SharedSliderKey.kt" "$DST/src/com/android/systemui/qs/shared/ui/slider/"
cp -a "$SRC/src/com/android/systemui/qs/ui/composable/"*.kt "$DST/src/com/android/systemui/qs/ui/composable/"
cp -a "$SRC/src/com/android/systemui/scene/ui/composable/transitions/"*.kt \
  "$DST/src/com/android/systemui/scene/ui/composable/transitions/"
cp -a "$SRC/src/com/android/systemui/shade/ui/composable/StyledShadeHeader.kt" \
  "$DST/src/com/android/systemui/shade/ui/composable/"
cp -a "$SRC/src/com/android/compose/gesture/effect/ControlCentreOverscrollEffect.kt" \
  "$DST/src/com/android/compose/gesture/effect/" 2>/dev/null || true

# Resources
cp -a "$SRC/res/values/penguin_qs_strings.xml" "$DST/res/values/"
cp -a "$SRC/res/values/penguin_qs_dimens.xml" "$DST/res/values/"
cp -a "$SRC/res/values-land/penguin_qs_dimens.xml" "$DST/res/values-land/" 2>/dev/null || true
cp -a "$SRC/res/drawable"/ic_penguin_media_*.xml "$DST/res/drawable/" 2>/dev/null || true
cp -a "$SRC/res/drawable"/ic_qs_brightness_auto_*.xml "$DST/res/drawable/" 2>/dev/null || true

echo "[styles-qs] files copied"
python3 "$ROOT/vendor/penguin/patches/systemui_styles_qs_panel.py" --source-dir "$SOURCE_DIR"
python3 "$ROOT/vendor/penguin/patches/systemui_qs_uwu_compat.py" --source-dir "$SOURCE_DIR"
