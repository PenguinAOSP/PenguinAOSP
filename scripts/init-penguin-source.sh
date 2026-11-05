#!/usr/bin/env bash
# PenguinAOSP: repo init/sync using the org release manifest (normal AOSP workflow).
# Keeps patch scripts: after sync, run apply-all.sh from the meta repo.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${PENGUIN_SOURCE_DIR:-$ROOT/source}"
MANIFEST_URL="${PENGUIN_MANIFEST_URL:-https://github.com/PenguinAOSP/platform_vendor_penguin-versions.git}"
MANIFEST_BRANCH="${PENGUIN_MANIFEST_BRANCH:-main}"

source "$ROOT/scripts/proxy-env.sh"
case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) [ -x "$HOME/.local/bin/repo" ] && PATH="$HOME/.local/bin:$PATH" ;;
esac
command -v repo >/dev/null || { echo "[init-penguin] need repo launcher" >&2; exit 1; }

mkdir -p "$SRC"
cd "$SRC"

if [[ ! -d .repo/manifests ]]; then
  echo "[init-penguin] repo init -u $MANIFEST_URL -b $MANIFEST_BRANCH --git-lfs"
  repo init -u "$MANIFEST_URL" -b "$MANIFEST_BRANCH" --git-lfs
else
  echo "[init-penguin] .repo exists — re-init to penguin versions manifest"
  repo init -u "$MANIFEST_URL" -b "$MANIFEST_BRANCH" --git-lfs -m default.xml
fi

echo "[init-penguin] repo sync"
repo sync -c -j"${PENGUIN_SYNC_JOBS:-$(nproc --all)}" \
  --force-sync --force-checkout --no-clone-bundle --no-tags \
  --optimized-fetch --prune

echo "[init-penguin] sync done. Next: bash $ROOT/scripts/apply-all.sh"
echo "[init-penguin] then: bash $ROOT/scripts/build-cerro.sh va"
