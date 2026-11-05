# PenguinAOSP 排障日志

> 规则（AGENTS.md 硬性规则）：**每次卡住、踩坑、误判必须记入本文件。**
> 只记在聊天记录里 = 没记。条目按时间倒序追加（新的在最上面）。

## 条目格式

```
## YYYY-MM-DD — <一句话症状>
- 症状：
- 试过：
- 根因：
- 解决：
- 关联：
```

## 2026-11-06 — sync 到 17.0.181：manifest 仍钉 17.0.139；meminfo import 锚点失效
- 症状：只 `git fetch` versions 后 `.repo/manifest.xml` 仍 `include manifest/17.0.139.xml`；`apply-launcher-meminfo` 报 `DeviceProfile.java: import anchor not found for LauncherPrefs`。
- 试过：更新 `.repo/manifests` 到 origin/main 后直接 `repo sync`（第一次脚本中途退出）；重放 apply-all。
- 根因：
  1. versions 仓库的 pin 在 `default.xml`；已 init 过的 client 不会自动把生成的 `manifest.xml` 改到新 default，需 `repo init -m default.xml`（或显式 `-m manifest/17.0.181.xml`）。
  2. `DeviceProfile` 与 `LauncherPrefs` 同包，UwU 新树无 `Utilities`/`Settings` import 行可作锚点；旧补丁仍试图插入同包 import。
- 解决：`repo init -u … -b main -m default.xml` → `repo sync`；`launcher3_meminfo.py` 去掉 DeviceProfile 的 LauncherPrefs import 注入。hooks 与 project-objects 不一致的 `error: hooks is different` 可忽略（sync 仍成功）。
- 关联：上游 bump；FT11。

## 2026-10-14 — Launcher：Folder 玻璃缺 Path import；MemInfo 缺 Fallback import
- 症状：`Launcher3QuickStepLib` turbine/kapt `could not resolve Path` / `MemInfoView`。
- 根因：`launcher3_liquid_glass.py` 只加了 `RectF`；`FallbackRecentsView` 签名用了 MemInfoView 未 import。
- 解决：补 `import android.graphics.Path`；Fallback 加 `import ...MemInfoView`；回写两处 patch 脚本。
- 关联：FT10/FT11。

## 2026-10-14 — QS Styles：penguin 源码直拷编不过（UwU API 漂移）
- 症状：`SystemUI-core` ~100+ 错：`includeSpecs`/`circleAroundIcon`/`TileSizing`/`HeaderTiles`/`ConnectivityFolder` Element、`largeTiles`、`ShadeStatusRow`、`harmony_*` 字符串、`ic_qs_brightness_auto_*_new` 等。
- 试过：整份拷贝 penguin QS 树进 main SystemUI。
- 根因：penguinOS QS 相对 UwU 17 多一批 API（TileGrid 过滤、TileGridCell.rows、GridLayout.TileSizing、ShadeScene VM 字段、场景 ElementKey）；StyledShadeHeader 还依赖未移植的 ShadeStatusRow/HeaderTiles。
- 解决：加 `vendor/penguin/patches/systemui_qs_uwu_compat.py`（在 `apply-styles-qs-panel.sh` 末尾跑）：补 API + 资源；`StyledShadeHeader`/`ControlCentreTop` 暂 stub（样式页主体走 `StyledQuickSettingsContent`/`PenguinGridContent`）。勿桥接 `UWU_QS_STYLE`。
- 关联：FT08c；`scripts/apply-styles-qs-panel.sh`。

## 2026-10-14 — Liquid Glass：整份拷贝 ENR/Scrim 编不过
- 症状：SystemUI javac 找不到 `NTForbiddenSwipeDownQSController` / `ScrimUtils` / `QS_DUAL_TONE`。
- 试过：从 penguinOS 整份拷贝 `ExpandableNotificationRow`、`ScrimController`、`NotificationGlassPress` 等到 UwU。
- 根因：penguinOS 通知/Scrim 栈依赖其自有类与常量，UwUAOSP 没有。
- 解决：回退整份拷贝；只保留 `LiquidGlass.kt` + `ShadeColors.kt` + glyphs/strings；表面触点用 B 类补丁 `systemui_liquid_glass_surfaces.py`（NBView tint/rim、Activatable blur 闸门、Scrim 监听、Tile `glassRim`）。framework 推 `boot-framework.{art,oat,vdex}` + reboot，不可只热推 APK。
- 关联：FT09；`scripts/apply-liquid-glass-core.sh`。

## 2026-10-14 — Power Menu：iOS 布局崩溃后回落 LegacyGlobalActions
- 症状：`power_menu_style=1` 后长按电源仍见「锁定/关机/重启」白卡片；窗口名 `LegacyGlobalActions`；SystemUI crash 后重启。
- 试过：确认 APK/odex md5、强制 `isActive=true`、UI dump。
- 根因：SystemUI 确实走到 `IosPowerMenuLayout`（log 有 `isActive style=IOS`），但 `ActionsDialogLiteDelegate.onStart` 无条件 `mGlobalActionsLayout.updateList()`；自定义布局未设置该字段 → NPE → 5s 超时回落 `LegacyGlobalActions`。同类问题还有 `startAnimation`/`refreshDialog`/`dismissWhenUnlockStatusChanges`。
- 解决：对齐 penguinOS 空指针防护：`onStart`/`refreshDialog` 判空；动画改走 `mAnimatedContent`/`mBackdrop`；stock 路径设置 `mAnimatedContent = mGlobalActionsLayout`。补丁脚本加 `MARKER_NULL` 段。
- 关联：FT08；`vendor/penguin/patches/systemui_power_menu_style.py`。

## 2026-10-13 — BackToApp：RunningTaskInfo 无 launchedFrom*
- 症状：SystemUI-core kotlinc `unresolved reference 'launchedFromTaskId'/'launchedFromPackage'`。
- 试过：直接移植 penguinOS BackToAppTracker。
- 根因：penguinOS 在 TaskInfo 里加了 launchedFrom 字段；UwUAOSP 没有。
- 解决：改写 BackToAppTracker，用 TaskStackChangeListener 记住上一个非系统 task（不依赖 TaskInfo 扩展）。
- 关联：FT05。

## 2026-10-13 — Settings.Secure 新键进 current.txt（@hide 未生效）
- 症状：`check current API` 失败，`current.txt` 多出 POWER_MENU_STYLE 等公开字段。
- 试过：仅加 `@SuppressLint`；金属ava 仍把字段打进 stubs。
- 根因：Javadoc 写成单行 `/** ... @hide */` 时 metalava 不认 `@hide`。
- 解决：改为多行 `/** … \\n * @hide \\n */` + SuppressLint；勿重复声明上游已有键。
- 关联：FT06。

## 2026-10-13 — Settings.Secure 新键：NoSettingsProvider / UnflaggedApi
- 症状：metalava `api-stubs-docs-non-updatable` 报 `NoSettingsProvider` + `UnflaggedApi`（POWER_MENU_STYLE 等）。
- 试过：完整 otapackage。
- 根因：A17 禁止未标注的新 Secure 键常量。
- 解决：对 Penguin Secure 键加 `@SuppressLint({"UnflaggedApi", "NoSettingsProvider"})`（同上游 `MIRROR_BUILT_IN_DISPLAY`）；且勿重复声明已有键。
- 关联：FT06。

## 2026-10-13 — Settings.java：duplicate field MIRROR_BUILT_IN_DISPLAY
- 症状：`framework-minus-apex-headers` turbine 失败，`duplicate declaration of field: MIRROR_BUILT_IN_DISPLAY`。
- 试过：完整 otapackage 增量编译。
- 根因：`PENGUIN_SECURE_KEYS` 补丁又声明了 UwUAOSP 已有的 `Settings.Secure.MIRROR_BUILT_IN_DISPLAY`。
- 解决：从 `settings_secure_keys.py` 与已应用的 Settings.java 块中删除该常量；重编。
- 关联：FT06。

## 索引

| 日期 | 症状 | 根因分类 |
|------|------|----------|
| 2026-10-13 | BackToApp launchedFrom* 缺失 | TaskInfo API |
| 2026-10-13 | Settings.Secure 新键 NoSettingsProvider/UnflaggedApi | metalava 政策 |
| 2026-10-13 | Settings.java duplicate MIRROR_BUILT_IN_DISPLAY | 补丁与上游重复 |
| 2026-10-12 | SIM 已识别但无信号：RF_HARDWARE_ISSUE | 硬件（天线排线松） |
| 2026-10-12 | 卡第二屏：privapp allowlist 缺 `.xml` | Laboratory / PackageManager |
| 2026-10-12 | GMS apex Invalid file（git-lfs 指针） | vendor/LFS |
| 2026-10-12 | Launcher3：unresolved canForceStopPackage | frameworks 漂移 |
| 2026-10-12 | sepolicy：unknown type sysfs_fan | sepolicy |
| 2026-10-12 | kernel：sde_rm pp_cfg 未初始化 | 内核 -Werror |
| 2026-10-12 | kernel：synx entry/map_entry 未初始化 | 内核 -Werror |
| 2026-10-12 | kernel：qcom-hv-haptics name 未初始化 | 内核 -Werror |
| 2026-10-11 | kati：zip: 未找到命令 | 宿主工具 |
| 2026-10-11 | aop.img SHA1 mismatch（git-lfs 指针） | vendor/LFS |
| 2026-10-11 | soong_build 分析阶段吃满 32G+swap | 内存 |
| 2026-10-11 | build-cerro：set -u / 无 mka·bacon | 脚本 / UwU 差异 |
| 2026-10-11 | repo sync 换网线后挂死 | 网络/git |
| 2026-10-11 | UwU release manifest 三仓同步失败 | sync/manifest |

## 2026-10-12 — SIM LOADED 但无信号：`RADIO_POWER` → `RF_HARDWARE_ISSUE`
- 症状：SIM `LOADED`（CMCC），但 `ServiceState=POWER_OFF`；RIL `RADIO_POWER on=true` → `RF_HARDWARE_ISSUE`(70)；`mRadioAccessFamily=0`。
- 试过：重刷同版本 `modem.img`、reboot——无效（**未**为此加软件补丁）。
- 根因：天线相关 **排线摔松**（用户复座后恢复）。日志里的 `RF_HARDWARE_ISSUE` 是 RF 链路物理断连的表现，不是 ROM 缺补丁。
- 解决：重新卡紧排线；现网 `IN_SERVICE` / `NR_SA` / CMCC。
- 结论：**不加**信号类软件修复。

## 2026-10-12 — 卡第二屏：`privileged permissions not in allowlist`（PenguinLaboratory）
- 症状：刷入首次 OTA 后卡第二开机动画；`init.svc.bootanim=running`，`sys.boot_completed` 空；`zygote`/`netd`/`audioserver` 等 restarting。
- 试过：recovery 里直接 push（当时 `/system_ext` 未挂真实动态分区，写进 ramdisk，重启丢失）；user 构建无 adb root。
- 根因：`prebuilt_etc` 模块名 `privapp_permissions_com.penguin.laboratory` **未设 `filename: ...xml`**，装到设备上变成无后缀文件。PackageManager 只解析 `*.xml`，于是 `WRITE_SECURE_SETTINGS` 不在特权白名单 → system_server FATAL：`Signature|privileged permissions not in privileged permission allowlist: {com.penguin.laboratory ... WRITE_SECURE_SETTINGS}`。
- 解决：
  1. 真相源 `vendor/penguin/files/.../Android.bp` 的 `prebuilt_etc` 加 `filename: "privapp_permissions_com.penguin.laboratory.xml"`；
  2. 热修：loop 挂载已有 `system_ext.img`，删无后缀文件、保留 `.xml`，`fastbootd` 刷 `system_ext`（必要时 `--disable-verity --disable-verification` 刷 `vbmeta_system`）。
- 关联：`docs/features/ft01-penguin-laboratory.md`；AGENTS 硬性规则 13；`scripts/validate-penguinaosp-tree.sh` 校验 filename。

## 2026-10-12 — 96%：`com.google.android.gmssystem.prodvic.apex` Invalid file
- 症状：独立编译到约 96% 失败：`apex-ls`/`validate apk in prebuilt_apex` 报 `Failed to open package ... Invalid file`；日志早先也有 `Skipping ... because it's not a zipfile`。
- 根因：`vendor/pixel/gms` 下该 apex（及 Maps/Photos/Gmail 等共 8 个）仍是 **git-lfs 指针**（134B）；此前只拉了 `vendor/nubia/*`。
- 解决：`scripts/pull-vendor-lfs.sh` 增加 `vendor/pixel/gms`；`USE_PROXY=0 bash scripts/pull-vendor-lfs.sh` 后文件应为真实 zip（prodvic ~140MB）。再 `bash scripts/run-cerro-detached.sh`。
- 关联：LFS endpoint `gitlab.com/PixelOS-AOSP/proprietary_vendor_pixel_gms-17`。

## 2026-10-12 — Launcher3：unresolved `canForceStopPackage` / `forceStopPackage`
- 症状：`Launcher3QuickStepLib` kotlinc 失败：`SystemApiWrapper.kt` 找不到 `LauncherApps.canForceStopPackage` / `forceStopPackage`。
- 根因：Launcher3 有 UwU 提交 `81a7f4ee`（菜单强停），对应 frameworks `0b4e9110` **不在** sync-repair 钉死的 `frameworks/base@1be8401` 历史上。
- 解决：把 `0b4e9110` 导出为 `patches/frameworks_base/launcherapps-force-stop-privileged.patch`，`PENGUIN_LAUNCHERAPPS_FORCE_STOP` 重放。勿在 source 里 commit。
- 关联：日后若 rebase 到已含该提交的 tip，补丁会 skip（检测方法：`LauncherApps.java` 含 `canForceStopPackage`）。

## 2026-10-12 — system_ext_sepolicy：unknown type `sysfs_fan`
- 症状：内核三补丁过后，`checkpolicy` 失败：`devicesettings_app.te:8: unknown type sysfs_fan`。
- 根因：基座/Rising 删了 `sysfs_fan` 类型（sm8650 无风扇），但 `devicesettings_app.te` / `genfs_contexts` 仍引用。
- 解决：真相源去掉 fan 相关 allow/genfscon，只保留 `proc_touchkey`；`apply-cerro-device` 镜像后重编。
- 关联：`devices/nubia/sm8650-common/sepolicy/private/{devicesettings_app.te,genfs_contexts}`。

## 2026-10-12 — kernel modules：sde_rm `pp_cfg` 未初始化
- 症状：synx 修好后续编，再失败：`sde_rm.c:1293: variable 'pp_cfg' is uninitialized`（传入 `_sde_rm_reserve_pp`）。
- 根因：`scripts/cerro/patch-sde-rm-pp-cfg.sh` 此前未挂链；callee 覆盖参数、caller 从未赋值。
- 解决：挂 `PENGUIN_SDE_RM_PP`；`pp_cfg` 改为 callee 局部变量并改掉调用点。
- 关联：`kernel/nubia/sm8650-modules/.../display-drivers/msm/sde/sde_rm.c`。至此 Rising 导入的 3 个内核 -Werror 补丁均已挂链。

## 2026-10-12 — kernel modules：synx `entry` / `map_entry` 未初始化
- 症状：hv-haptics 修好后续编，kernel 再失败：`synx_util.c:1569 entry uninitialized`、`synx.c:1199 map_entry sometimes-uninitialized`。
- 根因：`scripts/cerro/patch-synx-uninit.sh` 此前未挂 apply 链。
- 解决：挂 `PENGUIN_SYNX_UNINIT`；指针初始化为 NULL。
- 关联：目标在 `kernel/nubia/sm8650-modules/.../synx-kernel/`。

## 2026-10-12 — kernel Image：qcom-hv-haptics `name` 未初始化
- 症状：`m otapackage -j8` 约 37% 失败：`qcom-hv-haptics.c:1028: variable 'name' is used uninitialized`（`-Werror,-Wsometimes-uninitialized`）。
- 根因：Rising 已有修复脚本 `scripts/cerro/patch-qcom-hv-haptics.sh` 未挂 apply 链；且脚本 `ROOT` 写成 `scripts/`（少一层 `..`）。
- 解决：修 ROOT → 仓库根；`PENGUIN_HV_HAPTICS` 挂 `apply-all`；对 `name` 赋默认 `"UNKNOWN"`。同步修正 sde/synx 脚本的 ROOT（尚未挂链）。
- 关联：续编 `SKIP_APPLY=1` 前先跑该补丁或 `PENGUIN_HV_HAPTICS=1 bash scripts/cerro/patch-qcom-hv-haptics.sh`。

## 2026-10-11 — kati SBOM：`zip: 未找到命令`
- 症状：vendor LFS 修好后，ckati 在 `finishing Make packaging rules: Checking licensing and SBOM` 失败：`/bin/bash: zip: 未找到命令`（`build/make/core/main.mk:1937`）。
- 根因：宿主未装 `zip`（CachyOS 最小环境常见）。
- 解决：`sudo pacman -S --needed zip unzip`。
- 关联：续编 `SKIP_APPLY=1 JOBS=8 bash scripts/build-cerro.sh va`。

## 2026-10-11 — kati：vendor/nubia/cerro/radio/aop.img SHA1 mismatch
- 症状：Soong 过后 Phase2 `-j8` 在 ckati 报 `vendor/nubia/cerro/Android.mk:9: aop.img SHA1 mismatch (bcfa76fa… != 68fe45aa…)`。
- 试过：`ls`/`sha1sum`/`head` 该文件。
- 根因：磁盘上是 **git-lfs 指针**（131B，`version https://git-lfs.github.com/spec/v1`），不是真实 `aop.img`（指针写 size 335872）。`repo sync` 未拉 LFS blob。
- 解决：装 `git-lfs`，跑 `bash scripts/pull-vendor-lfs.sh`（默认直连 `lfs.undocumented.software`；代理死掉时勿 `USE_PROXY=1`）。拉完 `aop.img` sha1=`68fe45aa…`。再 `SKIP_APPLY=1 JOBS=8 bash scripts/build-cerro.sh va`。
- 注意：本机 flclash `127.0.0.1:7890` 未开时，`source proxy-env.sh` 会导致 LFS `connection refused`；nubia LFS 端点直连可达。
- 关联：`PENGUIN_VENDOR_LFS` / `scripts/pull-vendor-lfs.sh`；two-phase Phase2 曾因此 exit 1。

## 2026-10-11 — soong_build「Writing module Ninja buckets」OOM（32G 主机扛不住）
- 症状：`m otapackage` 在 Soong 分析阶段 RSS≈25Gi、swap≈21–24Gi；写到 `out/soong/build.penguin_cerro.ninja`（约 4.1–6.6G、未写完）时整机 OOM，Cursor agent 也被杀。
- 试过：`GOMAXPROCS=4` **无效**（`soong_ui` 过滤掉）；残缺 ninja 不可用。
- 根因：Android 17 全树 Soong 分析峰值超过 32G+zram。
- 解决/缓解：`scripts/build-cerro-two-phase.sh`——Phase1 挂 64G 文件 swap（`/run/media/rong/data/penguin-soong.swap`）把 Soong 跑完；确认 ninja 体积稳定后 `swapoff` 该文件，Phase2 另起 `m otapackage -j8`。日志：`logs/build-cerro-phase1-soong.log` / `phase2-j8.log` / `two-phase.log`。
- 关联：`scripts/build-cerro-two-phase.sh`、`scripts/build-cerro.sh`。

## 2026-10-11 — build-cerro：mka/bacon 不存在；lunch 遇 set -u
- 症状：① lunch 报 `ANDROID_LUNCH_BUILD_PATHS: 未绑定的变量`；② lunch 成功后 `mka: 未找到命令`。
- 试过：确认 `penguin_cerro.mk` 已镜像、apply-all 通过；lunch 显示 Product=penguin_cerro。
- 根因：① `build-cerro.sh` 在 envsetup 后又 `set -u`；② UwUAOSP 无 Lineage `mka`/`bacon`（`vendor/lineage` 几乎为空），应使用 soong 的 `m` + AOSP `otapackage`。
- 解决：lunch/构建阶段保持 `set +u`；`m otapackage -jN`（可用 `BUILD_TARGET` 覆盖）。
- 关联：`scripts/build-cerro.sh`。

## 2026-10-11 — repo sync 换网线后挂死（git fetch 假活）
- 症状：后台 sync 停止增长（30s delta=0），但多个 `git fetch`（aosp tag / lineageos）进程仍存活数分钟，log 无报错。
- 试过：du 双测确认零增长；TaskStop 杀 bash。
- 根因：物理网线更换导致连接死亡，git fetch 的 TCP 挂在死链上不超时（fetch --quiet 无心跳输出）。
- 解决：`pkill -9 -f \"git fetch\"` 清进程；删除 `.repo/project-objects/**/objects/pack/tmp_pack_*`（共 4.6G 残缺包）；已完成仓库（~18G）不受影响，`repo sync` 可断点续拉。
- 关联：sync 命令见 scripts/init-uwu-source.sh；并发用 PENGUIN_SYNC_JOBS 控制（用户偏好 j4 稳定）。

## 2026-10-11 — UwU release manifest 三个仓库无法同步（根因三个不同问题）
- 症状：frameworks_base / LineageOS android_hardware_interfaces / platform_external_tesseract 反复 sync 失败（update-ref "not a valid SHA1"、pack "56 个未解决的 delta"）。
- 根因：① /tmp（16G tmpfs）被塞满 → git index-pack 写坏（清理：挪走 rdp3.log 等到 data/tmp-quarantine/）；② UwU release manifest 钉的 LineageOS hw_interfaces commit 在 UwU 自己的 fork 里不存在（404，fork 没同步）；③ fb 钉的 f33ab812 被上游 force-push 成孤儿（所有分支不可达），tesseract 的 pack 经代理必然损坏（HTTP/socks5、thin/非 thin、clone 全试过）。
- 解决：repo init -m manifest/17.0.139.xml（fb 换成可达 commit 1be8401）；local_manifests/cerro.xml remove-project + 从真 LineageOS 拉 hw_interfaces；tesseract 用 `git clone --bare --filter=blob:none`（partial clone 绕开损坏 pack）手动搭 .repo/project-objects + projects gitdir（alternates/promisor config/core.worktree/.git 指针）再检出。
- 注意：git 2.55 已移除 --no-thin；在 source 子目录里裸跑 git 会解析到外层 PenguinAOSP 仓库（projects/*.git 缺失时），务必带 GIT_DIR。
- 关联：scripts/sync-repair.sh（修复循环，本轮重删了 fb 多次——修复前先查 /tmp 空间）。
