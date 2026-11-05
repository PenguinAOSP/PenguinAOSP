# 功能开发文档索引

每个 PenguinAOSP 功能必须在本目录有一篇 `<id>-<slug>.md` 开发文档。
文档标准见 `AGENTS.md` §功能开发文档；新功能先查重（本索引 + `../patch-toggles.md`）。

| ID | 文档 | 状态 | 开关 |
|----|------|------|------|
| DT01 | [dt01-cerro-device-layer.md](dt01-cerro-device-layer.md) | wip（M1 试编） | `PENGUIN_CERRO_DEVICE` / `PENGUIN_UWU_BUILD_PREFIX` / `PENGUIN_WFD_AIDL_V5` |
| FT01 | [ft01-penguin-laboratory.md](ft01-penguin-laboratory.md) | wip | `PENGUIN_LABORATORY` |
| FT02 | [ft02-settings-system-keys.md](ft02-settings-system-keys.md) | done | `PENGUIN_SETTINGS_KEYS` |
| FT03 | [ft03-laboratory-settings-entry.md](ft03-laboratory-settings-entry.md) | done | `PENGUIN_LAB_SETTINGS_ENTRY` |
| FT04 | [ft04-edgelighting.md](ft04-edgelighting.md) | done | `PENGUIN_EDGELIGHTING` |
| FT05 | [ft05-backtoapp.md](ft05-backtoapp.md) | done | `PENGUIN_BACKTOAPP` |
| FT06 | [ft06-settings-secure-keys.md](ft06-settings-secure-keys.md) | done | `PENGUIN_SECURE_KEYS` |
| FT08 | [ft08-styles-power-menu.md](ft08-styles-power-menu.md) | done | `PENGUIN_STYLES_POWER_MENU` |
| FT08b | [ft08-styles-volume-panel.md](ft08-styles-volume-panel.md) | done | `PENGUIN_STYLES_VOLUME_PANEL` |
| FT08c | [ft08-styles-qs-panel.md](ft08-styles-qs-panel.md) | in-progress（SystemUI-core 已编通；待热推验） | `PENGUIN_STYLES_QS_PANEL` |
| FT09 | [ft09-liquid-glass.md](ft09-liquid-glass.md) | done（MVP） | `PENGUIN_LIQUID_GLASS_CORE` |
| FT10 | [ft10-launcher-liquid-glass.md](ft10-launcher-liquid-glass.md) | done | `PENGUIN_LAUNCHER_LIQUID_GLASS` |
| FT11 | [ft11-launcher-meminfo.md](ft11-launcher-meminfo.md) | draft（补丁已落地，待编 Launcher） | `PENGUIN_LAUNCHER_MEMINFO` |
| FT07 | [ft07-frequent-apps.md](ft07-frequent-apps.md) | done | `PENGUIN_FREQUENT_APPS` |

---

## 功能开发文档模板

```markdown
# <ID>: <功能名>

> 状态: draft | wip | done | broken
> 开关: PENGUIN_<FEATURE> (0/1, 默认 1)
> 目标仓库: frameworks/base, vendor/penguin/files/... 等

## 1. 需求描述
一句话说清楚用户能看到/感受到什么。

## 2. 设计
实现思路、关键类/资源、为什么选这个锚点。

## 3. 涉及文件
| 目标仓库路径 | 补丁形式 (A/B/C) | 位置 |
|--------------|------------------|------|
| frameworks/base/... | B | vendor/penguin/patches/xxx.py |

## 4. Apply 链接入
- 脚本: scripts/apply-xxx.sh （或 apply-all.sh 内的函数）
- 幂等检测方式: 检查 MARKER `// PenguinOS: ...` 是否存在
- 开关联动: docs/patch-toggles.md 中的 KEY

## 5. 验证方法
如何确认功能生效（adb 命令 / 界面路径 / dumpsys 输出）。

## 6. 已知问题与坑
链接到 docs/TROUBLESHOOTING.md 对应条目。

## 7. 上游失效风险
哪些锚点在上游更新后最可能漂移，重放时的检查清单。
```
