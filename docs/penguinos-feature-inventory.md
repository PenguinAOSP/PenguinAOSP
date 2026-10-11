# penguinOS 功能盘点（供移植规划）

> 2026-10-11 基于参考树 `reference/penguinos/`（浅克隆 celerity 分支）实际源码盘点。
> 结论先行：**penguinOS 的专属功能没有一个"Settings 里的大类"** —— 专属功能集中在独立应用
> **PenguinLaboratory**（`com.penguin.laboratory`，Compose + Material3 Expressive 写的设置中心），
> Settings 应用里只有入口 + 3 个 widget；**真正的功能实现在 frameworks_base 的 SystemUI 内嵌 `penguin/` 包**
> 以及独立 APK **PenguinSystemUI**、**PenguinDex**、Launcher3 定制里。Laboratory 只负责写 `Settings.Secure/System` 键。

## 1. 参考树克隆清单

| 仓库 | 本地路径 | 大小 |
|------|----------|------|
| packages_apps_Settings | `reference/penguinos/packages_apps_Settings` | 439M |
| penguin_packages_apps_PenguinLaboratory | `reference/penguinos/packages_apps_PenguinLaboratory` | 5.4M |
| penguin_packages_apps_PenguinSystemUI | `reference/penguinos/penguin_packages_apps_PenguinSystemUI` | 2.4M |
| frameworks_base | `reference/penguinos/frameworks_base` | 2.9G |
| packages_apps_Launcher3 | `reference/penguinos/packages_apps_Launcher3` | 63M |
| vendor_custom-preference | `reference/penguinos/vendor_custom-preference` | 572K |
| manifest | `reference/penguinos/manifest` | — |

## 2. Settings 侧（com.android.settings）的 penguin 足迹

- `src/com/penguin/widget/`：`ShrinkablePreference`（my_device_info 用）、`WallpaperBlurView`、`DeviceNameTextView` —— 仅 UI 小件；
- `res/values/pengu_strings.xml` + `system_dashboard_fragment.xml`：唯一入口 "Penguin Laboratory" → 跳转 `com.penguin.laboratory/.LaboratoryActivity`；
- **Settings 内没有 penguin 专属功能类**；`co/aospa/settings/*`（charging control 等）和 `custom/`（font/monet/networktraffic/obscura/smartpixel/spoofing）是 AOSPA 系遗留，**不是 penguin 专属**，是否移植另议（UwU 大概率已有等价物）。

## 3. PenguinLaboratory 功能模块与设置键总表

### 3.1 Styles（样式）—— 全部 `Settings.Secure`
| 键 | 功能 | 消费端 |
|----|------|--------|
| `power_menu_style` | 关机菜单样式 | fb SystemUI `globalactions/GlobalActionsDialogLite.java` + `penguin/PowerMenuLayout.java`；独立 APK `globalactions/PowerMenuStyle.java` |
| `qs_panel_style` | QS 面板样式 | fb SystemUI `qs/shared/style/QsPanelStyle.kt`（同路径也在独立 APK）、`qs/panels/ui/compose/PenguinPanelLayout.kt`、`PenguinEditMode.kt`、`StyledQuickSettingsContent.kt` |
| `volume_panel_style` | 音量面板样式 | fb SystemUI `penguin/VolumePanelLook.kt`、`volume/dialog/**`（SlidersViewBinder 等）；独立 APK `volume/VolumePanelStyle.kt` |
| `qs_connectivity_folder` | QS 网络文件夹 | 独立 APK `qs/composefragment/ConnectivityFolder.kt` |
| `qs_oneui_experimental` | OneUI 风格 QS（实验） | 同 QS 面板样式族 |

### 3.2 Experiments（实验开关）—— `ExperimentsStore`（ExperimentsActivity.kt）
| 键 | 表 | 功能 | 消费端 |
|----|----|------|--------|
| `ls_media_expand` | System | 锁屏媒体展开 | fb SystemUI `compose/features/.../MediaElementProvider.kt`、`penguin/LockscreenPlayer.kt` |
| `ls_media_motion_art` | System（依赖 ls_media_expand） | 媒体动效 art | 同上 + `Settings.LS_MEDIA_ART_AOD_ENABLED/_DIM_LEVEL`（AOD 联动） |
| `depth_wallpaper_floating` | Secure | 景深壁纸浮动时钟 | fb SystemUI `penguin/DepthSubject.kt`、`util/WallpaperDepthUtils.java`、`ScrimController.java` |
| `qs_oneui_experimental` | Secure | 见上 | 同上 |
| `back_to_app_indicator` | System | 返回上个应用指示 | fb SystemUI `statusbar/backtoapp/BackToAppLabel.kt` + `BackToAppTracker.kt`、`StatusBarRoot.kt` |
| `recents_frequent_apps` | Secure | 最近任务常用应用行 | Launcher3 `quickstep/.../FrequentAppsView.java`、`DeviceProfile.java` |

框架侧键常量加在 `frameworks_base/core/java/android/provider/Settings.java`（~L7455 起：`LS_MEDIA_EXPAND/EXPANDED/MOTION_ART`、`BACK_TO_APP_INDICATOR` 等）。

### 3.3 Glass（液态玻璃）
| 键 | 功能 | 消费端 |
|----|------|--------|
| `penguin_liquid_glass` | 液态玻璃效果总开关 | fb SystemUI `qs/shared/style/LiquidGlass.kt`；fb core `com.android.internal.penguin.glass/{LiquidGlass,ComposeTabBar,LiquidMotion,LiquidTabBar,LiquidTabBars}.java`、`ViewRootImpl.java`；Launcher3 `util/LiquidGlass.kt`；`NotificationGlassPress.java` |
| `penguin_glass_tab_bars` (+`_excluded`、`_float`) | 底部 Tab 栏玻璃化 | 同上 LiquidTabBars 族 + Launcher3 |

### 3.4 PenguinDex（桌面模式）
| 键 | 功能 | 消费端 |
|----|------|--------|
| `penguin_dex_dock` / `penguin_dex_launchpad` / `penguin_dex_touchpad` / `penguin_dex_control_centre` | Dex 停靠/启动器/触控板/控制中心 | 独立仓库 `penguin_packages_apps_PenguinDex` + fb SystemUI `statusbar/phone/DexStatusBar.kt` |
| `mirror_built_in_display` | 内屏镜像 | PenguinDex / WM 侧（`services/core/.../WindowManagerService.java` 有 penguin 触点） |

### 3.5 EdgeLighting（边缘发光）
- 不走 Settings 键：Laboratory 内置 **ContentProvider** `com.penguin.laboratory.provider/state`（读权限 `android.permission.STATUS_BAR_SERVICE`）；
- 消费端：fb SystemUI `edgelighting/EdgeLightingController.java`、`EdgeLightingView.java`、`dagger/SystemUIModule.java`（DI 注入）；
- 素材：`Cutouts.java`、`Stickers.java`（发光形状/贴纸）。

### 3.6 Wonderland（3D 景深壁纸）
- `WonderlandWallpaperService`（BIND_WALLPAPER）+ `WonderlandEditorActivity`；
- **闭源/外部依赖重**：`libs/` 预编译 AAR（common-18.10.0、play-services-mlkit-subject-segmentation 16.0.0-beta1、firebase、image-1.0.0-beta1）——MLKit 抠图走 Play Services；
- `TiltSensor.java`、`SceneRenderer.java`（OpenGL 渲染）。

## 4. 消费端足迹统计（frameworks_base，共 72 个文件含 penguin 触点）

- `packages/SystemUI`：53 文件。核心是 `src/com/android/systemui/penguin/` 独立包（`PenguinHooksModule.kt`、`DepthSubject`、`LockscreenPlayer`、`QsPanels`、`ShadeMotion`、`StatusBarIsland`、`PowerMenuLayout`、`VolumePanelLook`）+ `backtoapp/` + `edgelighting/` + Compose scene/qs/media 各处插入点 + `res/values/custom_{config,strings,dimens}.xml`；
- `core/res`：12 文件（anim 转场动画等）；
- `core/java`：6 文件（`internal/penguin/glass/*`、`Settings.java`、`ViewRootImpl`）；
- `services/core`：1 文件（`WindowManagerService`）。

## 5. 移植要点 / 依赖性质分类

| 类别 | 内容 | 移植策略 |
|------|------|----------|
| **纯设置键 + 双端读写** | styles/experiments/glass/dex 键 | 键名可原样沿用（`Settings.java` 加常量的 B 类补丁） |
| **SystemUI 内嵌功能** | penguin/ 包、backtoapp、edgelighting、QsPanelStyle、PowerMenuLayout… | **重锚点移植**：penguinOS 的 SystemUI 是 AOSPA 系（scene/compose 结构），UwU 的 SystemUI 是 Lineage 系，逐文件读实现后在 UwU 对应类重写；这是主要工作量 |
| **独立 APK** | PenguinLaboratory、PenguinSystemUI、PenguinDex、PenguinSetupWizard | C 类 vendor 副本整体移植（自带 libs/ AAR，构建相对独立），注意 Laboratory 依赖 Play Services MLKit（无 GMS 设备上 wonderland/景深抠图降级） |
| **闭源 AAR 依赖** | Laboratory `libs/common-18.10.0.aar` 等 | 直接随 APK 拷贝，无法源码审计 |
| **Launcher3 定制** | FrequentAppsView、LiquidGlass | UwU 用自家 Launcher 需先确认，若同 Launcher3 系可 B 类补丁 |
| **AOSPA 遗留（非 penguin 专属）** | charging control、spoofing、smart pixel、obscura、network traffic、Glymps… | 先查 UwU（uwuSettingsExt）等价物，多数可跳过 |

## 6. 建议移植顺序（M3）

1. Experiments 六开关 + 框架键常量（量小、立刻有"专属感"）；
2. EdgeLighting（provider + SystemUI 控制器，边界清晰）；
3. BackToApp 指示（SystemUI 单点）；
4. recents_frequent_apps（Launcher3 单文件级）;
5. Styles 三件套（QS/音量/关机菜单 —— 工作量最大，需先把 UwU SystemUI 的对应面板摸清）；
6. Liquid Glass 族（框架 core + SystemUI + Launcher3 三端联动，最后做）；
7. PenguinDex / Wonderland（体量与外部依赖最大，可选）。
