# vol51–99 首跑补表批跑（A24，2026-10-26）

殿本 vol51–99 首跑（cv0.5.21-c23-g4，vol51 是 cv0.5.19）送审里 jys／ry／rm 大半是 L2 表缺格（cache_miss）。这里是给这 49 册补表的原始批跑结果，做法与 `../vol21_50/` 相同。

- `<组>/cells.json`：补的字位（ctx_key 上下文各 20 字）；`manifest.json`：批 → 字位 id；`sonnet_manifest.json`：sonnet 复核批；rm 另有 `joint_manifest.json`（194 格 ry 联判格，批 rmj_*）。
- `<组>/runs/{haiku,opus,sonnet}/*.json`：各模型逐条判（字、置信、依据），只按文意判，不看字形。
- 合表规则（表里 `panel_vol51_99` 注记，ver `+v5199`）：haiku 与 opus 同字且都 high ＝ strong；其余新格须 opus 同字才给字，否则 `abstain:strong_dissent`；三家都判「其他」＝ `abstain:other`。

回放（vol51–99 jys+ry+rm，`replay_groups.py --raw`）：送审 1,717 → 346（jys 1,159→121、ry 534→201、rm 24→24）；非 strong 的新放行／改字 269 格逐条读过，未见错。
