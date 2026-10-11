# PenguinAOSP 补丁开关总表

所有 apply 脚本支持环境变量开关：`KEY=0` 跳过、`KEY=1`（或不设）应用。
开关默认值统一写在 `scripts/apply-all.sh` 顶部的 `PENGUIN_DEFAULTS` 中。

| KEY | 功能 | 默认 | apply 脚本 | 文档 |
|-----|------|------|------------|------|
| `PENGUIN_BRANDING` | PenguinAOSP 品牌（名称/版本/OTA 属性） | 1 | `scripts/apply-penguin-branding.sh` | `docs/features/branding.md`（待建） |
| `PENGUIN_CERRO_DEVICE` | cerro/sm8650 设备层（基座+Rising 优化，无 UDC） | 1 | `scripts/apply-cerro-device.sh` | `docs/features/dt01-cerro-device-layer.md` |
| `PENGUIN_LABORATORY` | PenguinLaboratory 应用（penguinOS 设置中心，独立 APK） | 1 | `scripts/apply-penguin-laboratory.sh` | `docs/features/ft01-penguin-laboratory.md` |

用法示例：

```bash
PENGUIN_BRANDING=0 bash scripts/apply-all.sh   # 跳过品牌化
```
