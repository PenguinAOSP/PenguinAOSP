# FT07: Recents FrequentApps

> 状态: done（真相源就绪；随下一轮 apply/build 进树）
> 开关: PENGUIN_FREQUENT_APPS (0/1, 默认 1)
> 目标仓库: packages/apps/Launcher3

## 1. 需求描述
Laboratory Experiments 开启 `recents_frequent_apps` 后，最近任务底部显示本周最常用的最多 4 个应用图标。

## 2. 设计
- C 类：`FrequentAppsView.java` + dimens + ripple；
- B 类：`OverviewActionsView`（alpha/可见性/定位）、`overview_actions_container.xml`、`DeviceProfile.frequentAppsHeight`。

## 3. Apply
- `scripts/apply-frequent-apps.sh`
- MARKER: `// PenguinOS: frequent-apps` / `<!-- PenguinOS: frequent-apps -->`

## 4. 验证
Laboratory → Experiments → Frequently used apps；打开 Overview 应见图标行。切换后可能需旋转/重启 Launcher 以重建 DeviceProfile 占位高度。

## 5. 风险
`OverviewActionsView` / `DeviceProfile` 锚点漂移；需 `PACKAGE_USAGE_STATS`（系统 Launcher 通常已有）。
