#!/usr/bin/env bash
# PenguinAOSP: cerro (Nubia Z60 Ultra) 构建入口。
# 目标: penguin_cerro-cp2a-userdebug -> bacon (OTA zip)
# 用法: bash scripts/build-cerro.sh va   （SKIP_APPLY=1 跳过重放，直接编）
# 状态: 占位（M0）。设备树迁移（M1）完成后补全 lunch/产品注册。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"

echo "[build-cerro] 错误: 构建链尚未就绪（M0 骨架阶段）。" >&2
echo "[build-cerro] 前置条件:" >&2
echo "  1. cerro 设备树迁入 devices/nubia/cerro 并由 apply-all 拷入 source/device/nubia/cerro" >&2
echo "  2. vendor/penguin 注册 penguin_cerro 产品（lunch 前缀 penguin_，构建变量见 docs/SKELETON.md §5）" >&2
echo "  3. 此后本脚本实现: source build/envsetup.sh && lunch penguin_cerro-cp2a-userdebug && mka bacon" >&2
exit 2
