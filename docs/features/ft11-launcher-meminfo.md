# FT11 — Launcher Recents MemInfo

> 状态: in-progress（Launcher3QuickStep 已编通；待 cerro 真机热推）
> 开关: `PENGUIN_LAUNCHER_MEMINFO`
> 目标仓库: `packages/apps/Launcher3`

## 目标

最近任务页显示可用内存行（可选 ZRAM），开关 `pref_recents_meminfo` / `pref_recents_meminfo_zram`（LauncherPrefs）。

## 落地

- C：`MemInfoView.java`、`meminfo.xml`、`penguin_launcher_meminfo.xml`
- B：`vendor/penguin/patches/launcher3_meminfo.py`（overview_panel / DeviceProfile / RecentsView.init 链 / QuickstepLauncher / RecentsActivity / RecentsWindowManager / Fallback*）
- Apply：`scripts/apply-launcher-meminfo.sh`

## 验收

- `LauncherPrefs.RECENTS_MEMINFO=true` 后进 Overview，底部出现 `available | total` 文案。
- 与 FT07 FrequentApps 高度叠加不裁切。

## 未做（下一批）

TaskChanger 多布局、IconPack、Trust/Hidden、Quickspace/Spotlight — 改动面大，单独立项。
