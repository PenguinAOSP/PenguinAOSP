# cerro/sm8650 设备树基座来源

本目录 = `nubia-sm8650-devs`（lineage-23.2）基座 + RisingOS cerro `device-overlay` 优化层（已剔除屏下摄像头/UDC 相关改动，见 `docs/features/dt01-cerro-device-layer.md`）。

| 仓库 | 目标路径 | 基座 commit（lineage-23.2） |
|------|----------|------------------------------|
| android_device_nubia_cerro | `devices/nubia/cerro` | `a7ed9a2ab78485804ed384c3fae089a3b291494b` |
| android_device_nubia_sm8650-common | `devices/nubia/sm8650-common` | `d542710e64c2682e24a081fa20b74ce59294e539` |

克隆时间：2026-10-11。source 内的 kernel / devicetrees / modules / proprietary vendor 不落本仓库，由 `local_manifests/cerro.xml` 在 repo sync 时直接拉进 `source/`。

## 从 Rising overlay 剔除的 UDC 相关项

| Rising 位置 | 内容 | 处理 |
|-------------|------|------|
| `cerro/overlay/SystemUIResCerro/` | 仅含 `config_risingCerroUdcCameraProtect` 的 RRO | 不导入；`device.mk` 引用已移除（带 `# PenguinOS:` 注释） |
| `sm8650-common/rro_overlays/FrameworksResTarget_Vendor/res/values/config.xml` | diff 仅为 UDC cutout rect 置空 | 不导入，保留基座原值 |
| `scripts/patch_udc_camera_protection.py`（Rising 工程） | SystemUI UDC 黑点遮罩补丁 | 不导入 |
