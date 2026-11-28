# 测试集 ↔ 四大步小步映射

> 本仓目录按**功能模块**命名（`border-detection/`、`char-segmentation/` 等），不按管线步骤命名。
> 本文件把每个分片挂到 open-guji-cv 现行的**四大步、小步**上（2026-11-28 按 cv dev 859b25e 的
> `pipelines/_skeleton.yaml` 重排；原来按 Step0–9 写的旧表见文末对照）。
>
> - 小步的划分、每步做什么：cv `doc/1-版面/` … `doc/4-定字/` 各大步 README。
> - 每个小步跑哪个 benchmark、主指标、护栏、基线报告：cv [`doc/bench登记表.md`](https://github.com/open-guji/open-guji-cv/blob/dev/doc/bench登记表.md)（各线自己填）。本文件只管「金标分片在哪」。
> - 「条数」是 2026-11-28 `wc -l */items.jsonl` 实数，分片还在涨，**引用前自己重数**。
> - 一个分片量到两个小步的，在两处都列，写明以哪一处为主。

书名缩写（金标里 `anchor.book` 的写法各分片不统一，下表统一成书名）：

| 写法 | 书 | book id |
|---|---|---|
| `vol01`…`vol99`、`siku-zongmu`、`dianben` | 殿本《四庫全書總目》 | `96mid1ogzk` |
| `sj05`、`shiji`、`988g3f0wsu:01` | 史記（文淵閣本） | `988g3f0wsu` |
| `qtw005`、`qtw`、`995ejelvk0:005` | 全唐文 | `995ejelvk0` |
| `mj01`、`maijing`、`99k3i35yww:01` | 脉经 | `99k3i35yww` |
| `bxgb` | 北行日錄（古本） | `988g7gsqhd` |

## 1 版面（layout）

| 小步 | Step id | 分片 | 条数 | 覆盖的书 | 说明 |
|---|---|---|---|---|---|
| 1a 页面预检 | `page_survey`、`invert_detect` | 无独立分片 | — | — | 异常页、反色带只送审，人点头即算数；页型判别见 1b 闸 |
| 1b 版框界行 | `border_detect`（现代 `line_detect`、自由版式 `block_detect`） | [layout](layout) **主集** | 79 页 | 殿本 47、史記 11、全唐文 10、脉经 11 | 第 1 大步几何金标（直线、边框、界行、页型、行列数），`python -m open_guji_cv.eval.layout_bench` 读它 |
| | | [border-detection/column-split](border-detection/column-split) | 60 | 殿本 | 界行是不是都落在字缝上 |
| | | [border-detection/head-raise-presence](border-detection/head-raise-presence) | 117 | 殿本 | 页顶有没有抬头 |
| | | [border-detection/outer-edge](border-detection/outer-edge) | 108 | 殿本 | 外框外延线位置 |
| | | [border-detection/bottom-offset](border-detection/bottom-offset) | 187 | 殿本 vol02、vol03 | 下版框偏移 |
| | | [border-detection/vline-polyline](border-detection/vline-polyline) | 3 页 | 殿本 | 界行三段折线逐段人裁 |
| | | [border-detection/samples](border-detection/samples) | 14 | 殿本 | 早期整页边框金标 |
| 1b 闸·页型 | `border_detect_gate` | [page-type](page-type) | 460 页 | 殿本（vol01、vol02 全册＋各册抽样） | 八种页型 → 套不套刻本网格 |
| 1c 印章 | `seal_detect` | 无 | — | — | 缺：印章框 IoU、漏认压字的金标（bench 登记表 L2） |

## 2 切字（cut）

| 小步 | Step id | 分片 | 条数 | 覆盖的书 | 说明 |
|---|---|---|---|---|---|
| 2a 拉直 | `column_warp`（现代 `column_crop`、自由版式 `column_trace`） | [page-geometry](page-geometry) | 39 页（30 有效） | 殿本 | 页面形变标定：错切、射影、列距列相位；评测读 `column_windows` |
| | | [char-segmentation/column-warp](char-segmentation/column-warp) | 146 | 殿本、北行 | 拉直后两侧残余界行、两端残墨清没清干净；现在量的是 2b、2c 的结果，以那两处为主 |
| 2b 字带左右边 | `column_band` | [char-segmentation/side-rule](char-segmentation/side-rule) | 276 | 殿本 | 左右缘竖线剥没剥掉、字的竖笔有没有误伤（2e 也剥，两处共用） |
| | | [char-segmentation/text-band](char-segmentation/text-band) | 2 | 殿本 | 列窗口够不够装下一整列（全自动量，无需标注） |
| 2c 列端字 | `column_end` | [char-segmentation/cut-frame](char-segmentation/cut-frame) **主集** | 258 列端 | 史記、全唐文 | 列首、列尾字的紧框不带框线、不切笔画（CV2，11-26 起） |
| | | [char-segmentation/frame-end-crop](char-segmentation/frame-end-crop) | 451 格 | 殿本（10 册） | 列端字块带框／切笔，按字块指纹锚定 |
| | | [char-segmentation/column-end-class](char-segmentation/column-end-class) | 305 | 殿本 vol02 | 每列上下端削框前的形态类别 |
| | | [char-segmentation/frame-strip](char-segmentation/frame-strip) | 65 | 殿本 | 列端格去框后的干净度 |
| 列几何、出口闸 | `column_geometry`、`cut_gate` | 无 | — | — | 缺：闸的检出率、误报率回归例 |
| 2d 字间切分 | `row_segment`（现代 `row_segment_runs`、自由版式 `cell_cut`） | [cut-lattice](cut-lattice) **主集** | 165 列 | 脉经 57、史記 44、全唐文 44、殿本 20 | 切分多备选：现役切错列＋好列对照；好列误换、错放必须为 0（4a 挑路也用） |
| | | [char-segmentation/book-columns](char-segmentation/book-columns) | 32 列 | 脉经 | 各书切分难列整列人定格表，按书分子目录 |
| | | [char-segmentation/column-counts](char-segmentation/column-counts) | 14,987 列 | 殿本 vol01–10 | 逐列字数（双源一致） |
| | | [char-segmentation/touching-cuts-rev5](char-segmentation/touching-cuts-rev5) | 603 | 殿本（现行图源 rev5） | 粘连格线的理想切点；**殿本用这份** |
| | | [char-segmentation/touching-cuts](char-segmentation/touching-cuts) | 1,803 | 殿本（旧图 CADAL）、北行 | 同上，殿本条目坐标在旧图上，北行仍可用 |
| | | [char-segmentation/column-level](char-segmentation/column-level) | 117 列 | 殿本 vol01 | 这一列分对了没有 |
| | | [char-segmentation/column-slots](char-segmentation/column-slots) | 2 | 北行 | 一列几个正文字格 |
| | | [char-segmentation/seam](char-segmentation/seam) | 27 | 殿本 | 切缝墨率：这一刀是不是切在字上 |
| | | [char-segmentation/char-drop](char-segmentation/char-drop) | 16 | 殿本 | 字有没有被整个丢掉 |
| | | [char-segmentation/truncation](char-segmentation/truncation) | 全自动 | 殿本 | 格线切进字身多深 |
| | | [char-segmentation/cell-kind](char-segmentation/cell-kind) | 5 | 殿本 | 每格的类型 |
| | | [char-segmentation/head-raise-columns](char-segmentation/head-raise-columns) | 3 | 殿本 | 列级抬头：抬几格、首字被切 |
| | | [char-segmentation/jiazhu-tail](char-segmentation/jiazhu-tail) | 60 | 殿本 | 双行小注段端收编 |
| | | [char-segmentation/jiazhu-short-note-miss](char-segmentation/jiazhu-short-note-miss) | 6 | 殿本 | 提要末尾短小注漏检（已知错例，待改） |
| | | [column-layout](column-layout) | 36 列 | 殿本 | 列型：刚性／弹性排布 |
| 2e 字框压缩 | `cell_shrink` | [char-segmentation/instances](char-segmentation/instances) **主集** | 1,264 | 殿本、北行 | 单字图块四分类＋缺陷子类 |
| | | [char-segmentation/right-cut](char-segmentation/right-cut) | 52 列 | 殿本 | 右缘穿边笔画要被图块盖住 |
| | | [char-segmentation/left-cut](char-segmentation/left-cut) | 57 列 | 殿本 | 左缘镜像 |
| | | [char-segmentation/cells](char-segmentation/cells) | 60 | 合成 | 格内墨迹归属，逐像素合成金标 |
| | | side-rule、frame-strip、frame-end-crop | — | — | 见 2b、2c |

## 3 识字（read）

| 小步 | Step id | 分片 | 条数 | 覆盖的书 | 说明 |
|---|---|---|---|---|---|
| 3a 字形库匹配 | `glyph_match` | [glyph-match](glyph-match) `advset-siku-v2`、`advset-shiji`、`advset-qtw` **主集** | 1,550／919／1,704 | 殿本、史記、全唐文 | 对抗集：库外字不许判 same |
| | | glyph-match `damaged-siku-v2`、`damaged-shiji` | 554／261 | 殿本、史記 | 残损字 |
| | | glyph-match `pairs`、`pairs-siku-v2`、`pairs-shiji`、`pairs-qtw` | 5,915 起 | 殿本、史記、全唐文 | same 阈值标定 |
| | | glyph-match `triplets` | 193 | 殿本 | 同字须胜形近异字（排序） |
| | | glyph-match `nearform-qtw` | 40,259 | 全唐文 | 形近对 |
| | | glyph-match `bench` | 分档＋基线 | 三书 | 新图×字形库比对基准，查询图用 char-clustering 冻结分片 |
| | | [char-clustering](char-clustering) | 3 分片 | 殿本、北行、三书人裁冻结 | 保守聚类 purity |
| | | [char-normalization](char-normalization) | 32 | 殿本 | 字块归一化回归门（3a 的前处理） |
| 3b 形近字组 | `glyph_near` | [char-groups](char-groups) **主集** | jys 695、ry 1,830、rr 2,442 格 | 殿本 | 己已巳、日曰、入人八，每组一个子目录；4d 也用 |
| 3c 按图候选 | `glyph_candidate` | [char-candidates](char-candidates) **主集** | 7,873 | 殿本 4,206、全唐文 2,162、史記 1,505 | 甲层前 1、前 50 命中；4b 也用 |
| （旧）生僻字候选 | `rare_candidates` | [rare-char](rare-char)、[rare-char/qtw-995ejelvk0](rare-char/qtw-995ejelvk0) | 21／69 | 殿本、全唐文 | 退役中，读口改读 3c |
| 3d 其他特征 | `cell_traits` | 无 | — | — | 缺金标 |
| 3e 看图大模型 | `glyph_vis` | 无 | — | — | 缺触发量、答对率的金标 |
| 识字收尾 | `glyph_analyzer` | 无 | — | — | 缺：未定格前 1／前 10、ECE |

## 4 定字（decide）

| 小步 | Step id | 分片 | 条数 | 覆盖的书 | 说明 |
|---|---|---|---|---|---|
| 4a 参照对位 | `align_ref` | [decide-bench](decide-bench) 子步指标 **主集** | 见收尾 | 见收尾 | 错位格数、好列被换坏 |
| | | [char-segmentation/align-anchor](char-segmentation/align-anchor) | 11 | 殿本 | 锚定判据回归 |
| | | [char-segmentation/align-gate](char-segmentation/align-gate) | 4 | 殿本 | 采信闸回归 |
| | | [ref-mismatch](ref-mismatch) | 87 | 殿本 | 人裁字 ≠ 整理本字 |
| 4b 上下文 | `context_decide`、`context_rank` | [context-correction](context-correction)（用 `samples_v2/`） | 12 页／约 1,680 槽位 | 殿本 | 上下文＋LM 纠正，候选冻结 |
| | | [confusable-context](confusable-context) | 154 | 殿本 | 形近对上下文消歧 |
| | | [char-candidates](char-candidates) | 7,873 | 见 3c | 按上下文排序并补字 |
| 4c 格况 | `cell_state` | 无（待建 `decide-bench/cell-state`） | — | — | 人裁 seg_defect 等约 2,200 格待绑框 |
| 4d 字组 | `group_decision` | [char-groups](char-groups) | 见 3b | 殿本 | 字组定向金标先从全唐文三组起步 |
| 定字收尾 | `char_decide`（旧名 `seed_admit`） | [decide-bench/small](decide-bench) **主集** | 9,422 格 | 全唐文 004、史記 03、殿本 vol01 | 只跑第四步、关人裁；错放字必须为 0 |
| | | [decide-bench/large](decide-bench) | 11,355 格 | 史記 01–02、全唐文 005、殿本 vol02、脉经 01 等 | 同上，大样本 |
| | | [rough-bench](rough-bench) | 972 格／196 页 | 殿本 | 粗校基准：送审率变化、新增错放必须为 0 |
| 定字 gate | `decide_gate` | 无（事故回归例在 ai-team） | — | — | 缺：搬进本仓的回归分片 |

## 不归 cv 四大步的分片

| 分片 | 归属 | 说明 |
|---|---|---|
| [guji-markdown-render](guji-markdown-render) | guji-manager 第五步 `output`（原 cv Step9） | 坐标转字符位回归 |
| [collation](collation) | 规划中 | 参考校对，只有框架 |
| [char-ocr](char-ocr) | 已不在管线里（原 Step5-c PaddleOCR） | 9,571 条单字识别 (图块, 字)，留作训练与对照 |
| [book-profile](book-profile)、[cut-page](doc/cut-page.md) | 旧工具 `recognize-profile`、`cut` | 早期版面特征与切页检测，现行管线不读 |
| [char-segmentation/page-crop](char-segmentation/page-crop)、[char-segmentation/crop-margin](char-segmentation/crop-margin) | 旧 s3 裁边 | 现行管线不再裁页，留档 |
| [char-segmentation/row-boundaries](char-segmentation/row-boundaries)、[char-segmentation/cell-truncation](char-segmentation/cell-truncation) | 已退役 | 旧链路坐标系，不能直接评现役算法 |
| [near-form-groups](near-form-groups) | 已并入 char-groups | 只留去向说明 |

## 缺口一览（对照 cv 验收标准 S12）

- **没有任何分片的小步**：1a、1c、列几何与 `cut_gate`、3d、3e、识字收尾、4c、定字 gate。
- **只有殿本的小步**：1b 闸·页型、2b、2e、3b、4b。验收标准要求「写明覆盖了哪几部书、缺哪部」，补别的书时在上表「覆盖的书」一列改掉。
- 金标锚定：殿本两次换图源后，`touching-cuts` 等按旧图列图坐标记的分片对不上现行图，现行图用 `-rev5` 等迁移过的版本；新分片一律锚在原图页面坐标或字块指纹上（见 [README](README.md)「统一金标信封」）。

## 旧 Step 号对照

旧文档、旧分片 README 里写的 Step 号按下表换算（2026-11-22 九步并成四大步；2a–2e、4c、4d 等小步 11-25 至 11-28 陆续拆成独立 Step）。

| 旧 | 现在 |
|---|---|
| Step0 预清理／页面预检 | 1a |
| Step1 边框界行 | 1b |
| Step2 单列射影 | 2a 拉直；两侧抹线归 2b，上下端剥框归 2c |
| Step3 逐字切分 | 2d |
| Step4 字框收缩 | 2e |
| Step5-a 字形库匹配 | 3a |
| Step5-b 生僻字候选 | `rare_candidates`（将并进 3c） |
| Step5-c PaddleOCR | 不在管线里 |
| Step5-d 整理本匹配 | 4a |
| Step6 上下文裁决 | 4b |
| Step7 放行判定（`seed_admit`） | 4c、4d、定字收尾 `char_decide` |
| Step8 落库与反馈、Step9 结果整理 | guji-manager 第二步、第五步 |
