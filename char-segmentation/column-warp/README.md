# char-segmentation / column-warp —— Step2 单列矫正的收尾

## 这个子集在测什么

Step2 拿 Step1 的边框/界行把一列矫正成竖直矩形之后，还要**把两侧的残余界行
和上下两端的版框残墨清掉**，才交给 Step3 切字格。这个子集测的就是"清得干净
不干净、有没有切到字"。

两部分金标：

1. **文字带左右边界**（`text_band`）——矫正图局部 x 坐标里，文字带从哪到哪。
   带外只该剩界行残墨、带内字身要完整。
2. **上下两端的版框残墨类别**（`border_class`）——`clean`（有残墨且跟首字之间
   有间隙）/ `glued`（有残墨但粘连）/ `none`（没残墨）/ `idk`。

## 边界是一条**走廊**，不是一个点

标注人明说：「我标定的不一定是唯一的坐标，应该让坐标尽量靠近两边（保持墨量
接近 0）」。所以每列存两组：

- `human_left/right` —— 人拖到的位置，**保守端**，一定落在零区里
  （实测人标点处的墨占比均值 0.0010 / 最大 0.0097）；
- `canonical_left/right` —— 从人标点**往外推到墨占比仍 ≤0.005 的最远处**，
  **激进端**。

算法落在 `[canonical, human]` 之间都算对；推过 canonical = 留残墨，越过 human
= 吃字。走廊宽度实测左 3.8px / 右 2.2px（均值）。

**两把尺子必须分开报**：留一点界行残墨下游还能救，切掉的字身墨谁也补不回来。

## 上下版框只记类别，不记坐标

用户定的：「如果确认了属于哪一类，基本很好切分」。所以那一页的标注界面**没有
可拖的线**，也不显示算法打算削几行——印上去会把人的判断带偏，而要量的正是
"人怎么分类"。

## 输入口径（**换了就得重标，别假设能迁**）

列图取 open-guji-cv 的
`output/<book>/step2_columns/<page>/c<N>.png`，由 `scripts/regen_step2_columns.py`
用 **`detect_borders` 算法探测的边线** + `page_column_windows` 逐列窗口生成——
也就是生产链路真正会喂给 Step2 的那张图，**Step1 的误差包含在内**。
样本的 `input` 那一块存了复现这张图所需的全部量。

另一套口径（人工金标边线 + 页级 x=0 锚点，隔离 Step1 误差）归档在
[`legacy-page-anchor/`](legacy-page-anchor/README.md)。

**上游还会一直改，所以「怎么少重标」是这套金标的一等问题。** 已经因为上游
改动作废过三轮（`head_raise` 列号归属 → 标注全部幸存；`verticals_inner` 按真墨
重拟 → 7/32 失效；输入换成算法边线+逐列窗口 → 15/32 失效）。前三轮是手工逐条
复核的，现在固化成 `scripts/migrate_column_warp_gold.py`：

| 金标 | 留用判据 |
|---|---|
| 文字带 | 把 `human_left/right` 放到新列图上，重算那两个 x 处的墨占比，≤0.01 就留用（`canonical_*` 按新图重推）。判据**就是金标自己的定义**「边界处墨量接近 0」，不依赖算法 |
| 上下版框类别 | 比 `end_fingerprint`（导出时存的、人当时看的那两张端裁剪图的 32×24 缩略），平均绝对差 ≤6 灰阶就留用。类别取决于"窗口裁到哪"，墨量判不了 |

**不拿算法的一致性当留用判据**——那会让金标永远测不出算法错，是循环论证。
容差标定过：列图横向平移 1~3px 时指纹差 ≈0（带跟着移、图其实没变，正是"变化
不大就不重标"该有的行为），平移 8px 才开始报警。没有 `end_fingerprint` 的老
样本一律判"需重看"，不猜。

**复核必须对全部原始标注跑**，不能只查"当前还留在金标里的"——实测有 2 条在
上一轮失效、在下一轮的新输入下又变有效，只查幸存者会永久丢掉。

`metadata.json` 的 `pending_relabel` 记着当前哪几列待重标。

## 选列规则（明说的，不是挑跑得好看的）

`open-guji-cv scripts/build_column_warp_review.py::pick_columns`：全部真抬头列
+ 倾斜量前 8 + 梯形量前 8 + 页级锚点偏差前 6 + 6 条各项都低于中位数的平稳列
对照 = 32 列 / 13 页。**故意超采样难例，所以这批不能当全书比例的估计**，
只能用来找失败形态。

## 当前状态与跑分

```bash
python scripts/eval_column_warp.py ../open-guji-dataset/char-segmentation/column-warp
```

| | 现行口径 | 归档的 legacy |
|---|---|---|
| 样本 | 29 列 / 13 页 | 25 列 / 13 页 |
| 文字带·命中走廊 | **53/58 条界** | 43/50 条界 |
| 文字带·吃进字身 | **0 列** | 2 列各 1px |
| `border_class` | **61 条，一致 57/60** | 22 条，一致 22/22 |

现行口径还差：3 列文字带重标（vol01/47 c2、c6、c7）+ 3 条端裁决重看
（47 c2 上 / c4 上 / c7 下——界行残条清掉之后那三张图变了）。

## 样本怎么造的

1. `scripts/regen_step2_columns.py vol01 --gold-pages` 生成列图 + `windows.json`；
2. `scripts/build_column_warp_review.py` / `build_column_border_review.py` 出两个
   交互标注页（种子取自算法判据，页面自存）；
3. 人工逐列核校；
4. `Artifact action:"read"` 读回，`scripts/export_column_warp_gold.py`
   （先跑，整份重写 metadata）+ `export_column_border_gold.py`（后跑，只加字段）导出。

URL 台账在 open-guji-cv `artifacts/README.md`。
