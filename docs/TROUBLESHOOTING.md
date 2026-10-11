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

## 索引

| 日期 | 症状 | 根因分类 |
|------|------|----------|
| （暂无） | | |

## 2026-10-11 — repo sync 换网线后挂死（git fetch 假活）
- 症状：后台 sync 停止增长（30s delta=0），但多个 `git fetch`（aosp tag / lineageos）进程仍存活数分钟，log 无报错。
- 试过：du 双测确认零增长；TaskStop 杀 bash。
- 根因：物理网线更换导致连接死亡，git fetch 的 TCP 挂在死链上不超时（fetch --quiet 无心跳输出）。
- 解决：`pkill -9 -f \"git fetch\"` 清进程；删除 `.repo/project-objects/**/objects/pack/tmp_pack_*`（共 4.6G 残缺包）；已完成仓库（~18G）不受影响，`repo sync` 可断点续拉。
- 关联：sync 命令见 scripts/init-uwu-source.sh；并发用 PENGUIN_SYNC_JOBS 控制（用户偏好 j4 稳定）。
