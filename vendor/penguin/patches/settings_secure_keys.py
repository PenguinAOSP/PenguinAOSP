#!/usr/bin/env python3
"""PenguinOS: add Settings.Secure constants for Laboratory styles/glass/dex/experiments.

Proper multi-line @hide + @SuppressLint UnflaggedApi/NoSettingsProvider.
Does not redeclare upstream MIRROR_BUILT_IN_DISPLAY.
Idempotent via MARKER; refreshes block if @hide format is wrong.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MARKER = "// PenguinOS: settings-secure-keys"
SUP = '@SuppressLint({"UnflaggedApi", "NoSettingsProvider"})'

INSERT_BLOCK = f"""
        {MARKER}
        /**
         * Power menu visual style. Written by PenguinLaboratory.
         * @hide
         */
        {SUP}
        public static final String POWER_MENU_STYLE = "power_menu_style";

        /**
         * QS panel visual style. Written by PenguinLaboratory.
         * @hide
         */
        {SUP}
        public static final String QS_PANEL_STYLE = "qs_panel_style";

        /**
         * Volume panel visual style. Written by PenguinLaboratory.
         * @hide
         */
        {SUP}
        public static final String VOLUME_PANEL_STYLE = "volume_panel_style";

        /**
         * QS connectivity folder. Written by PenguinLaboratory.
         * @hide
         */
        {SUP}
        public static final String QS_CONNECTIVITY_FOLDER = "qs_connectivity_folder";

        /**
         * OneUI-style QS experimental. Written by PenguinLaboratory.
         * @hide
         */
        {SUP}
        public static final String QS_ONEUI_EXPERIMENTAL = "qs_oneui_experimental";

        /**
         * Depth wallpaper floating clock. Written by PenguinLaboratory.
         * @hide
         */
        {SUP}
        public static final String DEPTH_WALLPAPER_FLOATING = "depth_wallpaper_floating";

        /**
         * Frequently used apps row in recents. Written by PenguinLaboratory.
         * @hide
         */
        {SUP}
        public static final String RECENTS_FREQUENT_APPS = "recents_frequent_apps";

        /**
         * Liquid glass master switch. Written by PenguinLaboratory.
         * @hide
         */
        {SUP}
        public static final String PENGUIN_LIQUID_GLASS = "penguin_liquid_glass";

        /**
         * Glass tab bars. Written by PenguinLaboratory.
         * @hide
         */
        {SUP}
        public static final String PENGUIN_GLASS_TAB_BARS = "penguin_glass_tab_bars";

        /**
         * @hide
         */
        {SUP}
        public static final String PENGUIN_GLASS_TAB_BARS_EXCLUDED = "penguin_glass_tab_bars_excluded";

        /**
         * @hide
         */
        {SUP}
        public static final String PENGUIN_GLASS_TAB_BARS_FLOAT = "penguin_glass_tab_bars_float";

        /**
         * PenguinDex dock. Written by PenguinLaboratory.
         * @hide
         */
        {SUP}
        public static final String PENGUIN_DEX_DOCK = "penguin_dex_dock";

        /**
         * @hide
         */
        {SUP}
        public static final String PENGUIN_DEX_LAUNCHPAD = "penguin_dex_launchpad";

        /**
         * @hide
         */
        {SUP}
        public static final String PENGUIN_DEX_TOUCHPAD = "penguin_dex_touchpad";

        /**
         * @hide
         */
        {SUP}
        public static final String PENGUIN_DEX_CONTROL_CENTRE = "penguin_dex_control_centre";
"""

BLOCK_RE = re.compile(
    r"\n        // PenguinOS: settings-secure-keys\n"
    r".*?"
    r'public static final String PENGUIN_DEX_CONTROL_CENTRE = "penguin_dex_control_centre";\n',
    re.S,
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", default=None)
    args = ap.parse_args()
    root = Path(args.source_dir or __import__("os").environ.get("SOURCE_DIR", "source"))
    target = root / "frameworks" / "base" / "core" / "java" / "android" / "provider" / "Settings.java"
    if not target.is_file():
        print(f"[secure-keys] error: missing {target}", file=sys.stderr)
        return 1

    text = target.read_text(encoding="utf-8")
    if MARKER in text:
        # Refresh if inline @hide (broken for metalava) still present
        after = text.split(MARKER, 1)[1][:400]
        if "Written by PenguinLaboratory. @hide" in after or "* @hide\n" not in after[:800]:
            new_text, n = BLOCK_RE.subn("\n" + INSERT_BLOCK + "\n", text, count=1)
            if n != 1:
                print("[secure-keys] error: could not refresh block", file=sys.stderr)
                return 1
            target.write_text(new_text, encoding="utf-8")
            print(f"[secure-keys] refreshed @hide block: {target}")
            return 0
        print(f"[secure-keys] skip (already applied): {target}")
        return 0

    candidates = [
        '        public static final String USER_SETUP_COMPLETE = "user_setup_complete";\n',
        '        public static final String NAVIGATION_MODE = "navigation_mode";\n',
        '        public static final String ACCESSIBILITY_BUTTON_MODE = "accessibility_button_mode";\n',
    ]
    anchor = next((c for c in candidates if c in text), None)
    if anchor is None:
        print("[secure-keys] error: no Secure insertion anchor found", file=sys.stderr)
        return 1

    target.write_text(text.replace(anchor, anchor + INSERT_BLOCK, 1), encoding="utf-8")
    print(f"[secure-keys] applied: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
