#!/usr/bin/env bash
# Monitor SystemUI for crash loops / stuck boot; on FAIL dump logs then reboot recovery.
# AGENTS.md 硬性规则 10: 2 分钟内抓日志，冷却进 recovery — 禁止换旧 APK 赌开机。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERIAL="${1:-}"
DURATION_SEC="${DURATION_SEC:-60}"
CRASH_THRESHOLD="${CRASH_THRESHOLD:-2}"
GRACE_SEC="${GRACE_SEC:-20}"
LOG_DIR="${WATCH_LOG_DIR:-$ROOT/logs/systemui-watch}"
ADB=(adb)
if [[ -n "$SERIAL" ]]; then
  ADB+=( -s "$SERIAL" )
fi

mkdir -p "$LOG_DIR"
STAMP=$(date +%Y%m%d-%H%M%S)
DUMP="$LOG_DIR/fail-$STAMP"

echo "[watch-systemui] 监控 ${DURATION_SEC}s，设备=${SERIAL:-default}，崩溃阈值=${CRASH_THRESHOLD}，宽限期=${GRACE_SEC}s"

"${ADB[@]}" wait-for-device
start_pid="$("${ADB[@]}" shell pidof com.android.systemui 2>/dev/null | tr -d '\r' || true)"
echo "[watch-systemui] 起始 pid: ${start_pid:-none}"

"${ADB[@]}" logcat -c 2>/dev/null || true
start_time=$SECONDS
end=$((SECONDS + DURATION_SEC))
crash_count=0
restarts=0
last_pid="$start_pid"
boot_stuck=0

dump_and_recovery() {
  local reason=$1
  echo "[watch-systemui] FATAL: $reason — 抓日志后 reboot recovery（2 分钟内完成）"
  mkdir -p "$DUMP"
  {
    echo "reason=$reason"
    echo "time=$(date -Is)"
    echo "boot_completed=$("${ADB[@]}" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true)"
    echo "bootanim=$("${ADB[@]}" shell getprop init.svc.bootanim 2>/dev/null | tr -d '\r' || true)"
    echo "systemui_pid=$("${ADB[@]}" shell pidof com.android.systemui 2>/dev/null | tr -d '\r' || true)"
  } >"$DUMP/meta.txt"
  "${ADB[@]}" logcat -d -b crash -t 200 >"$DUMP/crash.txt" 2>/dev/null || true
  "${ADB[@]}" logcat -d -t 800 >"$DUMP/main.txt" 2>/dev/null || true
  "${ADB[@]}" logcat -d -b events -t 200 >"$DUMP/events.txt" 2>/dev/null || true
  "${ADB[@]}" shell getprop >"$DUMP/getprop.txt" 2>/dev/null || true
  grep -E 'FATAL EXCEPTION|Caused by:|Process: com.android.systemui|privileged permission|WRITE_SECURE|AndroidRuntime' \
    "$DUMP/crash.txt" "$DUMP/main.txt" 2>/dev/null | head -120 >"$DUMP/excerpt.txt" || true
  echo "[watch-systemui] logs -> $DUMP"
  "${ADB[@]}" reboot recovery || "${ADB[@]}" reboot || true
  exit 2
}

while (( SECONDS < end )); do
  sleep 2
  in_grace=0
  if (( SECONDS - start_time < GRACE_SEC )); then
    in_grace=1
  fi

  bc=$("${ADB[@]}" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true)
  anim=$("${ADB[@]}" shell getprop init.svc.bootanim 2>/dev/null | tr -d '\r' || true)
  if (( in_grace == 0 )) && [[ "$anim" == "running" || -z "$bc" || "$bc" != "1" ]]; then
    boot_stuck=$((boot_stuck + 1))
  else
    boot_stuck=0
  fi
  if (( boot_stuck >= 15 )); then
    dump_and_recovery "卡第二屏/bootanim 不退 (boot_completed=${bc:-empty} anim=${anim:-empty})"
  fi

  cur_pid="$("${ADB[@]}" shell pidof com.android.systemui 2>/dev/null | tr -d '\r' || true)"
  if [[ -n "$cur_pid" && -n "$last_pid" && "$cur_pid" != "$last_pid" ]]; then
    restarts=$((restarts + 1))
    echo "[watch-systemui] WARN: SystemUI 重启 ${last_pid} -> ${cur_pid} (累计 ${restarts})"
    last_pid="$cur_pid"
  elif [[ -z "$cur_pid" ]]; then
    echo "[watch-systemui] WARN: SystemUI 进程不存在"
    restarts=$((restarts + 1))
    last_pid=""
  else
    last_pid="${cur_pid:-$last_pid}"
  fi

  new_crashes="$("${ADB[@]}" logcat -d -b crash -t 40 2>/dev/null | grep -c "Process: com.android.systemui" || true)"
  if [[ "$new_crashes" -gt "$crash_count" ]]; then
    crash_count="$new_crashes"
    echo "[watch-systemui] WARN: SystemUI crash 日志条数=${crash_count}"
    "${ADB[@]}" logcat -d -b crash -t 5 2>/dev/null | tail -30 || true
  fi

  if (( in_grace == 0 )) && (( restarts >= CRASH_THRESHOLD || crash_count >= CRASH_THRESHOLD )); then
    dump_and_recovery "SystemUI 崩溃循环 restarts=${restarts} crash_logs=${crash_count}"
  fi
done

final_pid="$("${ADB[@]}" shell pidof com.android.systemui 2>/dev/null | tr -d '\r' || true)"
echo "[watch-systemui] 完成: pid=${final_pid:-none} restarts=${restarts} crash_logs=${crash_count}"
if [[ -z "$final_pid" ]]; then
  dump_and_recovery "监控结束时 SystemUI 未运行"
fi

exit 0
