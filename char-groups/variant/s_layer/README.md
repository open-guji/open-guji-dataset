# S 层（#431 第一步）：放行通道＝context、放行字在罕用码位、库 unsure 的放行格

- 来源：cv main `2ee6068` 沙箱重放（影子闸关，标准开关），vol04、vol05A；脚本 cv `research/char_groups/variant/s_layer.py`（分支 `claude/B-variant-1010`，只读产物）。
- `s_cells.jsonl`：79 格，一格一行：`id book X Y Y_from Y_variant cov shadow_vetoed label`。X＝现放行字；Y＝候选正字（影子 pick → 坐标证人 → 对齐字 → 上下文首选 → 库次选，取第一个≠X 的）；`label`＝已有的看图标签（Claude 系，**不是独立真值**）。
- `pairs.json`／`PAIRS.md`：按 (册, X, Y) 折叠，45 对。
- `crops/<id 的:换_>.png`：引擎自己的 `char_patch`（79 张）。
- 用途：整理侧看图判「图上形像 X、像 Y、都不像」，一对一对地定 `variant_ledger` 白名单；**判完的结果写进 `pair_verdicts.jsonl`（`book X Y verdict(X|Y|neither|mixed) n_cells 备注`）**。

## 看图结果（整理侧 Lucian，10-11；整理看图判标签，不当独立真值）
`pair_verdicts.jsonl`（来自 overview 仓 `项目进展/古籍文本/进度/E-文本整理本/S层pair_verdicts-431.jsonl`，commit `1e3615bc4`）：45 对＝Y 22／X 13／neither 9／mixed 1（79 格里 X 39、Y 27、neither 10、mixed 3）。
X＝放行字就是图上形（放对）；Y＝图上是候选正字（放行字是误识，**放错**）。影子闸（开）在这 79 格里拦了 17：拦对 Y 14／27，误拦 X 1／39，neither 2。
