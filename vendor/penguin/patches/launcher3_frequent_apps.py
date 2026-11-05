#!/usr/bin/env python3
"""PenguinOS: wire FrequentAppsView into Launcher3 overview actions.

Patches OverviewActionsView, overview_actions_container.xml, DeviceProfile.
Assumes FrequentAppsView.java + resources already copied by apply script.
Idempotent via MARKER.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARKER = "// PenguinOS: frequent-apps"
MARKER_XML = "<!-- PenguinOS: frequent-apps -->"


def fail(msg: str) -> int:
    print(f"[frequent-apps] error: {msg}", file=sys.stderr)
    return 1


def patch_overview(text: str) -> str | None:
    if MARKER in text:
        return None

    # expand MultiValueAlpha array 2 -> 3 and add index
    a1 = "    private final MultiValueAlpha[] mMultiValueAlphas = new MultiValueAlpha[2];\n"
    a1b = (
        f"    private final MultiValueAlpha[] mMultiValueAlphas = new MultiValueAlpha[3]; {MARKER}\n"
    )
    if a1 not in text:
        raise RuntimeError("mMultiValueAlphas[2] anchor not found")
    text = text.replace(a1, a1b, 1)

    a2 = "    private static final int GROUP_ACTIONS_ALPHAS = 1;\n"
    a2b = (
        "    private static final int GROUP_ACTIONS_ALPHAS = 1;\n"
        f"    private static final int FREQUENT_APPS_ALPHAS = 2; {MARKER}\n"
    )
    if a2 not in text:
        raise RuntimeError("GROUP_ACTIONS_ALPHAS anchor not found")
    text = text.replace(a2, a2b, 1)

    # field
    f1 = "    private final Rect mTaskSize = new Rect();\n"
    f1b = (
        "    private final Rect mTaskSize = new Rect();\n"
        f"    private FrequentAppsView mFrequentApps; {MARKER}\n"
    )
    if f1 not in text:
        raise RuntimeError("mTaskSize field anchor not found")
    text = text.replace(f1, f1b, 1)

    # onFinishInflate
    o1 = (
        "        mActionButtons = findViewById(R.id.action_buttons);\n"
        "        mSaveAppPairButton = findViewById(R.id.action_save_app_pair);\n"
        "        TypefaceUtils.setTypeface(mSaveAppPairButton, FontFamily.GSF_LABEL_LARGE);\n"
        "        // Initialize a list to hold alphas for mActionButtons and any group action buttons.\n"
        "        mMultiValueAlphas[ACTIONS_ALPHAS] = new MultiValueAlpha(mActionButtons, NUM_ALPHAS);\n"
        "        mMultiValueAlphas[GROUP_ACTIONS_ALPHAS] =\n"
        "                new MultiValueAlpha(mSaveAppPairButton, NUM_ALPHAS);\n"
    )
    o1b = (
        "        mActionButtons = findViewById(R.id.action_buttons);\n"
        "        mSaveAppPairButton = findViewById(R.id.action_save_app_pair);\n"
        f"        mFrequentApps = findViewById(R.id.frequent_apps); {MARKER}\n"
        "        TypefaceUtils.setTypeface(mSaveAppPairButton, FontFamily.GSF_LABEL_LARGE);\n"
        "        // Initialize a list to hold alphas for mActionButtons and any group action buttons.\n"
        "        mMultiValueAlphas[ACTIONS_ALPHAS] = new MultiValueAlpha(mActionButtons, NUM_ALPHAS);\n"
        "        mMultiValueAlphas[GROUP_ACTIONS_ALPHAS] =\n"
        "                new MultiValueAlpha(mSaveAppPairButton, NUM_ALPHAS);\n"
        f"        mMultiValueAlphas[FREQUENT_APPS_ALPHAS] = new MultiValueAlpha(mFrequentApps, NUM_ALPHAS); {MARKER}\n"
    )
    if o1 not in text:
        raise RuntimeError("onFinishInflate alpha init anchor not found")
    text = text.replace(o1, o1b, 1)

    # updateActionButtonsVisibility
    u1 = (
        "        getActionsAlphas().get(INDEX_GROUPED_ALPHA).setValue(showSingleTaskActions ? 1 : 0);\n"
        "        getGroupActionsAlphas().get(INDEX_GROUPED_ALPHA).setValue(showGroupActions ? 1 : 0);\n"
        "    }"
    )
    u1b = (
        "        getActionsAlphas().get(INDEX_GROUPED_ALPHA).setValue(showSingleTaskActions ? 1 : 0);\n"
        f"        boolean showFrequentApps = FrequentAppsView.isEnabled(getContext()) {MARKER}\n"
        "                && !mDp.getDeviceProperties().isLargeScreen();\n"
        "        mMultiValueAlphas[FREQUENT_APPS_ALPHAS].get(INDEX_GROUPED_ALPHA)\n"
        "                .setValue(showFrequentApps ? 1 : 0);\n"
        "        getGroupActionsAlphas().get(INDEX_GROUPED_ALPHA).setValue(showGroupActions ? 1 : 0);\n"
        "    }"
    )
    if u1 not in text:
        raise RuntimeError("updateActionButtonsVisibility alpha set anchor not found")
    text = text.replace(u1, u1b, 1)

    # updateVerticalMargin
    v1 = (
        "    public void updateVerticalMargin(NavigationMode mode) {\n"
        "        updateActionBarPosition(mActionButtons);\n"
        "        updateActionBarPosition(mSaveAppPairButton);\n"
        "    }"
    )
    v1b = (
        "    public void updateVerticalMargin(NavigationMode mode) {\n"
        "        updateActionBarPosition(mActionButtons);\n"
        "        updateActionBarPosition(mSaveAppPairButton);\n"
        f"        updateFrequentAppsPosition(); {MARKER}\n"
        "    }\n\n"
        f"    /** Centres frequent apps in the space reserved below overview actions. {MARKER} */\n"
        "    private void updateFrequentAppsPosition() {\n"
        "        if (mDp == null || mFrequentApps == null) {\n"
        "            return;\n"
        "        }\n"
        "        LayoutParams lp = (LayoutParams) mFrequentApps.getLayoutParams();\n"
        "        int iconSize = getResources().getDimensionPixelSize(R.dimen.frequent_apps_icon_size);\n"
        "        int bottomMargin = mDp.getOverviewActionsClaimedSpaceBelow()\n"
        "                + Math.max(0, mDp.frequentAppsHeight - iconSize) / 2;\n"
        "        lp.setMargins(lp.leftMargin, lp.topMargin, lp.rightMargin, bottomMargin);\n"
        "    }"
    )
    if v1 not in text:
        raise RuntimeError("updateVerticalMargin anchor not found")
    text = text.replace(v1, v1b, 1)
    return text


def patch_layout(text: str) -> str | None:
    if MARKER_XML in text:
        return None
    needle = """    <Button
        android:id="@+id/action_save_app_pair"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/action_save_app_pair"
        android:layout_gravity="bottom|center_horizontal"
        android:visibility="gone" />

</com.android.quickstep.views.OverviewActionsView>"""
    insert = """    <Button
        android:id="@+id/action_save_app_pair"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/action_save_app_pair"
        android:layout_gravity="bottom|center_horizontal"
        android:visibility="gone" />

    """ + MARKER_XML + """
    <com.android.quickstep.views.FrequentAppsView
        android:id="@+id/frequent_apps"
        android:layout_width="wrap_content"
        android:layout_height="@dimen/frequent_apps_icon_size"
        android:layout_gravity="bottom|center_horizontal"
        android:visibility="gone" />

</com.android.quickstep.views.OverviewActionsView>"""
    if needle not in text:
        raise RuntimeError("overview_actions_container.xml save_app_pair anchor not found")
    return text.replace(needle, insert, 1)


def patch_device_profile(text: str) -> str | None:
    if MARKER in text:
        return None

    # import Settings if missing
        text = text.replace(
            "import android.os.UserManager;\n",
            1,
        )

    # public field after overviewProfile
    f = "    private final OverviewProfile overviewProfile;\n\n    // Hotseat\n"
    fb = (
        "    private final OverviewProfile overviewProfile;\n\n"
        f"    /** Extra overview space when FrequentApps experiment is on. {MARKER} */\n"
        "    public int frequentAppsHeight;\n\n"
        "    // Hotseat\n"
    )
    if f not in text:
        raise RuntimeError("overviewProfile field anchor not found")
    text = text.replace(f, fb, 1)

    # init after overviewProfile create
    i = "        overviewProfile = OverviewProfile.Factory.createOverviewProfile(res);\n\n        mMetrics = res.getDisplayMetrics();\n"
    ib = (
        "        overviewProfile = OverviewProfile.Factory.createOverviewProfile(res);\n\n"
        f"        frequentAppsHeight = Settings.Secure.getInt(context.getContentResolver(), {MARKER}\n"
        '                "recents_frequent_apps", 0) == 1\n'
        "                ? res.getDimensionPixelSize(R.dimen.frequent_apps_claimed_height) : 0;\n\n"
        "        mMetrics = res.getDisplayMetrics();\n"
    )
    if i not in text:
        raise RuntimeError("overviewProfile create + mMetrics anchor not found")
    text = text.replace(i, ib, 1)

    # claimed space
    c = (
        "        int overviewActionsSpace = mDeviceProperties.isLargeScreen()\n"
        "                ? 0\n"
        "                : (overviewProfile.getActionsTopMarginPx() + overviewProfile.getActionsHeight());\n"
        "        return overviewActionsSpace + getOverviewActionsClaimedSpaceBelow();\n"
    )
    cb = (
        "        int overviewActionsSpace = mDeviceProperties.isLargeScreen()\n"
        "                ? 0\n"
        "                : (overviewProfile.getActionsTopMarginPx() + overviewProfile.getActionsHeight()\n"
        f"                        + frequentAppsHeight); {MARKER}\n"
        "        return overviewActionsSpace + getOverviewActionsClaimedSpaceBelow();\n"
    )
    if c not in text:
        raise RuntimeError("getOverviewActionsClaimedSpace body anchor not found")
    text = text.replace(c, cb, 1)
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", default=None)
    args = ap.parse_args()
    root = Path(args.source_dir or __import__("os").environ.get("SOURCE_DIR", "source"))
    launcher = root / "packages" / "apps" / "Launcher3"

    overview = (
        launcher
        / "quickstep"
        / "src"
        / "com"
        / "android"
        / "quickstep"
        / "views"
        / "OverviewActionsView.java"
    )
    layout = launcher / "quickstep" / "res" / "layout" / "overview_actions_container.xml"
    dp = launcher / "src" / "com" / "android" / "launcher3" / "DeviceProfile.java"
    view = (
        launcher
        / "quickstep"
        / "src"
        / "com"
        / "android"
        / "quickstep"
        / "views"
        / "FrequentAppsView.java"
    )

    if not view.is_file():
        return fail(f"missing {view} (apply script must copy it first)")

    for path, fn, label in (
        (overview, patch_overview, "OverviewActionsView"),
        (layout, patch_layout, "overview_actions_container.xml"),
        (dp, patch_device_profile, "DeviceProfile"),
    ):
        if not path.is_file():
            return fail(f"missing {path}")
        text = path.read_text(encoding="utf-8")
        try:
            new = fn(text)
        except RuntimeError as e:
            return fail(f"{label}: {e}")
        if new is None:
            print(f"[frequent-apps] skip {label} (already applied)")
        else:
            path.write_text(new, encoding="utf-8")
            print(f"[frequent-apps] applied: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
