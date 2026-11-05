# FT08c — QS Panel Styles（独立于 UwU QS）

> 状态: in-progress（SystemUI-core 已编通；待热推真机）
> 开关: `PENGUIN_STYLES_QS_PANEL`
> 目标仓库: `frameworks/base/packages/SystemUI`

## 目标

Laboratory `qs_panel_style` 驱动整页 QS（Penguin / OneUI / Harmony / MyUI…）。**不要**桥接 `UWU_QS_STYLE`；**不要**用 PenguinSystemUI 整包覆盖。Default 仍走 UwU 原路径。

## 落地

- C：`vendor/penguin/files/.../SystemUI` 下 QS style 树 + `PenguinQsPanels` / `PenguinHooksModule`
- B：`systemui_styles_qs_panel.py`（ViewModel + QuickSettingsContent takeover）
- B：`systemui_qs_uwu_compat.py`（UwU API 适配 + ShadeHeader stub）
- Apply：`scripts/apply-styles-qs-panel.sh`

## 验收

```bash
adb shell settings put secure qs_panel_style 1   # 或 penguin 枚举值
# 下拉 QS 应变为定制整页；0/Default 回 UwU
bash scripts/watch-systemui-stability.sh
```

## 已知缺口

- `StyledShadeHeader` / `ControlCentreTop` 暂 stub（缺 ShadeStatusRow 等）
- ShadeScene 侧完整 penguin 接线未全拷
