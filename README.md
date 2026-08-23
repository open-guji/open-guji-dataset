# open-guji-dataset

古籍计算机视觉 Benchmark 数据集，用于评估 [open-guji-cv](https://github.com/open-guji/open-guji-cv) 各阶段命令的识别准确率。

> **要新建一个测试集？先看 [doc/making-datasets.md](doc/making-datasets.md)**
> ——测什么（能力还是输出）、金标怎么定义、样本怎么抽、报告怎么写，
> 以及**哪些步骤可以并行开工**。给已有数据集补样本看
> [doc/adding-samples.md](doc/adding-samples.md)。
>
> **当前策略（2026-08 起）：只优化正文页。** 新建数据集要么只收正文页，
> 要么标出页型分层报。正文页金标见 [page-type](page-type)
> （`page_type == "body"`，vol01 296 页 / vol02 全书 186 页）。

## 数据集

| 数据集 | 评估命令 | 样本数 | 状态 | 说明 |
|--------|---------|--------|------|------|
| [book-profile](doc/book-profile.md) | `recognize-profile` | 24 | 可用 | 古籍版面特征识别（布局、行数、颜色、边框等） |
| [cut-page](doc/cut-page.md) | `cut` | 18 | 可用 | 页面切分类型检测（垂直/水平/无需切分） |
| [page-type](page-type) | `segment`（页型闸门）| 394 页（全书） | 可用 | 八种页型 → 三种网格策略，防止非正文页产出垃圾 |
| [page-geometry](page-geometry) | `segment`（版面几何）| 39 页 / 353 界行 | 可用 | 页面形变标定：错切/射影、列距列相位 |
| [column-layout](column-layout) | `segment`（行列识别）| 36 页 / 322 列 | 可用 | 逐列刚性/弹性判别 + 统一输出格式 |
| [char-segmentation/cells](char-segmentation/cells) | `segment`（格内净化）| 60 | 可用 | 合成逐像素金标：格内墨迹归属 |
| [char-segmentation/instances](char-segmentation/instances) | `chars`（图块自检）| 65 | 可用 | 真实图块四分类，评管线自检能力 |
| [char-normalization](doc/char-normalization.md) | `normalize`（纯函数） | 0 | 框架 | 归一化 golden 集（去残余 / 骨架化，逐像素回归） |
| [char-clustering](doc/char-clustering.md) | `cluster` | 0 | 框架 | 保守聚类 purity 集（含人工反馈难例对） |
| [char-ocr](doc/char-ocr.md) | `label` / `bench-ocr` | 0 | 框架 | 单字识别 (图块, 金标字)，按册划分 train/test |
| [context-correction](doc/context-correction.md) | `refine` | 0 | 框架 | 上下文 + LM 纠正（候选冻结） |
| [collation](doc/collation.md) | `collate`（规划中） | 0 | 框架 | 参考校对：对齐、参考质量 ρ 估计、分歧挖掘 |

其余「框架」状态的数据集是刻本字符识别管线（open-guji-cv Phase 3~6）的模块化拆分，
规格见 [doc/modules-roadmap.md](doc/modules-roadmap.md)。目前只建了目录
框架（metadata.json + doc + 占位样本），尚无真实样本；上表标「可用」的已有真实样本与基线。标注主要来源为
整理本对齐自动标注，因此每份 `expected.json` **必须**带三个溯源字段
`source_item` / `pipeline_version` / `label_origin`（`align` | `human` |
`synth`）——align 标注有噪声，清洗与分层评测都依赖它。

## 目录结构

```
open-guji-dataset/
├── book-profile/              # 版面识别数据集
│   ├── metadata.json
│   ├── samples/001-024/       # 每个含 image.png + expected.json + info.json
│   └── results/               # recognize-profile 输出 (gitignore)
├── cut-page/                  # 页面切分数据集
│   ├── samples/001-018/
│   └── results/
├── char-segmentation/         # 单字分拆（框架）
│   ├── metadata.json
│   ├── samples/000-example/   # 占位样本（placeholder: true）
│   └── results/               # 评测输出 (gitignore)
├── char-normalization/        # 归一化 golden 集（框架）
├── char-clustering/           # 保守聚类（框架）
├── char-ocr/                  # 单字识别（框架）
├── context-correction/        # 上下文纠正（框架）
├── collation/                 # 参考校对（框架）
├── doc/                       # 数据格式文档
│   ├── book-profile.md
│   ├── cut-page.md
│   ├── modules-roadmap.md
│   ├── char-segmentation.md
│   ├── char-normalization.md
│   ├── char-clustering.md
│   ├── char-ocr.md
│   ├── context-correction.md
│   └── collation.md
├── scripts/                   # benchmark 脚本
├── index.html                 # 标注 Web UI
└── server.py                  # 标注服务器（已废弃，改用 File System Access API）
```

新数据集统一布局：`metadata.json` + `samples/NNN/`（`expected.json` +
`info.json` + 各自的输入文件）+ `results/`。`results/` 只保留 `.gitkeep`
与 `.gitignore`，评测输出不入库（沿用 book-profile / cut-page 约定）。

## 标注 Web UI

直接用浏览器打开 `index.html`，选择本项目根目录即可浏览和编辑所有数据集的标注。

功能：
- 左侧样本列表，绿色勾/红色叉显示与识别结果的匹配状态
- 右侧图片预览 + 标注表单，修改后自动保存
- 顶部标签页切换不同数据集
- 上下方向键快速切换样本
- 目录句柄缓存在 IndexedDB，下次打开自动恢复

## Benchmark 脚本

```bash
# 版面识别 benchmark
python scripts/run_benchmark.py      # 对所有样本运行 recognize-profile
python scripts/evaluate.py           # 评估准确率

# 页面切分 benchmark
python scripts/run_cut_benchmark.py  # 对所有样本运行 cut 检测
```

## 数据来源

1. **open-guji-cv/data** — 内置测试数据（book1-book8）
2. **AncientDoc** — 古籍图片分类数据集（15 个分类）
3. **PDF 提取** — 续修四库全书总目提要、四库全书总目等

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
