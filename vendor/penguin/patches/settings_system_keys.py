#!/usr/bin/env python3
"""PenguinOS: add Settings.System constants for Laboratory experiments.

Keys: LS_MEDIA_EXPAND/EXPANDED/MOTION_ART, BACK_TO_APP_INDICATOR.
Uses @SuppressLint for metalava UnflaggedApi/NoSettingsProvider.
Idempotent via MARKER.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MARKER = "// PenguinOS: settings-system-keys"
SUP = '@SuppressLint({"UnflaggedApi", "NoSettingsProvider"})'

ANCHOR = """        public static final String AUTO_LAUNCH_MEDIA_CONTROLS = "auto_launch_media_controls";

        // Settings moved to Settings.Secure"""

INSERT = f"""        public static final String AUTO_LAUNCH_MEDIA_CONTROLS = "auto_launch_media_controls";

        {MARKER}
        /**
         * Whether lockscreen media controls can expand. Written by PenguinLaboratory.
         * @hide
         */
        {SUP}
        public static final String LS_MEDIA_EXPAND = "ls_media_expand";

        /**
         * Whether lockscreen media controls are currently expanded.
         * @hide
         */
        {SUP}
        public static final String LS_MEDIA_EXPANDED = "ls_media_expanded";

        /**
         * Whether lockscreen media uses motion art. Written by PenguinLaboratory.
         * @hide
         */
        {SUP}
        public static final String LS_MEDIA_MOTION_ART = "ls_media_motion_art";

        /**
         * Whether the status-bar back-to-previous-app indicator is enabled.
         * @hide
         */
        {SUP}
        public static final String BACK_TO_APP_INDICATOR = "back_to_app_indicator";

        // Settings moved to Settings.Secure"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", default=None)
    args = ap.parse_args()
    root = Path(args.source_dir or __import__("os").environ.get("SOURCE_DIR", "source"))
    target = root / "frameworks" / "base" / "core" / "java" / "android" / "provider" / "Settings.java"
    if not target.is_file():
        print(f"[settings-keys] error: missing {target}", file=sys.stderr)
        return 1

    text = target.read_text(encoding="utf-8")
    if MARKER in text:
        chunk = text.split(MARKER, 1)[1][:1500]
        if SUP not in chunk:
            pattern = (
                r"\n        // PenguinOS: settings-system-keys\n"
                r".*?"
                r"public static final String BACK_TO_APP_INDICATOR = \"back_to_app_indicator\";\n"
                r"\n        // Settings moved to Settings.Secure"
            )
            replacement = (
                "\n"
                + INSERT.split("AUTO_LAUNCH_MEDIA_CONTROLS", 1)[1].lstrip()
            )
            # Use INSERT from MARKER onward
            mid = INSERT.split(MARKER, 1)[1]
            replacement = (
                f"\n        {MARKER}"
                + mid
            )
            new_text, n = re.subn(pattern, replacement, text, count=1, flags=re.S)
            if n != 1:
                print("[settings-keys] error: could not refresh SuppressLint", file=sys.stderr)
                return 1
            target.write_text(new_text, encoding="utf-8")
            print(f"[settings-keys] refreshed SuppressLint: {target}")
            return 0
        print(f"[settings-keys] skip (already applied): {target}")
        return 0
    if ANCHOR not in text:
        print(
            "[settings-keys] error: anchor not found in Settings.java "
            "(AUTO_LAUNCH_MEDIA_CONTROLS / Settings moved block drifted)",
            file=sys.stderr,
        )
        return 1

    target.write_text(text.replace(ANCHOR, INSERT, 1), encoding="utf-8")
    print(f"[settings-keys] applied: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
