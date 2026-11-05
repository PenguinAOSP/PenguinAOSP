# FT05: BackToApp 状态栏指示

> 状态: done
> 开关: PENGUIN_BACKTOAPP (0/1, 默认 1)
> 目标仓库: frameworks/base/packages/SystemUI

## 1. 需求描述
开启后，状态栏时钟下方显示「返回上个应用」标签，点击跳回上一个非系统任务。

## 2. 设计
- C 类拷贝 `statusbar/backtoapp/{BackToAppTracker,BackToAppLabel}.kt`；
- B 类在 `StatusBarRoot.addStartSideComposable` 用 `stackBackToAppUnderClock` 把标签叠在时钟下；
- 开关键 `Settings.System.BACK_TO_APP_INDICATOR`（FT02）。

## 3. 涉及文件
| 目标仓库路径 | 补丁形式 | 位置 |
|--------------|----------|------|
| `.../statusbar/backtoapp/*.kt` | C | `vendor/penguin/files/.../backtoapp/` |
| `.../StatusBarRoot.kt` | B | `vendor/penguin/patches/systemui_backtoapp_statusbar.py` |

## 4. Apply 链接入
- 脚本: `scripts/apply-backtoapp.sh`
- 幂等: rsync + MARKER `// PenguinOS: backtoapp-statusbar`
- 开关: `PENGUIN_BACKTOAPP`
- 依赖: `PENGUIN_SETTINGS_KEYS`

## 5. 验证方法
Laboratory → Experiments → Back to app；打开 App A→B，状态栏应出现返回 A。

## 6. 已知问题与坑
UwU 无 TaskInfo.launchedFrom*：Tracker 改为记住上一个非系统 task。
ClockModernization 开启时原生 clock View 被 GONE，标签仍挂在 legacy clock 父链上；若不可见需再适配 Compose Clock。

## 7. 上游失效风险
`addStartSideComposable` 内 `clockView` 获取块漂移。
