#!/usr/bin/env bash
# PenguinAOSP: restore UwU LauncherApps force-stop APIs missing from pinned frameworks_base.
# Launcher3 (81a7f4ee) calls LauncherApps.canForceStopPackage / forceStopPackage;
# frameworks commit 0b4e9110 is not on our pinned tip (1be8401 from sync-repair).
# 开关: PENGUIN_LAUNCHERAPPS_FORCE_STOP
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"
PATCH="$ROOT/patches/frameworks_base/launcherapps-force-stop-privileged.patch"
FB="$SOURCE_DIR/frameworks/base"
TARGET="$FB/core/java/android/content/pm/LauncherApps.java"

if [[ ! -f "$TARGET" ]]; then
    echo "[launcherapps-force-stop] skip missing $TARGET"
    exit 0
fi
if grep -q 'canForceStopPackage' "$TARGET"; then
    echo "[launcherapps-force-stop] skip (already applied): $TARGET"
    exit 0
fi
if [[ ! -f "$PATCH" ]]; then
    echo "[launcherapps-force-stop] error: missing $PATCH" >&2
    exit 1
fi
if git -C "$FB" apply --check "$PATCH" 2>/dev/null; then
    git -C "$FB" apply "$PATCH"
    echo "[launcherapps-force-stop] applied: $PATCH"
else
    echo "[launcherapps-force-stop] error: patch does not apply to $FB" >&2
    exit 1
fi
