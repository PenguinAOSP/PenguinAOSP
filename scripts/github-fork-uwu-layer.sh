#!/usr/bin/env bash
# Fork UwUAOSP ROM-layer repos into github.com/PenguinAOSP (for penguin manifest).
# Usage:
#   GITHUB_TOKEN=ghp_xxx bash scripts/github-fork-uwu-layer.sh
#   bash scripts/github-fork-uwu-layer.sh --dry-run
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIST="${FORK_LIST:-$ROOT/meta/platform_vendor_penguin-versions/tools/uwu-layer-forks.txt}"
ORG="${PENGUIN_GITHUB_ORG:-PenguinAOSP}"
TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-${TOKEN:-}}}"
DRY=0
[[ "${1:-}" == "--dry-run" ]] && DRY=1

if [[ -z "$TOKEN" && "$DRY" -eq 0 ]]; then
  echo "[fork] need GITHUB_TOKEN (or GH_TOKEN)" >&2
  exit 2
fi
[[ -f "$LIST" ]] || { echo "[fork] missing $LIST" >&2; exit 2; }

source "$ROOT/scripts/proxy-env.sh" 2>/dev/null || true
API=https://api.github.com
AUTH=("Authorization: Bearer $TOKEN" "Accept: application/vnd.github+json" "User-Agent: PenguinAOSP-fork")

fork_one() {
  local src="$1" name="$2"
  local owner="${src%%/*}"
  local repo="${src#*/}"
  if [[ "$DRY" -eq 1 ]]; then
    echo "[dry] fork $owner/$repo -> $ORG/$name"
    return 0
  fi
  # already exists?
  code=$(curl -sS -o /tmp/gh-fork-check.json -w '%{http_code}' \
    -H "${AUTH[0]}" -H "${AUTH[1]}" -H "${AUTH[2]}" \
    "$API/repos/$ORG/$name" || true)
  if [[ "$code" == "200" ]]; then
    echo "[skip] exists $ORG/$name"
    return 0
  fi
  echo "[fork] $owner/$repo -> $ORG ..."
  code=$(curl -sS -o /tmp/gh-fork.json -w '%{http_code}' -X POST \
    -H "${AUTH[0]}" -H "${AUTH[1]}" -H "${AUTH[2]}" \
    -H 'Content-Type: application/json' \
    "$API/repos/$owner/$repo/forks" \
    -d "{\"organization\":\"$ORG\",\"name\":\"$name\",\"default_branch_only\":false}")
  if [[ "$code" == "202" || "$code" == "201" ]]; then
    echo "[ok] $code $ORG/$name"
  else
    echo "[err] $code $owner/$repo: $(head -c 300 /tmp/gh-fork.json)" >&2
    return 1
  fi
  # gentle rate limit
  sleep 1
}

ok=0
fail=0
while IFS=$'\t' read -r src name path; do
  [[ -z "${src:-}" || "$src" =~ ^# ]] && continue
  if fork_one "$src" "$name"; then
    ok=$((ok+1))
  else
    fail=$((fail+1))
  fi
done < "$LIST"

echo "[fork] done ok=$ok fail=$fail dry=$DRY"
[[ "$fail" -eq 0 ]]
