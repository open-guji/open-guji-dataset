# char-segmentation / column-end-class —— Step2 列端（上/下端）版框类别

## 这个子集在测什么

Step2 对每一列的**上端、下端**要决定「版框怎么处理」——现行是 `column_border_trim` 的 a~e 档（带层数后缀如 `a2`）
加 `triage` 的 `end_class`，约 33 个阈值、25+ 个分支，补丁按单页单列点名（overview 总览/16 盘点的「全管线之最」）。
这里记**人眼对每一端削版框之前的形态判断**，是把这套规则换成学习模型的训练/验收标签。

前身是 `column-warp` 里的 `border_class`（clean/glued/none/idk，64 条）。类别体系不一致，另起分片，不混。

## 类别（统一，用户 2026-10-01 定）

| `expected.class` | 含义 |
|---|---|
| `none` | 这一端没有版框墨 |
| `trim` | 版框与首字（末字）之间有间隙，**整段削掉不伤字** |
| `glued` | 版框粘着首字（末字），削不开 |
| `double` | 版框是两道（外粗内细等），要连第二道一起削 |
| `idk` | 拿不准 / 迁移来的旧卡（见下） |

旧体系值的映射：`clean`（「有框墨且与首字有间隙」）→ `trim`，`glued/none/idk` 同名同义，旧值留在 `expected.legacy_class`；
旧体系没有 `double`，旧 clean 里的双层框要重标，收割时不猜。

## 条目

`id = <book>:<page>:<col>:<top|bot>`（`bot` 下端）。`expected`：`class`、`end`、引擎当时的
`engine_trim_case` / `engine_trim_px` / `engine_end_class`（对账用，**不要拿来当特征训练人判**）。
`anchor`：`book/page/col`、`space = raw_page_px@top-right`、`bbox` = 端裁剪区（220 行）在原图上的外接框、
`product_key` = 出卡时 `column_warp` 产物的指纹。`input`：`source`、`version`、`batch`、
`end_fingerprint`（16×16 均值哈希，「人当时看的那张图还在不在」）、`geom_sig`、`fp_match`（点卡时产物指纹与出卡时是否一致）。

## 来源

| `input.source` | 含义 | 可进评测 |
|---|---|---|
| `L3-batch` | `guji label-batch make column-end` 出的分层批次，人在控制台 Step1「单列版框」点的，**削版框前**的列端图 | ✔ 带 `stratum` / `stratum_weight` |
| `legacy-overview` | overview 仓 `inbox/S-列尾抽查页/20260927-verdicts.jsonl` 的 104 张卡里的 **74 个列端**（vol02，列尾 59 / 列首 15），cv `92e75e3` 新版 | ✘ 只作线索 |

⚠️ **legacy-overview 问的不是这个分片的问题**：旧卡展示的是**削完之后**的新旧两版，问「这一端干净 / 还有框线残留 / 字被切掉」
（`clean`/`residual`/`cut<N>`），是削后状态，不是削前类别，无法无损映射——所以 `class` 一律 `idk`、`status=uncertain`，
原值存 `expected.legacy_verdict`，并附 `legacy_hint`（只是提示）。该批 104 条里另有 30 张是**末字块挂横线**卡（`l` 前缀，
问字块上的横线），不是列端，未迁入。旧卡没有图像/产物指纹、没有页面坐标锚（只有 `t008_p33c2` 这种卡片 id）。

## 抽样与无偏估计

`L3-batch` 是**分层、难例超采样**的（层 = 现行 trim 档位 × triage end_class），**不能直接数比例**。
每条带 `stratum` / `stratum_weight`（= 该层总体数 ÷ 抽样数），全书率 = Σ wᵢ·xᵢ / Σ wᵢ。各层总体数见批次的 `<批次>_sampling.json`
（在出批次那台机器的 `review/batches/`）。

## 怎么来的

```bash
guji label-batch make column-end <册> --n 240     # 本机，按现行 column_warp 产物
# 控制台 Step1「单列版框」页码框填 batch:<批次id>，点完
guji label-batch harvest <批次id> --dataset ../open-guji-dataset
guji label-batch migrate-legacy <overview>/…/20260927-verdicts.jsonl vol02   # 一次性，已执行
```
手册：open-guji-cv `.claude/doc/console_manual.md` §11。
