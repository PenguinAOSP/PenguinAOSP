# PenguinAOSP 工程骨架方案

> 状态：v2（2026-11-06）— 组织可 `repo sync` + 保留补丁层  
> 基座：**UwUAOSP（Android 17）**，https://github.com/uwuAOSP  
> GitHub org：**https://github.com/PenguinAOSP**  
> 首个目标设备：**Nubia Z60 Ultra (`cerro`, SM8650)**

---

## 1. 项目定位

**PenguinAOSP** 是基于 UwUAOSP 的定制 Android ROM，目标是：

1. **普通 AOSP 用法**：`repo init` Penguin 组织的 release manifest → `repo sync` → `lunch` → 编译；
2. **补丁层可重放**：功能仍用 `vendor/penguin` + `scripts/apply-all.sh` 维护，不把逻辑淹没在整树 history 里；
3. **文档齐全**：每个 feature 有独立开发文档。

### 组织里放什么（不是 1000+ 个 AOSP 镜像）

| 来源 | 数量级 | 策略 |
|------|--------|------|
| AOSP | ~867 | 继续 `android.googlesource.com` |
| LineageOS | ~159 | 继续 `github.com/LineageOS/...` |
| UwU ROM 层 | ~46 | **Fork 进 PenguinAOSP 组织** |
| Penguin 自有 | 设备/vendor/meta/versions | 组织仓 |

入口：[`platform_vendor_penguin-versions`](https://github.com/PenguinAOSP/platform_vendor_penguin-versions)（钉 **17.0.181**，自 UwU versions 衍生）。

### 与「纯 AlphaDroid 整树 fork」的差别

- AlphaDroid：功能直接 commit 进各 `platform_*`，下游难复现。
- PenguinAOSP：**组织提供可 sync 的完整树**，但 Penguin 功能真相源仍是补丁脚本；上游 UwU 升级时重放 `apply-all.sh`，锚点坏了就修。

### 与 UwUAOSP 的关系

- 基座代码来自 UwU；组织内 UwU 层是 fork，便于大家只对 `PenguinAOSP` 做 `repo init`；
- 上游更新：同步/快进 forks → 升 versions pin → `apply-all.sh`；
- UwU 自带功能按原样保留；品牌层最小覆盖（PenguinAOSP 名 / lunch 前缀）。

---

## 2. 目录结构（本仓库 = 真相源）

```
PenguinAOSP/
├── AGENTS.md                  # agent 工作约定（本仓库最高优先级文档）
├── docs/
│   ├── SKELETON.md            # 本文件：工程骨架方案
│   ├── features/              # 每个功能一篇开发文档（README.md 为索引）
│   ├── TROUBLESHOOTING.md     # 固定排障日志（卡住/踩坑/误判必记）
│   ├── patch-toggles.md       # 补丁开关表（PENGUIN_* KEY=0|1）
│   └── WORKLOG.md             # 工作日志（按日期倒序追加）
├── vendor/penguin/            # PenguinAOSP 功能真相源
│   ├── patches/               # B 类 Python 上下文补丁
│   ├── overlay/               # RRO runtime overlay
│   ├── files/                 # C 类整文件副本（按目标路径镜像存放）
│   ├── config/                # penguin_vendor.mk 等公共 make 配置
│   └── tools/                 # apply 脚本共享库（python 补丁引擎等）
├── patches/                   # A 类 unified diff（按目标仓库分子目录）
│   ├── frameworks_base/
│   ├── packages_apps_Settings/
│   └── ...
├── devices/nubia/cerro/       # cerro 设备层（树、RRO、预装、penguin_branding.mk）
├── scripts/                   # init / apply / build 脚本（全部可重放）
│   ├── proxy-env.sh
│   ├── init-uwu-source.sh
│   ├── apply-all.sh
│   ├── apply-penguin-branding.sh
│   └── build-cerro.sh
└── source/                    # UwUAOSP 检出树（可删可重下，非真相源）
    └── （repo sync 产物 + 补丁重放目标）
```

**铁律**：`source/` 不是真相源，随时可以 `rm -rf` 后重建；真相源只有 git 仓库里的 `vendor/`、`devices/`、`patches/`、`scripts/`、`docs/`。

---

## 3. 补丁方案（四级形式，禁止裸改 source）

| 级别 | 形式 | 适用 | 要求 |
|------|------|------|------|
| A | Unified diff（`patches/<repo>/xxx.patch`） | 小改动、锚点稳定 | 幂等可检测；路径以 `a/ b/` 相对目标仓库根 |
| B | Python 上下文补丁（`vendor/penguin/patches/xxx.py`） | 易漂移的 Java/Kotlin/XML | 锚点必须是稳定上下文；改动行加 `// PenguinOS: ...` MARKER；参数收 `SOURCE_DIR` |
| C | Vendor 文件副本（`vendor/penguin/files/`） | 新增整个文件/模块/overlay | 目录镜像目标路径；apply 脚本负责拷贝；删除时能清理 |
| D | **明确禁止** | — | 只改 `source/` 就收工；把补丁打进任何对照树；顺手大段覆盖上游 SystemUI/Settings |

### apply 脚本约定

- 每个补丁一个独立 apply 脚本（或脚本内一个函数），必须：
  - 收 `SOURCE_DIR`（默认 `$PWD/source`）；
  - **幂等**：已应用时检测并跳过，不重复打；
  - 失败时输出明确的"哪个锚点找不到"，方便上游更新后修复；
- `scripts/apply-all.sh` 是唯一入口，按依赖顺序调用所有子 apply；支持 `PENGUIN_<FEATURE>=0` 跳过（对应 `docs/patch-toggles.md`）；
- 新功能必须挂进 apply-all 链并在文档中登记开关。

### 品牌化

- 用户可见系统名统一 **PenguinAOSP**（SetupWizard 欢迎页 / About phone / 设置标题）；
- 统一由 `scripts/apply-penguin-branding.sh` 重放，不散落在各功能补丁里；
- 构建期变量：`ro.penguin.version`、`PENGUIN_BUILD_TYPE`、lunch 前缀 `penguin_`（见 §5）。

---

## 4. 同步与重放

```bash
# 首次拉取上游（走代理）
source scripts/proxy-env.sh
bash scripts/init-uwu-source.sh
# 等价于：
#   mkdir -p source && cd source
#   repo init -u https://github.com/uwuAOSP/platform_vendor_uwu-versions.git -b main --git-lfs
#   repo sync -c -j$(nproc --all) --force-sync --no-clone-bundle --no-tags --optimized-fetch --prune

# 重放 Penguin 层
bash scripts/apply-all.sh

# 品牌化
bash scripts/apply-penguin-branding.sh
```

上游更新后的标准动作：sync → apply-all → 逐个修复失效补丁 → 记录到 TROUBLESHOOTING。

---

## 5. 构建与设备层（cerro）

### lunch / 构建

- lunch 目标格式跟随上游宏但换前缀：`penguin_cerro-cp2a-userdebug`（UwUAOSP 的 lunch 为 `uwu_<device>-cp2a-userdebug`，我们在 vendor 层注册 `penguin_` product 前缀）；
- 构建命令：`bash scripts/build-cerro.sh va`（内部完成 lunch + `m otapackage`；UwU 无 Lineage `mka`/`bacon`）。

### cerro 设备层来源

- 基础树（kernel、vendor blobs、sm8650-common）：从既有 cerro 工作迁移 —— 本地参考 `MikuUI_cerro` / `RisingOS_cerro`，以及 AlphaDroid_Oneplus12 里 `device/oneplus/sm8650-common` 的组织方式（同为 sm8650，结构可对照）；
- 设备层本身放入 `devices/nubia/cerro/`，由 apply 脚本拷贝进 `source/device/nubia/cerro`；
- 需要的 common 依赖（如 `device/qcom/sepolicy_vndr`、`hardware/qcom-caf/sm8650`）按 UwUAOSP manifest 实际包含情况决定：上游有就复用，没有就写 snippet/副本进 `vendor/penguin/files/`。

### 里程碑

| 阶段 | 目标 | 验收 |
|------|------|------|
| M0 | 骨架 + git + 文档体系（本 PR） | 仓库可 clone，apply-all 空跑通过 |
| M1 | cerro 在 UwUAOSP 上点亮（first boot） | penguin_cerro-userdebug 刷机可开机进 Setup |
| M2 | 品牌化完成（PenguinAOSP 名称、版本号、OTA 属性） | About phone 显示 PenguinAOSP |
| M3 | 首个 Penguin 独有功能落地并文档化 | feature 文档 + 补丁 + 开关齐全 |

---

## 6. Git 策略

详见 `AGENTS.md` §Git 规范。要点：

- 本仓库（PenguinAOSP 真相源）自身是 git 仓库；`source/`、`*.log`、大文件一律 gitignore；
- 每个功能一个 feature 分支，commit 规范 `<area>: <summary>`（如 `vendor: add quick torch gesture`）；
- 上游源码仓库（`source/` 内）**不做任何 commit**——改动要么是补丁重放，要么尽快回写本仓库。

---

## 7. 文档体系

| 文档 | 作用 | 何时更新 |
|------|------|----------|
| `docs/features/<id>-<slug>.md` | 功能开发文档，别人照着能独立接入 | 每个功能开发前建稿，收工时补全 |
| `docs/WORKLOG.md` | 工作日志：日期 + 做了什么 + 遇到什么 | 每次工作会话结束 |
| `docs/TROUBLESHOOTING.md` | 排障日志：症状/试过/根因/解法 | 每次卡住、踩坑、误判 |
| `docs/patch-toggles.md` | `PENGUIN_*` 开关总表 | 每新增开关 |
| `docs/SKELETON.md` | 本骨架方案 | 结构性变化时 |

---

## 8. penguinOS 内容引入方案

penguinOS（AOSPA fork，https://github.com/Project-penguinOS ，Android 17 "cinnamon bun"，branch `celerity`）的仓库全部公开，只**当参考源码读、不当基座**。引入流程：

1. **参考树落位**：需要的 penguinOS 仓库浅克隆到 `reference/penguinos/`（gitignore，只读对照，禁止直接打进任何编译树）；
2. **查重先行**：UwU 自带大量定制（uwuSettingsExt 等），先确认功能在 UwU 上没有等价物，避免重复实现；
3. **移植而非 cherry-pick**：penguinOS 基座是 AOSPA 系，与 UwU（Lineage 系）树差异大，上游 commit 不能直接拣；按"读懂实现 → 在 UwU 锚点上重写 → 打 B 类补丁"走标准新功能流程；
4. **登记来源**：feature 文档必须写"上游参考: penguinOS <repo>@<commit>"，patch 头部注明移植自何处（AOSPA 系 Apache-2.0，保留署名即可）；
5. **品牌物料**：PenguinAOSP 名称/logo/壁纸等自建，不搬 penguinOS 的素材（它叫 PenguinOS，我们是 PenguinAOSP，避免品牌混淆）。

---
