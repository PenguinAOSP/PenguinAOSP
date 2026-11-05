# FT06: Settings.Secure 样式/玻璃/Dex 键常量

> 状态: done
> 开关: PENGUIN_SECURE_KEYS (0/1, 默认 1)
> 目标仓库: frameworks/base

## 1. 需求描述
为 Laboratory 写入的 Secure 键（Styles / Glass / Dex / 部分 Experiments）提供框架常量，供后续 SystemUI/Launcher 消费端编译期引用。

## 2. 设计
在 `Settings.Secure` 中 `NAVIGATION_MODE`（或回退锚点）之后插入常量块（B 类）。

## 3. 涉及文件
| 目标 | 形式 | 位置 |
|------|------|------|
| `Settings.java` Secure | B | `vendor/penguin/patches/settings_secure_keys.py` |

## 4. Apply
- `scripts/apply-settings-secure-keys.sh`
- MARKER: `// PenguinOS: settings-secure-keys`
- 开关: `PENGUIN_SECURE_KEYS`

## 5. 验证
`rg 'PenguinOS: settings-secure-keys' source/frameworks/base/core/java/android/provider/Settings.java`

## 6–7. 坑 / 风险
锚点 `NAVIGATION_MODE` 漂移时脚本会尝试备用锚点。
