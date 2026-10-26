# 象彖𧰼（xz）刻形标签与文意表补格（2026-10-26，A24 全册任务 08）

- `sheldon_labels.jsonl`：象／𧰼 刻形人裁表（343 格）＝unified.jsonl 人裁刻形＋sheldon 10-26 标注页（https://claude.ai/artifact/JXmfgGXNb1ZVAoSh6UEgVe，整理本预填、点改）。cv `config/groups/xz/ids_bank.json` 由它建（`build_shape_pair.py xz --labels=… --char-patch`）。
- `l2/xz.json`：文意 L2 表 ver `xz-l2-2`（原 500 格＋vol02–03、vol11–99 中 28 册 604 格），合表规则同 `groups.l2_panel`（haiku 主、opus 强、sonnet 第二）；`l2/runs/` 是三个模型的原始批结果，`l2/manifest.json`、`l2/cells.json` 是批与窗口。
- `回放-2026-10-26.jsonl`：30 册离线回放逐格结果（cv `research/m7/glyph_expand/replay_xz.py`）。
