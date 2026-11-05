#!/usr/bin/env bash
# Clang -Werror -Wsometimes-uninitialized: name is used if sel is outside
# BRAKE_CAL_SCALAR / CLAMPED_DUTY_CYCLE_STS / FIFO_REAL_TIME_STS.
# Voltage 0002 used name = "UNKNOWN". Keep the driver; do not drop Werror.
#
# PenguinOS: hooked as PENGUIN_HV_HAPTICS (M1 kernel -Werror).
# Target is kernel/nubia/sm8650 (local_manifest), not devices/ truth source.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE="${SOURCE_DIR:-$ROOT/source}"
f="$SOURCE/kernel/nubia/sm8650/drivers/input/misc/qcom-hv-haptics.c"
[[ -f "$f" ]] || { echo "[hv-haptics] skip missing $f"; exit 0; }
if grep -q 'const char \*name = "UNKNOWN"' "$f"; then
  echo "[hv-haptics] already patched"
  exit 0
fi
python3 - "$f" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
text = p.read_text(encoding="utf-8")
old = "\tconst char *name;\n"
new = '\tconst char *name = "UNKNOWN"; /* PenguinOS: hv-haptics clang -Wsometimes-uninitialized */\n'
if old not in text:
    # also try spaces-only indent variants
    sys.exit(f"[hv-haptics] declaration not found in {p}")
p.write_text(text.replace(old, new, 1), encoding="utf-8")
print("[hv-haptics] patched", p)
PY
