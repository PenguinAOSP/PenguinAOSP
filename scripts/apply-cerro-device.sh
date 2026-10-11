#!/usr/bin/env bash
# PenguinAOSP: cerro 设备层 —— 把 devices/nubia/（基座 + Rising 优化，无 UDC）拷进 source/。
# 真相源: devices/nubia/{cerro,sm8650-common}（见 devices/nubia/BASE.md）。
# 幂等: rsync 全量镜像，重放结果一致。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"

if [ ! -d "$SOURCE_DIR/.repo" ]; then
    echo "[cerro-device] 错误: $SOURCE_DIR 不是 repo 树，先跑 scripts/init-uwu-source.sh" >&2
    exit 1
fi

for tree in cerro sm8650-common; do
    src="$ROOT/devices/nubia/$tree"
    dst="$SOURCE_DIR/device/nubia/$tree"
    if [ ! -d "$src" ]; then
        echo "[cerro-device] 错误: 缺 $src" >&2
        exit 1
    fi
    mkdir -p "$SOURCE_DIR/device/nubia"
    rsync -a --delete --exclude='.git' "$src/" "$dst/"
    echo "[cerro-device] 已镜像 $tree -> device/nubia/$tree"
done

echo "[cerro-device] 完成。kernel/vendor 仓库由 local_manifests/cerro.xml 在 sync 时拉取。"
