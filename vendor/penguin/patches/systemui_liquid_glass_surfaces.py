#!/usr/bin/env python3
"""PenguinOS: Liquid Glass surfaces — notification tint/rim, blur gate, Scrim refresh, QS tiles.

Idempotent via MARKER.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARKER = "// PenguinOS: liquid-glass-surfaces"


def fail(msg: str) -> int:
    print(f"[liquid-glass-surfaces] error: {msg}", file=sys.stderr)
    return 1


def patch_notification_background(text: str) -> str:
    # Allow re-entry to fill hover-dismiss draw path even after primary MARKER applied.
    if MARKER in text and "drawGlassRim" in text and "if (backgroundBounds != null) drawGlassRim" in text:
        return text
    if MARKER in text and "drawGlassRim" in text:
        hover_anchor = (
            "            if (mBackgroundBlurDrawable != null) {\n"
            "                mBackgroundBlurDrawable.setBounds(backgroundBounds);\n"
            "                mBackgroundBlurDrawable.draw(canvas);\n"
            "            } else if (mBackground != null) {\n"
            "                mBackground.setBounds(backgroundBounds);\n"
            "                mBackground.draw(canvas);\n"
            "            }\n"
            "\n"
            "            canvas.restore();"
        )
        hover_insert = (
            "            if (mBackgroundBlurDrawable != null) {\n"
            "                mBackgroundBlurDrawable.setBounds(backgroundBounds);\n"
            "                mBackgroundBlurDrawable.draw(canvas);\n"
            "            } else if (mBackground != null) {\n"
            "                mBackground.setBounds(backgroundBounds);\n"
            "                mBackground.draw(canvas);\n"
            "            }\n"
            f"            if (backgroundBounds != null) drawGlassRim(canvas, backgroundBounds); {MARKER}\n"
            "\n"
            "            canvas.restore();"
        )
        if hover_anchor in text:
            return text.replace(hover_anchor, hover_insert, 1)
        return text

    if "import com.android.systemui.qs.shared.style.LiquidGlass;" not in text:
        anchor = "import com.android.internal.graphics.drawable.BackgroundBlurDrawable;"
        if anchor not in text:
            raise RuntimeError("BackgroundBlurDrawable import not found in NotificationBackgroundView")
        text = text.replace(
            anchor,
            anchor
            + "\n"
            + "import android.graphics.Color;\n"
            + "import android.graphics.RectF;\n"
            + f"import com.android.systemui.qs.shared.style.LiquidGlass; {MARKER}",
            1,
        )

    draw_anchor = (
        "            drawable.setBounds(left, top, right, bottom);\n"
        "            drawable.draw(canvas);\n"
        "        }\n"
        "    }\n"
        "\n"
        "    @Override\n"
        "    protected boolean verifyDrawable(Drawable who) {"
    )
    draw_insert = (
        "            drawable.setBounds(left, top, right, bottom);\n"
        "            drawable.draw(canvas);\n"
        f"            drawGlassRim(canvas, drawable.getBounds()); {MARKER}\n"
        "        }\n"
        "    }\n"
        "\n"
        "    private final RectF mGlassBounds = new RectF();\n"
        "\n"
        "    private void drawGlassRim(Canvas canvas, Rect bounds) {\n"
        "        if (bounds == null || !LiquidGlass.isEnabled(getContext())) {\n"
        "            return;\n"
        "        }\n"
        "        mGlassBounds.set(bounds);\n"
        "        LiquidGlass.drawRim(canvas, mGlassBounds, mCornerRadii,\n"
        "                getResources().getDisplayMetrics().density);\n"
        "    }\n"
        "\n"
        "    @Override\n"
        "    protected boolean verifyDrawable(Drawable who) {"
    )
    if draw_anchor not in text:
        raise RuntimeError("draw() end anchor not found in NotificationBackgroundView")
    text = text.replace(draw_anchor, draw_insert, 1)

    blur_gate = (
        "    public void setBlurBackgroundEnabled(boolean enabled) {\n"
        "        if (!lockscreenBlurForNotifications()) {\n"
        "            return;\n"
        "        }"
    )
    blur_gate_new = (
        "    public void setBlurBackgroundEnabled(boolean enabled) {\n"
        f"        if (!lockscreenBlurForNotifications() && !LiquidGlass.isEnabled(getContext())) {{ {MARKER}\n"
        "            return;\n"
        "        }"
    )
    if blur_gate not in text:
        raise RuntimeError("setBlurBackgroundEnabled gate not found")
    text = text.replace(blur_gate, blur_gate_new, 1)

    tint_anchor = (
        "    public void setTint(int tintColor) {\n"
        "        Drawable baseLayer = getBaseBackgroundLayer();\n"
        "        if (notificationRowTransparency()) {\n"
        "            ((GradientDrawable) baseLayer.mutate()).setColor(tintColor);\n"
        "        } else {\n"
        "            baseLayer.mutate().setTintMode(PorterDuff.Mode.SRC_ATOP);\n"
        "            baseLayer.setTint(tintColor);\n"
        "        }\n"
        "        if (mBackgroundBlurDrawable != null) {\n"
        "            mBackgroundBlurDrawable.setColor(tintColor);\n"
        "        }\n"
        "        mTintColor = tintColor;\n"
        "        setStatefulColors();\n"
        "        invalidate();\n"
        "    }"
    )
    tint_insert = (
        "    private int surfaceFor(int tintColor) {\n"
        f"        if (tintColor != mNormalColor || !LiquidGlass.isEnabled(getContext())) return tintColor; {MARKER}\n"
        "        return mHeadsUpGlass ? LiquidGlass.headsUpSurface() : LiquidGlass.viewSurface();\n"
        "    }\n"
        "\n"
        "    private boolean glassOnBlur() {\n"
        "        return mBackgroundBlurDrawable != null && LiquidGlass.isEnabled(getContext());\n"
        "    }\n"
        "\n"
        "    private boolean mHeadsUpGlass;\n"
        "\n"
        "    public void setHeadsUpGlass(boolean headsUp) {\n"
        "        if (mHeadsUpGlass == headsUp) return;\n"
        "        mHeadsUpGlass = headsUp;\n"
        "        setTint(mTintColor);\n"
        "    }\n"
        "\n"
        "    public void setTint(int tintColor) {\n"
        "        Drawable baseLayer = getBaseBackgroundLayer();\n"
        "        final int surface = glassOnBlur() && tintColor == mNormalColor\n"
        "                ? Color.TRANSPARENT : surfaceFor(tintColor);\n"
        "        if (notificationRowTransparency()) {\n"
        "            ((GradientDrawable) baseLayer.mutate()).setColor(surface);\n"
        "        } else {\n"
        "            baseLayer.mutate().setTintMode(PorterDuff.Mode.SRC_ATOP);\n"
        "            baseLayer.setTint(surface);\n"
        "        }\n"
        "        if (mBackgroundBlurDrawable != null) {\n"
        "            mBackgroundBlurDrawable.setColor(surfaceFor(tintColor));\n"
        "        }\n"
        "        mTintColor = tintColor;\n"
        "        setStatefulColors();\n"
        "        invalidate();\n"
        "    }"
    )
    if tint_anchor not in text:
        raise RuntimeError("setTint anchor not found in NotificationBackgroundView")
    text = text.replace(tint_anchor, tint_insert, 1)

    # Hover-dismiss path draws without private draw(); add rim there too.
    hover_anchor = (
        "            if (mBackgroundBlurDrawable != null) {\n"
        "                mBackgroundBlurDrawable.setBounds(backgroundBounds);\n"
        "                mBackgroundBlurDrawable.draw(canvas);\n"
        "            } else if (mBackground != null) {\n"
        "                mBackground.setBounds(backgroundBounds);\n"
        "                mBackground.draw(canvas);\n"
        "            }\n"
        "\n"
        "            canvas.restore();"
    )
    hover_insert = (
        "            if (mBackgroundBlurDrawable != null) {\n"
        "                mBackgroundBlurDrawable.setBounds(backgroundBounds);\n"
        "                mBackgroundBlurDrawable.draw(canvas);\n"
        "            } else if (mBackground != null) {\n"
        "                mBackground.setBounds(backgroundBounds);\n"
        "                mBackground.draw(canvas);\n"
        "            }\n"
        f"            if (backgroundBounds != null) drawGlassRim(canvas, backgroundBounds); {MARKER}\n"
        "\n"
        "            canvas.restore();"
    )
    if hover_anchor in text and "if (backgroundBounds != null) drawGlassRim" not in text:
        text = text.replace(hover_anchor, hover_insert, 1)
    return text


def patch_activatable(text: str) -> str:
    if MARKER in text and "LiquidGlass.isEnabled" in text:
        return text

    if "import com.android.systemui.qs.shared.style.LiquidGlass;" not in text:
        # find a stable import
        for anchor in (
            "import com.android.systemui.res.R;",
            "import com.android.systemui.statusbar.notification.row.ExpandableOutlineView;",
        ):
            if anchor in text:
                text = text.replace(
                    anchor,
                    f"import com.android.systemui.qs.shared.style.LiquidGlass; {MARKER}\n"
                    + anchor,
                    1,
                )
                break
        else:
            raise RuntimeError("import anchor not found in ActivatableNotificationView")

    old = (
        "    protected boolean usesBlurredBackground() {\n"
        "        return usesTransparentBackground() && lockscreenBlurForNotifications();\n"
        "    }"
    )
    new = (
        "    protected boolean usesBlurredBackground() {\n"
        f"        return usesTransparentBackground() {MARKER}\n"
        "                && (LiquidGlass.isEnabled(getContext()) || lockscreenBlurForNotifications());\n"
        "    }"
    )
    if old not in text:
        raise RuntimeError("usesBlurredBackground not found")
    return text.replace(old, new, 1)


def patch_scrim(text: str) -> str:
    if MARKER in text and "handleLiquidGlassChanged" in text:
        return text

    if "import android.database.ContentObserver;" not in text:
        # Settings / Handler already likely present
        for anchor in (
            "import android.content.Context;",
            "import android.graphics.Color;",
        ):
            if anchor in text:
                text = text.replace(
                    anchor,
                    anchor
                    + "\n"
                    + "import android.database.ContentObserver;\n"
                    + "import android.os.UserHandle;\n"
                    + "import android.provider.Settings;\n",
                    1,
                )
                break

    if "import com.android.systemui.qs.shared.style.LiquidGlass;" not in text:
        anchor = "import com.android.systemui.shade.ui.ShadeColors;"
        if anchor not in text:
            raise RuntimeError("ShadeColors import not found in ScrimController")
        text = text.replace(
            anchor,
            anchor
            + "\n"
            + f"import com.android.systemui.qs.shared.style.LiquidGlass; {MARKER}",
            1,
        )

    attach_anchor = (
        "        updateThemeColors();\n"
        "        mNotificationsScrim.setScrimName(getScrimName(mNotificationsScrim));\n"
    )
    attach_insert = (
        "        updateThemeColors();\n"
        f"        mContext.getContentResolver().registerContentObserver( {MARKER}\n"
        '                Settings.Secure.getUriFor("penguin_liquid_glass"),\n'
        "                false,\n"
        "                new ContentObserver(mHandler) {\n"
        "                    @Override\n"
        "                    public void onChange(boolean selfChange) {\n"
        "                        mHandler.post(() -> handleLiquidGlassChanged());\n"
        "                    }\n"
        "                },\n"
        "                UserHandle.USER_ALL);\n"
        "        // Warm LiquidGlass observer so ShadeColors reads stay live.\n"
        "        LiquidGlass.isEnabled(mContext);\n"
        "        mNotificationsScrim.setScrimName(getScrimName(mNotificationsScrim));\n"
    )
    if attach_anchor not in text:
        raise RuntimeError("attachViews theme update anchor not found")
    text = text.replace(attach_anchor, attach_insert, 1)

    # Insert handler near handleBlurSupportedChanged
    h_anchor = "    private void handleBlurSupportedChanged(boolean isBlurSupported) {"
    if h_anchor not in text:
        raise RuntimeError("handleBlurSupportedChanged not found")
    h_insert = (
        "    private void handleLiquidGlassChanged() {\n"
        f"        if (Flags.notificationShadeBlur()) {{ {MARKER}\n"
        "            for (ScrimState state : ScrimState.values()) {\n"
        "                state.setShadePanelColor(getShadePanelColor());\n"
        "            }\n"
        "        }\n"
        "        applyAndDispatchState();\n"
        "    }\n"
        "\n"
        "    private void handleBlurSupportedChanged(boolean isBlurSupported) {"
    )
    text = text.replace(h_anchor, h_insert, 1)
    return text


def patch_tile(text: str) -> str:
    if MARKER in text and "glassRim" in text:
        return text

    imports = (
        "import com.android.systemui.qs.shared.style.LiquidGlassSurface\n"
        "import com.android.systemui.qs.shared.style.glassRim\n"
        "import com.android.systemui.qs.shared.style.liquidGlassOn\n"
    )
    # Prefer after an existing qs import
    for anchor in (
        "import com.android.systemui.qs.panels.ui.viewmodel.TileUiState\n",
        "import com.android.systemui.qs.panels.ui.compose.infinitegrid.CommonTileDefaults.TileHeight\n",
    ):
        if anchor in text and "liquidGlassOn" not in text:
            text = text.replace(anchor, anchor + imports, 1)
            break
    else:
        if "liquidGlassOn" not in text:
            raise RuntimeError("Tile.kt import anchor not found")

    # TileExpandable: add glass rim after clip
    old_exp = (
        "        modifier =\n"
        "            modifier\n"
        "                .clip(shape)\n"
        "                .motionTestValues { squishiness() exportAs TileMotionTestKeys.Squishness }\n"
        "                .verticalSquish(squishiness),"
    )
    new_exp = (
        "        modifier =\n"
        "            modifier\n"
        "                .clip(shape)\n"
        f"                .then(if (liquidGlassOn) Modifier.glassRim(shape) else Modifier) {MARKER}\n"
        "                .motionTestValues { squishiness() exportAs TileMotionTestKeys.Squishness }\n"
        "                .verticalSquish(squishiness),"
    )
    if old_exp not in text:
        raise RuntimeError("TileExpandable modifier chain not found")
    text = text.replace(old_exp, new_exp, 1)

    # Inactive tile surface → LiquidGlassSurface when glass on
    old_inactive = (
        "    fun inactiveTileColors(): TileColors =\n"
        "        TileColors(\n"
        "            background = LocalAndroidColorScheme.current.surfaceEffect1,\n"
    )
    new_inactive = (
        "    fun inactiveTileColors(): TileColors =\n"
        "        TileColors(\n"
        f"            background = if (liquidGlassOn) LiquidGlassSurface else LocalAndroidColorScheme.current.surfaceEffect1, {MARKER}\n"
    )
    if old_inactive not in text:
        raise RuntimeError("inactiveTileColors not found")
    text = text.replace(old_inactive, new_inactive, 1)

    old_dual = (
        "    fun inactiveDualTargetTileColors(): TileColors =\n"
        "        TileColors(\n"
        "            background = LocalAndroidColorScheme.current.surfaceEffect1,\n"
    )
    new_dual = (
        "    fun inactiveDualTargetTileColors(): TileColors =\n"
        "        TileColors(\n"
        f"            background = if (liquidGlassOn) LiquidGlassSurface else LocalAndroidColorScheme.current.surfaceEffect1, {MARKER}\n"
    )
    if old_dual not in text:
        raise RuntimeError("inactiveDualTargetTileColors not found")
    text = text.replace(old_dual, new_dual, 1)

    old_active_dual = (
        "    fun activeDualTargetTileColors(): TileColors =\n"
        "        TileColors(\n"
        "            background = LocalAndroidColorScheme.current.surfaceEffect1,\n"
    )
    new_active_dual = (
        "    fun activeDualTargetTileColors(): TileColors =\n"
        "        TileColors(\n"
        f"            background = if (liquidGlassOn) LiquidGlassSurface else LocalAndroidColorScheme.current.surfaceEffect1, {MARKER}\n"
    )
    if old_active_dual not in text:
        raise RuntimeError("activeDualTargetTileColors not found")
    text = text.replace(old_active_dual, new_active_dual, 1)
    return text


def patch_file(path: Path, patcher) -> None:
    original = path.read_text(encoding="utf-8")
    updated = patcher(original)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        print(f"[liquid-glass-surfaces] patched {path}")
    else:
        print(f"[liquid-glass-surfaces] skip {path.name}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", default="source")
    args = ap.parse_args()
    root = Path(args.source_dir)
    sysui = root / "frameworks/base/packages/SystemUI/src/com/android/systemui"
    files = {
        sysui / "statusbar/notification/row/NotificationBackgroundView.java": patch_notification_background,
        sysui / "statusbar/notification/row/ActivatableNotificationView.java": patch_activatable,
        sysui / "statusbar/phone/ScrimController.java": patch_scrim,
        sysui / "qs/panels/ui/compose/infinitegrid/Tile.kt": patch_tile,
    }
    for path, patcher in files.items():
        if not path.is_file():
            return fail(f"missing {path}")
        try:
            patch_file(path, patcher)
        except RuntimeError as e:
            return fail(str(e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
