#!/usr/bin/env bash
# 检查 repo sync 进度与关键路径是否就绪
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"

echo "[sync-status] source: $SOURCE_DIR"
if [[ ! -d "$SOURCE_DIR/.repo" ]]; then
  echo "[sync-status] 未 init — 运行: bash scripts/init-uwu-source.sh"
  exit 1
fi

du -sh "$SOURCE_DIR" 2>/dev/null || true
pgrep -af "repo sync" >/dev/null && echo "[sync-status] repo sync 正在运行…" || echo "[sync-status] repo sync 未在运行"

for p in build/envsetup.sh frameworks/base device/nubia/cerro packages/apps/PenguinLaboratory; do
  if [[ -e "$SOURCE_DIR/$p" ]]; then
    echo "[sync-status] OK $p"
  else
    echo "[sync-status] 待同步/待 apply $p"
  fi
done

tail -3 "$SOURCE_DIR/init.log" 2>/dev/null || true
