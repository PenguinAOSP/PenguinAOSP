#!/usr/bin/env bash
# 编译前准备：大容量文件 swap，避免 Soong 阶段 OOM
# PENGUIN_SKIP_SWAP=1：不创建/不挂磁盘 swap
set -euo pipefail
SWAPFILE="${PENGUIN_SWAPFILE:-/run/media/rong/data/penguin-soong.swap}"
SWAP_GB="${PENGUIN_SWAP_GB:-64}"

if [[ "${PENGUIN_SKIP_SWAP:-0}" == "1" ]]; then
  echo "[prepare-swap] PENGUIN_SKIP_SWAP=1 — skip disk swapfile"
  free -h | sed -n '1,3p'
  swapon --show || true
  exit 0
fi

if [[ ! -f "$SWAPFILE" ]]; then
  echo "[prepare-swap] 创建 ${SWAP_GB}G swap: $SWAPFILE"
  sudo fallocate -l "${SWAP_GB}G" "$SWAPFILE" || sudo truncate -s "${SWAP_GB}G" "$SWAPFILE"
  sudo chmod 600 "$SWAPFILE"
  sudo mkswap "$SWAPFILE"
fi

if ! sudo swapon --show | grep -qF "$SWAPFILE"; then
  echo "[prepare-swap] swapon $SWAPFILE"
  sudo swapon "$SWAPFILE"
fi

sudo sysctl -w vm.swappiness="${PENGUIN_SWAPPINESS:-100}" >/dev/null
echo "[prepare-swap] $(free -h | sed -n '1,3p')"
swapon --show
