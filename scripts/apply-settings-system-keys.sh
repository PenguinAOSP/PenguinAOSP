#!/usr/bin/env bash
# PenguinAOSP: Settings.System experiment key constants (B 类).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT/source}"
export SOURCE_DIR
exec python3 "$ROOT/vendor/penguin/patches/settings_system_keys.py" --source-dir "$SOURCE_DIR"
