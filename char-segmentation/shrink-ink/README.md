# shrink-ink：2e 字框压缩不切字身墨（列中干净字）

归属：CV2（2026-11-28，四大步验收 L4：2e 补一个含史記、全唐文的小分片）。量 `cell_shrink` 的紧框在**列中**的字上有没有把字身墨切掉、有没有圈进框渣；列首、列尾字与上下版框归 [cut-frame](../cut-frame)。

## 金标怎么来（不是人画框）
从 [cut-bench](../cut-bench) 史記 42、全唐文 053 人核过的列（human／checked）取列中字格，在原图上做二值连通域（灰度 <128，面积 <30 像素的墨点不算）：
**干净格**＝没有一个连通域横跨格界（笔画粘连、贴界行的格都不收），字身墨框＝格内全部连通域的外包。
干净格的格界落在字缝里任何地方墨框都一样，所以只核到字数的 checked 列也能用。`label_origin` 记 `derived:human`／`derived:checked`。
脚本：cv `python -m open_guji_cv.eval.cut_ink build --bench <bench 根> --books shiji,qtw --out <本仓>/char-segmentation`（seed 1128，每列至多 3 格，每书约 150 格）。

## 覆盖
史記 42：150 格（tune 95／blind 55），全唐文 053：151 格（tune 110／blind 41）。殿本、脉经不收（11-25 Sheldon 定殿本尽量不动；脉经待补）。
干净格只占列中格的 15%（史記，写本笔画多粘连）～47%（全唐文），**难例（粘连、贴界行）不在本集**，那部分看 cut-lattice 的折线与 cut-frame。

## 字段（items.jsonl 一行一格）
`key`（书:册:页:列:slot[:sub]）、`book`、`vol`、`page`、`col`、`slot`、`sub`、`kind`、`split`（格键 sha1 整数除 3 余 0＝blind）、`status`、
`tight`（字身墨框 [x0,y0,x1,y1]）、`quad`（金标格四边形，用来判第二步格号对不对得上）、`label_origin`、`coord`（raw_page_px@top-right）。

## 打分
`python -m open_guji_cv.eval.cut_frame --items shrink-ink/items.jsonl --pred <产物根> --junk-tol 6 [--against <旧产物根>]`
- 切笔（护栏，必须为 0／不增）：紧框有一边比字身墨框往里收 >2px；
- 带渣：往外扩 >6px（紧框本来留 2–4px 边，所以容差放宽）；
- 错格：第二步切出的格与金标格 IoU <0.75，归 2d，不判切笔带渣。

## 基线（cv dev d040498，cut_bench run 不带人裁，2026-11-28）
| 书 | 格 | IoU@0.9 | 切笔 | 带渣 | 缺格 | 错格 |
|---|---|---|---|---|---|---|
| 史記 42 | 150 | 0.907 | 0 | 1 | 0 | 8 |
| 全唐文 053 | 151 | 0.921 | 1 | 8 | 2 | 8 |

看图（11-28）：全唐文带渣 8 格多是紧框圈进格边的纸面墨点或多留几像素，切笔 1 格（113:3「師」左边）是金标连通域与紧框各取一点的差；IoU@0.9 达不到 1 是因为紧框留边，不是错。

## 局限
金标没经人看，墨框的像素精度取决于二值门槛；用作护栏（切笔、带渣的**翻转**），不用作绝对分。以后出 col_check 抽查页让人点一轮再升 1.0。
