# open-guji-dataset

古籍计算机视觉 benchmark 数据集：给 [open-guji-cv](https://github.com/open-guji/open-guji-cv) 管线的**四大步、各小步**当固定尺子，改了某一步不用整册重跑就能知道变好还是变坏。

- **按大步、小步找测试集** → [STEP_MAP.md](STEP_MAP.md)（每个分片挂在哪个小步、多少条、覆盖哪几部书、缺口在哪）。
- **每个小步跑哪个 benchmark、主指标、护栏、基线报告** → cv [`doc/bench登记表.md`](https://github.com/open-guji/open-guji-cv/blob/dev/doc/bench登记表.md)。
- **验收标准**（小步 S1–S12、大步 B1–B6；本仓对应 S12：分片、信封、按书覆盖）→ cv [`doc/验收标准.md`](https://github.com/open-guji/open-guji-cv/blob/dev/doc/验收标准.md)。
- 要新建测试集，先看 [doc/making-datasets.md](doc/making-datasets.md)；给已有分片补样本看 [doc/adding-samples.md](doc/adding-samples.md)。

本仓目录按功能模块命名（`border-detection/`、`char-segmentation/`、`glyph-match/`…），不按步骤命名：一个分片可能同时量两个小步，小步重新划分时也不用搬目录。对应关系只在 [STEP_MAP.md](STEP_MAP.md) 一处维护。

## 四大步一览

cv 管线分四大步（2026-11-22 起；小步 11-25 至 11-28 拆成独立 Step）。下表每个小步只列主集，全部分片见 [STEP_MAP.md](STEP_MAP.md)。

| 大步 | 小步（Step id） | 主集 | 覆盖的书 |
|---|---|---|---|
| **1 版面** `layout` | 1a 页面预检（`page_survey`、`invert_detect`） | 无 | — |
| | 1b 版框界行（`border_detect`）＋页型闸 | [layout](layout)、[border-detection](border-detection)、[page-type](page-type) | 殿本为主；史記、全唐文、脉经各 10 页上下 |
| | 1c 印章（`seal_detect`） | 无 | — |
| **2 切字** `cut` | 2a 拉直（`column_warp`） | [page-geometry](page-geometry) | 殿本 |
| | 2b 字带左右边（`column_band`） | [char-segmentation/side-rule](char-segmentation/side-rule) | 殿本 |
| | 2c 列端字（`column_end`） | [char-segmentation/cut-frame](char-segmentation/cut-frame)、[frame-end-crop](char-segmentation/frame-end-crop) | 史記、全唐文；殿本 |
| | 2d 字间切分（`row_segment`） | [cut-lattice](cut-lattice)、[char-segmentation/column-counts](char-segmentation/column-counts) | 殿本、史記、全唐文、脉经 |
| | 2e 字框压缩（`cell_shrink`） | [char-segmentation/instances](char-segmentation/instances) | 殿本、北行 |
| **3 识字** `read` | 3a 字形库匹配（`glyph_match`） | [glyph-match](glyph-match) advset／damaged／pairs | 殿本、史記、全唐文 |
| | 3b 形近字组（`glyph_near`） | [char-groups](char-groups)、[glyph-near/bench3b](glyph-near/bench3b)（整体：触发／覆盖／一致率／ECE／耗时） | 殿本；bench3b 殿本、史記、全唐文 |
| | 3c 按图候选（`glyph_candidate`） | [char-candidates](char-candidates) | 殿本、全唐文、史記 |
| | 3d 其他特征、3e 看图大模型、识字收尾 `glyph_analyzer` | 无 | — |
| **4 定字** `decide` | 4a 参照对位（`align_ref`） | [decide-bench](decide-bench) 子步指标 | 见收尾 |
| | 4b 上下文（`context_decide`、`context_rank`） | [context-correction](context-correction)、[confusable-context](confusable-context) | 殿本 |
| | 4c 格况（`cell_state`） | [decide-bench/cell-state](decide-bench/cell-state)（起步） | 史記 03、全唐文 004、殿本 |
| | 4d 字组（`group_decision`） | [char-groups](char-groups) | 殿本 |
| | 定字收尾（`char_decide`）、gate（`decide_gate`） | [decide-bench](decide-bench) small／large、[rough-bench](rough-bench) | 殿本、史記、全唐文、脉经 |

## 怎么跑

各小步的 benchmark 命令以 cv [`doc/bench登记表.md`](https://github.com/open-guji/open-guji-cv/blob/dev/doc/bench登记表.md) 为准，常用的几条：

```bash
python -m open_guji_cv.eval.layout_bench          # 1 版面（cv 仓），读 layout/
guji eval list                                     # guji-manager 评测器登记的 bench（3a advset、match_pool、rare_* 等）
guji eval run <bench id>
```

切字的 `cut_bench.py` 现在还在 ai-team 仓；定字的 decide-bench `run`／`score`／`dyn`／`gate_bench` 已搬进 cv `open_guji_cv/eval/decide_bench/`（2026-11-28）。切字的搬进跟版本走的仓之前以登记表写的住处为准。

旧的 `python -m open_guji_cv console` 控制台和 `python -m open_guji_cv gold|eval|batch|events` 已退役（控制台拆成独立包 guji-console，人裁与金标收割走 guji-manager），不要再用；本仓根下的 `index.html`、`server.py`、`scripts/run_benchmark.py` 等是更早的标注与评测工具，只对 book-profile、cut-page 两个旧分片有效。

> 当前策略（2026-08 起）：只优化正文页。新建分片要么只收正文页，要么按页型分层报；正文页判定见 [page-type](page-type)。

## 统一金标信封（items.jsonl）

每个分片一份 `items.jsonl`，一行一条金标。**把既有纪律变成字段**，不再靠人记：

```json
{"id": "cols:vol02:171",
 "anchor": {"book": "vol02", "page": 171, "space": "raw_page_px@top-right",
            "bbox": [x0,y0,x1,y1], "content_sha": "…"},
 "input": {"legacy_source": "verdicts_r1.jsonl", "coord_space": "…口径说明…"},
 "expected": {"verdict": "ok"},
 "label_origin": "human",
 "stratum": "抽样·随机", "stratum_weight": 1.0,
 "status": "active",
 "source_events": ["evt_border-cols-r1_000001"],
 "history": [{"ts": "…", "change": "…", "why": "…"}]}
```

| 字段 | 为什么必须有 |
|---|---|
| `label_origin` | `align` 标注有噪声，清洗、分层、加权全靠它区分。不可省 |
| `stratum` + `stratum_weight` | 按可疑度挑的批次估不出总体比例，权重必须随条目走 |
| `status` | `uncertain` 评测跳过（人工也判不准）；`stale` 是上游重生后待重键的 |
| `history` | 每次改判记 why，对齐 `relabel_history` 的要求 |
| `source_events` | 这条金标由哪些人裁事件产生，可回溯 |
| `anchor` | `bbox` + `content_sha` 不随产物重生失效；`product_key` 允许失效 |

**`expected` 里只放金标内容**。`coord_space` 那种整段口径说明是给人看的文档，
放进 `input`——混进 `expected` 会让「金标改没改」的比较变成比较散文。


## 分片约定

- 一个分片一个目录：`items.jsonl`（统一金标）＋`README.md`（测什么、金标口径、来源、基线）＋可选 `metadata.json`、`samples/`、`report.json`。`results/` 只留 `.gitkeep`，评测输出不入库。
- README 第一段写清**量的是哪个小步**（用现行编号，如「2c 列端字」），以及覆盖了哪几部书、缺哪部。小步改划分时只改 [STEP_MAP.md](STEP_MAP.md)，不搬目录。
- 多书的分片按书分子目录（如 `char-segmentation/book-columns/maijing/`、`rare-char/qtw-995ejelvk0/`）或在 `anchor` 里写 `book_id`，分书报分。
- 随机页与难例分开放（`stratum` 字段或分开的子目录），否则估不出总体比例。
- 金标锚在不随切分变的键上：原图页面坐标（注明图源 rev）、`bbox`＋`content_sha`、字块指纹或字格永久编号 u；不要只锚在格号上（重切后会挂到邻格）。


## 旧分片的老载体

早期分片（book-profile、cut-page 等）还有 `samples/NNN/` 老载体，2026-09-03 已全部迁成 `items.jsonl`，老载体原样保留；新代码一律读 `items.jsonl`。

## 每个样本的结构

```
samples/001/
├── image.png          # 原始图片
├── expected.json      # Ground truth（人工标注的预期结果）
└── info.json          # 来源、描述、标签
```

新数据集的输入文件因模块而异（页图 + 列带、原始/golden 图对、字块目录、
或纯 JSON 的冻结候选），详见各数据集文档。

### info.json 格式

```json
{
  "id": "001",
  "source": "open-guji-cv/data/book1",
  "source_file": "4.png",
  "description": "四库全书简明目录，标准黑白半页扫描",
  "tags": ["cut_half", "regular", "bw"]
}
```

### expected.json 格式

与对应命令的输出 JSON 格式一致，详见各数据集文档。

六个新数据集额外要求顶层三个溯源字段：

```json
{
  "source_item": "06061301.cn",
  "pipeline_version": "…",
  "label_origin": "align"
}
```

| 字段 | 说明 |
|------|------|
| `source_item` | 来源册标识，支撑按册划分 train/test（跨册泛化是真实需求） |
| `pipeline_version` | 生成样本时 open-guji-cv 的版本 / commit，支撑管线升级后判断哪些样本要重生成 |
| `label_origin` | `align`（整理本对齐自动标注）/ `human`（人工）/ `synth`（合成） |

`label_origin` 不可省略：align 是唯一能规模化的标注来源，但它有噪声
（对齐错位、用字差异、参考本讹误），清洗、分层评测、加权使用三件事
全靠它区分。

