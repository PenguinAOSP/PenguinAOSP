#!/usr/bin/env python3
"""PenguinOS: Launcher3 LiquidGlass on folder open + preview icon.

Idempotent via MARKER.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARKER = "// PenguinOS: launcher-liquid-glass"


def fail(msg: str) -> int:
    print(f"[launcher-glass] error: {msg}", file=sys.stderr)
    return 1


def patch_folder(text: str) -> str:
    if MARKER in text and "drawGlassBackground" in text:
        return text

    if "import com.android.launcher3.util.LiquidGlass;" not in text:
        # insert after a common import
        for anchor in (
            "import com.android.launcher3.util.Executors;\n",
            "import com.android.launcher3.util.LauncherBindable;\n",
            "import com.android.launcher3.views.ActivityContext;\n",
        ):
            if anchor in text:
                text = text.replace(
                    anchor,
                    anchor + f"import com.android.launcher3.util.LiquidGlass; {MARKER}\n"
                    "import android.graphics.Path;\n"
                    "import android.graphics.RectF;\n",
                    1,
                )
                break
        else:
            raise RuntimeError("Folder.java import anchor not found")

    old = (
        "        } else {\n"
        "            mBlurBackgroundHelper.drawFolderBlur(canvas, null, this);\n"
        "            mBackground.draw(canvas);\n"
        "\n"
        "            super.dispatchDraw(canvas);\n"
        "        }\n"
        "    }\n"
        "\n"
        "    public FolderPagedView getContent() {"
    )
    new = (
        "        } else {\n"
        "            mBlurBackgroundHelper.drawFolderBlur(canvas, null, this);\n"
        f"            mGlassBounds.set(mBackground.getBounds()); {MARKER}\n"
        "            drawGlassBackground(canvas, mGlassBounds, mBackground.getCornerRadius(), null);\n"
        "\n"
        "            super.dispatchDraw(canvas);\n"
        "        }\n"
        "    }\n"
        "\n"
        "    private final RectF mGlassBounds = new RectF();\n"
        "\n"
        "    private void drawGlassBackground(Canvas canvas, RectF bounds, float radius, Path shape) {\n"
        "        boolean glass = LiquidGlass.isEnabled(getContext());\n"
        "        mBackground.setAlpha(glass ? 0x8C : 0xCC);\n"
        "        mBackground.draw(canvas);\n"
        "        if (glass) {\n"
        "            LiquidGlass.drawRim(canvas, bounds, radius, shape,\n"
        "                    getResources().getDisplayMetrics().density, 1f);\n"
        "        }\n"
        "    }\n"
        "\n"
        "    public FolderPagedView getContent() {"
    )
    if old not in text:
        raise RuntimeError("Folder.java dispatchDraw else-branch anchor not found")
    text = text.replace(old, new, 1)

    # Also glass path when clipPath non-null
    old_clip = (
        "            mBlurBackgroundHelper.drawFolderBlur(canvas, mClipPath, this);\n"
        "            mBackground.draw(canvas);\n"
        "\n"
        "            if (!mIsAnimatingClosed) {"
    )
    new_clip = (
        "            mBlurBackgroundHelper.drawFolderBlur(canvas, mClipPath, this);\n"
        f"            mGlassBounds.set(mBackground.getBounds()); {MARKER}\n"
        "            drawGlassBackground(canvas, mGlassBounds, mBackground.getCornerRadius(), null);\n"
        "\n"
        "            if (!mIsAnimatingClosed) {"
    )
    if old_clip in text:
        text = text.replace(old_clip, new_clip, 1)
    return text


def patch_preview(text: str) -> str:
    if MARKER in text and "LiquidGlass.drawRim" in text:
        return text

    if "import com.android.launcher3.util.LiquidGlass;" not in text:
        for anchor in (
            "import com.android.launcher3.graphics.ThemeManager;\n",
            "import com.android.launcher3.Utilities;\n",
        ):
            if anchor in text:
                text = text.replace(
                    anchor,
                    anchor
                    + f"import com.android.launcher3.util.LiquidGlass; {MARKER}\n"
                    "import android.graphics.Path;\n"
                    "import android.graphics.RectF;\n",
                    1,
                )
                break
        else:
            raise RuntimeError("PreviewBackground.java import anchor not found")

    old = (
        "    public void drawBackground(Canvas canvas) {\n"
        "        mPaint.setStyle(Paint.Style.FILL);\n"
        "        mPaint.setColor(getBgColor());\n"
        "\n"
        "        getShape().drawShape(canvas, getOffsetX(), getOffsetY(), getScaledRadius(), mPaint);\n"
        "        drawShadow(canvas);\n"
        "    }\n"
        "\n"
        "    private ShapeDelegate getShape() {"
    )
    new = (
        "    public void drawBackground(Canvas canvas) {\n"
        "        mPaint.setStyle(Paint.Style.FILL);\n"
        "        mPaint.setColor(getBgColor());\n"
        "\n"
        "        getShape().drawShape(canvas, getOffsetX(), getOffsetY(), getScaledRadius(), mPaint);\n"
        "        drawShadow(canvas);\n"
        f"        if (LiquidGlass.isEnabled(mContext)) {{ {MARKER}\n"
        "            float r = getScaledRadius();\n"
        "            mGlassPath.reset();\n"
        "            getShape().addToPath(mGlassPath, getOffsetX(), getOffsetY(), r);\n"
        "            mGlassBounds.set(getOffsetX(), getOffsetY(), getOffsetX() + 2 * r,\n"
        "                    getOffsetY() + 2 * r);\n"
        "            LiquidGlass.drawRim(canvas, mGlassBounds, r, mGlassPath,\n"
        "                    mContext.getResources().getDisplayMetrics().density, 0.8f);\n"
        "        }\n"
        "    }\n"
        "\n"
        "    private final Path mGlassPath = new Path();\n"
        "    private final RectF mGlassBounds = new RectF();\n"
        "\n"
        "    private ShapeDelegate getShape() {"
    )
    if old not in text:
        raise RuntimeError("PreviewBackground.drawBackground anchor not found")
    return text.replace(old, new, 1)


def patch_file(path: Path, patcher) -> None:
    original = path.read_text(encoding="utf-8")
    updated = patcher(original)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        print(f"[launcher-glass] patched {path}")
    else:
        print(f"[launcher-glass] skip {path.name}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", default="source")
    args = ap.parse_args()
    root = Path(args.source_dir) / "packages/apps/Launcher3"
    files = {
        root / "src/com/android/launcher3/folder/Folder.java": patch_folder,
        root / "src/com/android/launcher3/folder/PreviewBackground.java": patch_preview,
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
