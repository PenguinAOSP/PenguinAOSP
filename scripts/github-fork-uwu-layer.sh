#!/usr/bin/env bash
# Fork UwUAOSP ROM-layer repos into github.com/PenguinAOSP (for penguin manifest).
# Usage:
#   GITHUB_TOKEN=ghp_xxx bash scripts/github-fork-uwu-layer.sh
#   bash scripts/github-fork-uwu-layer.sh --dry-run
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIST="${FORK_LIST:-$ROOT/meta/platform_vendor_penguin-versions/tools/uwu-layer-forks.txt}"
ORG="${PENGUIN_GITHUB_ORG:-PenguinAOSP}"
TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-${TOKEN:-}}}"
DRY=0
[[ "${1:-}" == "--dry-run" ]] && DRY=1
CURL="${CURL_BIN:-/usr/bin/curl}"

if [[ -z "$TOKEN" && "$DRY" -eq 0 ]]; then
  echo "[fork] need GITHUB_TOKEN (or GH_TOKEN)" >&2
  exit 2
fi
[[ -f "$LIST" ]] || { echo "[fork] missing $LIST" >&2; exit 2; }

if [[ -f "$ROOT/scripts/proxy-env.sh" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT/scripts/proxy-env.sh" || true
fi
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:${HOME}/.local/bin:${PATH:-}"

API=https://api.github.com

fork_one() {
  local src="$1" name="$2"
  local owner="${src%%/*}"
  local repo="${src#*/}"
  local code body
  if [[ "$DRY" -eq 1 ]]; then
    echo "[dry] fork $owner/$repo -> $ORG/$name"
    return 0
  fi

  code="$("$CURL" -sS -o /tmp/gh-fork-check.json -w "%{http_code}" --max-time 60 \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    "${API}/repos/${ORG}/${name}" || echo 000)"
  if [[ "$code" == "200" ]]; then
    echo "[skip] exists ${ORG}/${name}"
    return 0
  fi

  echo "[fork] ${owner}/${repo} -> ${ORG}/${name} ..."
  body=$(printf '{"organization":"%s","name":"%s","default_branch_only":false}' "$ORG" "$name")
  code="$("$CURL" -sS -o /tmp/gh-fork.json -w "%{http_code}" --max-time 120 -X POST \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -H "Content-Type: application/json" \
    "${API}/repos/${owner}/${repo}/forks" \
    --data-binary "$body" || echo 000)"

  if [[ "$code" == "202" || "$code" == "201" ]]; then
    echo "[ok] ${code} ${ORG}/${name}"
    sleep 2
    return 0
  fi
  echo "[err] ${code} ${owner}/${repo}: $(head -c 300 /tmp/gh-fork.json 2>/dev/null)" >&2
  sleep 2
  return 1
}

ok=0
fail=0
while IFS=$'\t' read -r src name path || [[ -n "${src:-}" ]]; do
  [[ -z "${src:-}" || "$src" =~ ^# ]] && continue
  if fork_one "$src" "$name"; then
    ok=$((ok + 1))
  else
    fail=$((fail + 1))
  fi
done < "$LIST"

echo "[fork] done ok=${ok} fail=${fail} dry=${DRY}"
exit 0
