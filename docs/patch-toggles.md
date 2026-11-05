# PenguinAOSP 补丁开关总表

所有 apply 脚本支持环境变量开关：`KEY=0` 跳过、`KEY=1`（或不设）应用。
开关默认值统一写在 `scripts/apply-all.sh` 顶部的 `PENGUIN_DEFAULTS` 中。

| KEY | 功能 | 默认 | apply 脚本 | 文档 |
|-----|------|------|------------|------|
| `PENGUIN_BRANDING` | PenguinAOSP 品牌（名称/版本/OTA 属性） | 1 | `scripts/apply-penguin-branding.sh` | `docs/features/branding.md`（待建） |
| `PENGUIN_CERRO_DEVICE` | cerro/sm8650 设备层（基座+Rising 优化，无 UDC） | 1 | `scripts/apply-cerro-device.sh` | `docs/features/dt01-cerro-device-layer.md` |
| `PENGUIN_LABORATORY` | PenguinLaboratory 应用（penguinOS 设置中心，独立 APK） | 1 | `scripts/apply-penguin-laboratory.sh` | `docs/features/ft01-penguin-laboratory.md` |
| `PENGUIN_SETTINGS_KEYS` | Settings.System 实验键常量（ls_media_* / back_to_app） | 1 | `scripts/apply-settings-system-keys.sh` | `docs/features/ft02-settings-system-keys.md` |
| `PENGUIN_SECURE_KEYS` | Settings.Secure 样式/玻璃/Dex/实验键常量 | 1 | `scripts/apply-settings-secure-keys.sh` | `docs/features/ft06-settings-secure-keys.md` |
| `PENGUIN_LAB_SETTINGS_ENTRY` | 设置→系统→Penguin Laboratory 入口 | 1 | `scripts/apply-settings-laboratory-entry.sh` | `docs/features/ft03-laboratory-settings-entry.md` |
| `PENGUIN_EDGELIGHTING` | 边缘发光（SystemUI EdgeLighting + Doze 接线） | 1 | `scripts/apply-edgelighting.sh` | `docs/features/ft04-edgelighting.md` |
| `PENGUIN_BACKTOAPP` | 状态栏返回上个应用指示 | 1 | `scripts/apply-backtoapp.sh` | `docs/features/ft05-backtoapp.md` |
| `PENGUIN_STYLES_POWER_MENU` | 关机菜单样式（iOS Slide-to-power） | 1 | `scripts/apply-styles-power-menu.sh` | `docs/features/ft08-styles-power-menu.md` |
| `PENGUIN_STYLES_VOLUME_PANEL` | 音量面板样式（Expandable/OneUI/MyUI） | 1 | `scripts/apply-styles-volume-panel.sh` | `docs/features/ft08-styles-volume-panel.md` |
| `PENGUIN_STYLES_QS_PANEL` | QS 整页样式（`qs_panel_style`，≠ UWU_QS_STYLE） | 1 | `scripts/apply-styles-qs-panel.sh` | `docs/features/ft08-styles-qs-panel.md` |
| `PENGUIN_LIQUID_GLASS_CORE` | 液态玻璃框架核心 + ViewRootImpl | 1 | `scripts/apply-liquid-glass-core.sh` | `docs/features/ft09-liquid-glass.md` |
| `PENGUIN_LAUNCHER_LIQUID_GLASS` | Launcher3 文件夹/预览玻璃 + TabBar 配套 | 1 | `scripts/apply-launcher-liquid-glass.sh` | `docs/features/ft10-launcher-liquid-glass.md` |
| `PENGUIN_LAUNCHER_MEMINFO` | 最近任务 RAM 信息行（MemInfoView） | 1 | `scripts/apply-launcher-meminfo.sh` | `docs/features/ft11-launcher-meminfo.md` |
| `PENGUIN_FREQUENT_APPS` | 最近任务常用应用行 | 1 | `scripts/apply-frequent-apps.sh` | `docs/features/ft07-frequent-apps.md` |
| `PENGUIN_UWU_BUILD_PREFIX` | `penguin_*` lunch → 设置 `UWU_BUILD`（BoardConfigUwU 门控） | 1 | `scripts/apply-penguin-uwu-build-prefix.sh` | `docs/features/dt01-cerro-device-layer.md` |
| `PENGUIN_WFD_AIDL_V5` | WFD 预编译库 AIDL V4→V5（Soong 多版本冲突） | 1 | `scripts/cerro/patch-wfd-aidl-v5.sh` | `docs/features/dt01-cerro-device-layer.md` |
| `PENGUIN_VENDOR_LFS` | nubia vendor Git LFS 拉取（radio/*.img 等） | 1 | `scripts/pull-vendor-lfs.sh` | `docs/features/dt01-cerro-device-layer.md` |
| `PENGUIN_HV_HAPTICS` | qcom-hv-haptics `name` 未初始化（clang -Werror） | 1 | `scripts/cerro/patch-qcom-hv-haptics.sh` | `docs/features/dt01-cerro-device-layer.md` |
| `PENGUIN_SYNX_UNINIT` | synx-kernel `entry`/`map_entry` 未初始化（clang -Werror） | 1 | `scripts/cerro/patch-synx-uninit.sh` | `docs/features/dt01-cerro-device-layer.md` |
| `PENGUIN_SDE_RM_PP` | sde_rm `_sde_rm_reserve_pp` `pp_cfg` 未初始化（clang -Werror） | 1 | `scripts/cerro/patch-sde-rm-pp-cfg.sh` | `docs/features/dt01-cerro-device-layer.md` |
| `PENGUIN_LAUNCHERAPPS_FORCE_STOP` | 补回 LauncherApps force-stop API（钉死的 fb tip 缺此提交） | 1 | `scripts/apply-launcherapps-force-stop.sh` | `docs/features/dt01-cerro-device-layer.md` |

用法示例：

```bash
PENGUIN_BRANDING=0 bash scripts/apply-all.sh   # 跳过品牌化
```
