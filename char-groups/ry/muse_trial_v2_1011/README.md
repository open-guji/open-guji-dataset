# 日曰 v2（带弃权）三家对照（overview#437，Evan，2026-10-11）

用户 10-11 定：日曰再试一轮，提示词改成「没把握就说不确定」，muse／Gemini／Haiku 三家同表同提示词，看「覆盖率—准确率」。

## 给执行者（Dax＝muse，Dana＝Gemini，Haiku 道）
- **只读** `PROMPT_v2.txt`、`schema_v2.json`、`blind_99.jsonl`、`blind_holdout.jsonl`。**不要读** `truth_*_NOT_FOR_MUSE.json`、不要读别家的 `out_*`。
- 每格一次调用：提示词 + `前文：<left>\n【？】\n后文：<right>\ncid：<cid>`，输出 schema_v2。
- 两份表，**各跑一遍，不重跑、不调提示词**：
  1. `blind_99.jsonl`（99 格，与 v1 同表，用来对照 v1 的 93.9%）→ `out_<模型>_99.jsonl`
  2. `blind_holdout.jsonl`（200 格，**不与 99 重叠**，vol02–10 分层；v2 定稿后的留出）→ `out_<模型>_holdout.jsonl`
  `<模型>` 取 `muse`／`gemini`／`haiku`。共 299 次调用；muse 额度若不够（上轮口径 ≤200），先跑 99 再跑 holdout 的前 N 行，别超额，超了报 #437。
- muse 参数同 v1（`--max-model-steps 2 --disable-shell --disable-write --disable-web-tools --no-foreign-personal-context --no-session-log`，并发 2–4，撞 429 全体停）。
- 输出放回本目录推 dataset 分支 `claude/Evan-1011`，在 #437 回一行。

## 评测
`python research/char_groups/ry/muse_eval2.py <本目录> 99|holdout muse gemini haiku`（cv 分支 `claude/Evan-1011-ry`）。
每家：给字率、给字准确率、真日判曰、弃权格真值分布；再报「三家一致」「两家一致」「≥2 家一致且无反对」。
与已有字形分类器（宽高比＋搭配）的联合项，等三家结果到了再加（用 `../clf_scores.json`）。

## 口径与警告
- 过线：给字格「真日判曰」0 错且准确率 ≥99%，覆盖率不设下限。
- **99 格真值**：A_human 90＋B_vision 9，强真值。
- **holdout 真值是 C_weak**（现行管线放行的字，不是人裁）：日 80／曰 120，**会含真值本身的错**。所以 holdout 上「模型≠真值」的格不直接算模型错，要先人读（在线原文）裁一遍再记；第一遍报数时单列「与弱真值不一致的格」清单。
- 邻字里的「日／曰」是管线的字，可能错；提示词已告诉模型别当证据。
- 99 格上不再调提示词。
