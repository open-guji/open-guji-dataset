# ci 文意组 L2 表

2026-10-27，A24「组外异体对未定码位」。组卡见 open-guji-cv `doc/字组/ci.md`。

- `batches/`：出给模型的批（`research/m7/ctx/l2_new_groups.py make`），收的格＝回放补放入口的格＋复核里放行字是次形或与整理本不一致的格。
- `l2/runs/<模型>/`：haiku、opus、sonnet 三遍原始输出；`l2/ci.json`：`l2_new_groups.py ingest` 合表，三遍都 high 同字记 `strong`。
- `replay_2026-10-27.jsonl`：vol02–99（除 vol06）离线回放结论；改动逐格读过上下文（by=claude-a24-任务01）。
- 上线：`l2/ci.json` 放进中心库 `config/groups/l2/ci.json`（要「推」）。
- 2026-10-27 sheldon 定「乖剌」「剌謬」按文意录 剌（整理本一律作 刺）：已放行作 刺 的 15 格（vol06 不碰）另出一批 `batches_guai1027/`，三遍原始输出 `l2/runs_guai1027/`，并进 `l2/ci.json`（ver ci-l2-1+guai1027），strong 14。回放：复核改字 刺→剌 14、降审 1。
