# FT08: Styles — Power Menu

> 状态: done
> 开关: PENGUIN_STYLES_POWER_MENU (0/1, 默认 1)
> 目标仓库: frameworks/base/packages/SystemUI

## 1. 需求
Laboratory → Styles → Power menu：Penguin（默认网格）/ iOS（滑动关机）。

## 2. 设计
- C：`PowerMenuLayout` 接口 + `IosPowerMenuLayout`/`SlideToActView`/`GlobalActionsIosPowerDialog`/`PowerMenuStyle` + layout/drawable/values
- B：`GlobalActionsDialogLite` 注入 `Provider<PowerMenuLayout>`；`PenguinHooksModule` `@Binds`；`SystemUIModule` includes

## 3. Apply
`scripts/apply-styles-power-menu.sh` — MARKER `// PenguinOS: styles-power-menu`

## 4. 验证
`settings put secure power_menu_style 1` 后长按电源，应为 iOS 滑动条；`0` 恢复网格。
