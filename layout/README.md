# layout —— 第 1 大步「版面」几何金标

> A21，2026-11-23。评测代码在 open-guji-cv：`open_guji_cv/eval/layout_metrics.py`（指标）、
> `layout_gold.py`（适配器、体检）、`layout_bench.py`（入口）。

## 测什么

版面 = 直线（含破损线）→ 边框 → 界行 → 页型 → 几行几列。本分片是这一步的**几何金标**：
每页一条，记人核过的线的位置，不是「探测对不对」的判决。其他分片（`border-detection/*`、
`page-geometry`、`page-type`）仍留着，作历史回归和判决式护栏。

## 条目（统一信封，`items.jsonl`）

```json
{"id": "vol05:89", "anchor": {"book": "vol05", "page": 89, "source_rev": 5},
 "input": {"image_sha256": "…", "width": 2400, "height": 3200},
 "expected": { …LayoutDoc… },
 "label_origin": "human", "status": "active", "stratum": "keben-body|faint", "history": []}
```

`image_sha256` 必填：金标钉在**一张具体的图**上。殿本换过两次图源（IA → siku-qiefen-v2 →
文淵閣按版框重切），像素坐标换图就作废，不要按相似变换去「迁」几何金标（残差几个像素，
比要量的精度还大）；换图后重标。页型这类语义标签可以按页对照表迁。

## LayoutDoc（`expected`）

坐标：**原图像素、左上角原点**，x 向右、y 向下。竖线从**右到左**排。

| 字段 | 说明 |
|---|---|
| `width`、`height` | 图尺寸 |
| `vlines[]` | 竖线（界行＋左右版框）：`pts` 折线点 `[[x,y],…]`（y 递增）；`state`：`intact`／`faint`（淡、可见）／`broken`（有断口）／`inferred`（图上看不见，人按栅格补）；`gaps` 断口的 y 区间 `[[y0,y1],…]`（`broken`／`inferred` 必写） |
| `top`、`bottom` | 上、下**内**版框折线 `{pts}`；无则 null |
| `n_cols` | 正文列数（页内竖线数 −1）；有人核过才写 |
| `rows_per_col` | 每列字格数，右起；夹注列另记在 `tags` 里；没标写 null |
| `page_type`、`policy` | 页型与网格策略（`standard`／`custom`／`skip`），口径见 `page-type/README` |
| `frame` | 框型与外框（2026-11-23 起，可缺；缺＝没标过，不进框型指标）：`{top,bottom,left,right: {kind, outer, inner_w, outer_w}}`。`kind`：`double`（内外双线，`outer` 写外框折线）／`single`（只有一条线，如脈經上下；这条线记在 `top`/`bottom`）／`none`（没有，如装订侧）。`inner_w`、`outer_w` 线粗，像素（线两侧边缘间距，量不出写 null）。左右内框线是 `vlines[-1]`（左）、`vlines[0]`（右） |
| `tags[]` | 分层标签：`faint` `broken` `seal`（印章遮线）`wide`（宽页）`inverted`（反色带）`ink`（彩图）`bent`（折线弯页）`headraise`（抬头框）`gutter`（书口）等 |

`python -c "from open_guji_cv.eval.layout_gold import validate_doc"` 可体检一条（越界、乱序、
`broken` 没写 `gaps`、`n_cols` 与线数不符）。

## 框型与外框（2026-11-23）

各书框型不同：殿本、全唐文、史記上下都是内外双线、左右只在纸边一侧有外框；脈經上下**只有一条线**
（标在 `top`/`bottom`）、左右内外双线。金标写下每一边是哪种，评测量「框型认对没有」和「外框线位置偏差」
（`frame.kind_acc`、`frame.outer_px`）。
外框位置、粗细先由算法在内框线附近实测预填（`label_origin` 仍记 human 的是内框，外框历史里写明「frame prefilled」），
有把握的页直接并入，拿不准的页（外框不明、墨浅、超出图边、非正文页）做成复核包给人重标。

## 怎么标

1. 用现役算法跑出草稿（`layout_gold.doc_from_borders`），连叠图一起给标注人；
2. 人改线（拖点、补点、标 `state`／`gaps`）、改页型、数列数和每列格数；
3. 入库前跑 `validate_doc`；`label_origin=human`，草稿未改的页不得入库。

## 分层与抽样（每套书各类型抽几页，持续增补）

| 层（stratum） | 书 | 抽法 |
|---|---|---|
| `keben-body` | 殿本、全唐文 | 清楚页、淡线页、折线弯页、抬头页、印章遮线页、宽页各若干 |
| `keben-nonbody` | 殿本 | 职名、目录、封面、书签、牌记、上谕 |
| `shiji` | 史記（写本） | 正文、职名、年表、卷末大印 |
| `beixing-grid` | 北行（网格模式） | 线残破页、整页对开 |
| `free` | 幼学（自由版式） | 块与列 |
| `modern` | 现代排印书 | 正文、卷题、脚注 |
| `ink` | 彩图墨层书 | 压朱印前后 |

**dev**（迭代用）与 **test**（冻结）按页随机分，比例约 1:2；`test` 页不得用来调参，
新增页只增不换。`stratum` 字段形如 `<层>|<难例标签>`，split 记在 `input.split`。

## 评测

```bash
python -m open_guji_cv.eval.layout_bench --products <产物根> --book vol05 \
    --gold layout/items.jsonl --page-type-gold page-type/items.jsonl --out report.json
```

指标口径见 `layout_metrics.py` 模块头：线检出 P/R@{0.02,0.05,0.10}个列距、线偏差 p95（像素与列距比）、
破损线单独汇总（断口内偏差另记）、版框偏差、列数／行数准确率、页型策略准确率与**漏切率**。
