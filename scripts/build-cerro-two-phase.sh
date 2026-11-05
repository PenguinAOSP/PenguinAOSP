#!/usr/bin/env bash
# PenguinAOSP: two-phase cerro build for 32G hosts.
# Phase 1: enable a large file swap, run until Soong analysis finishes, then stop.
# Phase 2: swapoff that file, start a fresh m otapackage -j8 (reuses ninja).
#
# 用法:
#   bash scripts/build-cerro-two-phase.sh
#   SWAP_SIZE_GB=64 PHASE1_JOBS=2 PHASE2_JOBS=8 bash scripts/build-cerro-two-phase.sh
#   SKIP_APPLY=1 bash scripts/build-cerro-two-phase.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"
SWAP_FILE="${SWAP_FILE:-/run/media/rong/data/penguin-soong.swap}"
SWAP_SIZE_GB="${SWAP_SIZE_GB:-64}"
PHASE1_JOBS="${PHASE1_JOBS:-2}"
PHASE2_JOBS="${PHASE2_JOBS:-8}"
LUNCH_TARGET="${LUNCH_TARGET:-penguin_cerro-cp2a-userdebug}"
BUILD_TARGET="${BUILD_TARGET:-otapackage}"
LOG_DIR="${LOG_DIR:-$ROOT/logs}"
PHASE1_LOG="${PHASE1_LOG:-$LOG_DIR/build-cerro-phase1-soong.log}"
PHASE2_LOG="${PHASE2_LOG:-$LOG_DIR/build-cerro-phase2-j8.log}"
ORCH_LOG="${ORCH_LOG:-$LOG_DIR/build-cerro-two-phase.log}"
NINJA="$SOURCE_DIR/out/soong/build.penguin_cerro.ninja"
STABLE_SECS="${STABLE_SECS:-45}"

mkdir -p "$LOG_DIR"
exec > >(tee -a "$ORCH_LOG") 2>&1

log() { echo "[two-phase $(date '+%H:%M:%S')] $*"; }

cleanup_phase1() {
    if [[ -n "${PHASE1_PID:-}" ]] && kill -0 "$PHASE1_PID" 2>/dev/null; then
        log "stopping phase1 pid=$PHASE1_PID"
        kill "$PHASE1_PID" 2>/dev/null || true
        # also tear down soong/m children rooted at the wrapper
        pkill -P "$PHASE1_PID" 2>/dev/null || true
        sleep 2
        kill -9 "$PHASE1_PID" 2>/dev/null || true
        pkill -9 -f 'soong_build.*penguin_cerro' 2>/dev/null || true
        pkill -9 -f 'soong_ui.*otapackage' 2>/dev/null || true
    fi
}

swap_on() {
    if swapon --show=NAME --noheadings 2>/dev/null | grep -qx "$SWAP_FILE"; then
        log "swap already on: $SWAP_FILE"
        return 0
    fi
    if [[ ! -f "$SWAP_FILE" ]]; then
        log "creating ${SWAP_SIZE_GB}G swapfile at $SWAP_FILE ..."
        fallocate -l "${SWAP_SIZE_GB}G" "$SWAP_FILE"
        chmod 600 "$SWAP_FILE"
        mkswap "$SWAP_FILE"
    fi
    log "swapon $SWAP_FILE"
    sudo swapon "$SWAP_FILE"
    swapon --show
    free -h
}

swap_off_file() {
    if swapon --show=NAME --noheadings 2>/dev/null | grep -qx "$SWAP_FILE"; then
        log "swapoff $SWAP_FILE"
        sudo swapoff "$SWAP_FILE"
    else
        log "file swap already off"
    fi
    swapon --show || true
    free -h
}

soong_done() {
    # soong_build gone, ninja exists and size stable across STABLE_SECS
    if pgrep -x soong_build >/dev/null 2>&1; then
        return 1
    fi
    [[ -f "$NINJA" ]] || return 1
    local s1 s2
    s1=$(stat -c%s "$NINJA" 2>/dev/null || echo 0)
    [[ "$s1" -gt 1000000000 ]] || return 1  # >1G
    sleep "$STABLE_SECS"
    if pgrep -x soong_build >/dev/null 2>&1; then
        return 1
    fi
    s2=$(stat -c%s "$NINJA" 2>/dev/null || echo 0)
    [[ "$s1" == "$s2" ]] || return 1
    # incomplete OOM dumps often end mid-token; require a trailing newline-ish end
    # and that analysis_status is not stuck on Writing (file may linger — OK if soong gone + stable)
    return 0
}

# --- prep ---
if [[ ! -d "$SOURCE_DIR/build" ]]; then
    log "error: no source tree at $SOURCE_DIR"
    exit 1
fi

if [[ "${SKIP_APPLY:-0}" != "1" ]]; then
    log "apply-all ..."
    bash "$ROOT/scripts/apply-all.sh"
fi

# Drop OOM-truncated ninja so Soong regenerates cleanly.
if [[ -f "$NINJA" ]]; then
    log "removing incomplete/stale $NINJA ($(du -h "$NINJA" | awk '{print $1}'))"
    rm -f "$NINJA"
fi
rm -f "$SOURCE_DIR/out/soong/.analysis_status"

swap_on

# --- phase 1: soong with swap ---
log "PHASE1 start: lunch + m $BUILD_TARGET -j$PHASE1_JOBS (swap ON) log=$PHASE1_LOG"
(
    export SKIP_APPLY=1
    export JOBS="$PHASE1_JOBS"
    export BUILD_LOG="$PHASE1_LOG"
    export LUNCH_TARGET BUILD_TARGET SOURCE_DIR
    # empty the log for this phase
    : >"$PHASE1_LOG"
    bash "$ROOT/scripts/build-cerro.sh" va
) &
PHASE1_PID=$!
log "PHASE1 pid=$PHASE1_PID"

# Wait until soong has run at least once, then until it finishes.
log "waiting for soong_build to appear ..."
for _ in $(seq 1 120); do
    if pgrep -x soong_build >/dev/null 2>&1; then
        log "soong_build appeared"
        break
    fi
    if ! kill -0 "$PHASE1_PID" 2>/dev/null; then
        log "PHASE1 exited early before soong_build; see $PHASE1_LOG"
        wait "$PHASE1_PID" || true
        swap_off_file
        exit 1
    fi
    sleep 5
done

log "waiting for soong analysis to finish (stable ninja ${STABLE_SECS}s) ..."
while kill -0 "$PHASE1_PID" 2>/dev/null; do
    if soong_done; then
        log "soong DONE: $NINJA size=$(stat -c%s "$NINJA") bytes"
        break
    fi
    if pgrep -x soong_build >/dev/null 2>&1; then
        rss=$(ps -C soong_build -o rss= 2>/dev/null | awk '{s+=$1} END{printf "%.1fGi", s/1024/1024}')
        st=$(tail -1 "$SOURCE_DIR/out/soong/.analysis_status" 2>/dev/null || echo '?')
        sw=$(free -h | awk '/^(交换|Swap):/{print $3 "/" $2}')
        log "soong still running rss≈$rss | $st | swap=$sw"
    else
        log "soong_build not running; checking ninja stability ..."
    fi
    sleep 20
done

if ! [[ -f "$NINJA" ]] || [[ "$(stat -c%s "$NINJA")" -lt 1000000000 ]]; then
    log "error: soong did not produce a usable ninja"
    cleanup_phase1
    swap_off_file
    exit 1
fi

cleanup_phase1
# drop page cache pressure a bit before phase2
sync
swap_off_file

# --- phase 2: compile j8 without file swap ---
log "PHASE2 start: m $BUILD_TARGET -j$PHASE2_JOBS (file swap OFF) log=$PHASE2_LOG"
: >"$PHASE2_LOG"
export SKIP_APPLY=1
export JOBS="$PHASE2_JOBS"
export BUILD_LOG="$PHASE2_LOG"
export LUNCH_TARGET BUILD_TARGET SOURCE_DIR
set +e
bash "$ROOT/scripts/build-cerro.sh" va
ec=$?
set -e
log "PHASE2 exit=$ec"
echo "OUTER_EXIT:$ec"
exit "$ec"
