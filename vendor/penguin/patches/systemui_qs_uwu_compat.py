#!/usr/bin/env python3
"""PenguinOS: adapt qs_panel_style sources to UwU 17 APIs.

Patches TileGrid/GridLayout/TileColors/TileGridCell/QuickSettings.Elements/
TileGridViewModel/ShadeSceneContentViewModel and stubs ShadeHeader hooks
that need deeper ShadeScene integration.
Idempotent via MARKER.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARKER = "// PenguinOS: styles-qs-uwu-compat"
XML_MARKER = "<!-- PenguinOS: styles-qs-uwu-compat -->"


def fail(msg: str) -> int:
    print(f"[qs-uwu-compat] error: {msg}", file=sys.stderr)
    return 1


def write_if_changed(path: Path, text: str, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    old = path.read_text(encoding="utf-8") if path.is_file() else None
    if old == text:
        print(f"[qs-uwu-compat] skip {label}")
        return
    path.write_text(text, encoding="utf-8")
    print(f"[qs-uwu-compat] wrote {label}")


def patch_once(text: str, old: str, new: str, what: str) -> str:
    if MARKER in text and new.strip()[:40] in text:
        return text
    if old not in text:
        raise RuntimeError(f"{what}: anchor not found")
    return text.replace(old, new, 1)


def patch_tile_colors(text: str) -> str:
    if "circleAroundIcon" in text and MARKER in text:
        return text
    old = (
        "data class TileColors(\n"
        "    val background: Color,\n"
        "    val iconBackground: Color,\n"
        "    val label: Color,\n"
        "    val secondaryLabel: Color,\n"
        "    val icon: Color,\n"
        ")"
    )
    new = (
        "data class TileColors(\n"
        "    val background: Color,\n"
        "    val iconBackground: Color,\n"
        "    val label: Color,\n"
        "    val secondaryLabel: Color,\n"
        "    val icon: Color,\n"
        f"    val circleAroundIcon: Color = Color.Transparent, {MARKER}\n"
        ")"
    )
    if old not in text:
        raise RuntimeError("TileColors data class not found")
    return text.replace(old, new, 1)


def tile_grid_kt() -> str:
    return (
        "/*\n"
        " * Copyright (C) 2024 The Android Open Source Project\n"
        " * PenguinOS: styles-qs-uwu-compat — TileGrid filter/override shims\n"
        " */\n"
        "\n"
        "package com.android.systemui.qs.panels.ui.compose\n"
        "\n"
        "import androidx.compose.runtime.Composable\n"
        "import androidx.compose.ui.Modifier\n"
        "import com.android.compose.animation.scene.ContentScope\n"
        "import com.android.systemui.qs.panels.ui.viewmodel.TileGridViewModel\n"
        "import com.android.systemui.qs.pipeline.shared.TileSpec\n"
        "\n"
        f"{MARKER}\n"
        "@Composable\n"
        "fun ContentScope.TileGrid(\n"
        "    viewModel: TileGridViewModel,\n"
        "    modifier: Modifier = Modifier,\n"
        "    excludeSpecs: List<TileSpec> = emptyList(),\n"
        "    includeSpecs: List<TileSpec>? = null,\n"
        "    columnsOverride: Int? = null,\n"
        "    forceLargeTiles: Boolean = false,\n"
        "    listening: () -> Boolean = { true },\n"
        "    enableRevealEffect: Boolean = false,\n"
        "    showEditButton: Boolean = true,\n"
        "    belowTiles: @Composable () -> Unit = {},\n"
        ") {\n"
        "    val gridLayout = viewModel.gridLayout\n"
        "    val tiles =\n"
        "        viewModel.tileViewModels.filter {\n"
        "            (includeSpecs == null || it.spec in includeSpecs) && it.spec !in excludeSpecs\n"
        "        }\n"
        "    with(gridLayout) {\n"
        "        TileGrid(\n"
        "            tiles = tiles,\n"
        "            modifier = modifier,\n"
        "            listening = listening,\n"
        "            enableRevealEffect = enableRevealEffect,\n"
        "            showEditButton = showEditButton,\n"
        "            columnsOverride = columnsOverride,\n"
        "            forceLargeTiles = forceLargeTiles,\n"
        "        )\n"
        "    }\n"
        "    belowTiles()\n"
        "}\n"
    )


def patch_grid_layout(text: str) -> str:
    if MARKER in text and "columnsOverride" in text and "fun TileSizing" in text:
        return text
    old_sig = (
        "    @Composable\n"
        "    fun ContentScope.TileGrid(\n"
        "        tiles: List<TileViewModel>,\n"
        "        modifier: Modifier,\n"
        "        listening: () -> Boolean,\n"
        "        enableRevealEffect: Boolean,\n"
        "        showEditButton: Boolean = true,\n"
        "    )"
    )
    new_sig = (
        "    @Composable\n"
        "    fun ContentScope.TileGrid(\n"
        "        tiles: List<TileViewModel>,\n"
        "        modifier: Modifier,\n"
        "        listening: () -> Boolean,\n"
        "        enableRevealEffect: Boolean,\n"
        "        showEditButton: Boolean = true,\n"
        f"        columnsOverride: Int? = null, {MARKER}\n"
        "        forceLargeTiles: Boolean = false,\n"
        "    )"
    )
    if old_sig not in text:
        raise RuntimeError("GridLayout.TileGrid signature not found")
    text = text.replace(old_sig, new_sig, 1)

    tile_sizing = (
        "\n"
        f"    {MARKER}\n"
        "    @Composable\n"
        "    fun TileSizing(\n"
        "        content: @Composable (largeTiles: Set<TileSpec>, resize: (TileSpec, Boolean) -> Unit) -> Unit\n"
        "    ) {\n"
        "        content(emptySet()) { _, _ -> }\n"
        "    }\n"
    )
    if "fun TileSizing(" not in text:
        # insert before EditTileGrid
        anchor = "    @Composable\n    fun EditTileGrid("
        if anchor not in text:
            raise RuntimeError("GridLayout.EditTileGrid anchor not found")
        # need TileSpec import
        if "import com.android.systemui.qs.pipeline.shared.TileSpec" not in text:
            text = text.replace(
                "package com.android.systemui.qs.panels.ui.compose\n",
                "package com.android.systemui.qs.panels.ui.compose\n\n"
                "import com.android.systemui.qs.pipeline.shared.TileSpec\n",
                1,
            )
        text = text.replace(anchor, tile_sizing + "\n" + anchor, 1)
    return text


def patch_impl_signature(text: str, name: str) -> str:
    if MARKER in text and "columnsOverride" in text:
        return text
    old = (
        "    override fun ContentScope.TileGrid(\n"
        "        tiles: List<TileViewModel>,\n"
        "        modifier: Modifier,\n"
        "        listening: () -> Boolean,\n"
        "        enableRevealEffect: Boolean,\n"
        "        showEditButton: Boolean,\n"
        "    ) {"
    )
    new = (
        "    override fun ContentScope.TileGrid(\n"
        "        tiles: List<TileViewModel>,\n"
        "        modifier: Modifier,\n"
        "        listening: () -> Boolean,\n"
        "        enableRevealEffect: Boolean,\n"
        "        showEditButton: Boolean,\n"
        f"        columnsOverride: Int?, {MARKER}\n"
        "        forceLargeTiles: Boolean,\n"
        "    ) {"
    )
    if old not in text:
        raise RuntimeError(f"{name} TileGrid override not found")
    return text.replace(old, new, 1)


def patch_infinite_tile_sizing(text: str) -> str:
    if "override fun TileSizing" in text:
        return text
    insert = (
        "\n"
        f"    {MARKER}\n"
        "    @Composable\n"
        "    override fun TileSizing(\n"
        "        content: @Composable (largeTiles: Set<TileSpec>, resize: (TileSpec, Boolean) -> Unit) -> Unit\n"
        "    ) {\n"
        "        val viewModel =\n"
        '            rememberViewModel(traceName = "InfiniteGridLayout.TileSizing") {\n'
        "                viewModelFactory.create()\n"
        "            }\n"
        "        val largeTiles by viewModel.iconTilesViewModel.largeTilesState\n"
        "        content(largeTiles) { spec, large ->\n"
        "            viewModel.iconTilesViewModel.resize(spec, toIcon = !large)\n"
        "        }\n"
        "    }\n"
        "\n"
    )
    anchor = "    @Composable\n    override fun EditTileGrid("
    if anchor not in text:
        raise RuntimeError("InfiniteGridLayout.EditTileGrid anchor not found")
    if "import com.android.systemui.qs.pipeline.shared.TileSpec" not in text:
        text = text.replace(
            "package com.android.systemui.qs.panels.ui.compose.infinitegrid\n",
            "package com.android.systemui.qs.panels.ui.compose.infinitegrid\n\n"
            "import com.android.systemui.qs.pipeline.shared.TileSpec\n",
            1,
        )
    return text.replace(anchor, insert + anchor, 1)


def patch_tile_grid_cell(text: str) -> str:
    if "val rows: Int = 1" in text and MARKER in text:
        return text
    old = (
        "data class TileGridCell(\n"
        "    override val tile: EditTileViewModel,\n"
        "    override val row: Int,\n"
        "    override val width: Int,\n"
        "    override val span: GridItemSpan = GridItemSpan(width),\n"
        "    val column: Int,\n"
        ") : GridCell, SizedTile<EditTileViewModel>, CategoryAndName by tile {\n"
        '    val key: String = "${tile.tileSpec.spec}-$row"\n'
        "\n"
        "    constructor(\n"
        "        sizedTile: SizedTile<EditTileViewModel>,\n"
        "        row: Int,\n"
        "        column: Int,\n"
        "    ) : this(tile = sizedTile.tile, row = row, column = column, width = sizedTile.width)\n"
        "}"
    )
    new = (
        "data class TileGridCell(\n"
        "    override val tile: EditTileViewModel,\n"
        "    override val row: Int,\n"
        "    override val width: Int,\n"
        "    override val span: GridItemSpan = GridItemSpan(width),\n"
        "    val column: Int,\n"
        f"    val rows: Int = 1, {MARKER}\n"
        "    val hoistedBefore: Boolean = false,\n"
        ") : GridCell, SizedTile<EditTileViewModel>, CategoryAndName by tile {\n"
        '    val key: String = "${tile.tileSpec.spec}-$row"\n'
        "\n"
        "    constructor(\n"
        "        sizedTile: SizedTile<EditTileViewModel>,\n"
        "        row: Int,\n"
        "        column: Int,\n"
        "        rows: Int = 1,\n"
        "        hoistedBefore: Boolean = false,\n"
        "    ) : this(\n"
        "        tile = sizedTile.tile,\n"
        "        row = row,\n"
        "        column = column,\n"
        "        width = sizedTile.width,\n"
        "        rows = rows,\n"
        "        hoistedBefore = hoistedBefore,\n"
        "    )\n"
        "}"
    )
    if old not in text:
        raise RuntimeError("TileGridCell data class not found")
    return text.replace(old, new, 1)


def patch_quick_settings_elements(text: str) -> str:
    if "HeaderTiles" in text and MARKER in text:
        return text
    old = (
        "        val TileElementMatcher = ElementKey.withIdentity { it is TileIdentity }\n"
        "\n"
        "        val QuickQuickSettingsAndMedia = ElementKey(\"QuickQuickSettingsAndMedia\")\n"
    )
    new = (
        "        val TileElementMatcher = ElementKey.withIdentity { it is TileIdentity }\n"
        "\n"
        f"        {MARKER}\n"
        "        val HeaderTiles =\n"
        "            ElementKey(\"QuickSettingsHeaderTiles\", contentPicker = SharedQsTileContentPicker)\n"
        "\n"
        "        val ConnectivityFolder = ElementKey(\"ConnectivityFolder\")\n"
        "\n"
        "        val QuickQuickSettingsAndMedia = ElementKey(\"QuickQuickSettingsAndMedia\")\n"
    )
    if old not in text:
        raise RuntimeError("QuickSettings.Elements anchor not found")
    return text.replace(old, new, 1)


def patch_tile_grid_viewmodel(text: str) -> str:
    if "val largeTiles" in text and MARKER in text:
        return text
    if "import com.android.systemui.qs.panels.domain.interactor.IconTilesInteractor" not in text:
        text = text.replace(
            "import com.android.systemui.qs.panels.domain.interactor.GridLayoutTypeInteractor\n",
            "import com.android.systemui.qs.panels.domain.interactor.GridLayoutTypeInteractor\n"
            "import com.android.systemui.qs.panels.domain.interactor.IconTilesInteractor\n",
            1,
        )
    old_ctor = (
        "    gridLayoutTypeInteractor: GridLayoutTypeInteractor,\n"
        "    gridLayoutMap: Map<GridLayoutType, @JvmSuppressWildcards GridLayout>,\n"
        "    tilesInteractor: CurrentTilesInteractor,\n"
        "    @Named(\"Default\") defaultGridLayout: GridLayout,\n"
        ") : HydratedActivatable() {"
    )
    new_ctor = (
        "    gridLayoutTypeInteractor: GridLayoutTypeInteractor,\n"
        "    gridLayoutMap: Map<GridLayoutType, @JvmSuppressWildcards GridLayout>,\n"
        "    tilesInteractor: CurrentTilesInteractor,\n"
        f"    iconTilesInteractor: IconTilesInteractor, {MARKER}\n"
        "    @Named(\"Default\") defaultGridLayout: GridLayout,\n"
        ") : HydratedActivatable() {"
    )
    if old_ctor not in text:
        raise RuntimeError("TileGridViewModel ctor not found")
    text = text.replace(old_ctor, new_ctor, 1)
    old_body = (
        "            .hydratedStateOf(initialValue = defaultGridLayout)\n"
        "\n"
        "    private val tileModels by tilesInteractor.currentTiles.hydratedStateOf()"
    )
    new_body = (
        "            .hydratedStateOf(initialValue = defaultGridLayout)\n"
        "\n"
        f"    val largeTiles by iconTilesInteractor.largeTilesSpecs.hydratedStateOf() {MARKER}\n"
        "\n"
        "    private val tileModels by tilesInteractor.currentTiles.hydratedStateOf()"
    )
    if old_body not in text:
        raise RuntimeError("TileGridViewModel body anchor not found")
    return text.replace(old_body, new_body, 1)


def patch_shade_scene_vm(text: str) -> str:
    if "val hasMediaCards" in text and "val qsContainerViewModel =" in text and MARKER in text:
        return text
    if "import com.android.systemui.media.remedia.domain.interactor.MediaInteractor" not in text:
        # place after MediaCarouselInteractor import if present
        anchor = "import com.android.systemui.media.controls.domain.pipeline.interactor.MediaCarouselInteractor\n"
        if anchor not in text:
            # try alternate
            anchor = "import com.android.systemui.media.controls.ui.viewmodel.MediaViewModel\n"
        text = text.replace(
            anchor,
            anchor
            + "import com.android.systemui.media.remedia.domain.interactor.MediaInteractor\n",
            1,
        )

    # inject mediaInteractor into ctor — after mediaCarouselInteractor
    if "private val mediaInteractor: MediaInteractor" not in text:
        ctor_a = "    val mediaCarouselInteractor: MediaCarouselInteractor,\n"
        if ctor_a not in text:
            raise RuntimeError("ShadeSceneContentViewModel mediaCarouselInteractor not found")
        text = text.replace(
            ctor_a,
            ctor_a + f"    private val mediaInteractor: MediaInteractor, {MARKER}\n",
            1,
        )

    if "val hasMediaCards" not in text:
        show_a = (
            "    val showMedia: Boolean by\n"
            "        // mediaCarouselInteractor.hasAnyMedia if in SplitShade.\n"
            "        mediaCarouselInteractor.hasActiveMedia.hydratedStateOf()\n"
        )
        show_b = (
            "    val showMedia: Boolean by\n"
            "        // mediaCarouselInteractor.hasAnyMedia if in SplitShade.\n"
            "        mediaCarouselInteractor.hasActiveMedia.hydratedStateOf()\n"
            "\n"
            f"    val hasMediaCards: Boolean {MARKER}\n"
            "        get() = mediaInteractor.hasAnyMedia\n"
            "\n"
            "    fun expandQuickSettings(loggingReason: String) {\n"
            "        sceneInteractor.changeScene(Scenes.QuickSettings, loggingReason)\n"
            "    }\n"
        )
        if show_a not in text:
            raise RuntimeError("ShadeSceneContentViewModel showMedia anchor not found")
        text = text.replace(show_a, show_b, 1)

    if "val qsContainerViewModel =" not in text:
        qqs = (
            "    private val qqsMediaInRowViewModel =\n"
            "        mediaInRowInLandscapeViewModelFactory.create(LOCATION_QQS, qqsMediaUiBehavior)\n"
            "\n"
            "    override suspend fun onActivated() {\n"
            "        coroutineScope { launch { qqsMediaInRowViewModel.activate() } }\n"
            "    }"
        )
        qqs_new = (
            "    private val qqsMediaInRowViewModel =\n"
            "        mediaInRowInLandscapeViewModelFactory.create(LOCATION_QQS, qqsMediaUiBehavior)\n"
            "\n"
            f"    val qsContainerViewModel = {MARKER}\n"
            "        qsContainerViewModelFactory.create(supportsBrightnessMirroring = true)\n"
            "\n"
            "    override suspend fun onActivated() {\n"
            "        coroutineScope {\n"
            "            launch { qqsMediaInRowViewModel.activate() }\n"
            "            launch { qsContainerViewModel.activate() }\n"
            "        }\n"
            "    }"
        )
        if qqs not in text:
            raise RuntimeError("ShadeSceneContentViewModel onActivated anchor not found")
        text = text.replace(qqs, qqs_new, 1)
    return text


def style_of_view_models() -> str:
    return (
        "/*\n"
        " * Copyright (C) 2026 The PenguinOS Project\n"
        " * SPDX-License-Identifier: Apache-2.0\n"
        " */\n"
        "\n"
        "package com.android.systemui.qs.shared.style\n"
        "\n"
        "import androidx.compose.runtime.Composable\n"
        "import androidx.compose.runtime.collectAsState\n"
        "import com.android.systemui.qs.composefragment.ConnectivityFolderExpansion\n"
        "import com.android.systemui.qs.ui.viewmodel.QuickSettingsContainerViewModel\n"
        "import com.android.systemui.shade.ui.viewmodel.ShadeSceneContentViewModel\n"
        "\n"
        "object PenguinQsStyle {\n"
        "    lateinit var repository: QsPanelStyleRepository\n"
        "}\n"
        "\n"
        "val QuickSettingsContainerViewModel.panelStyle: QsPanelStyle\n"
        "    @Composable get() = PenguinQsStyle.repository.style.collectAsState().value\n"
        "\n"
        "val ShadeSceneContentViewModel.panelStyle: QsPanelStyle\n"
        "    @Composable get() = PenguinQsStyle.repository.style.collectAsState().value\n"
        "\n"
        f"// {MARKER}\n"
        "fun ShadeSceneContentViewModel.onConnectivityFolderExpandRequested() {\n"
        "    ConnectivityFolderExpansion.expanded = true\n"
        "    expandQuickSettings(\"connectivity folder\")\n"
        "}\n"
    )


def stub_styled_shade_header() -> str:
    return """package com.android.systemui.shade.ui.composable

import androidx.compose.runtime.Composable
import androidx.compose.ui.unit.Density
import androidx.compose.ui.unit.Dp
import com.android.compose.animation.scene.ContentScope
import com.android.systemui.shade.ui.viewmodel.ShadeSceneContentViewModel

// PenguinOS: styles-qs-uwu-compat — stub until full ShadeScene header hooks land
@Composable
fun ContentScope.StyledShadeHeader(
    viewModel: ShadeSceneContentViewModel,
    mediaInRow: Boolean,
    horizontalPadding: Dp,
    visualOffset: Density.() -> Int,
) {
}
"""


def stub_control_centre_top() -> str:
    return """package com.android.systemui.qs.ui.composable

import androidx.compose.runtime.Composable
import com.android.compose.animation.scene.ContentScope
import com.android.systemui.qs.panels.ui.viewmodel.toolbar.ToolbarViewModel
import com.android.systemui.qs.shared.style.QsPanelStyle
import com.android.systemui.qs.shared.style.panelStyle
import com.android.systemui.qs.ui.viewmodel.QuickSettingsContainerViewModel

// PenguinOS: styles-qs-uwu-compat — stub (UwU has no ShadeStatusRow)
@Composable
fun ContentScope.ControlCentreTop(
    viewModel: QuickSettingsContainerViewModel,
    toolbarViewModel: ToolbarViewModel,
) {
}

@Composable
fun controlCentreTopShown(viewModel: QuickSettingsContainerViewModel): Boolean =
    viewModel.panelStyle == QsPanelStyle.Penguin || viewModel.panelStyle == QsPanelStyle.OneUi

@Composable
fun controlCentreWide(viewModel: QuickSettingsContainerViewModel): Boolean =
    viewModel.panelStyle == QsPanelStyle.Penguin
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", default="source")
    args = ap.parse_args()
    sysui = Path(args.source_dir) / "frameworks/base/packages/SystemUI"

    try:
        tile_kt = sysui / "src/com/android/systemui/qs/panels/ui/compose/infinitegrid/Tile.kt"
        tile_kt.write_text(patch_tile_colors(tile_kt.read_text(encoding="utf-8")), encoding="utf-8")
        print("[qs-uwu-compat] patched TileColors")

        write_if_changed(
            sysui / "src/com/android/systemui/qs/panels/ui/compose/TileGrid.kt",
            tile_grid_kt(),
            "TileGrid.kt",
        )

        gl = sysui / "src/com/android/systemui/qs/panels/ui/compose/GridLayout.kt"
        gl.write_text(patch_grid_layout(gl.read_text(encoding="utf-8")), encoding="utf-8")
        print("[qs-uwu-compat] patched GridLayout.kt")

        for rel in (
            "src/com/android/systemui/qs/panels/ui/compose/infinitegrid/InfiniteGridLayout.kt",
            "src/com/android/systemui/qs/panels/ui/compose/PaginatedGridLayout.kt",
        ):
            p = sysui / rel
            t = patch_impl_signature(p.read_text(encoding="utf-8"), p.name)
            if p.name == "InfiniteGridLayout.kt":
                t = patch_infinite_tile_sizing(t)
            p.write_text(t, encoding="utf-8")
            print(f"[qs-uwu-compat] patched {p.name}")

        cell = sysui / "src/com/android/systemui/qs/panels/ui/model/TileGridCell.kt"
        cell.write_text(patch_tile_grid_cell(cell.read_text(encoding="utf-8")), encoding="utf-8")
        print("[qs-uwu-compat] patched TileGridCell.kt")

        qs = sysui / "src/com/android/systemui/qs/shared/ui/QuickSettings.kt"
        qs.write_text(
            patch_quick_settings_elements(qs.read_text(encoding="utf-8")), encoding="utf-8"
        )
        print("[qs-uwu-compat] patched QuickSettings.kt")

        tgv = sysui / "src/com/android/systemui/qs/panels/ui/viewmodel/TileGridViewModel.kt"
        tgv.write_text(
            patch_tile_grid_viewmodel(tgv.read_text(encoding="utf-8")), encoding="utf-8"
        )
        print("[qs-uwu-compat] patched TileGridViewModel.kt")

        ssvm = sysui / "src/com/android/systemui/shade/ui/viewmodel/ShadeSceneContentViewModel.kt"
        ssvm.write_text(patch_shade_scene_vm(ssvm.read_text(encoding="utf-8")), encoding="utf-8")
        print("[qs-uwu-compat] patched ShadeSceneContentViewModel.kt")

        write_if_changed(
            sysui / "src/com/android/systemui/qs/shared/style/StyleOfViewModels.kt",
            style_of_view_models(),
            "StyleOfViewModels.kt",
        )
        write_if_changed(
            sysui / "src/com/android/systemui/shade/ui/composable/StyledShadeHeader.kt",
            stub_styled_shade_header(),
            "StyledShadeHeader.kt (stub)",
        )
        write_if_changed(
            sysui / "src/com/android/systemui/qs/ui/composable/ControlCentreTop.kt",
            stub_control_centre_top(),
            "ControlCentreTop.kt (stub)",
        )
    except Exception as e:
        return fail(str(e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
