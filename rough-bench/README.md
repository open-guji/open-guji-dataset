# rough-bench —— 粗校基准（M9 D6-5，GUJI-669）

## 这个分片是什么
专家的改动（字组、字形库、切分、语料……）进 rc 之前，先在这份**冻结的**页与标签上量两个数：

1. **人审率变化**：正文页送审率（送审格 ÷ 正文页全部格），变体对基线；
2. **错放数**：有标签的格里，放行了、字又不对的格数。**新增错放（基线对、变体错）必须为 0**；
   基线本来就错的格另报，那是现行版的已知错，不算这次改动的账。

设计见 open-guji-cv `doc/design/M9-平台粗校-调研与总设计.md` D6 第 5 条，口径见 open-guji-cv `open_guji_cv/exp/rough_bench.py` 模块头。

## 文件
- `bench.yaml`：册（四庫總目殿本 vol04–10）、每册冻结的页、快照产物包标签、判准。
  - 页：每册正文页里，标签分最高的 16 页（`hard`，人裁一格 3 分、看图一格 1 分）加其余正文页里按种子 0 随机的 12 页（`random`）。
  - 快照：冻结时各册的 main 产物包（`snapshot_packs`），跑基准时从 R2 取回。vol04 的 main 还是 v0.4.6（没开版面先验），vol05–10 是 v0.4.9＋语料 9＋版面先验。
- `items.jsonl`：冻结的标签，统一金标信封，`guji exp` 的 `gold` 标签来源直接读。
  - `expected.char`：这格该是的字；`expected.defect`：切坏／非字；`expected.wrong`：只知道不是这些字（看图判错没认出）；`expected.sub`：夹注 a／b。
  - 没有 `stratum` 的是**随机样本**（出口 S8 对已放行格的抽查），可以估错率；`stratum` 为 `human_queue`（人裁，来自审查队列）、`vision_picked`（看图，来自差异核对）的是挑过的样本，**只报计数，不能当错率**。
  - `input.bind`：人裁对到快照切分的方式（`valid` 同格号、`rebound` 列内顺移后改绑）；`input.from_key`：人裁当时的格号。
- `report.json`：冻结时现行代码在快照上跑出来的基线数，只跑基线时的回归门比它。

## 标签怎么来的（金标不由被测算法生成）
- **人裁**：中心库 `feedback/events/` 里能当人裁用的格级 confirm（不含看图结论），每格取最新；按绑定表对到快照的切分，`valid`／`rebound` 才收（快照不带字块缓存，只按锚框几何判）。
- **看图结论**：中心库 `feedback/vision/`（会话看图，不是 seed_admit 的输出）。没有锚框，只收「快照这一格的现行字＝看图时显示的字」的格——同一块像素、同一个字，几乎不会对错格。`unsure` 不收。
- 同一格人裁优先；人裁与看图说的字不同的 6 格以人裁为准。

## 怎么用
```bash
cd ../open-guji-cv
# 现行代码对冻结基线（要工作区与读令牌；快照缺了自动取）
python scripts/eval_rough_bench.py ../open-guji-dataset/rough-bench -w $WS --jobs 2
# 专家改动：变体 yaml 同 guji exp（params: {seed_admit: {…}}）；改切分的从更早的步起
python scripts/eval_rough_bench.py ../open-guji-dataset/rough-bench -w $WS --var B.yaml [--from row_segment]
```
新的人裁要进基准就重建一版（`python scripts/rough_bench.py build --snapshot <各册 main 包取回的根>`），旧版的数照旧可比。

## 已知限制
- 标签多是挑过的（审查队列、差异核对），随机样本只有出口抽查那一小批，全册错率估不准；这里主要当回归门用（新增错放必须为 0）。
- 只管正文页；页型取快照 `border_detect_gate` 的 `page_type`，职名、目录分不出来，一律算正文。
- 改切分后格号会变：从切分步起跑的变体，同格号的框和快照里的框 IoU < 0.8 的标签不拿来考它（记在 `label_drift`），所以切分改动大的页上可判的标签会变少。
