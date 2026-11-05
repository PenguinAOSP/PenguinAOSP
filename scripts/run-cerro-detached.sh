#!/usr/bin/env bash
# PenguinAOSP: run cerro build fully detached from the IDE/agent shell.
# stdout/stderr go only to a log file; Cursor should only tail that log.
#
# 用法:
#   bash scripts/run-cerro-detached.sh
#   JOBS=6 SKIP_APPLY=1 bash scripts/run-cerro-detached.sh
#   USE_FILE_SWAP=1 bash scripts/run-cerro-detached.sh   # default 1
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${LOG_DIR:-$ROOT/logs}"
mkdir -p "$LOG_DIR"
STAMP=$(date '+%Y%m%d-%H%M%S')
LOG="${BUILD_LOG:-$LOG_DIR/build-cerro-detached-$STAMP.log}"
PIDFILE="${PIDFILE:-$LOG_DIR/build-cerro-detached.pid}"
SWAP_FILE="${SWAP_FILE:-/run/media/rong/data/penguin-soong.swap}"
USE_FILE_SWAP="${USE_FILE_SWAP:-1}"
JOBS="${JOBS:-6}"
SKIP_APPLY="${SKIP_APPLY:-1}"

if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "[detached] already running pid=$(cat "$PIDFILE") log see $PIDFILE"
    exit 1
fi

if [[ "$USE_FILE_SWAP" == "1" ]]; then
    if [[ -f "$SWAP_FILE" ]] && ! swapon --show=NAME --noheadings 2>/dev/null | grep -qx "$SWAP_FILE"; then
        sudo swapon "$SWAP_FILE" || true
    fi
fi

# Clear proxies that may be dead; build does not need them for local compile.
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY || true

# Ensure force-stop API present (idempotent).
bash "$ROOT/scripts/apply-launcherapps-force-stop.sh" >/dev/null 2>&1 || true

cd "$ROOT"
# setsid: new session, survives agent/IDE death; nohup: ignore SIGHUP
setsid nohup env SKIP_APPLY="$SKIP_APPLY" JOBS="$JOBS" BUILD_LOG="$LOG" \
    bash "$ROOT/scripts/build-cerro.sh" va \
    >"$LOG" 2>&1 < /dev/null &
echo $! >"$PIDFILE"
sleep 1
if ! kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "[detached] failed to start; see $LOG" >&2
    exit 1
fi

# Convenience symlink to latest log
ln -sfn "$LOG" "$LOG_DIR/build-cerro-detached-latest.log"
ln -sfn "$LOG" "$ROOT/build-cerro.log"

echo "[detached] started pid=$(cat "$PIDFILE")"
echo "[detached] log=$LOG"
echo "[detached] jobs=$JOBS skip_apply=$SKIP_APPLY file_swap=$USE_FILE_SWAP"
swapon --show || true
free -h | head -3
