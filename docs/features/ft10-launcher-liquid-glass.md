# FT10 — Launcher Liquid Glass + TabBar 配套

> 状态: done（文件夹/预览玻璃已接线；TabBar 玻璃走 FT09 ViewRootImpl）
> 开关: `PENGUIN_LAUNCHER_LIQUID_GLASS`
> 目标仓库: `packages/apps/Launcher3`

## 目标

- 文件夹打开背景 / preview 图标描边走 `LiquidGlass`（`penguin_liquid_glass`）。
- 底部 App TabBar 玻璃由框架 `LiquidTabBars`（`penguin_glass_tab_bars*`）处理，不在 Launcher 内重做输入分发。

## 落地

- C：`vendor/penguin/files/packages/apps/Launcher3/.../util/LiquidGlass.kt`
- B：`vendor/penguin/patches/launcher3_liquid_glass.py` → `Folder.java` / `PreviewBackground.java`
- Apply：`scripts/apply-launcher-liquid-glass.sh`

## 验收

- 开 `penguin_liquid_glass` 后打开文件夹，背景透明度/rim 与 shade 玻璃一致感。
- 开 `penguin_glass_tab_bars` 后第三方底部导航栏出现玻璃层（framework 侧，与 Launcher 包无关）。

## 注意

- TabBar 依赖已推送的 `boot-framework.*`（见 FT09）；只热推 Launcher 不够。
