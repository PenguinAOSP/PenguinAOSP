#!/usr/bin/env bash
# PenguinAOSP: pull Git LFS blobs in nubia vendor trees (radio images, etc.).
# Needed after repo sync: without this, radio/*.img are 131B pointers and kati
# fails SHA1 checks (see docs/TROUBLESHOOTING.md).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="${SOURCE_DIR:-$ROOT/source}"

# Optional proxy: only if USE_PROXY=1 and the port is up (default: direct —
# nubia LFS host lfs.undocumented.software is often reachable without proxy).
if [[ "${USE_PROXY:-0}" == "1" ]]; then
    # shellcheck disable=SC1091
    source "$ROOT/scripts/proxy-env.sh" 2>/dev/null || true
fi

if ! command -v git-lfs >/dev/null 2>&1; then
    echo "[vendor-lfs] error: git-lfs not installed (pacman -S git-lfs)" >&2
    exit 1
fi

# Ensure we are not stuck on filter.lfs.smudge --skip from a prior install.
export GIT_LFS_SKIP_SMUDGE=0

pulled=0
# nubia radio images + PixelOS GMS prebuilts (UwU ships vendor/pixel/gms with LFS)
for tree in vendor/nubia/cerro vendor/nubia/sm8650-common vendor/pixel/gms; do
    dir="$SOURCE/$tree"
    # repo uses .git -> .repo/projects/... symlink; -e covers file/dir/symlink
    if [[ ! -e "$dir/.git" ]]; then
        echo "[vendor-lfs] skip missing $tree"
        continue
    fi
    echo "[vendor-lfs] git lfs pull in $tree"
    # Re-enable smudge so pull materializes blobs into the worktree.
    git -C "$dir" config --local filter.lfs.smudge "git-lfs smudge -- %f" || true
    git -C "$dir" config --local filter.lfs.process "git-lfs filter-process" || true
    if ! git -C "$dir" lfs pull; then
        echo "[vendor-lfs] error: lfs pull failed in $tree" >&2
        exit 1
    fi
    pulled=1
done
if [[ "$pulled" -eq 0 ]]; then
    echo "[vendor-lfs] no vendor git trees found" >&2
    exit 1
fi

# quick sanity: cerro aop.img must not be an LFS pointer
AOP="$SOURCE/vendor/nubia/cerro/radio/aop.img"
if [[ -f "$AOP" ]] && head -1 "$AOP" | grep -q 'git-lfs'; then
    echo "[vendor-lfs] error: $AOP still an LFS pointer after pull" >&2
    exit 1
fi
if [[ -f "$AOP" ]]; then
    echo "[vendor-lfs] aop.img sha1=$(sha1sum "$AOP" | awk '{print $1}') size=$(stat -c%s "$AOP")"
fi
echo "[vendor-lfs] done"
