# band-ink：2b 字带左右边不抹字身墨

归属：CV2（2026-11-28，四大步验收 L4：2b 补一个含史記、全唐文的小分片）。量 `column_band` 定的文字带（带外抹白）有没有把字身墨抹掉。
殿本已有的 [side-rule](../side-rule)、[text-band](../text-band) 是殿本旧图源、旧量法；本集补史記、全唐文。

## 金标
同 [shrink-ink](../shrink-ink)：cut-bench 人核列里的列中干净格，字身墨框由连通域推出（不经人看）。每书 30 列，一列的干净格全收（史記 87 格、全唐文 275 格）。
`items.jsonl` 一行一列：`key`（书:册:页:列）、`split`（列键 sha1 整除 3 余 0＝blind）、`cells[]`（`slot`、`sub`、`ink` 字身墨框 [x0,y0,x1,y1]）、`label_origin: derived:cut-bench`、`coord`（raw_page_px@top-right）。

## 打分
`python -m open_guji_cv.eval.cut_ink band --items band-ink/items.jsonl --pred <产物根> [--against <旧产物根>] [--tol 2]`
读 `<册>/column_warp/`（列窗口）与 `<册>/column_band/`（字带），把字带左右边按列窗口映回原图，取每格纵向范围里字带最窄处：
- 抹墨（护栏，必须为 0／不增）：字身墨框伸出字带 >2px 的格；
- 余量：字带到字身墨的距离（像素，中位、p10），看字带收得多紧。

## 基线（cv dev d040498，2026-11-28）
| 书 | 列 | 格 | 抹墨格 | 余量中位／p10（px） |
|---|---|---|---|---|
| 史記 42 | 30 | 87 | 0 | 30.5／16.6 |
| 全唐文 053 | 30 | 275 | 0 | 64.9／50.6 |

## 局限
只收干净格，贴界行、笔画伸进界行的难例不在本集（那是 side_cut 最容易抹墨的地方，待人标一批再加）；余量大不等于有残线，残线看 cut-frame 与 cut_gate 的 L2c。
