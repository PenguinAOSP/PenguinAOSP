# devices/nubia/cerro — PenguinAOSP 设备层

Nubia Z60 Ultra (`cerro`, SM8650) 的设备层真相源。

## 计划内容（M1）

- `AndroidProducts.mk` / `penguin_cerro.mk` / `BoardConfig.mk` 等产品定义
- RRO（runtime resource overlay）
- 预装应用列表
- `penguin_branding.mk`（品牌构建变量）

## 迁移来源

- 本地参考树：`/run/media/rong/data/MikuUI_cerro/`、`/run/media/rong/data/RisingOS_cerro/`
- 结构对照：`/run/media/rong/data/AlphaDroid_Oneplus12/device/oneplus/{sm8650-common,waffle}/`（同为 sm8650）

由 `scripts/apply-all.sh` 负责拷贝进 `source/device/nubia/cerro`（具体挂载脚本随 M1 落地）。
