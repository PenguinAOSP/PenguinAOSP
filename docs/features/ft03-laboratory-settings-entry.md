# FT03: Settings → Penguin Laboratory 入口

> 状态: done
> 开关: PENGUIN_LAB_SETTINGS_ENTRY (0/1, 默认 1)
> 目标仓库: packages/apps/Settings

## 1. 需求描述
在「设置 → 系统」底部增加 “Penguin Laboratory” 偏好，点击跳转 `com.penguin.laboratory/.LaboratoryActivity`。

## 2. 设计
在 `system_dashboard_fragment.xml` 的 `reset_dashboard` 偏好后插入 Preference+intent；字符串放独立 `penguin_strings.xml`（含 zh-rCN）。图标复用 `ic_settings_development`。

## 3. 涉及文件
| 目标仓库路径 | 补丁形式 | 位置 |
|--------------|----------|------|
| `res/xml/system_dashboard_fragment.xml` | B | `vendor/penguin/patches/settings_laboratory_entry.py` |
| `res/values{,-zh-rCN}/penguin_strings.xml` | B（写入） | 同上 |

## 4. Apply 链接入
- 脚本: `scripts/apply-settings-laboratory-entry.sh`
- 幂等: MARKER `<!-- PenguinOS: laboratory-settings-entry -->`
- 开关: `PENGUIN_LAB_SETTINGS_ENTRY`

## 5. 验证方法
设置 → 系统 → 底部 “Penguin Laboratory” 可打开 Laboratory。

## 6. 已知问题与坑
禁止热推 Settings APK（需进 system image / OTA）。

## 7. 上游失效风险
`reset_dashboard` 偏好 XML 漂移。
