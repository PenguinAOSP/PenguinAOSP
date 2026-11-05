# FT02: Settings.System 实验键常量

> 状态: done
> 开关: PENGUIN_SETTINGS_KEYS (0/1, 默认 1)
> 目标仓库: frameworks/base

## 1. 需求描述
为 PenguinLaboratory Experiments 写入的 System 键提供框架常量，供 SystemUI（BackToApp、后续锁屏媒体）编译期引用。

## 2. 设计
在 `Settings.System` 的 `AUTO_LAUNCH_MEDIA_CONTROLS` 与 `// Settings moved to Settings.Secure` 之间插入常量（B 类 Python 补丁）。

## 3. 涉及文件
| 目标仓库路径 | 补丁形式 | 位置 |
|--------------|----------|------|
| `frameworks/base/core/java/android/provider/Settings.java` | B | `vendor/penguin/patches/settings_system_keys.py` |

键：`LS_MEDIA_EXPAND` / `LS_MEDIA_EXPANDED` / `LS_MEDIA_MOTION_ART` / `BACK_TO_APP_INDICATOR`。

## 4. Apply 链接入
- 脚本: `scripts/apply-settings-system-keys.sh`
- 幂等: MARKER `// PenguinOS: settings-system-keys`
- 开关: `PENGUIN_SETTINGS_KEYS`

## 5. 验证方法
```bash
rg 'PenguinOS: settings-system-keys' source/frameworks/base/core/java/android/provider/Settings.java
```

## 6. 已知问题与坑
无。

## 7. 上游失效风险
`AUTO_LAUNCH_MEDIA_CONTROLS` 块漂移时需更新锚点。
