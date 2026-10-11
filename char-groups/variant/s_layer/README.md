# S 层（#431 第一步）：放行通道＝context、放行字在罕用码位、库 unsure 的放行格

- 来源：cv main `2ee6068` 沙箱重放（影子闸关，标准开关），vol04、vol05A；脚本 cv `research/char_groups/variant/s_layer.py`（分支 `claude/B-variant-1010`，只读产物）。
- `s_cells.jsonl`：79 格，一格一行：`id book X Y Y_from Y_variant cov shadow_vetoed label`。X＝现放行字；Y＝候选正字（影子 pick → 坐标证人 → 对齐字 → 上下文首选 → 库次选，取第一个≠X 的）；`label`＝已有的看图标签（Claude 系，**不是独立真值**）。
- `pairs.json`／`PAIRS.md`：按 (册, X, Y) 折叠，45 对。
- `crops/<id 的:换_>.png`：引擎自己的 `char_patch`（79 张）。
- 用途：整理侧看图判「图上形像 X、像 Y、都不像」，一对一对地定 `variant_ledger` 白名单；**判完的结果写进 `pair_verdicts.jsonl`（`book X Y verdict(X|Y|neither|mixed) n_cells 备注`）**。
