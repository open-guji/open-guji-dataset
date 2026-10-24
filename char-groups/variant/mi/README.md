# mi 宻密 训练集（2026-10-24）

- `labels.jsonl`：一格一行。`src` 为「已放行格（放行字当标签）」「central:人裁刻形」或「看图（剔出模板的格）」；`in_bank` 表示进没进模板库。
- `crops/`：建库用的字块（bbox_page 从原图切、`ids_whole.clean_patch` 清洗后）。
- `split.json`：按册分折，评测判哪册，模板就不含哪册。
- 生成：cv `research/m7/glyph_expand/build_shape_pair.py mi <原图根> <工作区> <产物根> --write --dataset=<本仓>/char-groups/variant`。卡见 cv `doc/字组/mi.md`。
