# 日曰 muse 有界试验（overview#437，Evan，2026-10-11）

给 Dax（muse 驱动）。**只喂 `blind.jsonl` 里的 `left`／`right`，不要读 `truth_NOT_FOR_MUSE.json`**（真值，用于事后评测）。
- 输入：`blind.jsonl` 99 行 `{cid,left,right}`（前后各 30 字，刻本读序；未放行邻格是整理本字——不是整理本全文，只是邻字）。
- 提示词：`PROMPT.txt` + 每行拼接 `前文：<left>\n【？】\n后文：<right>\ncid：<cid>`，一格一次调用；schema `schema.json`。
- 调用数：99（一遍）；若要补第二遍，只对 `conf` 不是 high 的行，**总调用 ≤200**。
- 参数：`muse exec --prompt-file … --output-schema schema.json --max-model-steps 2 --disable-shell --disable-write --disable-web-tools --no-foreign-personal-context --no-session-log`，并发 2–4，撞 429 全体停。
- 输出：`muse_out.jsonl`（每行 muse 的 JSON），放回本目录推分支；评测 `python research/char_groups/ry/muse_eval.py <本目录>`。
- 判据（Mila 定）：**给字准确率 ≥95% 且「真日判成曰」方向 0 错**；够 → 下一步再扩样；不够 → 日曰收口（不接线）。
