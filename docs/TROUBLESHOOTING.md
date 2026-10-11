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

## 2026-10-11 — UwU release manifest 三个仓库无法同步（根因三个不同问题）
- 症状：frameworks_base / LineageOS android_hardware_interfaces / platform_external_tesseract 反复 sync 失败（update-ref "not a valid SHA1"、pack "56 个未解决的 delta"）。
- 根因：① /tmp（16G tmpfs）被塞满 → git index-pack 写坏（清理：挪走 rdp3.log 等到 data/tmp-quarantine/）；② UwU release manifest 钉的 LineageOS hw_interfaces commit 在 UwU 自己的 fork 里不存在（404，fork 没同步）；③ fb 钉的 f33ab812 被上游 force-push 成孤儿（所有分支不可达），tesseract 的 pack 经代理必然损坏（HTTP/socks5、thin/非 thin、clone 全试过）。
- 解决：repo init -m manifest/17.0.139.xml（fb 换成可达 commit 1be8401）；local_manifests/cerro.xml remove-project + 从真 LineageOS 拉 hw_interfaces；tesseract 用 `git clone --bare --filter=blob:none`（partial clone 绕开损坏 pack）手动搭 .repo/project-objects + projects gitdir（alternates/promisor config/core.worktree/.git 指针）再检出。
- 注意：git 2.55 已移除 --no-thin；在 source 子目录里裸跑 git 会解析到外层 PenguinAOSP 仓库（projects/*.git 缺失时），务必带 GIT_DIR。
- 关联：scripts/sync-repair.sh（修复循环，本轮重删了 fb 多次——修复前先查 /tmp 空间）。
