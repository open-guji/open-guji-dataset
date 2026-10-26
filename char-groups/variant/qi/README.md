# qi 奇竒 刻形标签（A24，2026-10-26）

建库：open-guji-cv `research/m7/glyph_expand/build_shape_pair.py qi`（`PLAN["qi"]`），判法见 cv `doc/字组/qi.md`。
- 字形差别：上部 大（奇）／立（竒）；库常把 竒 排成 青音。
- `labels.jsonl`：殿本 vol51–99 已放行格（放行字当标签，每册每字 ≤12）＋首轮按册留出错例看图改标（src「看图补」）：放行成 奇、刻 竒 的 11 格，放行成 苛、刻 竒 的 1 格，放行成 竒、刻 奇 的 3 格改标；陪衬 音苛司 每字 ≤160。
- `crops/`：按 cell_shrink 框从原图裁的字块；`split.json`：按册留出的分组。
