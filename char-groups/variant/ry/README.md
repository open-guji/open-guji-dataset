# 日曰（ry）＋日目（rm）逐格细读与新 L2 表（2026-10-24，A24）

殿本 vol11–20 日曰送审 137 格、日目 14 格。这批数据用来压送审、查错放。方法与回放结果见 cv 仓 `doc/字组/ry.md`、`rm.md`，
脚本在 cv `research/char_groups/ry/verify_1024/`。**本目录不进中心库**；新表等成批上线时随「推」替换。

## 文件

| 文件 | 内容 |
|---|---|
| `labels.jsonl` | 197 格文意标注（`kind=reading`，`by=claude-A24-ry`）。一行一格：`form` 读出的字（日／曰／目／其他，读不定为 null）、`conf`、`note` 依据、`orig` 原标签（已放行字 `released`、整理本对位 `ref`、坐标对位 `coord`、旧 L2 表 `ry_l2`／`rm_l2`、组流程结论 `group_flow`）、`event` 事件号、`left`／`right` 建表窗口（`seed_admit._clf_ctx`，各 20 字）、`flagged_released`（已放行格里读出另一字）、`haiku_1024`（补跑的 haiku 第二家意见） |
| `split.json` | 按册分折；vol04–10 是留出册 |
| `haiku_1024.json` | haiku 补跑 27 格（ry 提示词），只补表里没有 haiku 票的格 |
| `l2/ry.json`、`l2/rm.json` | 新 L2 表（`ry-l2-3+v1024`、`rm-l2-1+v1024`）：中心库现行表＋细读票（模型名 `opus`）＋haiku 补票，按 cv `ctx_l2.add_verify` 合 |

## 197 格怎么来的

- 176 格：vol11–20 里旧 L2 表有答案、或组流程留审的日曰目格（回放取的）。
- 21 格：已放行的 1888 个日曰目格逐格读过，读出另一字的（整理本错、match_ref 跟着放错）：日→曰 9、曰→日 11、目→曰 1。
- 读法先在 72 格人工标注上盲测：63 同、3 弃权、6 不同（多是按刻形标的格，见 ry 卡）。
- 「其他」5 格：白（白璧之瑕）、自（自序）、臼（窠臼）、两格讲偏旁。读不定 3 格写 null。

## 合表规则（`ctx_l2.add_verify`）

细读与表里的字不同（high／mid）→ 弃权 `disagree:verify`；表里低把握、细读 high 且没有别的遍以 high 给别的字 → 用细读的字；
至少两遍都 high 同字才 strong（strong 才能改掉别的通道放行的字）。rm 表：读成日→日、目→目、曰或别的字→其他。

## 回放（现有产物，不重跑整册）

| 范围 | 送审 前→后 | 放行／改字对真值的错 |
|---|---|---|
| vol11–20 ry | 137 → 31 | 每册 0（前：24） |
| vol11–20 rm | 14 → 11 | 0 |
| vol04–10 留出（中心库现行表） | 持平 | 0 |

重建（cv 仓）：`python research/char_groups/ry/verify_1024/build_tables.py <中心库 config/groups/l2> labels.jsonl haiku_1024.json <out>`，与本目录 `l2/` 逐字节相同。
中心库表若已不是 `ry-l2-3`／`rm-l2-1`，要在新表上重建，不能直接覆盖。
