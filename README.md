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
| [char-segmentation/instances](char-segmentation/instances) | `chars`（图块自检）| 426 | 可用 | 真实图块四分类 + `defect` 子类（rule_bar/frame_bar），评管线自检能力。含历次实审回流（r1~r6）与隔壁进库审查的 149 条 |
| [char-segmentation/frame-strip](char-segmentation/frame-strip) | `chars`（列端去框）| 65 | 可用 | 列端格「去框后」干净度：残余率/误剥率/字保全 |
| [char-segmentation/side-rule](char-segmentation/side-rule) | `chars`（侧边去线）| 265 | 可用 | 图块左右缘的界行竖条剥没剥掉，字的边竖有没有被误剥 |
| [char-segmentation/page-crop](char-segmentation/page-crop) | `segment`（上游裁切）| 6 页 | 可用 | 列窗越出页图多少＝最外列被 s3 吃掉多少（全自动，无需标注）|
| [char-segmentation/text-band](char-segmentation/text-band) | `segment`（版面窗口）| 294 页 | 可用 | 窗口高 /（每列字数 × 书级格高）＝列的纵向窗口够不够装下一整列（全自动，无需标注）|
| [char-segmentation/jiazhu-tail](char-segmentation/jiazhu-tail) | `chars`（夹注段端）| 57 | 可用 | 奇数字末行单字收编成 a 行 / 漏拆末行补拆，正文拒收（三分类，非对称零容忍）|
| [char-segmentation/right-cut](char-segmentation/right-cut) | `chars`（右缘救援）| 51 列 213 点 | 可用 | 贴界行书写的字，捺脚/横尾穿过右裁切边必须被图块盖住 |
| [char-segmentation/seam](char-segmentation/seam) | `segment`（格线落点）| 294 页 | 可用 | 切缝墨率＝格线那一行的墨 / 上下两格字峰，量「这一刀是不是切在字上」（全自动，无需标注）|
| [char-normalization](char-normalization) | `normalize`（纯函数） | 35 字块 | 可用 | 归一化 golden 回归门（32 verified + 3 已知缺陷）|
| [char-clustering](char-clustering) | `cluster` | 3 分片 / 6297 实例 | 可用 | 保守聚类 purity 集（align 两册 + 人工复核层 + 难例对）|
| [glyph-match](glyph-match) | `match`/`verify` | 98 三元组 | 可用 | 匹配排序：同字形须胜形近异字（体检人裁产出；hard 基线 0.079，control 护栏 1.0）|
| [char-ocr](doc/char-ocr.md) | `label` / `bench-ocr` | 0 | 框架 | 单字识别 (图块, 金标字)，按册划分 train/test |
| [context-correction](doc/context-correction.md) | `refine` / seed context 通道 | 11 页 / 1681 槽位 | 可用 | 上下文 + LM 纠正（候选冻结；vol01 进库协议金标，human 529 分层）。首轮基线：门槛化混合 LM +2.32%（救41/坏2）；无门槛重排任何 λ 净亏 |
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
├── char-normalization/        # 归一化 golden 回归门（35 字块，两层）
├── char-clustering/           # 保守聚类 purity（3 个册分片）
├── glyph-match/               # 匹配排序三元组（体检人裁产出）
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
