# 批次 A-cutline-vol02-1011 收割说明（用户 2026-10-11 点卡后补充）

200 张（vol02，`guji label-batch make cutline-gold vol02 --n 200`），服务器 `43.162.109.111` 控制台人审，`guji label-batch harvest` 收割进本分片 `char-segmentation/touching-cuts/items.jsonl`（新增 200 条）。

## 结果

| 项 | 数 |
|---|---|
| 金标（`status: active`，含 `ok`/`moved`/`cand`） | 196 |
| 不确定（`status: uncertain`，verdict=`idk`） | 4 |
| 总计 | 200 |

`idk` 的 4 格都在 vol02 第 3 页（`vol02:3:1:11`、`vol02:3:2:6`、`vol02:3:2:8`、`vol02:3:2:9`），`char_above`/`char_below` 均为空——对应用户说的"印章污点、没有字"那几格，按无字记（`status: uncertain`），不当漏点。

**核对一处口径差**：用户原话说"三个标了跳过"，实测事件日志（`feedback/events/A-cutline-vol02-1011.jsonl`）里 `verdict=idk` 的是 **4 条**（不是 3），且都落在同一页（第 3 页）、上下文都是空字符串，形态一致，大概率就是用户说的那批、口头数错了一个，不是我这边漏收或多收——已如实按实测的 4 条记，供复核。
