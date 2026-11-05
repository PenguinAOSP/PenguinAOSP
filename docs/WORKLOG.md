# PenguinAOSP 工作日志

> 规则（AGENTS.md 硬性规则）：**每次工作会话结束，必须在本文件追加一条日志**（新的在最上面）。
> 这是跨会话的连续性记录：下个 agent 读日志即可接上进度。

## 条目格式

```
## YYYY-MM-DD — <主题>
- 做了：
- 没做完 / 下一步：
- 产出（commit / 文档）：
```

---

## 2026-11-06 — 基座 sync 17.0.181 + 补丁重放
- 做了：
  - UwUAOSP release：`17.0.139` → **`17.0.181`**（`repo init -m default.xml` 后 `repo sync`；`frameworks/base` → `cf335ab632a8`）。
  - `bash scripts/apply-all.sh` 全层重放通过；修 `launcher3_meminfo.py`：`DeviceProfile` 与 `LauncherPrefs` 同包，不再强插 import（上游去掉 Utilities/Settings 锚点后会挂）。
  - penguinOS `celerity` 仍仅作参考（未合树）。
- 没做完 / 下一步：
  - 在 17.0.181 上重编 `otapackage` / 模块验证（SystemUI、Launcher3QuickStep）；真机接上后再热推。
  - 出包后若 SystemUI QS/shade 行为异常，对照 UwU 10/29–11/02 shade 手势相关提交。
- 产出：`vendor/penguin/patches/launcher3_meminfo.py`、本 WORKLOG、TROUBLESHOOTING。

## 2026-10-14 — QS Styles 编通 + Launcher 玻璃/MemInfo
- 做了：
  - **FT08c**：补 `systemui_qs_uwu_compat.py`（TileGrid includeSpecs/columnsOverride、TileColors.circleAroundIcon、TileGridCell.rows、QuickSettings.Elements、TileGridViewModel.largeTiles、ShadeScene VM hasMediaCards/expandQuickSettings/qsContainerViewModel；Stub StyledShadeHeader/ControlCentreTop；harmony 字符串 + brightness 图标）。`SystemUI-core` kotlinc 通过；signed APK 在 intermediates（`m SystemUI` 仍被 metalava/kernel 拖住）。
  - **FT10**：`apply-launcher-liquid-glass` 已打进 Folder/PreviewBackground；TabBar 仍靠 FT09 ViewRootImpl。
  - **FT11**：MemInfoView 整链 apply（overview_panel / RecentsView.init / QuickstepLauncher / Fallback / RecentsWindowManager）；挂 `PENGUIN_LAUNCHER_MEMINFO`。
- 没做完 / 下一步：
  - **SystemUI + Launcher3QuickStep 均已编通**（含 oat）；当前 adb 是三星 `b5q` user，不是 cerro — 接上 Z60 Ultra userdebug 后再 remount 热推验 `qs_panel_style` / 文件夹玻璃 / MemInfo。
  - Launcher 下一批：TaskChanger / IconPack / Trust（未开做）。
- 产出：compat 脚本、FT10/FT11、apply-launcher-meminfo、patch-toggles、本 WORKLOG。
- 产物路径：
  - `source/out/target/product/cerro/system_ext/priv-app/SystemUI/{SystemUI.apk,oat/arm64/*}`
  - `source/out/target/product/cerro/system_ext/priv-app/Launcher3QuickStep/{Launcher3QuickStep.apk,oat/arm64/*}`

## 2026-10-14 — Styles + Liquid Glass 真机可用（续）
- 做了：
  - 回退 ENR/Scrim 整份拷贝；glass 收敛为 LiquidGlass+ShadeColors + `systemui_liquid_glass_surfaces.py`（通知 tint/rim、blur 闸门、Scrim 监听、Tile glassRim）。
  - 编通 `framework-minus-apex`/`services` + SystemUI；remount 推 `boot-framework.{art,oat,vdex}` + services 后 reboot；再热推 SystemUI apk/odex/vdex。
  - 真机：`penguin_liquid_glass=1/0` 下拉 shade/QS 外观有差；与 `volume_panel_style=1` 竖条同屏共存；watch 稳定。
  - Power/Volume 样式此前已验证；FT08b/FT09 文档标 done（MVP）。
- 没做完 / 下一步：
  - **FT08c `qs_panel_style`**（≠ `UWU_QS_STYLE`，勿桥接；禁 PenguinSystemUI 整包覆盖）— 见 `docs/features/ft08-styles-qs-panel.md`；
  - Launcher LiquidGlass / TabBars 未接。
- 产出：`systemui_liquid_glass_surfaces.py`、更新 `apply-liquid-glass-core.sh`、FT09/FT08b、FT08c draft、TROUBLESHOOTING 整份拷贝条目、本 WORKLOG。

## 2026-10-14 — Styles + Liquid Glass（FT08/FT08b/FT09）
- 做了：
  - **Power Menu（FT08）**：修好 iOS 布局 NPE（`onStart`/`startAnimation` 空布局）后热推；`power_menu_style=1` 真机见 slide-to-power-off / restart / SOS；稳定性 60s OK。
  - **Volume（FT08b）**：接入 `VolumePanelLook`/`StyledVolumePanelLook`/`ExpansionInteractor` + dialog binders；热推后 `volume_panel_style` 1/2/3 均出定制竖条面板；SystemUI 稳定。
  - **Liquid Glass（FT09）**：落地 core java + ViewRootImpl 补丁 + SystemUI LiquidGlass/ShadeColors/通知栈触点到 vendor；开关 `PENGUIN_LIQUID_GLASS_CORE`。
- 没做完 / 下一步：见上条「续」。
- 产出：`apply-styles-volume-panel.sh`、`apply-liquid-glass-core.sh`、FT08b/FT09 文档、`systemui_power_menu_style.py` null-guard、TROUBLESHOOTING 条目。

## 2026-10-13 — OTA 刷入验证（FT02–FT07）
- 做了：`penguin_cerro-ota.zip`（05:55 编成）sideload 成功；`boot_completed=1`；system fingerprint `userdebug/test-keys`；Laboratory 可启动；SystemUI 含 EdgeLighting/BackToApp；Launcher 含 FrequentApps；`back_to_app_indicator`/`recents_frequent_apps` 可写。07:30 后未再移植。
- 没做完 / 下一步：UI 手测 EdgeLighting 预览、BackToApp 指示、设置→系统入口、FrequentApps 行；Styles/LiquidGlass/Dex 等大块等你说再移植。
- 产出：刷机验证记录（本条）。

## 2026-10-13 — 无人值守移植 batch1（FT02–FT07）+ otapackage
- 做了：Settings.System/Secure 键、Settings→Laboratory 入口、EdgeLighting+Doze、BackToApp（UwU 无 launchedFrom* 已改写 Tracker）、FrequentApps；修 metalava/@hide/重复键；`run-cerro-detached` 编通 OTA。
- 没做完 / 下一步：见上条刷机验证；Styles/LiquidGlass/Dex 未做。
- 产出：FT02–FT07 补丁/文档/开关；`penguin_cerro-ota.zip`。

## 2026-10-12 — 无信号：排线松（非软件）

- 做了：排查到 `RF_HARDWARE_ISSUE`；重刷 modem 无效且**未合入信号补丁**。用户复座排线后 `IN_SERVICE`/`NR_SA`。文档改为硬件根因，明确不加软件修复。

## 2026-10-12 — 卡第二屏修复 + 同步 ArtistAOSP AGENTS/工具
- 做了：日志定位 system_server FATAL（Laboratory `WRITE_SECURE_SETTINGS` 不在 privapp allowlist）；根因是白名单装成无 `.xml` 后缀。修 `Android.bp` `filename`；挂载修补 `system_ext.img` 后 fastbootd 刷入，`boot_completed=1`。从 `rong@192.168.0.229:/mnt/data/ArtistAOSP` 同步 AGENTS 硬性规则 9–13（真机验证/监控/降温/禁止偷懒验收）与工具：`watch-systemui-stability.sh`、`validate-penguinaosp-tree.sh`、`sync-status.sh`、`prepare-build-swap.sh`、`unlimit-build-env.sh`。
- 没做完 / 下一步：下次完整 otapackage 需带上 filename 修复；品牌层仍占位；未要求前不 commit。
- 产出：vendor Laboratory bp、AGENTS、TROUBLESHOOTING、上述 scripts。

## 2026-10-12 — M1 首次 otapackage 成功（penguin_cerro）
- 做了：独立 `setsid nohup` 编译 + `watch-cerro-build` 盯日志；修通 LFS（nubia + pixel/gms）、内核三 -Werror、sysfs_fan sepolicy、LauncherApps force-stop、宿主 zip 等。
- 结果：`#### build completed successfully`；产物 `source/out/target/product/cerro/penguin_cerro-ota.zip`。
- 没做完 / 下一步：刷机验证 first boot；品牌层仍占位；未要求前不 commit。
- 产出：若干 apply 开关/补丁 + `scripts/run-cerro-detached.sh` / `watch-cerro-build.sh`。

## 2026-10-11 — M1 产品接入收尾（penguin_cerro + apply/试编）
- 做了：产品 mk / UWU_BUILD / WFD / build-cerro；Soong 两阶段与 OOM 缓解起步。
- 没做完：当时未编通（后续见上条）。
- 产出：见 git status / 功能文档。


## 2026-10-11 — 项目立项与工程骨架（M0）
- 做了：
  - 调研确定基座：UwUAOSP（Android 17，`uwu-17.0` / release manifest `platform_vendor_uwu-versions@main`）；penguinOS（AOSPA fork）仅作参考不采用。
  - 写工程骨架方案 `docs/SKELETON.md`；建立目录骨架（vendor/penguin、patches、scripts、devices/nubia/cerro、docs 体系）。
  - 写 `AGENTS.md`（含工作日志、功能文档、git 规范）；初始化本仓库 git。
- 没做完 / 下一步：
  - `scripts/init-uwu-source.sh` 尚未实际跑过一次完整 sync（约需大空间 + 代理）。
  - cerro 设备树迁移（M1）：参考本地 `MikuUI_cerro` / `RisingOS_cerro`，及 `AlphaDroid_Oneplus12/device/oneplus/sm8650-common` 组织方式。
  - `build-cerro.sh` 为占位，待 M1 补全。
- 产出：本仓库首个 commit；`docs/SKELETON.md`、`AGENTS.md`、docs 体系初始化。

## 2026-10-11 — cerro 设备层导入（DT01）
- 做了：
  - 确认 Rising cerro 基座 = nubia-sm8650-devs（lineage-23.2）；Rising 优化 = device-overlay 增量（经全量 diff 确认）。
  - 克隆基座到 devices/nubia/{cerro,sm8650-common}（commit 记录于 BASE.md），叠加 overlay 并剔除 UDC 三处（SystemUIResCerro RRO / FrameworksResTarget_Vendor config.xml / patch_udc_camera_protection.py）。
  - local_manifests/cerro.xml（自定义 remote nubia，避开 UwU manifest remote 名）；init-uwu-source.sh 自动安装。
  - scripts/apply-cerro-device.sh 挂 apply-all 第 1 层，开关 PENGUIN_CERRO_DEVICE；导入 Rising 驱动编译修复 4 个到 scripts/cerro/（未挂链，M1 验证）。
- 没做完 / 下一步：
  - source 同步已启动（后台，UwU release manifest + cerro local manifest）。
  - M1: UwU 树上接入 penguin_cerro 产品（lunch 前缀 penguin_）、vendor/lineage 依赖确认、scripts/cerro 补丁逐个验证。
- 产出：commit（devices/scripts/docs）；docs/features/dt01-cerro-device-layer.md。

## 2026-10-11 — penguinOS 功能盘点（移植规划输入）
- 做了：克隆 penguinOS 6 个参考仓库到 reference/penguinos/；确认专属功能不在 Settings（只有入口+3 widget），核心是独立应用 PenguinLaboratory + frameworks_base SystemUI 内嵌 penguin/ 包 + 独立 APK（PenguinSystemUI/PenguinDex）；产出 docs/penguinos-feature-inventory.md（功能×设置键×消费端×依赖 全表 + 移植顺序建议）。
- 没做完 / 下一步：M3 按盘点顺序移植；sync 修复循环仍在后台跑。
- 产出：docs/penguinos-feature-inventory.md；参考树 reference/penguinos/（gitignore）。
