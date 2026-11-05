#!/usr/bin/env bash
# PenguinAOSP: cerro (Nubia Z60 Ultra) 构建入口。
# 目标: penguin_cerro-cp2a-userdebug -> otapackage (OTA zip)
# 用法:
#   bash scripts/build-cerro.sh va          # apply-all 后 lunch + m otapackage
#   SKIP_APPLY=1 bash scripts/build-cerro.sh va
#   JOBS=8 bash scripts/build-cerro.sh va
# 说明: UwUAOSP 无 Lineage 的 mka/bacon；用 soong 的 m + AOSP otapackage。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"
LUNCH_TARGET="${LUNCH_TARGET:-penguin_cerro-cp2a-userdebug}"
BUILD_TARGET="${BUILD_TARGET:-otapackage}"
# Default -j4 on typical 32G hosts; override with JOBS=N. (Soong analysis peak
# is largely independent of JOBS — see docs/TROUBLESHOOTING.md.)
JOBS="${JOBS:-4}"
LOG="${BUILD_LOG:-$ROOT/build-cerro.log}"

# Optional first arg: "va" (vanilla) kept for PlasmaAOSP muscle memory.
case "${1:-}" in
    va | "" ) ;;
    * )
        echo "[build-cerro] 用法: bash scripts/build-cerro.sh [va]" >&2
        exit 2
        ;;
esac

if [ ! -d "$SOURCE_DIR/build" ]; then
    echo "[build-cerro] 错误: $SOURCE_DIR 不像 AOSP 树。先跑: bash scripts/init-uwu-source.sh" >&2
    exit 1
fi

if [ "${SKIP_APPLY:-0}" != "1" ]; then
    echo "[build-cerro] apply-all ..."
    bash "$ROOT/scripts/apply-all.sh"
else
    echo "[build-cerro] SKIP_APPLY=1 — 跳过重放"
fi

if [ ! -f "$SOURCE_DIR/device/nubia/cerro/penguin_cerro.mk" ]; then
    echo "[build-cerro] 错误: 缺 penguin_cerro.mk（apply-cerro-device 未生效）" >&2
    exit 1
fi

# shellcheck disable=SC1091
source "$ROOT/scripts/proxy-env.sh" 2>/dev/null || true

export USE_CCACHE="${USE_CCACHE:-1}"
export CCACHE_DIR="${CCACHE_DIR:-$ROOT/.ccache}"
if command -v ccache >/dev/null 2>&1; then
    export CCACHE_EXEC="${CCACHE_EXEC:-$(command -v ccache)}"
    mkdir -p "$CCACHE_DIR"
fi

# Note: soong_ui strips GOMAXPROCS before soong_build; exporting it does not
# currently cap analysis RAM. Kept for hosts/tools that honor it outside sandbox.
export GOMAXPROCS="${GOMAXPROCS:-4}"
echo "[build-cerro] GOMAXPROCS=$GOMAXPROCS JOBS=$JOBS (soong analysis may ignore GOMAXPROCS)"

cd "$SOURCE_DIR"
# AOSP envsetup/lunch/mka touch many unbound vars; keep nounset off from here on.
set +u
# shellcheck disable=SC1091
source build/envsetup.sh

echo "[build-cerro] lunch $LUNCH_TARGET"
lunch "$LUNCH_TARGET" || {
    echo "[build-cerro] 错误: lunch 失败 ($LUNCH_TARGET)" >&2
    exit 1
}

echo "[build-cerro] m $BUILD_TARGET -j$JOBS  log=$LOG"
set +e
set -o pipefail
# Prefer soong wrapper `m` (on PATH after envsetup); fall back to make.
if command -v m >/dev/null 2>&1; then
    m "$BUILD_TARGET" -j"$JOBS" 2>&1 | tee "$LOG"
else
    make "$BUILD_TARGET" -j"$JOBS" 2>&1 | tee "$LOG"
fi
ec=${PIPESTATUS[0]}
echo "EXIT:$ec" | tee -a "$LOG" >/dev/null
exit "$ec"
