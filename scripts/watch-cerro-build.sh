#!/usr/bin/env bash
# Lightweight log watcher for detached cerro builds. Does NOT attach to ninja.
# Prints a status line every INTERVAL seconds; exits when build pid dies or
# log shows success/failure.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${LOG_DIR:-$ROOT/logs}"
PIDFILE="${PIDFILE:-$LOG_DIR/build-cerro-detached.pid}"
LOG="${BUILD_LOG:-$LOG_DIR/build-cerro-detached-latest.log}"
INTERVAL="${INTERVAL:-60}"

echo "[watch $(date '+%H:%M:%S')] log=$LOG pidfile=$PIDFILE interval=${INTERVAL}s"

while true; do
    pid=""
    [[ -f "$PIDFILE" ]] && pid=$(cat "$PIDFILE" 2>/dev/null || true)
    alive=0
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        alive=1
    fi

    prog=$(rg -o '\[[ 0-9]+% [0-9]+/[0-9]+\]' "$LOG" 2>/dev/null | tail -1 || true)
    [[ -z "$prog" ]] && prog='(no % yet)'
    mem=$(free -h | awk '/^内存:|^Mem:/{print $3"/"$2" used"}')
    sw=$(free -h | awk '/^交换:|^Swap:/{print $3"/"$2" swap"}')

    echo "[watch $(date '+%H:%M:%S')] alive=$alive pid=${pid:-?} $prog | $mem | $sw"

    if rg -q '#### build completed successfully|BUILD_EXIT:0|EXIT:0$' "$LOG" 2>/dev/null; then
        echo "[watch] SUCCESS"
        tail -n 20 "$LOG"
        exit 0
    fi
    if rg -q '#### failed to build|BUILD_EXIT:[1-9]|EXIT:[1-9]' "$LOG" 2>/dev/null; then
        echo "[watch] FAILED"
        rg -n 'FAILED:|error: |#### failed|EXIT:' "$LOG" | tail -30
        exit 1
    fi
    if [[ "$alive" -eq 0 ]]; then
        echo "[watch] build pid gone without success marker — check $LOG"
        tail -n 40 "$LOG"
        exit 2
    fi
    sleep "$INTERVAL"
done
