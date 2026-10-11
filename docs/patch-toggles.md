# PenguinAOSP 补丁开关总表

所有 apply 脚本支持环境变量开关：`KEY=0` 跳过、`KEY=1`（或不设）应用。
开关默认值统一写在 `scripts/apply-all.sh` 顶部的 `PENGUIN_DEFAULTS` 中。

| KEY | 功能 | 默认 | apply 脚本 | 文档 |
|-----|------|------|------------|------|
| `PENGUIN_BRANDING` | PenguinAOSP 品牌（名称/版本/OTA 属性） | 1 | `scripts/apply-penguin-branding.sh` | `docs/features/branding.md`（待建） |

用法示例：

```bash
PENGUIN_BRANDING=0 bash scripts/apply-all.sh   # 跳过品牌化
```
