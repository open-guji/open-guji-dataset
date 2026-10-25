# vol21–50 首跑补表批跑（A24，2026-10-25）

殿本 vol21–50 首跑（cv0.5.17-c22-g4）送审里 ry／rm／jys 大半是 L2 表缺格（cache_miss）。这里是给这 30 册补表的原始批跑结果。

- `<组>/cells.json`：补的字位（ctx_key 上下文各 20 字）；`manifest.json`：批 → 字位 id。
- `<组>/runs/{haiku,opus,sonnet}/*.json`：各模型逐条判（字、置信、依据），只按文意判，不看字形。
- 合表规则（`panel_vol21_50` 注记在表里）：haiku 与 opus 同字且都 high ＝ strong（可改已放行字）；其余新格须 opus 同字才给字，否则 `abstain:strong_dissent`；三家都判「其他」＝ `abstain:other`（日曰目 联判用）。
- rm 另有 217 格 ry 联判格（`joint_manifest.json`，批 rmj_*）。

回放（vol21–50 jys+ry+rm）：送审 1,181 → 253；`weak` 新放行 199 格人工逐条读过。
