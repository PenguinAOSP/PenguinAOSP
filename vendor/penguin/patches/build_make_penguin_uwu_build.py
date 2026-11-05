#!/usr/bin/env python3
"""PenguinOS: derive UWU_BUILD from penguin_* lunch targets.

UwUAOSP's build/make/core/config.mk only sets UWU_BUILD when TARGET_PRODUCT
matches uwu_*. PenguinAOSP lunch targets use penguin_* (e.g. penguin_cerro);
without UWU_BUILD, BoardConfigUwU.mk is skipped and QCOM WiFi Soong namespaces
(and other UwU board hooks) never apply.

Idempotent: skips when MARKER is already present.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARKER = "# PenguinOS: penguin_uwu_build_prefix"
ANCHOR = """ifeq ($(UWU_BUILD),)
ifneq ($(filter uwu_%,$(TARGET_PRODUCT)),)
UWU_BUILD := $(patsubst uwu_%,%,$(TARGET_PRODUCT))
endif
endif"""

INSERT = """ifeq ($(UWU_BUILD),)
ifneq ($(filter uwu_%,$(TARGET_PRODUCT)),)
UWU_BUILD := $(patsubst uwu_%,%,$(TARGET_PRODUCT))
endif
endif

""" + MARKER + """
ifeq ($(UWU_BUILD),)
ifneq ($(filter penguin_%,$(TARGET_PRODUCT)),)
UWU_BUILD := $(patsubst penguin_%,%,$(TARGET_PRODUCT))
endif
endif"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--source-dir",
        default=None,
        help="AOSP source root (default: $SOURCE_DIR or ./source)",
    )
    args = ap.parse_args()
    root = Path(args.source_dir or __import__("os").environ.get("SOURCE_DIR", "source"))
    target = root / "build" / "make" / "core" / "config.mk"
    if not target.is_file():
        print(f"[penguin-uwu-build] error: missing {target}", file=sys.stderr)
        return 1

    text = target.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"[penguin-uwu-build] skip (already applied): {target}")
        return 0
    if ANCHOR not in text:
        print(
            "[penguin-uwu-build] error: anchor not found in "
            f"{target} (uwu_% UWU_BUILD block drifted)",
            file=sys.stderr,
        )
        return 1

    target.write_text(text.replace(ANCHOR, INSERT, 1), encoding="utf-8")
    print(f"[penguin-uwu-build] applied: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
