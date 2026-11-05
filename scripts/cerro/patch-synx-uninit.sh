#!/usr/bin/env bash
# synx-kernel: clang -Werror uninitialized on error paths.
# Keep the driver; initialize pointers so IS_ERR_OR_NULL / kfree are defined.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE="${SOURCE_DIR:-$ROOT/source}"
python3 - "$SOURCE" <<'PY'
from pathlib import Path
import sys

source = Path(sys.argv[1])
changed = False

util = source / "kernel/nubia/sm8650-modules/qcom/opensource/synx-kernel/msm/synx/synx_util.c"
if util.is_file():
    t = util.read_text(encoding="utf-8")
    old = "\tstruct synx_entry_64 *entry, *curr;\n"
    new = '\tstruct synx_entry_64 *entry = NULL, *curr; /* PenguinOS: synx clang -Wuninitialized */\n'
    if "synx_entry_64 *entry = NULL, *curr" in t:
        print("[synx-uninit] synx_util.c already patched")
    elif old not in t:
        sys.exit(f"[synx-uninit] synx_util.c declaration not found")
    else:
        util.write_text(t.replace(old, new, 1), encoding="utf-8")
        print("[synx-uninit] patched", util)
        changed = True
else:
    print("[synx-uninit] skip missing", util)

synx = source / "kernel/nubia/sm8650-modules/qcom/opensource/synx-kernel/msm/synx/synx.c"
if synx.is_file():
    t = synx.read_text(encoding="utf-8")
    old = """\tstruct dma_fence **fences = NULL;
	struct synx_map_entry *map_entry;
	struct synx_coredata *synx_obj, *synx_obj_child;
"""
    new = """\tstruct dma_fence **fences = NULL;
	struct synx_map_entry *map_entry = NULL; /* PenguinOS: synx clang -Wsometimes-uninitialized */
	struct synx_coredata *synx_obj, *synx_obj_child;
"""
    if "map_entry = NULL; /* PenguinOS: synx" in t or "map_entry = NULL; /* RisingOS cerro" in t:
        print("[synx-uninit] synx.c already patched")
    elif old not in t:
        sys.exit(f"[synx-uninit] synx.c synx_merge declaration not found")
    else:
        synx.write_text(t.replace(old, new, 1), encoding="utf-8")
        print("[synx-uninit] patched", synx)
        changed = True
else:
    print("[synx-uninit] skip missing", synx)
PY
