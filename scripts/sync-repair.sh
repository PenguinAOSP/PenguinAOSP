#!/usr/bin/env bash
# PenguinAOSP: repo sync 自愈循环 —— 网络中断常留下"对象库残缺"的仓库，
# 表现为 update-ref "not a valid SHA1" / pack 未解决 delta。
# 每轮: sync -> 解析失败仓库 -> 删除其 worktree/.repo/projects/.git/.repo/project-objects -> 重试。
# 用法: PENGUIN_SYNC_JOBS=2 bash scripts/sync-repair.sh [最大轮数, 默认6]
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JOBS="${PENGUIN_SYNC_JOBS:-2}"
MAX_ROUNDS="${1:-6}"

source "$ROOT/scripts/proxy-env.sh"
export PATH="$HOME/.local/bin:$PATH"
cd "$ROOT/source" || exit 1

# name -> path 映射（repo list 输出 "path : name"）
declare -A NAME2PATH
while IFS= read -r line; do
    p="${line%% : *}"
    n="${line##* : }"
    NAME2PATH["$n"]="$p"
done < <(repo list 2>/dev/null)

for round in $(seq 1 "$MAX_ROUNDS"); do
    log=$(mktemp)
    echo "[repair] === 第 $round 轮 sync (-j$JOBS) ==="
    repo sync -c -j"$JOBS" --force-sync --force-checkout --no-clone-bundle \
        --no-tags --optimized-fetch --prune 2>&1 | tee "$log" | \
        grep -E 'GitCommandError|error: |fatal:' | grep -v 'bytes' | head -20
    rc=${PIPESTATUS[0]}
    broken=$(grep -oE "on [A-Za-z0-9_/.-]+ failed" "$log" | awk '{print $2}' | sort -u)
    rm -f "$log"
    if [ -z "$broken" ]; then
        if [ "$rc" -eq 0 ]; then
            echo "[repair] sync 完成，无损坏。"
            exit 0
        fi
        echo "[repair] sync 退出码 $rc 但无可识别的损坏仓库，人工检查。"
        exit "$rc"
    fi
    for name in $broken; do
        path="${NAME2PATH[$name]:-}"
        echo "[repair] 修复损坏仓库: $name (path=$path)"
        [ -n "$path" ] || { echo "[repair]   找不到 name->path 映射，跳过"; continue; }
        rm -rf "$path" ".repo/projects/$path.git"
        find .repo/project-objects -maxdepth 2 -type d -path "*${name}*.git" \
            -exec rm -rf {} + 2>/dev/null
    done
done

echo "[repair] 达到最大轮数仍有失败，人工检查。" >&2
exit 1
