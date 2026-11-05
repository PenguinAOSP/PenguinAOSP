#!/usr/bin/env python3
"""PenguinOS: wire LiquidTabBars into ViewRootImpl (framework). Idempotent via MARKER."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARKER = "// PenguinOS: liquid-glass"


def fail(msg: str) -> int:
    print(f"[liquid-glass] error: {msg}", file=sys.stderr)
    return 1


def patch(text: str) -> str:
    if MARKER in text:
        return text

    # Field + create in setView (application windows)
    # Anchor: start of setView(View, LayoutParams, View, int)
    a = (
        "    public void setView(View view, WindowManager.LayoutParams attrs, View panelParentView,\n"
        "            int userId) {\n"
        "        checkThreadCompat();\n"
        "        synchronized (this) {\n"
        "            if (mView == null) {\n"
        "                mView = view;\n"
    )
    if a not in text:
        raise RuntimeError("setView(userId) anchor not found")
    text = text.replace(
        a,
        "    private com.android.internal.penguin.glass.LiquidTabBars mLiquidTabBars; "
        + MARKER
        + "\n\n"
        + a
        + "                if (attrs.type >= WindowManager.LayoutParams.FIRST_APPLICATION_WINDOW\n"
        "                        && attrs.type <= WindowManager.LayoutParams.LAST_APPLICATION_WINDOW) {\n"
        "                    mLiquidTabBars =\n"
        "                            com.android.internal.penguin.glass.LiquidTabBars.create(mContext);\n"
        "                }\n",
        1,
    )

    # onLayout after performLayout
    b = (
        "        if (didLayout) {\n"
        "            performLayout(lp, mWidth, mHeight);\n"
    )
    if b not in text:
        raise RuntimeError("performLayout anchor not found")
    text = text.replace(
        b,
        "        if (didLayout) {\n"
        "            performLayout(lp, mWidth, mHeight);\n"
        f"            if (mLiquidTabBars != null) {{ {MARKER}\n"
        "                mLiquidTabBars.onLayout(host);\n"
        "            }\n",
        1,
    )

    # Touch intercept before dispatchPointerEvent (UwU may have handwriting comment)
    c = (
        "            mAttachInfo.mHandlingPointerEvent = true;\n"
        "            // If the event was fully handled by the handwriting initiator, then don't dispatch it\n"
        "            // to the view tree.\n"
        "            handled = handled || mView.dispatchPointerEvent(event);\n"
    )
    c_alt = (
        "            mAttachInfo.mHandlingPointerEvent = true;\n"
        "            handled = mView.dispatchPointerEvent(event);\n"
    )
    insert = (
        "            mAttachInfo.mHandlingPointerEvent = true;\n"
        f"            if (mLiquidTabBars != null && event.isFromSource(InputDevice.SOURCE_TOUCHSCREEN)\n"
        f"                    && mLiquidTabBars.onTouch(event)) {{ {MARKER}\n"
        "                event.setAction(MotionEvent.ACTION_CANCEL);\n"
        "            }\n"
    )
    if c in text:
        text = text.replace(
            c,
            insert
            + "            // If the event was fully handled by the handwriting initiator, then don't dispatch it\n"
            "            // to the view tree.\n"
            "            handled = handled || mView.dispatchPointerEvent(event);\n",
            1,
        )
    elif c_alt in text:
        text = text.replace(
            c_alt,
            insert + "            handled = mView.dispatchPointerEvent(event);\n",
            1,
        )
    else:
        raise RuntimeError("dispatchPointerEvent anchor not found")
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", default=None)
    args = ap.parse_args()
    root = Path(args.source_dir or __import__("os").environ.get("SOURCE_DIR", "source"))
    path = root / "frameworks/base/core/java/android/view/ViewRootImpl.java"
    if not path.is_file():
        return fail(f"missing {path}")
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print("[liquid-glass] skip ViewRootImpl")
        return 0
    try:
        new = patch(text)
    except RuntimeError as e:
        return fail(str(e))
    path.write_text(new, encoding="utf-8")
    print(f"[liquid-glass] applied: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
