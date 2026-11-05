#!/usr/bin/env bash
# PenguinAOSP: Liquid Glass — framework core + ViewRootImpl + SystemUI ShadeColors/LiquidGlass.
# Framework changes need system flash; SystemUI portion can hotpush after framework is present.
# NOTE: Do NOT wholesale-copy penguinOS ExpandableNotificationRow/ScrimController — they pull
# NTForbiddenSwipeDownQSController / ScrimUtils / QS_DUAL_TONE (not in UwU).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"
CORE_SRC="$ROOT/vendor/penguin/files/frameworks/base/core/java/com/android/internal/penguin/glass"
CORE_DST="$SOURCE_DIR/frameworks/base/core/java/com/android/internal/penguin/glass"
SYS_SRC="$ROOT/vendor/penguin/files/frameworks/base/packages/SystemUI"
SYS_DST="$SOURCE_DIR/frameworks/base/packages/SystemUI"

if [ ! -d "$SOURCE_DIR/build" ]; then
    echo "[liquid-glass] 错误: $SOURCE_DIR 不像 AOSP 树" >&2
    exit 1
fi

mkdir -p "$CORE_DST"
cp -a "$CORE_SRC"/*.java "$CORE_DST/"
echo "[liquid-glass] core java copied"
python3 "$ROOT/vendor/penguin/patches/framework_viewroot_liquid_glass.py" --source-dir "$SOURCE_DIR"

for rel in \
    src/com/android/systemui/qs/shared/style/LiquidGlass.kt \
    src/com/android/systemui/shade/ui/ShadeColors.kt
do
    if [ -f "$SYS_SRC/$rel" ]; then
        mkdir -p "$SYS_DST/$(dirname "$rel")"
        cp -a "$SYS_SRC/$rel" "$SYS_DST/$rel"
    fi
done

mkdir -p "$SYS_DST/res/drawable" "$SYS_DST/res/values"
if compgen -G "$SYS_SRC/res/drawable/lg_glyph*.xml" >/dev/null; then
    cp -a "$SYS_SRC/res/drawable"/lg_glyph*.xml "$SYS_DST/res/drawable/"
fi
if [ -f "$SYS_SRC/res/values/liquid_glass_strings.xml" ]; then
    cp -a "$SYS_SRC/res/values/liquid_glass_strings.xml" "$SYS_DST/res/values/"
fi
echo "[liquid-glass] SystemUI LiquidGlass + ShadeColors + glyphs copied"
python3 "$ROOT/vendor/penguin/patches/systemui_liquid_glass_surfaces.py" --source-dir "$SOURCE_DIR"
