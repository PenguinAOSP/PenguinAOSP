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
    PENGUIN_UWU_BUILD_PREFIX=1
    PENGUIN_WFD_AIDL_V5=1
    PENGUIN_VENDOR_LFS=1
    PENGUIN_HV_HAPTICS=1
    PENGUIN_SYNX_UNINIT=1
    PENGUIN_SDE_RM_PP=1
    PENGUIN_LAUNCHERAPPS_FORCE_STOP=1
    PENGUIN_SETTINGS_KEYS=1
    PENGUIN_SECURE_KEYS=1
    PENGUIN_LAB_SETTINGS_ENTRY=1
    PENGUIN_EDGELIGHTING=1
    PENGUIN_BACKTOAPP=1
    PENGUIN_FREQUENT_APPS=1
    PENGUIN_STYLES_POWER_MENU=1
    PENGUIN_STYLES_VOLUME_PANEL=1
    PENGUIN_STYLES_QS_PANEL=1
    PENGUIN_LIQUID_GLASS_CORE=1
    PENGUIN_LAUNCHER_LIQUID_GLASS=1
    PENGUIN_LAUNCHER_MEMINFO=1
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
    "penguin-uwu-build-prefix|$ROOT/scripts/apply-penguin-uwu-build-prefix.sh|PENGUIN_UWU_BUILD_PREFIX"
    "launcherapps-force-stop|$ROOT/scripts/apply-launcherapps-force-stop.sh|PENGUIN_LAUNCHERAPPS_FORCE_STOP"
    "penguin-laboratory|$ROOT/scripts/apply-penguin-laboratory.sh|PENGUIN_LABORATORY"
    "settings-system-keys|$ROOT/scripts/apply-settings-system-keys.sh|PENGUIN_SETTINGS_KEYS"
    "settings-secure-keys|$ROOT/scripts/apply-settings-secure-keys.sh|PENGUIN_SECURE_KEYS"
    "lab-settings-entry|$ROOT/scripts/apply-settings-laboratory-entry.sh|PENGUIN_LAB_SETTINGS_ENTRY"
    "edgelighting|$ROOT/scripts/apply-edgelighting.sh|PENGUIN_EDGELIGHTING"
    "backtoapp|$ROOT/scripts/apply-backtoapp.sh|PENGUIN_BACKTOAPP"
    "frequent-apps|$ROOT/scripts/apply-frequent-apps.sh|PENGUIN_FREQUENT_APPS"
    "styles-power-menu|$ROOT/scripts/apply-styles-power-menu.sh|PENGUIN_STYLES_POWER_MENU"
    "styles-volume-panel|$ROOT/scripts/apply-styles-volume-panel.sh|PENGUIN_STYLES_VOLUME_PANEL"
    "styles-qs-panel|$ROOT/scripts/apply-styles-qs-panel.sh|PENGUIN_STYLES_QS_PANEL"
    "liquid-glass-core|$ROOT/scripts/apply-liquid-glass-core.sh|PENGUIN_LIQUID_GLASS_CORE"
    "launcher-liquid-glass|$ROOT/scripts/apply-launcher-liquid-glass.sh|PENGUIN_LAUNCHER_LIQUID_GLASS"
    "launcher-meminfo|$ROOT/scripts/apply-launcher-meminfo.sh|PENGUIN_LAUNCHER_MEMINFO"
    "cerro-device|$ROOT/scripts/apply-cerro-device.sh|PENGUIN_CERRO_DEVICE"
    "vendor-lfs|$ROOT/scripts/pull-vendor-lfs.sh|PENGUIN_VENDOR_LFS"
    "wfd-aidl-v5|$ROOT/scripts/cerro/patch-wfd-aidl-v5.sh|PENGUIN_WFD_AIDL_V5"
    "hv-haptics|$ROOT/scripts/cerro/patch-qcom-hv-haptics.sh|PENGUIN_HV_HAPTICS"
    "synx-uninit|$ROOT/scripts/cerro/patch-synx-uninit.sh|PENGUIN_SYNX_UNINIT"
    "sde-rm-pp|$ROOT/scripts/cerro/patch-sde-rm-pp-cfg.sh|PENGUIN_SDE_RM_PP"
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
