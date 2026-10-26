# pai 派𣲖 刻形标签（A24，2026-10-26）

建库：open-guji-cv `research/m7/glyph_expand/build_shape_pair.py pai`（`PLAN["pai"]`），判法见 cv `doc/字组/pai.md`。
- 字形差别：右边 𠂢 有横（派）／无横三竖（𣲖）；字形库没有 𣲖，库排成 泒。
- `labels.jsonl`：殿本 vol51–99 已放行格（放行字当标签，每册每字 ≤12）＋首轮按册留出错例看图改标（src「看图补」）：放行成 泒、刻 𣲖 的 vol62:140:5:16 改标。
- `crops/`：按 cell_shrink 框从原图裁的字块；`split.json`：按册留出的分组。
