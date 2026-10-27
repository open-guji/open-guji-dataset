# feng 文意组 L2 表

2026-10-27，A24「组外异体对未定码位」。组卡见 open-guji-cv `doc/字组/feng.md`。

- `batches/`：出给模型的批（`research/m7/ctx/l2_new_groups.py make`），收的格＝回放补放入口的格＋复核里放行字是次形或与整理本不一致的格。
- `l2/runs/<模型>/`：haiku、opus、sonnet 三遍原始输出；`l2/feng.json`：`l2_new_groups.py ingest` 合表，三遍都 high 同字记 `strong`。
- `replay_2026-10-27.jsonl`：vol02–99（除 vol06）离线回放结论；改动逐格读过上下文（by=claude-a24-任务01）。
- 上线：`l2/feng.json` 放进中心库 `config/groups/l2/feng.json`（要「推」）。
