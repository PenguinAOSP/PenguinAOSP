# DT01: cerro/sm8650 设备层（基座 + Rising 驱动优化，无 UDC）

> 状态: wip（设备层导入 done；M1 产品接入 / 试编进行中）
> 开关: `PENGUIN_CERRO_DEVICE`、`PENGUIN_UWU_BUILD_PREFIX`、`PENGUIN_WFD_AIDL_V5` (0/1, 默认 1)
> 目标仓库: `source/device/nubia/*`（由本仓库 `devices/nubia/` 镜像）+ `local_manifests/cerro.xml` 注入的 kernel/vendor 仓库 + `source/build/make/core/config.mk`（UWU_BUILD 前缀补丁）

## 1. 需求描述

为 PenguinAOSP 提供 cerro (Nubia Z60 Ultra, SM8650) 设备层：以 `nubia-sm8650-devs`（lineage-23.2）为基座，叠加 RisingOS cerro 工程验证过的驱动优化；**按用户要求剔除全部屏下摄像头（UDC）相关改动**。M1 起提供可 lunch 的 `penguin_cerro` 产品，并挂上 UwU 编译门控与已知 Soong 阻塞补丁。

## 2. 设计（来源与决策）

- RisingOS cerro 的 `device-overlay` 是它对 nubia-sm8650-devs 基座的改动层（经 diff 确认基座树已自带 touch/fingerprint/parts 等大部分硬件组件）；
- 因此本功能的构成 = **基座树（git clone，commit 记录在 `devices/nubia/BASE.md`）+ overlay 增量（rsync）- UDC 三处**；
- kernel / devicetrees / modules / proprietary vendor 仓库不落本仓库（体积大且未改动），走 `local_manifests/cerro.xml` 在 repo sync 时拉进 `source/`（remote 自定义名 `nubia`，避开 UwUAOSP manifest 的 `aosp/lineageos/github/gitlab`）；
- 设备层仍是"基座原味 + 明确列出的优化"，便于逐项溯源。

### M1 产品接入（`penguin_cerro`）

- `devices/nubia/cerro/penguin_cerro.mk`：`PRODUCT_NAME := penguin_cerro`，继承 `device.mk` + `vendor/uwu/config/common.mk`；显式 `UWU_BUILD := cerro`（须在 inherit 前）。
- `AndroidProducts.mk`：注册 `penguin_cerro.mk` 与 lunch choices；`lineage_cerro` 保留作对照。
- **UWU_BUILD 门控**：UwU 的 `BoardConfigUwU.mk` / QCOM WiFi Soong namespaces 等依赖 `UWU_BUILD`。上游 `build/make/core/config.mk` 只从 `uwu_*` 推导；`PENGUIN_UWU_BUILD_PREFIX`（B 类 Python）在同文件为 `penguin_*` 增加等价推导，MARKER `# PenguinOS: penguin_uwu_build_prefix`。
- **NubiaParts / NubiaGameSwitch**：暂注释（依赖 UwU 不带的 LineageParts）；后续单独功能文档再移植。
- **WFD AIDL V5**：`scripts/cerro/patch-wfd-aidl-v5.sh` 已挂 apply 链（`PENGUIN_WFD_AIDL_V5`），改 `vendor/nubia/sm8650-common/Android.bp`（local_manifest 拉的 blob 树，非 devices/ 真相源）。
- 构建入口：`scripts/build-cerro.sh` → apply-all → `lunch penguin_cerro-cp2a-userdebug` → `m otapackage`（UwU 无 Lineage `mka`/`bacon`）。

### 已剔除的 UDC 相关项（完整清单）

见 `devices/nubia/BASE.md` 的表格：`SystemUIResCerro` RRO、`FrameworksResTarget_Vendor/res/values/config.xml`（diff 仅 UDC cutout）、Rising 的 `patch_udc_camera_protection.py`。`device.mk` 中对 SystemUIResCerro 的引用已移除并留 `# PenguinOS:` 注释。

### 保留的 Rising 驱动优化（本层相对基座的全部增量）

| 文件 | 优化内容 |
|------|----------|
| `sm8650-common/vendor.prop` | SF 调度参数（idle/display_power/touch timer、HDR、game_default_frame_rate_override、gl_backpressure 等）+ perf-hal 3.0/framepacing + smooth_motion |
| `cerro/vendor.prop` | SF timer 三件套（对齐 OP12 waffle）+ `persist.vendor.camera.use_aux=1`（副摄镜头，非 UDC） |
| `sm8650-common/common.mk` + `configs/perf/*.xml` | perfboostsconfig / perfconfigstore 装入 vendor |
| `sm8650-common/rootdir/etc/init.target.rc` | camera-daemon cpuset 收窄 0-5（CERRO_CAMERA_CPUSET） |
| `sm8650-common/TouchscreenRotation/` | 解锁后触控恢复（touch recovery）逻辑 |
| `sm8650-common/sepolicy/` | devicesettings_app coredomain、platform_app_36 相机 API 36 允许规则等 |
| `cerro/overlay/LineageSdkResCerro/` | Nubia 侧边滑块（NubiaGameSwitch）接入 key handler |
| `cerro/device.mk` | 上述 RRO +（暂缓）NubiaParts + 相机 watermark/dualcali bootstrap（后摄，非 UDC） |
| `cerro/AndroidProducts.mk` / `penguin_cerro.mk` / `lineage_cerro.mk` | lunch：`penguin_cerro-*` 为主；`lineage_cerro` 对照 |
| `sm8650-common/BoardConfigCommon.mk` | 内核编译修复：`TARGET_KERNEL_ADDITIONAL_FLAGS`（pineapple conf 选择、PERL 路径） |
| `sm8650-common/build/host-bin/perl` | 内核 Makefile 的 perl PATH 包装 |

## 3. 涉及文件

| 目标路径 | 形式 | 真相源位置 |
|----------|------|------------|
| `source/device/nubia/cerro/**` | C（整树镜像） | `devices/nubia/cerro/`（含 `penguin_cerro.mk`） |
| `source/device/nubia/sm8650-common/**` | C（整树镜像） | `devices/nubia/sm8650-common/` |
| `source/.repo/local_manifests/cerro.xml` | C | `local_manifests/cerro.xml` |
| `source/build/make/core/config.mk` | B | `vendor/penguin/patches/build_make_penguin_uwu_build.py` |
| `source/vendor/nubia/sm8650-common/Android.bp` | 脚本就地改（blob 树） | `scripts/cerro/patch-wfd-aidl-v5.sh` |

## 4. Apply 链接入

| 层 | 脚本 | 开关 | 顺序说明 |
|----|------|------|----------|
| penguin-uwu-build-prefix | `scripts/apply-penguin-uwu-build-prefix.sh` | `PENGUIN_UWU_BUILD_PREFIX` | 尽早；lunch 前 config.mk 已带 penguin_* |
| cerro-device | `scripts/apply-cerro-device.sh` | `PENGUIN_CERRO_DEVICE` | rsync `--delete` 镜像 devices/ |
| wfd-aidl-v5 | `scripts/cerro/patch-wfd-aidl-v5.sh` | `PENGUIN_WFD_AIDL_V5` | 在 cerro-device 之后；改 vendor blob Android.bp |

- local manifest: `scripts/init-uwu-source.sh` 在 repo init 后自动拷入 `.repo/local_manifests/`
- 幂等：UWU 前缀看 MARKER；WFD 看 V5 + `check_elf_files: false`；设备层 rsync 全量覆盖

## 5. 验证方法

```bash
bash scripts/apply-all.sh                      # 上述三层 + laboratory + branding 应成功
diff -rq devices/nubia/cerro source/device/nubia/cerro          # 应无差异
diff -rq devices/nubia/sm8650-common source/device/nubia/sm8650-common
grep -r UdcCameraProtect source/device/nubia/                   # 应无结果（UDC 已剔除）
grep 'PenguinOS: penguin_uwu_build_prefix' source/build/make/core/config.mk
bash scripts/build-cerro.sh va                 # lunch penguin_cerro-cp2a-userdebug + m otapackage
# 或 SKIP_APPLY=1 bash scripts/build-cerro.sh va
```

## 6. 已知问题与坑

- 基座树内 `sepolicy` 删掉了 `sysfs_fan`（风扇）类型——须同步去掉 `devicesettings_app.te` / `genfs_contexts` 中的 fan 引用（否则 checkpolicy `unknown type sysfs_fan`）；
- nubia vendor 用 git-lfs（`lfs.undocumented.software`）：`PENGUIN_VENDOR_LFS` / `scripts/pull-vendor-lfs.sh`；未拉时 radio/*.img 为指针，kati SHA1 失败；
- NubiaParts 暂缓：缺 `packages/apps/NubiaParts` / LineageParts 时会挂 inherit；
- `patch-wfd-aidl-v5.sh` 的 ROOT 必须是仓库根（`scripts/cerro/../..`），旧版写成 `scripts/` 会找错 `source/`。

## 7. 上游失效风险

- 基座升级（nubia-sm8650-devs lineage-23.2 前进）时：本层是"基座+优化"的整树快照，需重新 clone 新基座并重放 overlay（BASE.md 有 commit 记录可 diff）；
- `config.mk` 里 `uwu_%` / `UWU_BUILD` 锚点漂移时修补丁，不丢功能；
- 其余 `scripts/cerro/` HAL 编译修复（sde / synx / hv-haptics）仍未挂链，试编遇到再挂（见 `scripts/cerro/README.md`）。
