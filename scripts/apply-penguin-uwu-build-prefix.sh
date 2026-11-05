#!/usr/bin/env bash
# PenguinAOSP: let penguin_* lunch targets set UWU_BUILD (BoardConfigUwU gate).
# 开关: PENGUIN_UWU_BUILD_PREFIX
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"
export SOURCE_DIR

exec python3 "$ROOT/vendor/penguin/patches/build_make_penguin_uwu_build.py" \
    --source-dir "$SOURCE_DIR"
