# xuan 選𨕖 训练集（2026-10-26，A24 全册任务 03）

- labels.jsonl：339 格（選 297、𨕖 42）。選 是殿本 vol02–99 已放行格（放行字当标签）；𨕖 是看图补标：
  整理本作 𨕖 的送审格 35 格（看图都是丌形）＋放行成 選 而刻丌形的 7 格。
- crops/：字块（原图按 cell_shrink 框裁、去邻格碎墨）；split.json 按册。
- 建库与评测：open-guji-cv `research/m7/glyph_expand/build_shape_pair.py xuan`，组卡 `doc/字组/xuan.md`。
