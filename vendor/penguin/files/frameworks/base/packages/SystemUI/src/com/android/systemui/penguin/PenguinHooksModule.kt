/*
 * Copyright (C) 2026 The PenguinOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

package com.android.systemui.penguin

import com.android.systemui.globalactions.IosPowerMenuLayout
import com.android.systemui.volume.StyledVolumePanelLooks
import com.penguin.systemui.qs.PenguinQsPanels
import com.penguin.systemui.qs.PenguinShadeMotion
import dagger.Binds
import dagger.BindsOptionalOf
import dagger.Module

/** Penguin style hooks bound into SystemUI. */
@Module
abstract class PenguinHooksModule {
    // PenguinOS: styles-power-menu
    @Binds abstract fun powerMenuLayout(impl: IosPowerMenuLayout): PowerMenuLayout

    // PenguinOS: styles-volume-panel — Optional inject sites + concrete bind
    @BindsOptionalOf abstract fun optionalVolumePanelLooks(): VolumePanelLooks

    @Binds abstract fun volumePanelLooks(impl: StyledVolumePanelLooks): VolumePanelLooks

    // PenguinOS: styles-qs-panel
    @BindsOptionalOf abstract fun optionalQsPanels(): QsPanels

    @Binds abstract fun qsPanels(impl: PenguinQsPanels): QsPanels

    @BindsOptionalOf abstract fun optionalShadeMotion(): ShadeMotion

    @Binds abstract fun shadeMotion(impl: PenguinShadeMotion): ShadeMotion
}
