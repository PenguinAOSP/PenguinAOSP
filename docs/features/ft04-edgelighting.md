# FT04: EdgeLighting 边缘发光

> 状态: done
> 开关: PENGUIN_EDGELIGHTING (0/1, 默认 1)
> 目标仓库: frameworks/base/packages/SystemUI

## 1. 需求描述
通知脉冲/亮屏 heads-up 时按 Laboratory EdgeLighting 配置在屏幕边缘播放发光特效。

## 2. 设计
- C 类拷贝 `edgelighting/EdgeLightingController.java` + `EdgeLightingView.java`；
- B 类把 `EdgeLightingController` 注入 `DozeServiceHost`，在通知脉冲 start/finish 调用；
- 状态读 Laboratory ContentProvider `com.penguin.laboratory.provider/state`（需 `STATUS_BAR_SERVICE`）。

## 3. 涉及文件
| 目标仓库路径 | 补丁形式 | 位置 |
|--------------|----------|------|
| `.../edgelighting/*.java` | C | `vendor/penguin/files/.../edgelighting/` |
| `.../phone/DozeServiceHost.java` | B | `vendor/penguin/patches/systemui_edgelighting_doze.py` |

## 4. Apply 链接入
- 脚本: `scripts/apply-edgelighting.sh`
- 幂等: 文件 rsync + MARKER `// PenguinOS: edgelighting-doze`
- 开关: `PENGUIN_EDGELIGHTING`
- 依赖: FT01 Laboratory（provider）

## 5. 验证方法
Laboratory → Edge Lighting 开启并选素材；发通知或 AOD 脉冲时边缘发光；预览广播亦可。

## 6. 已知问题与坑
无 GMS 不影响本功能（不依赖 MLKit）。

## 7. 上游失效风险
`DozeServiceHost` 构造函数参数列表漂移。
