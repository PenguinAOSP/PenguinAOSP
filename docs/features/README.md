# 功能开发文档索引

每个 PenguinAOSP 功能必须在本目录有一篇 `<id>-<slug>.md` 开发文档。
文档标准见 `AGENTS.md` §功能开发文档；新功能先查重（本索引 + `../patch-toggles.md`）。

| ID | 文档 | 状态 | 开关 |
|----|------|------|------|
| （暂无） | | | |

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
