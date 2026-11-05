#!/usr/bin/env python3
"""PenguinOS: wire Optional-free PowerMenuLayout into GlobalActionsDialogLite + SystemUIModule.

Idempotent via MARKER.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARKER = "// PenguinOS: styles-power-menu"


def fail(msg: str) -> int:
    print(f"[power-menu] error: {msg}", file=sys.stderr)
    return 1


def patch_global_actions(text: str) -> str:
    if MARKER in text:
        return text

    # import
    if "import com.android.systemui.penguin.PowerMenuLayout;" not in text:
        anchor = "import com.android.systemui.plugins.ActivityStarter;"
        if anchor not in text:
            raise RuntimeError("ActivityStarter import not found")
        text = text.replace(
            anchor,
            "import com.android.systemui.penguin.PowerMenuLayout; "
            + MARKER
            + "\n"
            + "import javax.inject.Provider;\n"
            + anchor,
            1,
        )

    # fields on ActionsDialogLiteDelegate
    f_anchor = (
        "        @VisibleForTesting\n"
        "        @Nullable\n"
        "        SystemUIDialog mCurrentDialog;\n"
        "        private GlobalActionsLayoutLite mGlobalActionsLayout;\n"
    )
    f_insert = (
        "        @VisibleForTesting\n"
        "        @Nullable\n"
        "        SystemUIDialog mCurrentDialog;\n"
        "        private GlobalActionsLayoutLite mGlobalActionsLayout;\n"
        f"        @Nullable private View mAnimatedContent; {MARKER}\n"
        "        @Nullable private android.graphics.drawable.Drawable mBackdrop;\n"
        "        @NonNull private final Provider<PowerMenuLayout> mPowerMenuLayout;\n"
        "        private boolean mLayoutBlurSupported;\n"
    )
    if f_anchor not in text:
        raise RuntimeError("ActionsDialogLiteDelegate fields anchor not found")
    text = text.replace(f_anchor, f_insert, 1)

    # ctor param + assign
    c_anchor = (
        "                @NonNull SystemUIDialog.Factory systemUIDialogFactory,\n"
        "                @NonNull DeviceEntryInteractor deviceEntryInteractor) {"
    )
    c_insert = (
        "                @NonNull SystemUIDialog.Factory systemUIDialogFactory,\n"
        "                @NonNull DeviceEntryInteractor deviceEntryInteractor,\n"
        f"                @NonNull Provider<PowerMenuLayout> powerMenuLayout) {{ {MARKER}"
    )
    if c_anchor not in text:
        raise RuntimeError("ActionsDialogLiteDelegate ctor signature not found")
    text = text.replace(c_anchor, c_insert, 1)

    a_anchor = "            mDeviceEntryInteractor = deviceEntryInteractor;\n        }"
    # Only first occurrence after ctor — may match others; use more context
    a_anchor = (
        "            mGestureDetector = new GestureDetector(context, mGestureListener);\n"
        "            mDeviceEntryInteractor = deviceEntryInteractor;\n"
        "        }"
    )
    a_insert = (
        "            mGestureDetector = new GestureDetector(context, mGestureListener);\n"
        "            mDeviceEntryInteractor = deviceEntryInteractor;\n"
        f"            mPowerMenuLayout = powerMenuLayout; {MARKER}\n"
        "        }\n\n"
        f"        @Nullable private PowerMenuLayout activeLayout(@NonNull Context context) {{ {MARKER}\n"
        "            PowerMenuLayout layout = mPowerMenuLayout.get();\n"
        "            return layout.isActive(context) ? layout : null;\n"
        "        }"
    )
    if a_anchor not in text:
        raise RuntimeError("ctor assignment anchor not found")
    text = text.replace(a_anchor, a_insert, 1)

    # showPower/Restart options menus
    s_anchor = (
        "        public void showPowerOptionsMenu() {\n"
        "            mPowerOptionsDialog = GlobalActionsPowerDialog.create(mContext, mPowerOptionsAdapter);\n"
        "            mPowerOptionsDialog.show();\n"
        "        }\n\n"
        "        public void showRestartOptionsMenu() {\n"
        "            mRestartOptionsDialog = GlobalActionsPowerDialog.create(mContext,\n"
        "                    mRestartOptionsAdapter);\n"
        "            mRestartOptionsDialog.show();\n"
        "        }"
    )
    s_insert = (
        f"        public void showPowerOptionsMenu() {{ {MARKER}\n"
        "            mPowerOptionsDialog = createSubMenu(mPowerOptionsAdapter);\n"
        "            showSubMenu(mPowerOptionsDialog);\n"
        "        }\n\n"
        "        public void showRestartOptionsMenu() {\n"
        "            mRestartOptionsDialog = createSubMenu(mRestartOptionsAdapter);\n"
        "            showSubMenu(mRestartOptionsDialog);\n"
        "        }\n\n"
        "        @NonNull\n"
        "        private Dialog createSubMenu(@NonNull android.widget.ListAdapter adapter) {\n"
        "            PowerMenuLayout layout = activeLayout(mContext);\n"
        "            if (layout != null) {\n"
        "                return layout.createSubMenu(mContext, adapter, mLayoutBlurSupported);\n"
        "            }\n"
        "            return GlobalActionsPowerDialog.create(mContext, adapter);\n"
        "        }\n\n"
        "        private void showSubMenu(@NonNull Dialog subMenu) {\n"
        "            final View parentContent = mAnimatedContent;\n"
        "            if (parentContent != null) {\n"
        "                parentContent.setVisibility(View.INVISIBLE);\n"
        "                subMenu.setOnDismissListener(d -> parentContent.setVisibility(View.VISIBLE));\n"
        "            }\n"
        "            subMenu.show();\n"
        "        }"
    )
    if s_anchor not in text:
        raise RuntimeError("showPowerOptionsMenu anchor not found")
    text = text.replace(s_anchor, s_insert, 1)

    # initializeLayout early return for custom layout
    i_anchor = (
        "        private void initializeLayout(@NonNull SystemUIDialog dialog) {\n"
        "            dialog.setContentView(com.android.systemui.res.R.layout.global_actions_grid_lite);\n"
    )
    i_insert = (
        "        private void initializeLayout(@NonNull SystemUIDialog dialog) {\n"
        f"            PowerMenuLayout powerMenuLayout = activeLayout(dialog.getContext()); {MARKER}\n"
        "            if (powerMenuLayout != null) {\n"
        "                powerMenuLayout.inflate(dialog, mLayoutHost);\n"
        "                return;\n"
        "            }\n"
        "            dialog.setContentView(com.android.systemui.res.R.layout.global_actions_grid_lite);\n"
    )
    if i_anchor not in text:
        raise RuntimeError("initializeLayout anchor not found")
    text = text.replace(i_anchor, i_insert, 1)

    # Host + findAction before fixNavBarClipping
    h_anchor = (
        "        private void fixNavBarClipping(@NonNull SystemUIDialog dialog) {\n"
        "            ViewGroup content = dialog.findViewById(android.R.id.content);\n"
    )
    h_insert = (
        f"        private final PowerMenuLayout.Host mLayoutHost = new PowerMenuLayout.Host() {{ {MARKER}\n"
        "            @Nullable @Override\n"
        "            public PowerMenuLayout.Option findOption(int kind) {\n"
        "                Class<? extends Action> type = switch (kind) {\n"
        "                    case POWER_OFF -> ShutDownAction.class;\n"
        "                    case RESTART -> RestartAction.class;\n"
        "                    case EMERGENCY -> EmergencyAction.class;\n"
        "                    default -> throw new IllegalArgumentException(\"Unknown option \" + kind);\n"
        "                };\n"
        "                Action action = findAction(type);\n"
        "                if (action == null) return null;\n"
        "                return new PowerMenuLayout.Option() {\n"
        "                    @NonNull @Override\n"
        "                    public android.graphics.drawable.Drawable getIcon(@NonNull Context context) {\n"
        "                        return action.getIcon(context);\n"
        "                    }\n"
        "                    @Override public void trigger() {\n"
        "                        // iOS slides act immediately; only PowerOptions keeps dialog.\n"
        "                        if (!(action instanceof PowerOptionsAction)) {\n"
        "                            dismissWithoutAnimation();\n"
        "                        }\n"
        "                        action.onPress();\n"
        "                    }\n"
        "                };\n"
        "            }\n"
        "            @Override public void onContainerTouch(@NonNull MotionEvent event) {\n"
        "                mGestureDetector.onTouchEvent(event);\n"
        "            }\n"
        "            @Override public boolean isBlurBackdropAllowed() {\n"
        "                return isVolumeAndPowerBlurEnabled() && mContext.getResources().getBoolean(\n"
        "                        com.android.systemui.res.R.bool.config_translucentStandalonePowerMenu);\n"
        "            }\n"
        "            @Override public void setBlurSupported(boolean supported) {\n"
        "                mLayoutBlurSupported = supported;\n"
        "            }\n"
        "            @Override public void close() {\n"
        "                mUiEventLogger.log(GlobalActionsEvent.GA_CLOSE_TAP_OUTSIDE);\n"
        "                dismiss();\n"
        "            }\n"
        "            @Override public void setAnimatedContent(@NonNull View content,\n"
        "                    @Nullable android.graphics.drawable.Drawable backdrop) {\n"
        "                mAnimatedContent = content;\n"
        "                mBackdrop = backdrop;\n"
        "            }\n"
        "            @Override public void onLayoutInflated(@NonNull Context context,\n"
        "                    @NonNull ViewGroup container) {\n"
        "                if (mBackgroundDrawable == null) {\n"
        "                    mBackgroundDrawable = new ScrimDrawable();\n"
        "                }\n"
        "                int user = mSelectedUserInteractor.getSelectedUserId();\n"
        "                if (mKeyguardShowing && mKeyguardUpdateMonitor.getUserHasTrust(user)) {\n"
        "                    mLockPatternUtils.requireCredentialEntry(user);\n"
        "                    showSmartLockDisabledMessage(context, container);\n"
        "                }\n"
        "            }\n"
        "        };\n\n"
        "        @Nullable\n"
        "        private Action findAction(@NonNull Class<? extends Action> type) {\n"
        "            for (int i = 0; i < mAdapter.getCount(); i++) {\n"
        "                Action action = mAdapter.getItem(i);\n"
        "                if (type.isInstance(action)) return action;\n"
        "            }\n"
        "            return null;\n"
        "        }\n\n"
        "        private void fixNavBarClipping(@NonNull SystemUIDialog dialog) {\n"
        "            ViewGroup content = dialog.findViewById(android.R.id.content);\n"
    )
    if h_anchor not in text:
        raise RuntimeError("fixNavBarClipping anchor not found")
    text = text.replace(h_anchor, h_insert, 1)
    return text


def patch_systemui_module(text: str) -> str:
    if MARKER in text:
        return text
    if "PenguinHooksModule" in text:
        return text
    # add import
    anchor_imp = "import com.android.systemui.BootCompleteCache;"
    if anchor_imp not in text:
        raise RuntimeError("SystemUIModule import anchor not found")
    text = text.replace(
        anchor_imp,
        "import com.android.systemui.BootCompleteCache;\n"
        f"import com.android.systemui.penguin.PenguinHooksModule; {MARKER}",
        1,
    )
    # add to includes list after ActivityModule
    a = "        ActivityModule.class,\n"
    if a not in text:
        raise RuntimeError("ActivityModule.class include not found")
    text = text.replace(
        a,
        f"        ActivityModule.class,\n        PenguinHooksModule.class, {MARKER}\n",
        1,
    )
    return text


MARKER_NULL = "// PenguinOS: styles-power-menu-null"


def patch_custom_layout_null_guards(text: str) -> str:
    """Null-safe onStart/animation when iOS layout leaves mGlobalActionsLayout unset."""
    if MARKER_NULL in text:
        return text

    # Stock path: keep animated content for enter/exit animation
    a = (
        "            if (mBackgroundDrawable == null) {\n"
        "                mBackgroundDrawable = new ScrimDrawable();\n"
        "            }\n"
        "            // If user entered from the lock screen and smart lock was enabled, disable it\n"
    )
    if a in text and "mAnimatedContent = mGlobalActionsLayout;" not in text:
        text = text.replace(
            a,
            "            mAnimatedContent = mGlobalActionsLayout; "
            + MARKER_NULL
            + "\n"
            "            mBackdrop = null;\n\n"
            + a,
            1,
        )

    # onStart
    o = (
        "        public void onStart(@NonNull SystemUIDialog dialog) {\n"
        "            mGlobalActionsLayout.updateList();\n"
    )
    if o in text:
        text = text.replace(
            o,
            "        public void onStart(@NonNull SystemUIDialog dialog) {\n"
            f"            if (mGlobalActionsLayout != null) {{ {MARKER_NULL}\n"
            "                mGlobalActionsLayout.updateList();\n"
            "            }\n",
            1,
        )

    # dismissWhenUnlockStatusChanges
    d = (
        "        private void dismissWhenUnlockStatusChanges(boolean initialValue) {\n"
        "            collectFlow(\n"
        "                    mGlobalActionsLayout,\n"
    )
    if d in text:
        text = text.replace(
            d,
            "        private void dismissWhenUnlockStatusChanges(boolean initialValue) {\n"
            f"            if (mAnimatedContent == null) {{ {MARKER_NULL}\n"
            "                return;\n"
            "            }\n"
            "            collectFlow(\n"
            "                    mAnimatedContent,\n",
            1,
        )

    # show(): don't animate from expandable for custom layouts
    s = (
        "            DialogTransitionAnimator.Controller controller =\n"
        "                    expandable != null ? expandable.dialogTransitionController(\n"
    )
    if s in text and "animateFromExpandable" not in text:
        text = text.replace(
            s,
            "            boolean animateFromExpandable =\n"
            f"                    expandable != null && activeLayout(mContext) == null; {MARKER_NULL}\n"
            "            DialogTransitionAnimator.Controller controller =\n"
            "                    animateFromExpandable ? expandable.dialogTransitionController(\n",
            1,
        )

    # startAnimation: use mAnimatedContent
    sa = (
        "        private void startAnimation(@NonNull SystemUIDialog dialog, boolean isEnter,\n"
        "                @Nullable Runnable then) {\n"
        "            ValueAnimator animator = ValueAnimator.ofFloat(0f, 1f);\n"
    )
    if sa in text:
        text = text.replace(
            sa,
            "        private void startAnimation(@NonNull SystemUIDialog dialog, boolean isEnter,\n"
            "                @Nullable Runnable then) {\n"
            f"            final View content = mAnimatedContent; {MARKER_NULL}\n"
            "            final android.graphics.drawable.Drawable backdrop = mBackdrop;\n"
            "            if (content == null) {\n"
            "                if (then != null) {\n"
            "                    then.run();\n"
            "                }\n"
            "                return;\n"
            "            }\n"
            "            ValueAnimator animator = ValueAnimator.ofFloat(0f, 1f);\n",
            1,
        )
        text = text.replace(
            "                mGlobalActionsLayout.setAlpha(alpha);\n"
            "                window.setDimAmount(mInitialWindowDimAmount * alpha);\n",
            "                content.setAlpha(alpha);\n"
            "                if (backdrop != null) {\n"
            "                    backdrop.setAlpha(Math.round(alpha * 255));\n"
            "                }\n"
            "                window.setDimAmount(mInitialWindowDimAmount * alpha);\n",
            1,
        )
        for old, new in (
            ("mGlobalActionsLayout.setTranslationX(translation);", "content.setTranslationX(translation);"),
            ("mGlobalActionsLayout.setTranslationY(-translation);", "content.setTranslationY(-translation);"),
            ("mGlobalActionsLayout.setTranslationX(-translation);", "content.setTranslationX(-translation);"),
            ("mGlobalActionsLayout.setTranslationY(translation);", "content.setTranslationY(translation);"),
            (
                "mPreviousLayerType = mGlobalActionsLayout.getLayerType();\n"
                "                    mGlobalActionsLayout.setLayerType(View.LAYER_TYPE_HARDWARE, null);",
                "mPreviousLayerType = content.getLayerType();\n"
                "                    content.setLayerType(View.LAYER_TYPE_HARDWARE, null);",
            ),
            (
                "mGlobalActionsLayout.setLayerType(mPreviousLayerType, null);",
                "content.setLayerType(mPreviousLayerType, null);",
            ),
        ):
            if old in text:
                text = text.replace(old, new, 1)

    # refreshDialog
    r = (
        "            // Update the list as the max number of items per row has probably changed.\n"
        "            mGlobalActionsLayout.updateList();\n"
    )
    if r in text:
        text = text.replace(
            r,
            "            // Update the list as the max number of items per row has probably changed.\n"
            f"            if (mGlobalActionsLayout != null) {{ {MARKER_NULL}\n"
            "                mGlobalActionsLayout.updateList();\n"
            "            }\n",
            1,
        )

    if MARKER_NULL not in text:
        raise RuntimeError("null-guard anchors not found / already partially applied")
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", default=None)
    args = ap.parse_args()
    root = Path(args.source_dir or __import__("os").environ.get("SOURCE_DIR", "source"))
    gad = (
        root
        / "frameworks/base/packages/SystemUI/src/com/android/systemui/globalactions/GlobalActionsDialogLite.java"
    )
    mod = (
        root
        / "frameworks/base/packages/SystemUI/src/com/android/systemui/dagger/SystemUIModule.java"
    )
    if not gad.is_file():
        return fail(f"missing {gad}")
    if not mod.is_file():
        return fail(f"missing {mod}")

    text = gad.read_text(encoding="utf-8")
    try:
        if MARKER not in text:
            text = patch_global_actions(text)
            print(f"[power-menu] applied wiring: {gad}")
        else:
            print("[power-menu] skip wiring (already marked)")
        if MARKER_NULL not in text:
            text = patch_custom_layout_null_guards(text)
            print(f"[power-menu] applied null-guards: {gad}")
        else:
            print("[power-menu] skip null-guards")
    except RuntimeError as e:
        return fail(f"GlobalActionsDialogLite: {e}")
    gad.write_text(text, encoding="utf-8")

    mod_text = mod.read_text(encoding="utf-8")
    try:
        new_mod = patch_systemui_module(mod_text)
    except RuntimeError as e:
        return fail(f"SystemUIModule: {e}")
    if new_mod != mod_text:
        mod.write_text(new_mod, encoding="utf-8")
        print(f"[power-menu] applied: {mod}")
    else:
        print("[power-menu] skip SystemUIModule")
    return 0


if __name__ == "__main__":
    sys.exit(main())
