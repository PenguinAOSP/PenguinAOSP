# PenguinAOSP Agent Guide

给后续 agent 的工作约定。**改代码前先读本文件、`docs/SKELETON.md`、对应功能文档、以及 `docs/TROUBLESHOOTING.md`。**

本仓库是 **PenguinAOSP** 定制 ROM 的**唯一真相源**。对外系统名 **PenguinAOSP**。
基座是 **UwUAOSP（Android 17）**。GitHub 组织 **https://github.com/PenguinAOSP**：
- 对外 sync 入口：`platform_vendor_penguin-versions`（钉 UwU **17.0.181**；UwU ROM 层 fork 进组织；AOSP/Lineage 仍走上游）；
- 本仓库 + `vendor_penguin`：补丁层真相源（`apply-all.sh` 必须可重放）。
penguinOS（https://github.com/Project-penguinOS）仅作功能参考，**不使用其代码和树**。
首个目标设备：**Nubia Z60 Ultra (`cerro`, SM8650)**。

核心模式：**组织可 `repo sync` 的完整树 + 可重放补丁层**。工程结构详见 `docs/SKELETON.md`。

---

## 硬性规则

1. **不要把 `source/` 当成真相源。** 那只是 UwUAOSP 检出树，随时会被 sync / 删除覆盖。真相源只有本仓库的 `vendor/`、`devices/`、`patches/`、`scripts/`、`docs/`。
2. **修改和新增功能必须以补丁形式落地**（见 §补丁形式）。可编译验证时可以改 `source/`，但结束前必须回写到本仓库，并保证 `bash scripts/apply-all.sh` 能从干净树重放。
3. **每做一个功能，必须写一篇功能开发文档**（`docs/features/<id>-<slug>.md`，模板见 `docs/features/README.md`）。文档要让没读过本次对话的 agent 能独立接入 AOSP。
4. **每次卡住、踩坑、误判，必须记入 `docs/TROUBLESHOOTING.md`。** 记症状、试过的方法、最终原因、解决办法。只记在聊天里 = 没记。
5. **每次工作会话结束，必须往 `docs/WORKLOG.md` 顶部追加一条工作日志**（做了 / 没做完 / 产出）。下个 agent 靠它接续进度。
6. **不要直接大段覆盖上游 SystemUI / Settings 来"顺便"带功能。** UwU 自带功能保持原样，品牌层做最小覆盖。
7. **不要提交 git commit，除非用户明确要求**（Git 规范例外见 §Git 规范）。用户说「搞一下 git / 提交 / commit / 存一下」即视为明确要求。
8. **不要把 Penguin 补丁打进任何对照/参考树**（如 `MikuUI_cerro/`、`RisingOS_cerro/`、`AlphaDroid_Oneplus12/`），它们只读。
9. **功能做完尽量编译并刷到真机验证，不要只改代码就停。** 默认可热推对应模块（SystemUI / Launcher 等）。**禁止**热推 `Settings.apk`（历史卡第二屏 / 签名问题）。
10. **刷机 / 热推后的固定循环（冷却用 recovery，禁止乱回滚旧 APK）。**
    - 推完后必须持续监控：`boot_completed` / bootanim、SystemUI **pid 是否反复变**、`logcat -b crash`。用 `bash scripts/watch-systemui-stability.sh`（默认 ≥60s）。仅瞬间 `pidof` **不算**通过。
    - **FAIL（崩循环 / 卡第二屏 / bootanim 不退）时的唯一降温动作：**
      1. **2 分钟内**抓齐日志（crash + 相关 logcat，落到 `logs/`），**不要**先去换旧版 APK「赌能开机」。
      2. 立刻 `adb reboot recovery`（只要冷却进 recovery；**不要**默认 `reboot bootloader`，也**不要**用跨版本旧 SystemUI/Settings 覆盖）。
      3. 在主机上根据日志修代码 → 再编再刷/热推 → **再跑同一监控** → 通过才进入下一功能。
11. **禁止偷懒式验收。** 用户报的症状要逐条对着测；测不过就记入 `TROUBLESHOOTING.md` 并继续修，不得用无关指标糊弄。
12. **用户说「先别弄了」时立刻停当前功能线**，只做其点名的收尾（如 git / 文档），不要夹带继续改其它功能。
13. **priv-app 权限白名单文件名必须带 `.xml`。** `prebuilt_etc` 默认按 module `name` 安装；PackageManager 只加载 `*.xml`。缺后缀会导致 system_server 在 allowlist 校验时直接 FATAL（卡第二屏）。见 `docs/TROUBLESHOOTING.md`。

---

## 目录与真相源

| 路径 | 角色 |
|------|------|
| `vendor/penguin/` | PenguinAOSP 功能真相源（B 类补丁、overlay、files 副本、config、apply 工具库） |
| `devices/nubia/cerro/` | cerro 设备层真相源（产品定义、RRO、预装、品牌 make） |
| `patches/` | A 类 unified diff（按目标仓库分子目录） |
| `scripts/` | init / apply / build 脚本；新功能必须挂进 `apply-all.sh` 的 LAYERS |
| `docs/SKELETON.md` | 工程骨架方案（目录、补丁方案、里程碑） |
| `docs/features/` | **每个功能一篇开发文档**（README.md 为索引 + 模板） |
| `docs/TROUBLESHOOTING.md` | **固定排障日志** |
| `docs/WORKLOG.md` | **工作日志**（新条目置顶） |
| `docs/patch-toggles.md` | 补丁开关表（`PENGUIN_*`，`KEY=0\|1`） |
| `source/` | UwUAOSP 检出树，**可删可重下**，非真相源 |
| `/run/media/rong/data/AlphaDroid_Oneplus12/` | 参考树（整树 fork 方案 + sm8650 设备结构对照），只读 |
| `/run/media/rong/data/MikuUI_cerro/`、`/run/media/rong/data/RisingOS_cerro/` | cerro 设备树参考，只读 |

`source/` 里出现的 Penguin 改动若还没回写本仓库：先跑 `bash scripts/apply-all.sh` 确认重放结果一致，再手动提取差异回写；**收工前 `git status` 不允许出现"只在 source 里"的功能改动**。

---

## 补丁形式（必须）

按可维护性从高到低选一种。**禁止**只改 `source/` 而不留下可重放产物。

### A. Unified diff（`patches/<repo>/xxx.patch`，小改动首选）
- 路径相对目标仓库根（标准 `a/ b/` 前缀）；
- 幂等可检测：apply 前先 `git -C <repo> apply --check`，已应用则跳过。

### B. Python 上下文补丁（`vendor/penguin/patches/xxx.py`，易漂移的 Java/Kotlin/XML 首选）
- 锚点用稳定的上下文片段，不用行号；
- 改动行加 MARKER：`// PenguinOS: <feature>`（XML 用 `<!-- PenguinOS: <feature> -->`）；
- 脚本参数收 `SOURCE_DIR`（默认 `$PWD/source`），幂等：检测到 MARKER 已存在即跳过；
- 失败时输出"哪个锚点找不到"。

### C. Vendor 文件副本（`vendor/penguin/files/`）
- 新增整个文件/模块/overlay 用此形式，目录镜像目标路径（如 `vendor/penguin/files/packages/apps/PenguinSettings/...`）；
- apply 脚本负责拷贝进 `source/`，并记录清单以便清理。

### D. 明确禁止
- 只改 `source/` 就收工；
- 把补丁打进参考树；
- fork UwUAOSP 仓库、改 manifest 指向自己的 fork（我们不做整树 fork，见 `docs/SKELETON.md` §1）。

---

## 新功能标准流程

1. **查重**：`docs/features/README.md` 索引、`docs/patch-toggles.md`，确认不是重复造轮子；
2. 写 `docs/features/<id>-<slug>.md` 草稿（状态 draft，用 README.md 里的模板）；
3. 实现到 `vendor/penguin/` / `devices/` / `patches/` / `scripts/`；
4. 挂 apply 链：在 `scripts/apply-all.sh` 的 `LAYERS` 登记，在 `PENGUIN_DEFAULTS` 登记开关，并同步 `docs/patch-toggles.md`；
5. 补全功能文档（状态 → done）与索引；
6. 验证：
   ```bash
   bash scripts/apply-all.sh        # 全链重放通过
   ```
   涉及构建的功能再跑 `bash scripts/build-cerro.sh`；
7. **收尾三件套**（缺一不算收工）：
   - `docs/TROUBLESHOOTING.md` 记坑（有坑才记）；
   - `docs/WORKLOG.md` 追加日志（必做）；
   - 本仓库 git commit（规范见下）。

---

## 上游更新后如何重放

```bash
bash scripts/init-uwu-source.sh     # repo init + sync（走代理）
bash scripts/apply-all.sh           # 重放 Penguin 层
bash scripts/apply-penguin-branding.sh
```

补丁失效（锚点找不到）时：修补丁锚点，**不丢功能**；把失效原因和解法记入 `docs/TROUBLESHOOTING.md`。

---

## 日常命令

```bash
bash scripts/init-penguin-source.sh                   # 组织 manifest：repo init/sync（推荐）
bash scripts/init-uwu-source.sh                       # 仅 UwU 官方 versions（对照）
bash scripts/github-fork-uwu-layer.sh                 # 维护：UwU ROM 层 fork 进组织
bash scripts/apply-all.sh                             # 重放全部补丁
PENGUIN_BRANDING=0 bash scripts/apply-all.sh          # 跳过某一层
bash scripts/apply-penguin-branding.sh                # 只重放品牌层
bash scripts/build-cerro.sh va                        # 构建 cerro（M1 后可用）
SKIP_APPLY=1 bash scripts/build-cerro.sh va           # 跳过重放直接编
bash scripts/run-cerro-detached.sh                    # 脱离 IDE 后台编（看 logs/）
bash scripts/watch-cerro-build.sh                     # 盯编译日志
bash scripts/watch-systemui-stability.sh [serial]     # 刷机/热推后稳定性监控
bash scripts/validate-penguinaosp-tree.sh             # 树完整性快检（不编译）
bash scripts/sync-status.sh                           # repo sync 进度
bash scripts/prepare-build-swap.sh                    # 大容量文件 swap（防 Soong OOM）
source scripts/unlimit-build-env.sh                   # 解除 ulimit；配合 aurora_build/prlimit
source scripts/proxy-env.sh                           # 代理（flclash 127.0.0.1:7890）
```

---

## Git 规范

本仓库（PenguinAOSP 真相源）**自身就是 git 仓库**，用 git 管理补丁层的演进史。

### 什么进 git

- 全部文档、`vendor/penguin/`、`devices/`、`patches/`、`scripts/`；
- **不进 git**（见 `.gitignore`）：`source/`、构建产物、日志文件、`*.pyc` 等临时物。

### 分支模型

- `main`：稳定可重放状态。**任何时刻 main 上的 `apply-all.sh` 都应当能在干净树上通过**；
- 功能开发用 feature 分支：`feat/<id>-<slug>`（如 `feat/fp-quick-torch`）；
- 修上游漂移用 `fix/upstream-<日期>` 分支；
- 功能完成后合回 `main`（fast-forward 或 --no-ff merge 均可）。

### Commit 规范

- 格式：`<area>: <一句话摘要>`，area 取 `vendor` / `patches` / `devices` / `scripts` / `docs` / `repo`；
  示例：`vendor: add quick torch gesture patch`、`docs: add fp-quick-torch feature doc`；
- 一个功能拆成多个 commit 时按 area 拆，不混提交；
- commit body 里写"为什么"，不写流水账（做了什么看 diff 和 feature 文档）。

### 提交时机（与硬性规则的关系）

- agent 日常**不主动 commit**，除非用户明确要求或该功能处于"收尾三件套"阶段（用户已要求用 git 维护本项目）；
- 每次用户明确说"提交/commit"时，按上述规范执行，并确认 `git status` 干净、`apply-all.sh` 可重放后再提交。

### 与 source/ 的关系

- `source/` 内的上游仓库**禁止任何 commit**（那是上游 UwUAOSP 的历史）；
- 调试时的临时改动要么尽快回写本仓库，要么 `git -C <repo> checkout -- .` 丢弃。

---

## 完成前自检

- [ ] `source/` 改动已回写补丁 / vendor / apply
- [ ] 干净树上 `apply-all.sh` 可重放
- [ ] 开关已登记（`apply-all.sh` + `docs/patch-toggles.md`）
- [ ] 功能文档已写/更新（`docs/features/`）
- [ ] 坑已写入 `docs/TROUBLESHOOTING.md`（如有）
- [ ] `docs/WORKLOG.md` 已追加本会话日志
- [ ] 未把参考树（AlphaDroid/MikuUI/RisingOS）当主线
- [ ] 用户可见系统名为 **PenguinAOSP**（非 UwUAOSP / 裸 AOSP）
- [ ] 功能已编译并刷到真机（规则 9）
- [ ] 若动过 SystemUI / 热推：已按硬性规则 10 监控；FAIL 时已抓日志并 `reboot recovery`（未热推 Settings、未乱回滚旧 APK）
- [ ] priv-app 白名单若新增：设备上文件名带 `.xml`（规则 13）
