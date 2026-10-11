#!/usr/bin/env bash
# PenguinAOSP: 品牌化层 —— 用户可见系统名统一 PenguinAOSP。
# 收工自检项（AGENTS.md）: 关于手机 / SetupWizard 欢迎页 / 设置标题 显示 PenguinAOSP。
# 幂等: 检查目标文件是否已含 "PenguinAOSP" 标记。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"
MARK="// PenguinOS: branding"

if [ ! -d "$SOURCE_DIR/build" ]; then
    echo "[branding] 错误: $SOURCE_DIR 不像 AOSP 树" >&2
    exit 1
fi

echo "[branding] 当前为占位实现（M0）：尚未有任何品牌补丁。"
echo "[branding] M2 时在此实现: ro.penguin.version / PENGUIN_BUILD_TYPE / uwu->penguin 资源覆盖。"
exit 0
