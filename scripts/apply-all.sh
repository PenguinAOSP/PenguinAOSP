#!/usr/bin/env bash
# PenguinAOSP: 补丁重放唯一入口。
# 约定（AGENTS.md）：
#   - 每个功能在 apply_layers 里注册一行；
#   - 每个子 apply 必须: 收 SOURCE_DIR、幂等、失败时报明确锚点；
#   - 开关 PENGUIN_*=0 跳过对应层（见 docs/patch-toggles.md）。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"

# 开关默认值（新功能在这里登记，并同步 docs/patch-toggles.md）
PENGUIN_DEFAULTS=(
    PENGUIN_BRANDING=1
    PENGUIN_CERRO_DEVICE=1
    PENGUIN_LABORATORY=1
)
for kv in "${PENGUIN_DEFAULTS[@]}"; do
    key="${kv%%=*}"
    if [ -z "${!key:-}" ]; then export "$key"="${kv#*=}"; fi
done

if [ ! -d "$SOURCE_DIR/build" ]; then
    echo "[apply-all] 错误: $SOURCE_DIR 不像 AOSP 树（缺 build/）" >&2
    echo "[apply-all] 先运行: bash scripts/init-uwu-source.sh" >&2
    exit 1
fi

FAILED=()

apply_layer() {
    local name="$1" script="$2" key="$3"
    if [ "${!key:-1}" = "0" ]; then
        echo "[apply-all] 跳过 $name ($key=0)"
        return 0
    fi
    echo "[apply-all] ==> $name"
    if ! bash "$script"; then
        echo "[apply-all] 失败: $name ($script)" >&2
        FAILED+=("$name")
        return 1
    fi
}

# ---- apply layers（按依赖顺序，新功能按编号往下加） --------------------------
LAYERS=(
    "penguin-laboratory|$ROOT/scripts/apply-penguin-laboratory.sh|PENGUIN_LABORATORY"
    "cerro-device|$ROOT/scripts/apply-cerro-device.sh|PENGUIN_CERRO_DEVICE"
    "branding|$ROOT/scripts/apply-penguin-branding.sh|PENGUIN_BRANDING"
)
# -----------------------------------------------------------------------------

for entry in "${LAYERS[@]}"; do
    IFS='|' read -r name script key <<<"$entry"
    apply_layer "$name" "$script" "$key" || true
done

if [ "${#FAILED[@]}" -gt 0 ]; then
    echo "[apply-all] 失败层: ${FAILED[*]}" >&2
    echo "[apply-all] 修复后重跑 apply-all.sh（各层幂等，可安全重放）" >&2
    exit 1
fi

echo "[apply-all] 全部完成: $SOURCE_DIR"
