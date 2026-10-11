# DT01: cerro/sm8650 设备层（基座 + Rising 驱动优化，无 UDC）

> 状态: done（设备层导入部分；UwU 上的编译验证属 M1）
> 开关: `PENGUIN_CERRO_DEVICE` (0/1, 默认 1)
> 目标仓库: `source/device/nubia/*`（由本仓库 `devices/nubia/` 镜像）+ `local_manifests/cerro.xml` 注入的 kernel/vendor 仓库

## 1. 需求描述

为 PenguinAOSP 提供 cerro (Nubia Z60 Ultra, SM8650) 设备层：以 `nubia-sm8650-devs`（lineage-23.2）为基座，叠加 RisingOS cerro 工程验证过的驱动优化；**按用户要求剔除全部屏下摄像头（UDC）相关改动**。

## 2. 设计（来源与决策）

- RisingOS cerro 的 `device-overlay` 是它对 nubia-sm8650-devs 基座的改动层（经 diff 确认基座树已自带 touch/fingerprint/parts 等大部分硬件组件）；
- 因此本功能的构成 = **基座树（git clone，commit 记录在 `devices/nubia/BASE.md`）+ overlay 增量（rsync）- UDC 三处**；
- kernel / devicetrees / modules / proprietary vendor 仓库不落本仓库（体积大且未改动），走 `local_manifests/cerro.xml` 在 repo sync 时拉进 `source/`（remote 自定义名 `nubia`，避开 UwUAOSP manifest 的 `aosp/lineageos/github/gitlab`）；
- 设备层仍是"基座原味 + 明确列出的优化"，便于逐项溯源；产品层（`lineage_cerro.mk`、Rising 的 `WITH_GMS`/`RISING_MAINTAINER`）按原样保留，M1 会新增 `penguin_cerro.mk` 做品牌/产品切换。

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
| `cerro/device.mk` | 上述 RRO + NubiaParts + 相机 watermark/dualcali bootstrap（后摄，非 UDC） |
| `cerro/AndroidProducts.mk` / `lineage_cerro.mk` | lunch choices / Rising 产品行（M1 改品牌） |
| `sm8650-common/BoardConfigCommon.mk` | 内核编译修复：`TARGET_KERNEL_ADDITIONAL_FLAGS`（pineapple conf 选择、PERL 路径） |
| `sm8650-common/build/host-bin/perl` | 内核 Makefile 的 perl PATH 包装 |

## 3. 涉及文件

| 目标路径 | 形式 | 真相源位置 |
|----------|------|------------|
| `source/device/nubia/cerro/**` | C（整树镜像） | `devices/nubia/cerro/` |
| `source/device/nubia/sm8650-common/**` | C（整树镜像） | `devices/nubia/sm8650-common/` |
| `source/.repo/local_manifests/cerro.xml` | C | `local_manifests/cerro.xml` |

## 4. Apply 链接入

- 脚本: `scripts/apply-cerro-device.sh`（rsync `--delete --exclude='.git'` 全量镜像，幂等）
- 挂载: `apply-all.sh` LAYERS 第 1 层（先于 branding）；开关 `PENGUIN_CERRO_DEVICE`
- local manifest: `scripts/init-uwu-source.sh` 在 repo init 后自动拷入 `.repo/local_manifests/`

## 5. 验证方法

```bash
bash scripts/apply-all.sh                      # cerro-device 层应成功镜像
diff -rq devices/nubia/cerro source/device/nubia/cerro          # 应无差异
diff -rq devices/nubia/sm8650-common source/device/nubia/sm8650-common
grep -r UdcCameraProtect source/device/nubia/                   # 应无结果（UDC 已剔除）
```

## 6. 已知问题与坑

- 基座树内 `sepolicy` 删掉了 `sysfs_fan`（风扇）类型——Rising 有意为之（sm8650 无风扇外设），照搬；
- `nubia-sm8650-devs` 的 vendor 仓库可能用 git-lfs（Rising 有 `pull-vendor-lfs.sh`），sync 后若 blob 缺失再处理。

## 7. 上游失效风险

- 基座升级（nubia-sm8650-devs lineage-23.2 前进）时：本层是"基座+优化"的整树快照，需重新 clone 新基座并重放 overlay（BASE.md 有 commit 记录可 diff）；
- M1 在 UwU 上编译时，`scripts/cerro/` 的 HAL 编译修复补丁需逐个验证后挂 apply 链（见 `scripts/cerro/README.md`）。
