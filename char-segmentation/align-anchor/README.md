# char-segmentation / align-anchor —— Step5-d 整理本锚定回归集

## 这个分片在测什么

Step5-d（`open-guji-cv` `clustering/align_eval.py::anchor_page`）要做的事：
一页的识别候选串（库/OCR 证据拼出来的文本，**含错字**）+ 整理本语料 →
8-gram 投票找出这页在语料里的起始偏移（锚定），给后续 `difflib` 逐字
对齐用。锚不上，这一页就拿不到整理本这一路证据（四路里"文本"那一路）。

这个分片测的不是"对齐准不准"（那是 `align_label.py` 的采信闸与
`seed_admit` 下游的事），只测**锚定这一步的判据本身**：给定查询串和
语料窗口，`anchor_page`/`anchor_page_diag` 该不该判定锚定成功、偏移对
不对。

## 2026-09-11 首次建档：POOL_RADIUS 3→8 修复的回归套

用户观察到 vol03 第33、35页"有几列没匹配上"，查实是**整页**锚定失败
（`PageAlignRef.anchored=False`）。深挖后发现：最初判断"语料里存在格式
化套话撞出的假峰"是误判——完整展开票数分布后看到，所谓"次高簇"与
"peak"其实是**同一个真实锚点**，只是页内**多处**漏字/多字让真锚点附近
的偏移票数漂移了 9~12 位（如 vol03 p33：59519~59528 这段区间），而
`POOL_RADIUS=3`（合并相邻偏移的半径）不够大，把同一个锚点的票硬生生
切成两三堆、互相当对手，各堆的占比/优势判据都凑不够，整页被误判锚定
失败。改成 `POOL_RADIUS=8` 后，vol01+vol02+vol03 全量337页回归**零退化**
（没有页从成功变失败，已成功页 equal 占比不降），另回收4页失败。

这个分片把那次验证用到的案例固化下来，防止以后再动 `POOL_RADIUS`（或
任何影响合并逻辑的改动）时，不知不觉把这几个"奇形怪状"的整理本匹配
案例又改坏。

| 类别 | 页 | 说明 |
|---|---|---|
| **踩坑案例**（需 POOL_RADIUS≥8 才能锚定） | vol01/5、vol01/63、vol01/77、vol03/7、vol03/17、vol03/33、vol03/35 | 真锚点漂移跨度大（9~12位），`POOL_RADIUS=3` 会把票切散导致误判失败 |
| **正常对照页**（`POOL_RADIUS=3` 本就能过） | vol03/31、vol03/34、vol03/36 | 漂移小，防止改大半径之外的改动（比如改判据本身）把这类简单页改坏 |
| **真实失败反例**（任何半径都不该锚定） | vol01/184 | 目录页（"卷一百八 子部十八 術數類一"这类分类条目列表），语料确实没收录这种内容，修复不能让它"来者不拒" |

## 数据结构

`query_text`：`steps/align_ref.py::slots_from_evidence` 拼出的识别候选串
（库 kNN / OCR top1 取信度较高者），原样摘自对应页的真实 `glyph_match`/
`ocr_candidates` 产物，**含识别错字**（如 vol03 p33 里"千頃堂"被识别成
"千項堂"、"兩江總督"识别成"雨江總督"）——这些错字正是导致漂移的原因，
不能清洗掉。

`corpus_window`：`corpus/zongmu_wenyuange_wikisource.txt` 的一段片段
（不是整部265万字语料），覆盖真锚点前后各约40~140字，足够容纳漂移范围
与可能的竞争候选，不需要也不应该把完整语料塞进这个分片。

`window_offset_in_corpus`：这段窗口在完整语料里的起始位置，仅供溯源，
测试本身不需要用到（测试只在窗口内部坐标系里验证）。

`expected.anchored` / `expected.offset_in_window`：锚定应该成功/失败，
成功时偏移应落在窗口内的哪个位置。`offset_in_window` 为 `null` 表示
不应锚定成功（反例）。

## 怎么跑

`open-guji-cv` 仓 `tests/clustering/test_align_anchor_bench.py` 读本分片
`items.jsonl`，对每条记录用 `corpus_window` 现建一个临时 n-gram 索引，
跑 `anchor_page_diag(query_text, index)`，断言 `anchored`/`offset` 与
`expected` 一致。纯文本输入，不依赖 `GUJI_WORKSPACE`/真图/模型，跑在
常规 `pytest` 回归里。

## 维护口径

- 这是回归集，不是随机抽样的准确率基准——新增案例只在"踩过坑、且坑
  与锚定判据本身相关"时才加，不要把一般的对齐失败页也塞进来（那类
  去 `char-segmentation/touching-cuts` 等分片，或者走 `collation` 人裁）。
- `label_origin: "derived"`——不是人工标注，是从已验证的产物/算法行为
  派生而来（见各条 `history.why`）。
