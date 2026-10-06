# near-form-groups — 形近字组样本集

三组：**己/已/巳**（jys）、**日/曰**（ry）、**入/人/八**（rr）。来源：四庫总目武英殿刻本 vol02、vol03 的人裁，加 vol04 试跑里看图判过的格
（overview#428，N1，2026-10-06）。一格只要放行字、整理本字、坐标证人字、库前二候选、上下文首选、真值任一落在某组里，就进那一组
（一格可同属多组，`group` 字段区分；做总数时按 `id` 去重）。

## 一行一格（`items.jsonl`）
`id` `book` `page` `col` `slot` `sub` `group` · `gold` `gold_src` `gold_note` · 现行产物：`admit` `channel` `char` `doubts` `ref`（对位整理本字）
`coord_ref`（坐标对位证人字）`lib`（库前三候选）`ctx`/`ctx_ranked`（Step6 上下文）`ocr` `ji_yi_si` ·
上下文：`left`/`right`（读序前/后各 5 字，未知格用整理本字补，缺位「□」）`ref_left`/`ref_right`（整理本的对应字）`word`（前 2 字【本格】后 2 字）·
图：`crop`（`crops/` 下字块灰度图）`kind` `ink` `wh`。

## 真值分档（`gold_src`）
- **强真值**：`human`（人裁事件，后到覆盖；己已巳老事件取「读作」一栏）、`look_v04_jys`/`look_v04_s8`/`look_v03_s8`（看图结论）、`card426`、`muse_truth`（vol03 muse 试点，human + 看图）；
- **弱真值**：`witness_agree`（已放行、非人裁、放行字＝整理本＝坐标证人）——**对 match_ref 是循环的**，只作参考，己已巳不给这一档；
- 其余 `gold=null`。

## 偏差（用之前要看）
强真值格是机器拿不准才送人看的，**是难例，不是全书的随机样本**。拿它量出的错率比全书错率高；入人八强真值只有 12 格，只能当线索。

## 数量
| 组 | 册 | 强真值 | 弱真值 | 无真值 | 合计 |
|---|---|---|---|---|---|
| jys | vol02 | 53 | 2 | 7 | 62 |
| jys | vol03 | 56 | 5 | 0 | 61 |
| jys | vol04 | 20 | 2 | 73 | 95 |
| ry | vol02 | 36 | 274 | 6 | 316 |
| ry | vol03 | 18 | 98 | 4 | 120 |
| ry | vol04 | 4 | 229 | 31 | 264 |
| rr | vol02 | 6 | 267 | 4 | 277 |
| rr | vol03 | 5 | 173 | 5 | 183 |
| rr | vol04 | 1 | 389 | 18 | 408 |

量法与结果见 overview#428 与 open-guji-cv `research/near_form/`（`build_samples.py` 建集、`measure.py` 各通道错率、`ctx_eval.py` 上下文表、`final_report.py` 前后对照）。
