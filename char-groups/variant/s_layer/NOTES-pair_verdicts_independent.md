# `pair_verdicts_independent.jsonl` 说明（2026-10-12）

跟已有的 `pair_verdicts.jsonl`（Lucian 看图判断，Claude 系，非独立真值）**不是同一个来源**：这份是用户在服务器审阅平台（`/variant-review/`）亲自逐对点出来的，按 Mila 10-11 定的口径算**独立真值**。

覆盖 Elena 在 overview#431 贴的 13 行（11 个 (册,X) 分组，39 格，vol05 的 㫖→None 和 㫖→背 按候选 Y 不同拆成两张卡单独点）。

字段：`book`、`X`、`Y`（可为 null）、`verdict`（`X`＝忠实原刻放对了、`Y`＝应为候选正字放错了、`neither`＝都不是、`mixed`＝同对里格不一致需逐格看）、`n_cells`、`cell_ids`、`mixed_cells`（仅 `mixed` 时有值，这轮没用到）、`reviewer`、`ts`。

**结果**：13 对里 **12 个 `X`**（忠实原刻，含 㫖→旨 21 格、㕘→叅/參 8 格等最大几宗）、**1 个 `neither`**（`vol04:𢑴→〓`，用户判都不是，候选 Y「〓」本来就是占位符不是真字，这个结果符合预期）。没有出现 `Y`（候选正字才对，即真放行错）或 `mixed`。

落用字账（`rare_x_confirmed`）那步按规矩仍是 H 道／Elena-Evan 接线做，这份只是原始独立判断，我（Eliot）没有写 `variant_ledger`。
