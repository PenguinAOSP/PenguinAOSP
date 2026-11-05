#!/usr/bin/env bash
# Validate PenguinAOSP project tree before apply/build (no full compile)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ERR=0

check() {
  if [[ -e "$1" ]]; then
    echo "[validate] OK $2"
  else
    echo "[validate] MISSING $2 ($1)" >&2
    ERR=1
  fi
}

check "$ROOT/AGENTS.md" "AGENTS.md"
check "$ROOT/docs/SKELETON.md" "SKELETON"
check "$ROOT/docs/TROUBLESHOOTING.md" "TROUBLESHOOTING"
check "$ROOT/docs/WORKLOG.md" "WORKLOG"
check "$ROOT/docs/patch-toggles.md" "patch-toggles"
check "$ROOT/scripts/apply-all.sh" "apply-all"
check "$ROOT/scripts/build-cerro.sh" "build-cerro"
check "$ROOT/scripts/run-cerro-detached.sh" "detached build"
check "$ROOT/scripts/watch-cerro-build.sh" "watch build"
check "$ROOT/scripts/watch-systemui-stability.sh" "watch systemui"
check "$ROOT/scripts/proxy-env.sh" "proxy-env"
check "$ROOT/devices/nubia/cerro/penguin_cerro.mk" "penguin_cerro product"
check "$ROOT/devices/nubia/cerro/device.mk" "cerro device.mk"
check "$ROOT/devices/nubia/cerro/AndroidProducts.mk" "AndroidProducts"
check "$ROOT/vendor/penguin/files/packages/apps/PenguinLaboratory/Android.bp" "PenguinLaboratory bp"
check "$ROOT/vendor/penguin/files/packages/apps/PenguinLaboratory/privapp_permissions_com.penguin.laboratory.xml" "Laboratory privapp xml"

# privapp prebuilt must install with .xml suffix (PackageManager only loads *.xml)
if grep -q 'filename: "privapp_permissions_com.penguin.laboratory.xml"' \
  "$ROOT/vendor/penguin/files/packages/apps/PenguinLaboratory/Android.bp"; then
  echo "[validate] OK Laboratory privapp filename=.xml"
else
  echo "[validate] MISSING Laboratory prebuilt_etc filename: ...xml（会卡第二屏）" >&2
  ERR=1
fi

if [[ -d "$ROOT/source/build" ]]; then
  echo "[validate] source/ 已 sync，可运行 apply-all.sh"
else
  echo "[validate] WARN source/ 未就绪 — bash scripts/init-uwu-source.sh" >&2
fi

if [[ "$ERR" -ne 0 ]]; then
  echo "[validate] FAILED" >&2
  exit 1
fi
echo "[validate] OK"
