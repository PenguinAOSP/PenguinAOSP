# FT08b: Volume panel style

> 状态: done（style 1/2/3 定制竖条可用；OneUI/MyUI 卡片展开手感可再调）
> 开关: PENGUIN_STYLES_VOLUME_PANEL (0/1, 默认 1)
> 目标: frameworks/base SystemUI volume dialog

## 1. 需求
Laboratory / `volume_panel_style`：0 系统默认；1 Expandable；2 OneUI；3 MyUI — 非 0 时出定制竖条音量面板。

## 2. 设计
- C：`VolumePanelLook` / `VolumePanelStyle` / `StyledVolumePanelLook` + dialog binder 副本
- B/Dagger：`PenguinHooksModule` `@Binds` + `@BindsOptionalOf` Optional\<VolumePanelLook\>
- Apply：`scripts/apply-styles-volume-panel.sh`

## 3. 验证
```bash
adb shell settings put secure volume_panel_style 1   # 或 2 / 3
adb shell input keyevent KEYCODE_VOLUME_UP
# 应见定制竖条；SystemUI 不崩
```

## 4. 已知问题
Optional MissingBinding、`VOLUME_PANEL_ON_LEFT` 字符串、AppVolume Interactor merge — 见 TROUBLESHOOTING。
