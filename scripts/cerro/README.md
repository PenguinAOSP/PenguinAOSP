# scripts/cerro — cerro 驱动/编译修复补丁（自 RisingOS cerro 工程导入，未挂 apply 链）

来源：`/run/media/rong/data/RisingOS_cerro/scripts/`（2026-10-11 导入）。
这些补丁修的是设备相关 HAL / 内核仓库的编译错误或兼容问题，目标仓库在
`source/` 内由 `local_manifests/cerro.xml` 拉取的部分或上游 vendor 树，
**尚未针对 UwUAOSP 验证，M1 bring-up 时逐个验证后挂进 `apply-all.sh` LAYERS**。

| 脚本 | 修什么 | 目标仓库 | UwU 适用性 |
|------|--------|----------|------------|
| `patch-sde-rm-pp-cfg.sh` | sde display `_sde_rm_reserve_pp` 未初始化（clang -Werror） | hardware/qcom-caf display 类 | 预计适用，待验证 |
| `patch-synx-uninit.sh` | synx 内核驱动错误路径未初始化（clang -Werror） | vendor/openshift synx-kernel 类 | 预计适用，待验证 |
| `patch-qcom-hv-haptics.sh` | hv haptics 驱动未初始化（clang -Werror） | vendor haptics 驱动 | 预计适用，待验证 |
| `patch-wfd-aidl-v5.sh` | WFD 预编译库 AIDL V4 vs 平台 V5 版本冲突 | vendor/qcom/opensource/wfd | 取决于 UwU 是否带 WFD prebuilts |

**未导入（UDC 屏下摄像头相关）**：`patch_udc_camera_protection.py`（SystemUI UDC 黑点遮罩）——按用户要求剔除。
**未导入（Rising 产品层专用）**：`patch-tflite-gpu-vendor.sh`（依赖 Rising `vendor/addons` 的 ax_tflite，UwU 无此仓库）。
