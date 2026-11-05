#!/usr/bin/env python3
"""PenguinOS: wire QsPanels Optional into QuickSettingsContainerViewModel + QuickSettingsContent.

Idempotent via MARKER.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARKER = "// PenguinOS: styles-qs-panel"


def fail(msg: str) -> int:
    print(f"[styles-qs] error: {msg}", file=sys.stderr)
    return 1


def patch_viewmodel(text: str) -> str:
    if MARKER in text and "val penguin:" in text:
        return text

    if "import com.android.systemui.penguin.QsPanels" not in text:
        anchor = "import com.android.systemui.qs.panels.ui.viewmodel.TileGridViewModel\n"
        if anchor not in text:
            raise RuntimeError("TileGridViewModel import not found")
        text = text.replace(
            anchor,
            anchor
            + "import com.android.systemui.qs.panels.ui.viewmodel.toolbar.EditModeButtonViewModel\n"
            + "import com.android.systemui.media.remedia.domain.interactor.MediaInteractor\n"
            + f"import com.android.systemui.penguin.QsPanels {MARKER}\n"
            + "import java.util.Optional\n",
            1,
        )

    ctor_anchor = (
        "    val editModeViewModel: EditModeViewModel,\n"
        "    val detailsViewModel: DetailsViewModel,\n"
        "    private val mediaCarouselInteractor: MediaCarouselInteractor,\n"
        "    val mediaViewModelFactory: MediaViewModel.Factory,\n"
        "    mediaInRowInLandscapeViewModelFactory: MediaInRowInLandscapeViewModel.Factory,\n"
        "    @ShadeDisplayAware shadeDisplayTypeRepository: DisplayTypeRepository,\n"
        ") : HydratedActivatable() {"
    )
    ctor_insert = (
        "    val editModeViewModel: EditModeViewModel,\n"
        f"    val editModeButtonViewModelFactory: EditModeButtonViewModel.Factory, {MARKER}\n"
        "    val detailsViewModel: DetailsViewModel,\n"
        "    private val mediaCarouselInteractor: MediaCarouselInteractor,\n"
        "    private val mediaInteractor: MediaInteractor,\n"
        "    val mediaViewModelFactory: MediaViewModel.Factory,\n"
        "    mediaInRowInLandscapeViewModelFactory: MediaInRowInLandscapeViewModel.Factory,\n"
        "    @ShadeDisplayAware shadeDisplayTypeRepository: DisplayTypeRepository,\n"
        "    qsPanels: Optional<QsPanels>,\n"
        ") : HydratedActivatable() {\n"
        "\n"
        "    val penguin: QsPanels? = qsPanels.orElse(null)\n"
    )
    if ctor_anchor not in text:
        raise RuntimeError("QuickSettingsContainerViewModel ctor anchor not found")
    text = text.replace(ctor_anchor, ctor_insert, 1)

    show_anchor = (
        "    val showMedia: Boolean by mediaCarouselInteractor.hasAnyMedia.hydratedStateOf()\n"
        "\n"
        "    val showMediaInRow: Boolean"
    )
    show_insert = (
        "    val showMedia: Boolean by mediaCarouselInteractor.hasAnyMedia.hydratedStateOf()\n"
        "\n"
        f"    val hasMediaCards: Boolean {MARKER}\n"
        "        get() = mediaInteractor.hasAnyMedia\n"
        "\n"
        "    val showMediaInRow: Boolean"
    )
    if show_anchor not in text:
        raise RuntimeError("showMedia anchor not found")
    text = text.replace(show_anchor, show_insert, 1)
    return text


def patch_qs_content(text: str) -> str:
    if MARKER in text and "viewModel.penguin" in text:
        return text

    if "import com.android.systemui.penguin.LocalQsPanels" not in text:
        anchor = "import com.android.systemui.qs.ui.viewmodel.QuickSettingsContainerViewModel\n"
        if anchor not in text:
            raise RuntimeError("QuickSettingsContainerViewModel import not found in QuickSettingsContent")
        text = text.replace(
            anchor,
            anchor
            + "import com.android.systemui.penguin.LocalQsPanels\n"
            + "import com.android.systemui.penguin.QsPanelsHost\n"
            + "import com.android.systemui.qs.shared.style.QsPanelStyle\n"
            + "import com.android.systemui.qs.shared.style.panelStyle\n"
            + "import androidx.compose.runtime.CompositionLocalProvider\n",
            1,
        )

    # Insert takeover after function signature opening brace
    sig = (
        "@Composable\n"
        "fun ContentScope.QuickSettingsContent(\n"
        "    viewModel: QuickSettingsContainerViewModel,\n"
        "    mediaInRow: Boolean,\n"
        "    modifier: Modifier = Modifier,\n"
        "    mediaSquishiness: () -> Float = { 1f },\n"
        ") {\n"
    )
    if sig not in text:
        raise RuntimeError("QuickSettingsContent signature not found")
    insert = (
        sig
        + f"    // PenguinOS: styles-qs-panel — non-Default styles take over; Default keeps UwU path\n"
        + "    val penguin = viewModel.penguin\n"
        + "    if (penguin != null && viewModel.panelStyle != QsPanelStyle.Default) {\n"
        + "        CompositionLocalProvider(LocalQsPanels provides QsPanelsHost(penguin, viewModel)) {\n"
        + "            with(penguin) { Content(viewModel, mediaInRow, modifier, mediaSquishiness) }\n"
        + "        }\n"
        + "        return\n"
        + "    }\n"
    )
    text = text.replace(sig, insert, 1)
    if MARKER not in text:
        # ensure marker present for idempotency
        text = text.replace(
            "    // PenguinOS: styles-qs-panel — non-Default styles take over; Default keeps UwU path\n",
            f"    {MARKER}\n"
            "    // non-Default styles take over; Default keeps UwU path\n",
            1,
        )
    return text


def patch_file(path: Path, patcher) -> None:
    original = path.read_text(encoding="utf-8")
    updated = patcher(original)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        print(f"[styles-qs] patched {path}")
    else:
        print(f"[styles-qs] skip {path.name}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", default="source")
    args = ap.parse_args()
    root = Path(args.source_dir)
    vm = root / "frameworks/base/packages/SystemUI/src/com/android/systemui/qs/ui/viewmodel/QuickSettingsContainerViewModel.kt"
    qs = root / "frameworks/base/packages/SystemUI/compose/features/src/com/android/systemui/qs/ui/composable/QuickSettingsContent.kt"
    for path, patcher in ((vm, patch_viewmodel), (qs, patch_qs_content)):
        if not path.is_file():
            return fail(f"missing {path}")
        try:
            patch_file(path, patcher)
        except RuntimeError as e:
            return fail(str(e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
