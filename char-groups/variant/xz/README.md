# 象彖𧰼（xz）刻形标签与文意表补格（2026-10-26，A24 全册任务 08）

- `sheldon_labels.jsonl`：象／𧰼 刻形人裁表（343 格）＝unified.jsonl 人裁刻形＋sheldon 10-26 标注页（https://claude.ai/artifact/JXmfgGXNb1ZVAoSh6UEgVe，整理本预填、点改）。cv `config/groups/xz/ids_bank.json` 由它建（`build_shape_pair.py xz --labels=… --char-patch`）。
- `l2/xz.json`：文意 L2 表 ver `xz-l2-2`（原 500 格＋vol02–03、vol11–99 中 28 册 604 格），合表规则同 `groups.l2_panel`（haiku 主、opus 强、sonnet 第二）；`l2/runs/` 是三个模型的原始批结果，`l2/manifest.json`、`l2/cells.json` 是批与窗口。
- `回放-2026-10-26.jsonl`：30 册离线回放逐格结果（cv `research/m7/glyph_expand/replay_xz.py`）。

## 2026-11-01 补：新图源（qiefen-v2）格号版标签
- `sheldon_labels_qiefen.jsonl`：`sheldon_labels.jsonl` 按新图源改键（`id`＝现格号，`old_id`＝原格号）。vol01–50 用 ai-team `图源迁移/siku-qiefen-v2/results/old_new_cells` 格级表（对不上的丢弃）；vol51–99 暂无对照表，页号减 1（列、格不变）——抽查 vol51/68/78/87/95/97 共 88 格全部落在 象𧰼彖 上。
- 原 `sheldon_labels.jsonl` 键是旧图源格号，对现在的包是错位的（用它直接裁图会裁到别的字），只供重建模板库（模板自带字块图）用。
- 其中 vol20+ 的 ★main 包里仍在送审的 55 格（A24「压低象彖冠寇入人八送审」），已按本表做成人裁事件，待 sheldon 说「推」。
