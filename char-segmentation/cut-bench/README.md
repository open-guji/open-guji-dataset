# cut-bench：第二步「切字」整步固定样本集（金标）

归属：CV2。2026-11-23 起在 ai-team `domain/CV/A22/cut-bench/gold/` 维护，2026-11-28 搬进本仓（四大步验收 S12）。
打分脚本住 cv：`python -m open_guji_cv.eval.cut_bench`（freeze／run／score／gate，见 cv `doc/2-切字/README.md`「benchmark」）。

## 覆盖
| 书 | 册 | 页 | 测试集 random／hard（页） | 人核列（human＋checked） |
|---|---|---|---|---|
| 史記（988g3f0wsu） | 42 | 40 | 15／25 | 310 |
| 全唐文（995ejelvk0） | 053 | 40 | 18／22 | 321 |
| 殿本 四库总目（96mid1ogzk） | vol01 | 40 | 27／13 | 333 |
| 脉经（99k3i35yww） | 01 | 35 | 12／23 | 420 |

缺：朱楓林集、汉书（验收标准第三节要的「同上＋朱楓林集、汉书」还没有）。

## 文件
- `<书>/bench.json`：册、页、冻结时的产物包、测试集划分 `splits`（random＝随机整页，量真实准确率；hard＝有人钉的页与点名难例，偏低）。
- `<书>/<册>-<页4位>.jsonl`：一列一行。`label_origin`：human＝人钉或人修过、Sheldon 确认；checked＝算法格经人抽查全对（`checked_level`：count 只核到字数与大致位置，cut 切点也核过）；silver＝没抽查的草稿（`status: draft`，不计分）。`status: needs_fix` 金标待修，不计分。
- 每列：`n`、`kinds`（L1 字数与类型序列），`cells[]`：`slot`、`sub`、`kind`、`quad`（L2 格四边形）、`tight`（冻结时的紧框，**不是金标**：人钉只定上下，左右沿用列宽）。坐标一律原图 raw_page_px@top-right。
- 格的键（册:页:列:slot）挂在原图坐标上，拉直、缩放怎么改都不失效；殿本 11-04 换过图源，本集按新图源。

## 用法
冻结输入（原图、第一步产物、册配置）要从中心库与产物包取，见 cv `open_guji_cv/eval/cut_bench.py` 模块头；
`freeze --gold-from <本目录>/<书>` 直接拷本集金标，不再从产物包起草稿。

## 版本
- 1.0.0（2026-11-28，CV2）：从 ai-team cut-bench gold 原样搬来（截至 11-25 v1.1 修正、11-27 折线不在这里，折线在 `cut-lattice/polylines.jsonl`）。
