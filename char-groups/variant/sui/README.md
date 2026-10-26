# sui 歲嵗 刻形标签（A24，2026-10-26）

建库：open-guji-cv `research/m7/glyph_expand/build_shape_pair.py sui`（`PLAN["sui"]`），判法见 cv `doc/字组/sui.md`。
- 字形差别：上部 止（歲）／山（嵗）；库把 嵗 排成 歲 或 熾康嚴。
- `labels.jsonl`：殿本 vol51–99 已放行格（放行字当标签，每册每字 ≤12）＋首轮按册留出错例看图改标（src「看图补」）：vol56:48:2:5 上部墨糊剔出；陪衬 嚴巖熾 也在库里。
- `crops/`：按 cell_shrink 框从原图裁的字块；`split.json`：按册留出的分组。
