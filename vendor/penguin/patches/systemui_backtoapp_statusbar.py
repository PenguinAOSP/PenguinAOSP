#!/usr/bin/env python3
"""PenguinOS: wire BackToApp under the status-bar clock in StatusBarRoot.

Inserts stackBackToAppUnderClock helper + call + import.
Idempotent via MARKER.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARKER = "// PenguinOS: backtoapp-statusbar"

IMPORT_ANCHOR = "import com.android.systemui.statusbar.phone.PhoneStatusBarView"
IMPORT_LINE = (
    "import com.android.systemui.statusbar.backtoapp.BackToAppLabel "
    f"{MARKER}\n"
    "import com.android.systemui.statusbar.phone.PhoneStatusBarView"
)

CALL_ANCHOR = """    val clockView = phoneStatusBarView.requireViewById<Clock>(R.id.clock)

    val composeView =
        ComposeView(context).apply {
            val showDate = Flags.statusBarDate() && statusBarViewModel.useDesktopStatusBar"""

CALL_INSERT = """    val clockView = phoneStatusBarView.requireViewById<Clock>(R.id.clock)
    stackBackToAppUnderClock(clockView, statusBarViewModel, context) """ + MARKER + """

    val composeView =
        ComposeView(context).apply {
            val showDate = Flags.statusBarDate() && statusBarViewModel.useDesktopStatusBar"""

HELPER = '''
/** PenguinOS: stack back-to-app label under the legacy clock view. ''' + MARKER + ''' */
private fun stackBackToAppUnderClock(
    clockView: Clock,
    statusBarViewModel: HomeStatusBarViewModel,
    context: Context,
) {
    val parent = clockView.parent as? ViewGroup ?: return
    val index = parent.indexOfChild(clockView)
    val clockParams = clockView.layoutParams
    val column =
        LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            gravity = android.view.Gravity.CENTER_VERTICAL or android.view.Gravity.START
            clipChildren = false
            layoutParams =
                LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.MATCH_PARENT,
                )
        }
    parent.removeViewAt(index)
    parent.addView(column, index)
    clockView.minHeight = 0
    clockView.minimumHeight = 0
    clockView.includeFontPadding = false
    column.addView(
        clockView,
        LinearLayout.LayoutParams(clockParams.width, LinearLayout.LayoutParams.WRAP_CONTENT),
    )
    val labelStart = clockView.paddingStart / context.resources.displayMetrics.density
    column.addView(
        ComposeView(context).apply {
            setContent {
                WithAdaptiveTint(
                    isDarkProvider = { bounds -> statusBarViewModel.areaDark.isDarkTheme(bounds) }
                ) { tint ->
                    BackToAppLabel(tint = tint, startPadding = labelStart.dp)
                }
            }
        },
        LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.WRAP_CONTENT,
            LinearLayout.LayoutParams.WRAP_CONTENT,
        ),
    )
}
'''


def fail(msg: str) -> int:
    print(f"[backtoapp-sb] error: {msg}", file=sys.stderr)
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
        / "pipeline"
        / "shared"
        / "ui"
        / "composable"
        / "StatusBarRoot.kt"
    )
    if not target.is_file():
        return fail(f"missing {target}")

    text = target.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"[backtoapp-sb] skip (already applied): {target}")
        return 0

    if IMPORT_ANCHOR not in text:
        return fail("PhoneStatusBarView import not found")
    text = text.replace(IMPORT_ANCHOR, IMPORT_LINE, 1)

    if CALL_ANCHOR not in text:
        return fail("addStartSideComposable clockView anchor not found")
    text = text.replace(CALL_ANCHOR, CALL_INSERT, 1)

    # Append helper before end of file (after last function). Insert after
    # addStartSideComposable's opening comment block's preceding function end.
    # Put helper right before addStartSideComposable definition.
    fn_anchor = "/** Adds the composable chips shown on the start side of the status bar. */\nprivate fun addStartSideComposable("
    if fn_anchor not in text:
        return fail("addStartSideComposable doc comment not found")
    text = text.replace(fn_anchor, HELPER + "\n" + fn_anchor, 1)

    # Ensure ViewGroup import if missing
    if "import android.view.ViewGroup" not in text:
        if "import android.view.View\n" in text:
            text = text.replace(
                "import android.view.View\n",
                "import android.view.View\nimport android.view.ViewGroup\n",
                1,
            )
        else:
            return fail("android.view.View import not found (needed for ViewGroup)")

    target.write_text(text, encoding="utf-8")
    print(f"[backtoapp-sb] applied: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
