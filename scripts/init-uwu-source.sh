#!/usr/bin/env bash
# PenguinAOSP: 拉取 UwUAOSP 上游源码树到 source/
# 真相源不是这里 —— source/ 可随时删除重下；Penguin 层用 scripts/apply-all.sh 重放。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${PENGUIN_SOURCE_DIR:-$ROOT/source}"

# UwUAOSP 官方推荐走 release manifest（开发分支官方标注"可能不稳定"）。
MANIFEST_URL="${PENGUIN_MANIFEST_URL:-https://github.com/uwuAOSP/platform_vendor_uwu-versions.git}"
MANIFEST_BRANCH="${PENGUIN_MANIFEST_BRANCH:-main}"

source "$ROOT/scripts/proxy-env.sh"

# repo 启动器可能装在 ~/.local/bin 而不在 PATH
case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) [ -x "$HOME/.local/bin/repo" ] && PATH="$HOME/.local/bin:$PATH" ;;
esac
command -v repo >/dev/null || { echo "[init] 错误: 找不到 repo 启动器" >&2; exit 1; }

mkdir -p "$SRC"
cd "$SRC"

if [ ! -d .repo/manifests ]; then
    echo "[init] repo init -u $MANIFEST_URL -b $MANIFEST_BRANCH --git-lfs"
    repo init -u "$MANIFEST_URL" -b "$MANIFEST_BRANCH" --git-lfs
else
    echo "[init] .repo 已存在，跳过 repo init"
fi

# cerro 设备/内核/vendor 仓库（nubia-sm8650-devs）通过 local manifest 注入
if [ -d "$ROOT/local_manifests" ]; then
    mkdir -p .repo/local_manifests
    for xml in "$ROOT/local_manifests"/*.xml; do
        [ -f "$xml" ] || continue
        cp -a "$xml" .repo/local_manifests/
        echo "[init] 安装 local_manifests/$(basename "$xml")"
    done
fi

echo "[init] repo sync（可先用 PENGUIN_SYNC_JOBS 限制并发）"
repo sync -c -j"${PENGUIN_SYNC_JOBS:-$(nproc --all)}" \
    --force-sync --force-checkout --no-clone-bundle --no-tags \
    --optimized-fetch --prune

echo "[init] 完成。下一步: bash scripts/apply-all.sh"
