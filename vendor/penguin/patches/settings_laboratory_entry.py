#!/usr/bin/env python3
"""PenguinOS: Settings → System entry that opens PenguinLaboratory.

Patches system_dashboard_fragment.xml and adds penguin_strings.xml.
Idempotent via MARKER / existing string file.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARKER = "<!-- PenguinOS: laboratory-settings-entry -->"
PREF = f"""
    {MARKER}
    <Preference
        android:key="penguin_laboratory"
        android:title="@string/penguin_laboratory_title"
        android:summary="@string/penguin_laboratory_summary"
        android:icon="@drawable/ic_settings_development"
        android:order="89">
        <intent
            android:targetPackage="com.penguin.laboratory"
            android:targetClass="com.penguin.laboratory.LaboratoryActivity" />
    </Preference>
"""

STRINGS_EN = """<?xml version="1.0" encoding="utf-8"?>
<!-- PenguinOS: laboratory-settings-entry -->
<resources>
    <string name="penguin_laboratory_title">Penguin Laboratory</string>
    <string name="penguin_laboratory_summary">Styles, experiments, edge lighting and more</string>
</resources>
"""

STRINGS_ZH = """<?xml version="1.0" encoding="utf-8"?>
<!-- PenguinOS: laboratory-settings-entry -->
<resources>
    <string name="penguin_laboratory_title">Penguin 实验室</string>
    <string name="penguin_laboratory_summary">样式、实验、边缘发光等</string>
</resources>
"""

NEEDLE = """        <Preference
            android:key="reset_dashboard"
            android:title="@string/reset_dashboard_title"
            android:icon="@drawable/ic_restore"
            android:fragment="com.android.settings.system.ResetDashboardFragment"
            settings:controller="com.android.settings.system.ResetPreferenceController"/>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", default=None)
    args = ap.parse_args()
    root = Path(args.source_dir or __import__("os").environ.get("SOURCE_DIR", "source"))
    settings = root / "packages" / "apps" / "Settings"
    xml = settings / "res" / "xml" / "system_dashboard_fragment.xml"
    values = settings / "res" / "values" / "penguin_strings.xml"
    values_zh = settings / "res" / "values-zh-rCN" / "penguin_strings.xml"

    if not xml.is_file():
        print(f"[lab-entry] error: missing {xml}", file=sys.stderr)
        return 1

    text = xml.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"[lab-entry] skip xml (already applied): {xml}")
    else:
        if NEEDLE not in text:
            print(
                "[lab-entry] error: reset_dashboard preference drifted in "
                "system_dashboard_fragment.xml",
                file=sys.stderr,
            )
            return 1
        xml.write_text(text.replace(NEEDLE, NEEDLE + PREF, 1), encoding="utf-8")
        print(f"[lab-entry] applied: {xml}")

    if values.is_file() and "penguin_laboratory_title" in values.read_text(encoding="utf-8"):
        print(f"[lab-entry] skip strings (already applied): {values}")
    else:
        values.parent.mkdir(parents=True, exist_ok=True)
        values.write_text(STRINGS_EN, encoding="utf-8")
        print(f"[lab-entry] wrote: {values}")

    values_zh.parent.mkdir(parents=True, exist_ok=True)
    if values_zh.is_file() and "penguin_laboratory_title" in values_zh.read_text(encoding="utf-8"):
        print(f"[lab-entry] skip zh strings (already applied): {values_zh}")
    else:
        values_zh.write_text(STRINGS_ZH, encoding="utf-8")
        print(f"[lab-entry] wrote: {values_zh}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
