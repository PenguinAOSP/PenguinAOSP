#!/usr/bin/env bash
# PenguinAOSP: PenguinLaboratory 应用层 —— penguinOS 专属设置中心（独立 APK，C 类 vendor 副本）。
# 来源: Project-penguinOS/penguin_packages_apps_PenguinLaboratory @ celerity
# 功能盘点见 docs/penguinos-feature-inventory.md。幂等: rsync 镜像。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"
SRC="$ROOT/vendor/penguin/files/packages/apps/PenguinLaboratory"

if [ ! -d "$SOURCE_DIR/build" ]; then
    echo "[laboratory] 错误: $SOURCE_DIR 不像 AOSP 树" >&2
    exit 1
fi
if [ ! -f "$SRC/Android.bp" ]; then
    echo "[laboratory] 错误: 缺 $SRC/Android.bp" >&2
    exit 1
fi

mkdir -p "$SOURCE_DIR/packages/apps"
rsync -a --delete --exclude='.git' "$SRC/" "$SOURCE_DIR/packages/apps/PenguinLaboratory/"
echo "[laboratory] PenguinLaboratory -> packages/apps/PenguinLaboratory"
echo "[laboratory] 记得在产品 mk 里: PRODUCT_PACKAGES += PenguinLaboratory（cerro 层已含）"
