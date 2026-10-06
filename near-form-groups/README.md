# near-form-groups → 已并入 [char-groups/](../char-groups)

N1（overview#428，2026-10-06）建的形近字组样本集（己/已/巳、日/曰、入/人/八，vol02–04，1,786 行），
已于 2026-10-06 由 G0（overview#437）**整体并入 `char-groups/`、按组拆开**：

| 原来 | 现在 |
|---|---|
| `items.jsonl`（`group` 字段区分 jys/ry/rr） | `char-groups/jys/items.jsonl`、`ry/items.jsonl`、`rr/items.jsonl`，字段是这里的超集（补了真值档 `gold_tier`/`label_origin`/`golds`、`core`、`split`、`page_type`，上下文从 5 字加到 8 字） |
| `crops/` | 各组 `crops/` |
| 只收 vol02–04 | vol02–vol10 全量，外加 vol01 confusable-context 题 |

N1 的每一行（id × 组）在 `char-groups` 里都有，只有 2 行例外：`vol03:25:3:20`（ry）、`vol03:106:9:13`（rr）。
N1 建 vol03 时取的上游快照（`20260928T1708-full`）与它用的 seed_admit（`20260930T0457`）不配套，这两格的放行字是「書」「兵」，
对位字却是旧切分的「目」「人」，所以被误收进组；换成配套的上游（`20260929T0451`）后，这两格不属于任何一组。
另外修了 N1 解析 vol03 看图表的一处错（「同形」「同上」读成「同」），见 `char-groups/README.md`「来历」。

原文件在 git 历史里（dataset main `8567e16`）。N1 的脚本 `open-guji-cv research/near_form/` 照旧能跑旧文件；新工作请用
`research/char_groups/`。
