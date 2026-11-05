#!/usr/bin/env python3
"""PenguinOS: Recents MemInfoView wiring into UwU Launcher3.

Idempotent via MARKER. Copies are handled by apply-launcher-meminfo.sh.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARKER = "// PenguinOS: launcher-meminfo"


def fail(msg: str) -> int:
    print(f"[launcher-meminfo] error: {msg}", file=sys.stderr)
    return 1


def ensure_import(text: str, import_line: str, anchors: tuple[str, ...]) -> str:
    if import_line in text:
        return text
    for a in anchors:
        if a in text:
            return text.replace(a, a + import_line + "\n", 1)
    raise RuntimeError(f"import anchor not found for {import_line}")


def patch_overview_panel(text: str) -> str:
    if "layout/meminfo" in text and MARKER in text:
        return text
    needle = (
        '    <include\n'
        '        android:id="@+id/empty_recents_message_view"\n'
        '        layout="@layout/overview_empty_recents_message"\n'
        '        android:visibility="gone"/>\n'
        "\n"
        "</merge>"
    )
    insert = (
        '    <include\n'
        '        android:id="@+id/empty_recents_message_view"\n'
        '        layout="@layout/overview_empty_recents_message"\n'
        '        android:visibility="gone"/>\n'
        "\n"
        f"    <!-- {MARKER} -->\n"
        "    <include\n"
        '        layout="@layout/meminfo" />\n'
        "\n"
        "</merge>"
    )
    if needle not in text:
        raise RuntimeError("overview_panel.xml anchor not found")
    return text.replace(needle, insert, 1)


def patch_launcher_prefs(text: str) -> str:
    if "RECENTS_MEMINFO" in text and MARKER in text:
        return text
    # Insert near other custom prefs — after ICON_PACK_PACKAGE if present
    anchor = '        val ICON_PACK_PACKAGE = backedUpItem("pref_icon_pack_package", "")\n'
    if anchor not in text:
        # fallback: end of companion object before closing
        raise RuntimeError("LauncherPrefs ICON_PACK_PACKAGE anchor not found")
    insert = (
        anchor
        + f"\n        {MARKER}\n"
        + '        @JvmField val RECENTS_MEMINFO = backedUpItem("pref_recents_meminfo", false)\n'
        + '        @JvmField val RECENTS_MEMINFO_ZRAM = backedUpItem("pref_recents_meminfo_zram", false)\n'
    )
    return text.replace(anchor, insert, 1)


def patch_device_profile(text: str) -> str:
    if "memInfoHeight" in text and MARKER in text:
        return text
    if "public int memInfoHeight;" not in text:
        fa = "    public int frequentAppsHeight;"
        if fa not in text:
            raise RuntimeError("DeviceProfile frequentAppsHeight field not found")
        text = text.replace(
            fa, fa + f"\n    public int memInfoHeight; {MARKER}", 1
        )
    # assignment near frequentAppsHeight
    old = (
        "        frequentAppsHeight = Settings.Secure.getInt(context.getContentResolver(), // PenguinOS: frequent-apps\n"
        '                "recents_frequent_apps", 0) == 1\n'
        "                ? res.getDimensionPixelSize(R.dimen.frequent_apps_claimed_height) : 0;\n"
    )
    if old not in text:
        raise RuntimeError("DeviceProfile frequentAppsHeight assignment not found")
    new = (
        old
        + f"        memInfoHeight = LauncherPrefs.RECENTS_MEMINFO.get(context) {MARKER}\n"
        + "                ? res.getDimensionPixelSize(R.dimen.meminfo_claimed_height) : 0;\n"
    )
    text = text.replace(old, new, 1)
    # DeviceProfile is package com.android.launcher3 — same as LauncherPrefs; no import.
    # Add memInfoHeight into overview actions reserved space if frequentApps is there
    old_sum = "+ frequentAppsHeight); // PenguinOS: frequent-apps"
    if old_sum in text and "memInfoHeight" not in text[text.find(old_sum) - 80 : text.find(old_sum) + 80]:
        text = text.replace(
            old_sum,
            "+ frequentAppsHeight + memInfoHeight); // PenguinOS: frequent-apps + meminfo",
            1,
        )
    return text


def patch_recents_view_container(text: str) -> str:
    if "getMemInfoView" in text and MARKER in text:
        return text
    if "import com.android.quickstep.views.MemInfoView;" not in text:
        # same package — no import needed if in same package; RecentsViewContainer is in views
        pass
    if not text.rstrip().endswith("}"):
        raise RuntimeError("RecentsViewContainer unexpected ending")
    # insert before final closing brace
    idx = text.rfind("}")
    method = (
        f"\n    {MARKER}\n"
        "    MemInfoView getMemInfoView();\n"
    )
    return text[:idx] + method + text[idx:]


def patch_recents_view_init(text: str) -> str:
    if "MemInfoView memInfoView" in text and MARKER in text:
        return text
    # Same package — no import required for MemInfoView.
    if "private MemInfoView mMemInfoView;" not in text:
        for a in (
            "    private ViewGroup mEmptyRecentsMessageView;\n",
            "    @Nullable private ViewGroup mEmptyRecentsMessageView;\n",
        ):
            if a in text:
                text = text.replace(
                    a, a + f"    private MemInfoView mMemInfoView; {MARKER}\n", 1
                )
                break
        else:
            raise RuntimeError("RecentsView mEmptyRecentsMessageView field not found")

    old_sig = (
        "    public void init(OverviewActionsView actionsView, SplitSelectStateController splitController,\n"
        "            @Nullable DesktopRecentsTransitionController desktopRecentsTransitionController,\n"
        "            SurfaceTransactionApplier surfaceTransactionApplier,\n"
        "            @Nullable ViewGroup emptyRecentsMessageView) {"
    )
    new_sig = (
        "    public void init(OverviewActionsView actionsView, SplitSelectStateController splitController,\n"
        "            @Nullable DesktopRecentsTransitionController desktopRecentsTransitionController,\n"
        "            SurfaceTransactionApplier surfaceTransactionApplier,\n"
        "            @Nullable ViewGroup emptyRecentsMessageView,\n"
        f"            MemInfoView memInfoView) {{ {MARKER}"
    )
    if old_sig not in text:
        raise RuntimeError("RecentsView.init signature not found")
    text = text.replace(old_sig, new_sig, 1)

    if "mMemInfoView = memInfoView;" not in text:
        a = "        mEmptyRecentsMessageView = emptyRecentsMessageView;\n"
        if a not in text:
            raise RuntimeError("RecentsView init body assign anchor not found")
        text = text.replace(a, a + "        mMemInfoView = memInfoView;\n", 1)
    return text


def patch_launcher_recents_view(text: str) -> str:
    if "MemInfoView memInfoView" in text and MARKER in text:
        return text
    old = (
        "    public void init(OverviewActionsView actionsView,\n"
        "            SplitSelectStateController splitPlaceholderView,\n"
        "            @Nullable DesktopRecentsTransitionController desktopRecentsTransitionController,\n"
        "            SurfaceTransactionApplier surfaceTransactionApplier,\n"
        "            @Nullable ViewGroup emptyRecentsMessageView) {\n"
        "        super.init(actionsView, splitPlaceholderView, desktopRecentsTransitionController,\n"
        "                surfaceTransactionApplier, emptyRecentsMessageView);\n"
    )
    new = (
        "    public void init(OverviewActionsView actionsView,\n"
        "            SplitSelectStateController splitPlaceholderView,\n"
        "            @Nullable DesktopRecentsTransitionController desktopRecentsTransitionController,\n"
        "            SurfaceTransactionApplier surfaceTransactionApplier,\n"
        "            @Nullable ViewGroup emptyRecentsMessageView,\n"
        f"            MemInfoView memInfoView) {{ {MARKER}\n"
        "        super.init(actionsView, splitPlaceholderView, desktopRecentsTransitionController,\n"
        "                surfaceTransactionApplier, emptyRecentsMessageView, memInfoView);\n"
    )
    if old not in text:
        raise RuntimeError("LauncherRecentsView.init not found")
    return text.replace(old, new, 1)


def patch_fallback_recents_view(text: str) -> str:
    if "MemInfoView memInfoView" in text and MARKER in text and "import com.android.quickstep.views.MemInfoView" in text:
        return text
    if "import com.android.quickstep.views.MemInfoView" not in text:
        text = ensure_import(
            text,
            f"import com.android.quickstep.views.MemInfoView; {MARKER}",
            ("import com.android.quickstep.views.OverviewActionsView;\n",),
        )
    if "MemInfoView memInfoView" in text and MARKER in text:
        return text
    old = (
        "    public void init(OverviewActionsView actionsView, SplitSelectStateController splitController,\n"
        "            @Nullable DesktopRecentsTransitionController desktopRecentsTransitionController,\n"
        "            SurfaceTransactionApplier surfaceTransactionApplier,\n"
        "            @Nullable ViewGroup emptyRecentsMessageView) {\n"
        "        super.init(actionsView, splitController, desktopRecentsTransitionController,\n"
        "                surfaceTransactionApplier, emptyRecentsMessageView);\n"
    )
    # Try reading actual content if mismatch
    if old not in text:
        # looser replace of signature only
        old_sig = (
            "            @Nullable ViewGroup emptyRecentsMessageView) {\n"
            "        super.init(actionsView, splitController, desktopRecentsTransitionController,\n"
            "                surfaceTransactionApplier, emptyRecentsMessageView);\n"
        )
        new_sig = (
            "            @Nullable ViewGroup emptyRecentsMessageView,\n"
            f"            MemInfoView memInfoView) {{ {MARKER}\n"
            "        super.init(actionsView, splitController, desktopRecentsTransitionController,\n"
            "                surfaceTransactionApplier, emptyRecentsMessageView, memInfoView);\n"
        )
        if old_sig not in text:
            raise RuntimeError("FallbackRecentsView.init not found")
        return text.replace(old_sig, new_sig, 1)
    new = (
        "    public void init(OverviewActionsView actionsView, SplitSelectStateController splitController,\n"
        "            @Nullable DesktopRecentsTransitionController desktopRecentsTransitionController,\n"
        "            SurfaceTransactionApplier surfaceTransactionApplier,\n"
        "            @Nullable ViewGroup emptyRecentsMessageView,\n"
        f"            MemInfoView memInfoView) {{ {MARKER}\n"
        "        super.init(actionsView, splitController, desktopRecentsTransitionController,\n"
        "                surfaceTransactionApplier, emptyRecentsMessageView, memInfoView);\n"
    )
    return text.replace(old, new, 1)


def patch_fallback_layout(text: str) -> str:
    if "layout/meminfo" in text and MARKER in text:
        return text
    needle = (
        '            android:id="@+id/empty_recents_message_view"\n'
        '            layout="@layout/overview_empty_recents_message"'
    )
    if needle not in text:
        raise RuntimeError("fallback_recents_activity empty message not found")
    # After the include block — find closing of that include
    # Insert sibling include after empty message include ends
    # Read typical structure: include ... /> or multi-line
    marker_point = text.find(needle)
    close = text.find("/>", marker_point)
    if close < 0:
        raise RuntimeError("fallback include close not found")
    insert_at = close + 2
    insert = (
        "\n\n"
        f"        <!-- {MARKER} -->\n"
        "        <include\n"
        '            layout="@layout/meminfo" />'
    )
    return text[:insert_at] + insert + text[insert_at:]


def patch_quickstep_launcher(text: str) -> str:
    if "getMemInfoView()" in text and MARKER in text:
        return text
    text = ensure_import(
        text,
        f"import com.android.quickstep.views.MemInfoView; {MARKER}",
        (
            "import com.android.quickstep.views.OverviewActionsView;\n",
            "import com.android.quickstep.views.RecentsView;\n",
        ),
    )
    if "private MemInfoView mMemInfoView;" not in text:
        for a in (
            "    private OverviewActionsView mActionsView;\n",
            "    private OverviewActionsView<?> mActionsView;\n",
            "    private ScrimView mScrimView;\n",
        ):
            if a in text:
                text = text.replace(a, a + "    private MemInfoView mMemInfoView;\n", 1)
                break
        else:
            raise RuntimeError("QuickstepLauncher field anchor not found")

    if "R.id.meminfo" not in text:
        a = (
            "        ViewGroup emptyRecentsMessageView = findViewById(R.id.empty_recents_message_view);\n"
        )
        if a not in text:
            raise RuntimeError("QuickstepLauncher emptyRecentsMessageView local not found")
        text = text.replace(
            a,
            a + "        mMemInfoView = findViewById(R.id.meminfo);\n",
            1,
        )

    old_call = (
        "        overviewPanel.init(mActionsView, mSplitSelectStateController,\n"
    )
    # Find the multi-line init ending with emptyRecentsMessageView);
    needle = "                emptyRecentsMessageView);"
    if "emptyRecentsMessageView, mMemInfoView)" not in text:
        if needle not in text:
            raise RuntimeError("QuickstepLauncher init call ending not found")
        text = text.replace(
            needle, "                emptyRecentsMessageView, mMemInfoView);", 1
        )

    if "mMemInfoView.setDp" not in text and "emptyRecentsMessageView, mMemInfoView);" in text:
        text = text.replace(
            "                emptyRecentsMessageView, mMemInfoView);",
            "                emptyRecentsMessageView, mMemInfoView);\n"
            "        mMemInfoView.setDp(getDeviceProfile());\n"
            "        mMemInfoView.updateVerticalMargin(DisplayController.getNavigationMode(this));",
            1,
        )

    if "getMemInfoView()" not in text:
        idx = text.rfind("\n}")
        text = (
            text[:idx]
            + f"\n\n    {MARKER}\n"
            + "    @Override\n"
            + "    public MemInfoView getMemInfoView() {\n"
            + "        return mMemInfoView;\n"
            + "    }\n"
            + text[idx:]
        )
    return text


def patch_recents_activity(text: str) -> str:
    if "getMemInfoView()" in text and MARKER in text:
        return text
    text = ensure_import(
        text,
        f"import com.android.quickstep.views.MemInfoView; {MARKER}",
        (
            "import com.android.quickstep.views.OverviewActionsView;\n",
            "import com.android.quickstep.views.RecentsView;\n",
        ),
    )
    if "private MemInfoView mMemInfoView;" not in text:
        for a in (
            "    private OverviewActionsView<?> mActionsView;\n",
            "    private OverviewActionsView mActionsView;\n",
        ):
            if a in text:
                text = text.replace(a, a + "    private MemInfoView mMemInfoView;\n", 1)
                break
        else:
            raise RuntimeError("RecentsActivity field anchor not found")

    if "R.id.meminfo" not in text:
        a = (
            "        ViewGroup emptyRecentsMessageView = rootView.findViewById(R.id.empty_recents_message_view);\n"
        )
        if a not in text:
            raise RuntimeError("RecentsActivity emptyRecentsMessageView local not found")
        text = text.replace(
            a,
            a + "        mMemInfoView = rootView.findViewById(R.id.meminfo);\n",
            1,
        )

    needle = "                emptyRecentsMessageView);"
    if "emptyRecentsMessageView, mMemInfoView)" not in text:
        if needle not in text:
            raise RuntimeError("RecentsActivity init call ending not found")
        text = text.replace(
            needle, "                emptyRecentsMessageView, mMemInfoView);", 1
        )

    if "getMemInfoView()" not in text:
        idx = text.rfind("\n}")
        text = (
            text[:idx]
            + f"\n\n    {MARKER}\n"
            + "    @Override\n"
            + "    public MemInfoView getMemInfoView() {\n"
            + "        return mMemInfoView;\n"
            + "    }\n"
            + text[idx:]
        )
    return text


def patch_recents_window_manager(text: str) -> str:
    if "getMemInfoView" in text and MARKER in text:
        return text
    if "import com.android.quickstep.views.MemInfoView" not in text:
        for a in (
            "import com.android.quickstep.views.OverviewActionsView\n",
            "import com.android.quickstep.views.RecentsView\n",
        ):
            if a in text:
                text = text.replace(
                    a,
                    a + f"import com.android.quickstep.views.MemInfoView {MARKER}\n",
                    1,
                )
                break
        else:
            raise RuntimeError("RecentsWindowManager import anchor not found")

    if "private var memInfoView: MemInfoView? = null" not in text:
        # insert near other view fields
        for a in (
            "    private var actionsView: OverviewActionsView<*>? = null\n",
            "    private var emptyRecentsMessageView: ViewGroup? = null\n",
        ):
            if a in text:
                text = text.replace(
                    a, a + "    private var memInfoView: MemInfoView? = null\n", 1
                )
                break
        else:
            # soft-fail: still add getter returning null via lateinit skip
            raise RuntimeError("RecentsWindowManager field anchor not found")

    if "R.id.meminfo" not in text:
        a = "it.findViewById<ViewGroup?>(R.id.empty_recents_message_view)"
        i = text.find(a)
        if i < 0:
            raise RuntimeError("RecentsWindowManager empty_recents findViewById not found")
        nl = text.find("\n", i)
        text = (
            text[: nl + 1]
            + "            memInfoView = it.findViewById(R.id.meminfo)\n"
            + text[nl + 1 :]
        )

    # init(...) call needs memInfoView arg
    old_init_end = "                            emptyRecentsMessageView,\n                        )"
    new_init_end = (
        "                            emptyRecentsMessageView,\n"
        "                            memInfoView,\n"
        "                        )"
    )
    if "memInfoView," not in text[text.find("init(") : text.find("init(") + 500]:
        if old_init_end not in text:
            raise RuntimeError("RecentsWindowManager init ending not found")
        text = text.replace(old_init_end, new_init_end, 1)

    if "override fun getMemInfoView()" not in text:
        idx = text.rfind("\n}")
        text = (
            text[:idx]
            + f"\n\n    {MARKER}\n"
            + "    override fun getMemInfoView(): MemInfoView? = memInfoView\n"
            + text[idx:]
        )
    return text


def patch_state_controller(text: str) -> str:
    # Optional fade with overview; skip if complex — MemInfo still works.
    if MARKER in text:
        return text
    return text + f"\n// {MARKER} (state alpha wiring deferred)\n"



def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", default="source")
    args = ap.parse_args()
    l3 = Path(args.source_dir) / "packages/apps/Launcher3"

    patches = [
        (l3 / "quickstep/res/layout/overview_panel.xml", patch_overview_panel),
        (l3 / "src/com/android/launcher3/LauncherPrefs.kt", patch_launcher_prefs),
        (l3 / "src/com/android/launcher3/DeviceProfile.java", patch_device_profile),
        (l3 / "quickstep/src/com/android/quickstep/views/RecentsViewContainer.java", patch_recents_view_container),
        (l3 / "quickstep/src/com/android/quickstep/views/RecentsView.java", patch_recents_view_init),
        (l3 / "quickstep/src/com/android/quickstep/views/LauncherRecentsView.java", patch_launcher_recents_view),
        (l3 / "quickstep/src/com/android/quickstep/fallback/FallbackRecentsView.java", patch_fallback_recents_view),
        (l3 / "quickstep/res/layout/fallback_recents_activity.xml", patch_fallback_layout),
        (l3 / "quickstep/src/com/android/launcher3/uioverrides/QuickstepLauncher.java", patch_quickstep_launcher),
        (l3 / "quickstep/src/com/android/quickstep/RecentsActivity.java", patch_recents_activity),
        (l3 / "quickstep/src/com/android/quickstep/window/RecentsWindowManager.kt", patch_recents_window_manager),
        (l3 / "quickstep/src/com/android/launcher3/uioverrides/RecentsViewStateController.kt", patch_state_controller),
    ]
    for path, fn in patches:
        if not path.is_file():
            return fail(f"missing {path}")
        try:
            old = path.read_text(encoding="utf-8")
            new = fn(old)
            if new != old:
                path.write_text(new, encoding="utf-8")
                print(f"[launcher-meminfo] patched {path.name}")
            else:
                print(f"[launcher-meminfo] skip {path.name}")
        except RuntimeError as e:
            return fail(f"{path.name}: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
