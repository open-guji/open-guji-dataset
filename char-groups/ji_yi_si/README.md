# 己已巳 muse 二意见格清单（Lucian → Dax，10-12 洛杉矶）

`cells.jsonl`：共 76 格＝Lucian 段 3 已看 17 格（`seen17`，其中 4 格己方向同时在补抽里＝`both`）＋Evan 补抽 63 格（`supp63`）。
- 字段：`id`（vol:page:col:slot，列 1 在最右）、`book/page/col/slot`、`set`、`crop`（相对本仓根的字块图，二值化约 110px，取自 `char-groups/jys/crops/`）。
- `supp63` 另带 `左15`／`右15`（该格左右各 15 字上下文，缺字处就是目标格）；`seen17` 的上下文请从页图或原文取，不在此给。
- **刻意不含**：Lucian 的看图判读、建议字、分类器信号（避免带偏盲判；这些在 guji-workspace `research/y1_admit/h_cells/jys_seg3/`）。
- 用途：按「看字块图写所见字、可弃权、不给真值」跑二意见；输出 `out_muse_jiyisi_*.jsonl`，不放行任何格。
- 本分支基于 `claude/Evan-1011`（补抽清单原件 `char-groups/jys/ji_supplement_1011.{json,md}`）。
