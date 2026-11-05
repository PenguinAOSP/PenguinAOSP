# FT01: PenguinLaboratory 应用移植

> 状态: done（已进 OTA；privapp `.xml` 后缀热修后 boot_completed=1）
> 开关: `PENGUIN_LABORATORY` (0/1, 默认 1)
> 目标仓库: `source/packages/apps/PenguinLaboratory`（C 类整包副本）+ cerro 产品引用

## 1. 需求描述

把 penguinOS 的专属功能设置中心 **PenguinLaboratory**（`com.penguin.laboratory`）移植进 PenguinAOSP。它是独立 APK（Compose + Material3 Expressive，自带预编译 AAR），负责写入/提供 penguin 功能的全部设置键（styles / experiments / glass / dex）与 EdgeLighting 的 ContentProvider。完整功能盘点见 `docs/penguinos-feature-inventory.md`。

## 2. 设计

- **C 类整包移植**：`vendor/penguin/files/packages/apps/PenguinLaboratory/`（源码 + `libs/` 预编译 AAR + privapp 权限 XML），apply 时 rsync 进 `source/packages/apps/PenguinLaboratory`；
- 来源 commit：penguinOS `penguin_packages_apps_PenguinLaboratory @ celerity`（2026-10-11 浅克隆）；
- 产品引用：`devices/nubia/cerro/device.mk` 加 `PRODUCT_PACKAGES += PenguinLaboratory`（system_ext priv-app）；
- APK 特性（上游 Android.bp 原样）：`sdk_version: current`、`privileged: true`、`system_ext_specific: true`、`optimize disabled`（MLKit 反射需要）；
- **第一轮只带应用本体**（纯增量，不碰 SystemUI/框架）；各功能消费端（SystemUI 的 penguin/ 包、glass 框架包等）按 `docs/penguinos-feature-inventory.md` §6 顺序后续轮次移植——第一轮里这些开关无效果属预期。
- **Material Symbols AAR**：UwU 树不提供 `com.composables_icons-material-symbols-rounded-filled-android`；已将 Maven Central `com.composables:icons-material-symbols-rounded-filled-android:2.2.1` 落盘为 `libs/icons-material-symbols-rounded-filled-android-2.2.1.aar`，并在 `Android.bp` 用 `android_library_import` 注册同名模块。

## 3. 涉及文件

| 目标路径 | 形式 | 真相源 |
|----------|------|--------|
| `source/packages/apps/PenguinLaboratory/**` | C | `vendor/penguin/files/packages/apps/PenguinLaboratory/` |
| `.../libs/icons-material-symbols-rounded-filled-android-2.2.1.aar` | C | 同上 `libs/` |
| `source/device/nubia/cerro/device.mk`（PRODUCT_PACKAGES） | 随 cerro 设备层 | `devices/nubia/cerro/device.mk` |

## 4. Apply 链接入

- 脚本: `scripts/apply-penguin-laboratory.sh`（rsync 镜像，幂等）
- 挂载: `apply-all.sh` LAYERS（在 uwu-build-prefix 之后、cerro-device 之前）；开关 `PENGUIN_LABORATORY`

## 5. 验证方法

- 编译通过：`m otapackage`（或 `bash scripts/build-cerro.sh`）产物含 `system_ext/priv-app/PenguinLaboratory/PenguinLaboratory.apk`；
- 设备上（后续轮次）：设置 → 系统 底部 "Penguin Laboratory" 入口可打开。

## 6. 已知问题与坑

- Material Symbols 已用预编译 AAR 补齐；若 Soong 仍报缺模块，检查 apply 是否把 `libs/` 同步进 `source/packages/apps/PenguinLaboratory`；
- wonderland/景深模块依赖 Play Services MLKit，VANILLA 包上运行时会降级（不影响编译）。
- **`prebuilt_etc` 必须设 `filename: "...xml"`**：否则装到 `/system_ext/etc/permissions/` 无后缀，PackageManager 不加载 → system_server 因 `WRITE_SECURE_SETTINGS` 不在 allowlist 而 FATAL，卡第二屏（见 `docs/TROUBLESHOOTING.md` 2026-10-12）。

## 7. 上游失效风险

- 上游 penguinOS Laboratory 更新时重拷贝 `vendor/penguin/files/` 即可（整包替换，无锚点漂移问题）。
