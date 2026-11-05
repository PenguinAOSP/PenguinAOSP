#!/usr/bin/env python3
"""PenguinOS: wire EdgeLightingController into DozeServiceHost.

Adds import, field, ctor param/assignment, and pulse start/finish hooks.
Idempotent via MARKER.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARKER = "// PenguinOS: edgelighting-doze"


def fail(msg: str) -> int:
    print(f"[edgelighting-doze] error: {msg}", file=sys.stderr)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", default=None)
    args = ap.parse_args()
    root = Path(args.source_dir or __import__("os").environ.get("SOURCE_DIR", "source"))
    target = (
        root
        / "frameworks"
        / "base"
        / "packages"
        / "SystemUI"
        / "src"
        / "com"
        / "android"
        / "systemui"
        / "statusbar"
        / "phone"
        / "DozeServiceHost.java"
    )
    if not target.is_file():
        return fail(f"missing {target}")

    text = target.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"[edgelighting-doze] skip (already applied): {target}")
        return 0

    # 1) import
    import_anchor = "import com.android.systemui.doze.DozeReceiver;"
    import_insert = (
        "import com.android.systemui.doze.DozeReceiver;\n"
        f"import com.android.systemui.edgelighting.EdgeLightingController; {MARKER}"
    )
    if import_anchor not in text:
        return fail("import anchor DozeReceiver not found")
    text = text.replace(import_anchor, import_insert, 1)

    # 2) field after SelectedUserInteractor
    field_anchor = "    private final SelectedUserInteractor mSelectedUserInteractor;\n\n    @Inject"
    field_insert = (
        "    private final SelectedUserInteractor mSelectedUserInteractor;\n"
        f"    private final EdgeLightingController mEdgeLightingController; {MARKER}\n\n"
        "    @Inject"
    )
    if field_anchor not in text:
        return fail("field anchor mSelectedUserInteractor not found")
    text = text.replace(field_anchor, field_insert, 1)

    # 3) ctor param + assignment
    ctor_anchor = (
        "            AodDimInteractor aodDimInteractor,\n"
        "            SelectedUserInteractor selectedUserInteractor) {"
    )
    ctor_insert = (
        "            AodDimInteractor aodDimInteractor,\n"
        "            SelectedUserInteractor selectedUserInteractor,\n"
        f"            EdgeLightingController edgeLightingController) {{ {MARKER}"
    )
    if ctor_anchor not in text:
        return fail("ctor signature anchor not found")
    text = text.replace(ctor_anchor, ctor_insert, 1)

    assign_anchor = "        mSelectedUserInteractor = selectedUserInteractor;\n    }"
    assign_insert = (
        "        mSelectedUserInteractor = selectedUserInteractor;\n"
        f"        mEdgeLightingController = edgeLightingController; {MARKER}\n"
        "    }"
    )
    if assign_anchor not in text:
        return fail("ctor assignment anchor not found")
    text = text.replace(assign_anchor, assign_insert, 1)

    # 4) pulse started hook
    pulse_start_anchor = (
        "                setPulsing(true);\n"
        "            }\n\n"
        "            @Override\n"
        "            public void onPulseFinished() {"
    )
    pulse_start_insert = (
        "                setPulsing(true);\n"
        f"                if (reason == DozeLog.PULSE_REASON_NOTIFICATION) {{ {MARKER}\n"
        "                    mEdgeLightingController.onNotificationPulseStarted(\n"
        "                            mHeadsUpManager.getTopEntry());\n"
        "                }\n"
        "            }\n\n"
        "            @Override\n"
        "            public void onPulseFinished() {"
    )
    if pulse_start_anchor not in text:
        return fail("onPulseStarted setPulsing(true) anchor not found")
    text = text.replace(pulse_start_anchor, pulse_start_insert, 1)

    # 5) pulse finished hook
    pulse_finish_anchor = (
        "            public void onPulseFinished() {\n"
        "                mPulsing = false;\n"
        "                callback.onPulseFinished();"
    )
    pulse_finish_insert = (
        "            public void onPulseFinished() {\n"
        "                mPulsing = false;\n"
        f"                mEdgeLightingController.onPulseFinished(); {MARKER}\n"
        "                callback.onPulseFinished();"
    )
    if pulse_finish_anchor not in text:
        return fail("onPulseFinished anchor not found")
    text = text.replace(pulse_finish_anchor, pulse_finish_insert, 1)

    target.write_text(text, encoding="utf-8")
    print(f"[edgelighting-doze] applied: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
