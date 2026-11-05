# scripts/cerro — cerro 驱动/编译修复补丁（自 RisingOS cerro 工程导入）

来源：`/run/media/rong/data/RisingOS_cerro/scripts/`（2026-10-11 导入）。
这些补丁修的是设备相关 HAL / 内核 / vendor blob 的编译错误或兼容问题，目标仓库在
`source/` 内由 `local_manifests/cerro.xml` 拉取的部分或上游 vendor 树。

| 脚本 | 修什么 | 目标 | apply 链 | 开关 |
|------|--------|------|----------|------|
| `patch-wfd-aidl-v5.sh` | WFD 预编译库 AIDL V4 vs 平台 V5 | `vendor/nubia/sm8650-common/Android.bp` | 已挂 | `PENGUIN_WFD_AIDL_V5` |
| `patch-qcom-hv-haptics.sh` | hv haptics `name` 未初始化（clang -Werror） | `kernel/nubia/sm8650/.../qcom-hv-haptics.c` | 已挂 | `PENGUIN_HV_HAPTICS` |
| `patch-synx-uninit.sh` | synx `entry`/`map_entry` 未初始化（clang -Werror） | sm8650-modules synx-kernel | 已挂 | `PENGUIN_SYNX_UNINIT` |
| `patch-sde-rm-pp-cfg.sh` | sde `_sde_rm_reserve_pp` `pp_cfg` 未初始化（clang -Werror） | sm8650-modules display | 已挂 | `PENGUIN_SDE_RM_PP` |

**未导入（UDC 屏下摄像头相关）**：`patch_udc_camera_protection.py`（SystemUI UDC 黑点遮罩）——按用户要求剔除。
**未导入（Rising 产品层专用）**：`patch-tflite-gpu-vendor.sh`（依赖 Rising `vendor/addons` 的 ax_tflite，UwU 无此仓库）。

未挂链的脚本在 M1 试编撞到对应错误后再挂进 `apply-all.sh` LAYERS，并同步 `docs/patch-toggles.md`。
