# FT09: Liquid Glass

> 状态: done（shade/QS/通知 MVP 可用；Launcher TabBar 后续）
> 开关: PENGUIN_LIQUID_GLASS_CORE (0/1, 默认 1)
> 目标: frameworks/base (core + ViewRootImpl) + SystemUI surfaces

## 1. 需求
Laboratory → Liquid Glass：`penguin_liquid_glass` 总开关；通知栏/QS 朦胧玻璃；可选 TabBar 玻璃。

## 2. 设计
- C：`com.android.internal.penguin.glass/*`（LiquidGlass shader、LiquidTabBars…）
- B：`ViewRootImpl` 注入 TabBars（MARKER `// PenguinOS: liquid-glass`）
- C：SystemUI `qs/shared/style/LiquidGlass.kt` + `ShadeColors.kt` + glyphs/strings
- B：`systemui_liquid_glass_surfaces.py`（MARKER `// PenguinOS: liquid-glass-surfaces`）
  - `NotificationBackgroundView`：`surfaceFor` / `drawGlassRim` / blur 闸门放行 glass
  - `ActivatableNotificationView`：`usesBlurredBackground` OR glass
  - `ScrimController`：监听 `penguin_liquid_glass` → 刷新 shade panel 色
  - `Tile.kt`：`glassRim` + inactive 表面用 `LiquidGlassSurface`
- **禁止**整份拷贝 penguinOS `ExpandableNotificationRow`/`ScrimController`（会拖入 `NTForbiddenSwipeDownQSController` / `ScrimUtils` / `QS_DUAL_TONE`）
- 框架改动需刷 `boot-framework.{art,oat,vdex}`（或 system 分区）；SystemUI 可热推

## 3. 涉及文件
| 目标 | 形式 | 位置 |
|------|------|------|
| `frameworks/base/core/java/com/android/internal/penguin/glass/*` | C | `vendor/penguin/files/.../glass/` |
| `ViewRootImpl.java` | B | `vendor/penguin/patches/framework_viewroot_liquid_glass.py` |
| SystemUI LiquidGlass/ShadeColors/glyphs | C | `vendor/penguin/files/frameworks/base/packages/SystemUI/...` |
| 通知/Scrim/Tile 触点 | B | `vendor/penguin/patches/systemui_liquid_glass_surfaces.py` |

## 4. Apply
`scripts/apply-liquid-glass-core.sh`（挂在 `apply-all.sh` / `PENGUIN_LIQUID_GLASS_CORE`）

## 5. 验证
```bash
adb shell settings put secure penguin_liquid_glass 1
adb shell cmd statusbar expand-notifications   # shade 更暗/半透明
adb shell cmd statusbar expand-settings        # QS tile 玻璃边+表面
adb shell settings put secure penguin_liquid_glass 0  # 恢复
```
framework：对比设备与 out 的 `boot-framework.vdex` md5；不一致则 remount 推送后 reboot。

## 6. 已知问题
- 整份 ENR/Scrim 拷贝会编不过 → 见 TROUBLESHOOTING
- Launcher 文件夹玻璃见 FT10；TabBars 由本 FT ViewRootImpl 覆盖
- 深色壁纸上 tile blur 对比度偏低；USB 调试通知在 glass on 时对比度可能偏弱

## 7. 上游失效风险
`setTint`/`usesBlurredBackground`/`TileExpandable`/`attachViews` 锚点漂移时修 python 补丁，不丢功能。
