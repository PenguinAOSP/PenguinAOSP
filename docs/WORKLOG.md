# PenguinAOSP 工作日志

> 规则（AGENTS.md 硬性规则）：**每次工作会话结束，必须在本文件追加一条日志**（新的在最上面）。
> 这是跨会话的连续性记录：下个 agent 读日志即可接上进度。

## 条目格式

```
## YYYY-MM-DD — <主题>
- 做了：
- 没做完 / 下一步：
- 产出（commit / 文档）：
```

---

## 2026-10-11 — 项目立项与工程骨架（M0）
- 做了：
  - 调研确定基座：UwUAOSP（Android 17，`uwu-17.0` / release manifest `platform_vendor_uwu-versions@main`）；penguinOS（AOSPA fork）仅作参考不采用。
  - 写工程骨架方案 `docs/SKELETON.md`；建立目录骨架（vendor/penguin、patches、scripts、devices/nubia/cerro、docs 体系）。
  - 写 `AGENTS.md`（含工作日志、功能文档、git 规范）；初始化本仓库 git。
- 没做完 / 下一步：
  - `scripts/init-uwu-source.sh` 尚未实际跑过一次完整 sync（约需大空间 + 代理）。
  - cerro 设备树迁移（M1）：参考本地 `MikuUI_cerro` / `RisingOS_cerro`，及 `AlphaDroid_Oneplus12/device/oneplus/sm8650-common` 组织方式。
  - `build-cerro.sh` 为占位，待 M1 补全。
- 产出：本仓库首个 commit；`docs/SKELETON.md`、`AGENTS.md`、docs 体系初始化。
