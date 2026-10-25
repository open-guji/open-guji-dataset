# zhuan 撰𢰅 训练集（2026-10-24）

- `labels.jsonl`：一格一行。`src` 为「已放行格（放行字当标签）」或「看图补」（放行成 撰、看图刻形是 𢰅 的 22 格，改标 𢰅，`by=claude-压低3-4格异体对送审`）；`in_bank` 都进了模板库。
- `crops/`：建库用的字块（bbox_page 从原图切、`ids_whole.clean_patch` 清洗后）。
- `split.json`：按册分折，评测判哪册，模板就不含哪册。
- 生成：cv `research/m7/glyph_expand/build_shape_pair.py zhuan <原图根> <数据目录> <产物根> --write --dataset=<本仓>/char-groups/variant`。卡见 cv `doc/字组/zhuan.md`。
