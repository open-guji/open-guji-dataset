# char-segmentation / touching-cuts —— 粘连格线的理想切点

## 这个子集在测什么

Step3 的 R2s（真粘连）格线：格线处行墨占比 > 0.02，且 ±12px 内没有 ≤ 0.02 的墨谷
——投影法在这里没有任何信号，此前只能"标 flag 交人审"。2026-09-05 用户裁定
「R2s 从现在起不该被忽略，也要优化；先让我添加金标确定理想位置，再想算法」。

本子集记录的是**每条粘连格线人眼认为该切在哪**（像素级 y），是所有粘连切分算法
共用的尺子。人裁缺陷（`instances` 的 truncated/contaminated）只说"切坏了"，不说
"该切哪"；这里补的正是位置。

## 金标怎么来的

控制台「切线」页：卡片 = 上下两格的列图裁片（1:1 像素，前端放大 2 倍显示）+ 一条
可拖的横线（初值 = 现役 Step3 切点）。人把线拖到理想位置后：

| verdict | 含义 | y |
|---|---|---|
| `moved` | 拖到了更好的位置 | 新位置 |
| `ok` | 现役切点就是理想位置 | = y_old |
| `overlap` | 上下字物理重叠，切在哪都会伤字；y 是人给的折中位置 | 折中位置 |
| `seam_ok` | 现役折线缝（卡片上的绿虚线）已经是理想切法；`polyline` = 现役缝每 6px 抽样 | 缝的平均高 |
| `idk` | 拿不准（进 `uncertain`，不进指标） | — |

事件 kind = `cutline`（`feedback/events.py`），路由 → `gold_add` → 本子集。

**干扰标签 `tags`**（可多选，落定前点；用户 2026-09-05 裁完第一批点名的两类）：

| tag | 含义 | 例 |
|---|---|---|
| `stain` | 污点正好在分界处 | vol01:157:1:13 |
| `border` | 界行 / 版框压进裁片，影响判断 | vol01:30:3:20 |
| `residue` | 邻字残墨拖过格线 | |
| `other` | 其他（`note` 里写一句） | |

带标签的条目在评测里**单独一档**，不进像素误差——切点本身不是切分算法能决定的。

**折线 `polyline`**（2026-09-05，用户：「相当多的情况，一条折线的无墨路线是最优解」）：
卡片的折线模式下，人在图上点 ≥2 个点连成折线，存 `polyline: [[x, y], …]`（列图坐标，
x 递增）；`y` 仍记折线的平均高，直线口径的评测照常用。评测把折线按 x 插值成"每 x 一个 y"
（与 `Cell.seam_*` 同口径），与现役缝（没有缝就是直线）比**最大 / 平均纵向偏差**。

## 坐标系（金标什么时候会过期）

`y` 记在**现役 v2 Step2 列图**（`column_image` 产物）的行坐标里，同时记了
`col_h`（该列图高度）。Step2 的矫正矩形不变，这批 y 就一直可用；若将来 Step2 改了
矫正（列图高度变化），`col_h` 对不上即为信号，需要像 `row-boundaries` 那样用
版框 / 墨量曲线重锚定（`scripts/eval_row_boundaries.py` 有现成做法）。

条目 id = `book:page:col:slot_above`（以上格格位定名），`bi` 是该列内部格线序号
（1 = 第一格与第二格之间）。

## 评测

```bash
python -m open_guji_cv eval run touching_cuts
```

指标：现役切点与金标 y 的像素误差（mean / median / p90；≤3 / ≤5 / ≤10px 比例），
只算 `moved` / `ok`；`overlap` 单独计数（这一档算法只能折中，不算误差）。

## 采样口径

- 只出**正文页**（page-type 金标 body）；职名页 / 目录页格数先验不同，稍后另出。
- 上下两格都是正文字格（`kind == "char"`）；夹注旁的切线另案。
- 确定性抽样（seed=0），按页轮转，避免全落在两三页挤排页上。


## L3 补标签批（2026-10-01）：页面坐标口径的新条目

`input.source = L3-batch` 的条目由 `guji label-batch make cutline-gold <册>` 出的**分层抽样**批次收割而来
（open-guji-cv `.claude/doc/console_manual.md` §11）。与旧条目的区别：

- **锚在原图页面坐标**：`expected.page_x_tr / page_y / page_w`（`anchor.space = raw_page_px@top-right`，右上原点），
  `anchor.bbox` = 上下两格外接框，`anchor.product_key` = 出卡时 `row_segment` 产物指纹；
  `expected.y` 仍是列图行号（评测沿用），换到当前列图用 `eval/colgeom.gold_rows_now`。
  控制台事件里原有的 `page_x/page_y` 是**左上原点**，收割时统一换成右上原点（旧值留在 `expected.page_x/page_y`，
  `expected.page_xy_space_legacy` 标明口径）。
- **带 `version` / `source`**：`input.version = L3-batch:<批次>`，`input.sampling` 记该切点的上下文/难度/候选数/`dis_unet`/`agree`。
- **分层超采样**：`stratum` = `上下文|难度`，`stratum_weight` = 该层总体数 ÷ 抽样数。**不能直接数比例**，
  加权估计：Σ wᵢ·errᵢ / Σ wᵢ。旧条目没有权重，**别把两批混着算均值**。
- 只新增、不改旧条目；已在金标里的切点不出卡、id 撞了也不覆盖。
- `status=stale`：事件没带页面坐标（取不到列窗几何），不进评测；`uncertain`：拿不准。
