# char-segmentation / column-counts —— 殿本逐列字数（双源一致金标）

## 这个分片在测什么

**切分产物每一列切出几个字，对不对。** 一列一条，覆盖殿本（96mid1ogzk）vol01–vol10 正文页。

| 字段 | 含义 |
|---|---|
| `anchor` | `{book: volNN, page, col}`；列号右起、从 1 开始（与我们的切分口径一致） |
| `expected.n` | 这一列的字数（正文 + 双行小注两行，读序） |
| `expected.n_main` / `note` | 正文字数；双行小注 `{start, r, l}`（小注起格、右行字数、左行字数），无小注为 `null` |
| `expected.start` | 首字格位（daizhige 口径：0 起，−1 = 出格抬头） |
| `expected.text` | 这一列的字（daizhige 逐列本，映不上的 PUA 记 〓） |
| `input` | 两份来源的出处：`dzg_half`（daizhige 半叶）、`release`（另一印本的切分 release：卷序 ch、页 p、字数 n） |

评测：`guji eval run column_counts`（`open-guji-cv/scripts/eval_column_counts.py`），报告型，无回归门。

## 金标怎么来的、为什么能信

**不是任何一份来源本身，是两份互相独立的来源一致时的那个数**（open-guji-cv `doc/design/19-…总设计.md` §三）：

1. **daizhige 逐列本**——维基文库人工逐列校对（文淵閣四庫全書總目 0001–0004 冊 Progress=C），
   每列带首字格位；`guji-workspace/96mid1ogzk…/corpus/daizhige/page_map.jsonl` 已把我们 vol01–10 的
   1,707 页逐页对到它的半叶（人读锚点 + DP，2026-09-28）。
2. **release**——open-guji-core/file_archive `siku-qiefen`：殿本另一印本扫描上 yolo-tool 出框、人工修框，
   每框一字（16,516 页）。页面与 daizhige 半叶按文本单调配对，列按读序单调 DP 配对。

两边这一列**字数相同、文本相似度 ≥0.8** → `label_origin: consensus`。
生成：`python scripts/dzg_import.py colgold --ws <四庫工作区> --release <release 目录> --export <本分片>`（open-guji-cv）。

| 量 | 数 |
|---|---|
| vol01–10 列 | 14,987（全部进金标；另 2 条撞号已剔除，见下） |
| 两源一致（`consensus`） | 14,931（99.62%） |
| 不一致（`human`） | 56：多在夹注列与职名页长列，release 按 x 聚列把一列拆成两列。人裁 7 张全判 daizhige 对；用户 2026-10-19 定其余 49 列一律取 daizhige（history 里记了是统一裁定） |

**撞号剔除**（2026-10-19）：一个 (册,页,列) 只许一条。vol01 p102 c1 是职名页，daizhige 把一物理列的上下两段（「翰林院庶吉士臣蔡廷舉」「收掌官」）记成两列、撞到同一列号，两条都不收（`dzg_import colgold` 起标 `dup`，不进本分片也不进 C 的表）。

**残错抽检没做**：原定一致列随机抽 300 列人看（种子 20261019，卡表在 open-guji-cv
`research/yolo_release_compare/results/colgold_review_cards.jsonl`），用户 10-19 定不做（「太多、没意义」）。
所以金标的残错率**未量**；依据只有「两份独立来源一致」与「抽看的分歧都是我们切错」这两条间接证据。

**用法纪律**：报「与金标一致率」时，凡据此下结论的改动，把前后翻转的列全部出图人看——
残错只要不偏向改动的那一边，就不影响比较。发现金标错，改金标并记 `history`。

## 基线（2026-10-19，open-guji-cv main 0ddbec3 起的 feat/yolo-colcount-prior）

| 口径 | 全对 | 说明 |
|---|---|---|
| 纯算法（不带人裁），vol04/05 抽 100 页 | 872/899 = 97.0%（正文 97.2%、夹注 94.1%） | 研究文档测试 B 那 100 页 |
| 同上 + 原生 YOLO 并格（实验） | 885/899 = 98.4% | doc/design/19 块 D |
| 同上 + C+D（逐列字数先验＋原生 YOLO 并格，最终版） | 886/900 = 98.44% | 金标含 56 列人裁后 900 列 |
| 现行生产（带人裁）全书 10 册 | 14,514/14,987 = 96.84% | 各册 93.9%（vol08）～98.9%（vol02） |
| 现行生产 + C+D 全书 10 册 | 14,662/14,987 = 97.83% | 修 149、新错 1（vol07:44:5，即上面改过 start 的那条）；人裁过的列 C、D 不动 |

## 与 `column-slots` 的分工

`column-slots` 是人裁「这一列 DP 切几格」（DP 的输入约束，含留白格）；本分片是「这一列有几个字」（产出的验收）。
