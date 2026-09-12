# 测试集 ↔ 管线 Step 映射

> 本仓的目录按**功能模块**命名（`border-detection/`、`char-segmentation/` 等），
> 不按 `open-guji-cv` 管线的 `Step0`～`Step8` 命名。两者的对应关系此前只写在
> `overview` 仓的 [模块测试与现状.md](https://github.com/open-guji/overview/blob/main/项目进展/图片初步数字化/模块测试与现状.md) 里，
> 是人工维护的一层翻译，本仓自己没有落地。本文件把那份映射搬一份到这里，
> 与实际测试数据同仓存放，换人接手时不必先跳到另一个仓才能查到「这一步测试集在哪」。
>
> 行数是 2026-09-11 `wc -l */items.jsonl` 现场实测，随分片持续增量标注会再涨，
> **引用前请自己重新数一遍**，不要直接抄这张表当最新值——它只保证映射关系不错。

| Step | 分片路径 | 行数 |
|---|---|---|
| Step0 预清理 | 无独立金标（人工确认页级候选） | — |
| Step1 边框界行 | [border-detection/samples](border-detection/samples) | 14 |
| | [border-detection/column-split](border-detection/column-split) | 60 |
| | [border-detection/head-raise-presence](border-detection/head-raise-presence) | 60 |
| | [border-detection/outer-edge](border-detection/outer-edge) | 108 |
| | [border-detection/vline-polyline](border-detection/vline-polyline) | 3 |
| | [char-segmentation/side-rule](char-segmentation/side-rule)（界行/版框路由，Step1/2 共用） | 276 |
| Step2 单列射影 | [char-segmentation/column-warp](char-segmentation/column-warp) | 115 |
| | [char-segmentation/column-warp/legacy-page-anchor](char-segmentation/column-warp/legacy-page-anchor) | 25 |
| | [char-segmentation/frame-strip](char-segmentation/frame-strip) | 65 |
| | [char-segmentation/page-crop](char-segmentation/page-crop) | 6 |
| | [char-segmentation/text-band](char-segmentation/text-band) | 2（自动量，非人裁） |
| | [char-segmentation/column-level](char-segmentation/column-level) | 117 |
| Step3 逐字切分 | [char-segmentation/touching-cuts](char-segmentation/touching-cuts)（主集，vol01/vol02/**vol03**） | 895 |
| | [char-segmentation/cells](char-segmentation/cells)（合成逐像素金标） | 60 |
| | [char-segmentation/cell-kind](char-segmentation/cell-kind) | 5 |
| | [char-segmentation/seam](char-segmentation/seam) | 27 |
| | [char-segmentation/char-drop](char-segmentation/char-drop) | 16 |
| | [char-segmentation/row-boundaries](char-segmentation/row-boundaries)（已退役，旧坐标系） | 2 |
| | [char-segmentation/cell-truncation](char-segmentation/cell-truncation)（已退役，旧坐标系） | 23 |
| Step3 附·夹注切分 | [char-segmentation/jiazhu-tail](char-segmentation/jiazhu-tail) | 57 |
| Step4 字框收缩 | [char-segmentation/instances](char-segmentation/instances) | 829 |
| | [char-segmentation/left-cut](char-segmentation/left-cut) | 57 |
| | [char-segmentation/right-cut](char-segmentation/right-cut) | 52 |
| | [char-segmentation/crop-margin](char-segmentation/crop-margin) | 394 |
| Step5-a 字形库匹配 | [glyph-match/pairs](glyph-match/pairs) | 5,915 |
| | [glyph-match/triplets](glyph-match/triplets) | 193 |
| | [char-clustering](char-clustering) | 3（分片数，非实例数；实例数另计） |
| Step5-b 生僻字候选 | `glyph-bench`（**不在本仓**，是 open-guji-cv 仓本地缓存 `cache/glyph_bench/items.jsonl`，`.gitignore` 排除；重建脚本 `scripts/build_glyph_bench.py`） | 15,482（cv 仓内实测） |
| | [rare-char](rare-char) | 21 |
| Step5-c Paddle OCR | [char-ocr](char-ocr) | 9,571 |
| Step5-d 整理本匹配 | [char-segmentation/align-anchor](char-segmentation/align-anchor)（锚定判据回归集，2026-09-11 新建） | 11 |
| | [char-segmentation/align-gate](char-segmentation/align-gate)（采信闸回归集，2026-09-11 新建） | 4 |
| | 对齐金标本身仍是自动生成，无独立分片；人裁两本对比未落 dataset 仓分片 | — |
| Step6 上下文裁决 | [context-correction](context-correction) | 12（顶层信封）/ 嵌套槽位 ≈1,682 |
| | [confusable-context](confusable-context) | 154 |
| Step7 放行判定 | 复用人裁历史回放（`open-guji-cv` 仓 `feedback/events/`），未落 dataset 仓独立分片 | — |
| Step8 落库与反馈 | [char-normalization](char-normalization) | 32 |
| Step9 结果整理 · 坐标转字符位 | [guji-markdown-render](guji-markdown-render)（2026-09-11 新建） | 4 |
| 页型/版面通用 | [page-type](page-type) | 394 |
| | [page-geometry](page-geometry) | 39 |
| | [column-layout](column-layout) | 36 |
| | [book-profile](book-profile) | 24 |
| 其他/规划中 | [cut-page](doc/cut-page.md)、[collation](collation) | 见各自 README |

## 已知空白

- **Step0（预清理）、Step7（放行判定）没有独立落在本仓的测试集分片**，
  判据是自动生成或人工confirm，Step7 复用的是 `open-guji-cv` 仓自己的事件回放，
  两者目前都不受本仓「统一金标信封 items.jsonl」这套机制约束。是否需要补齐，见
  overview 仓 [01-各步骤测试集合金标汇总审阅.md](https://github.com/open-guji/overview/blob/main/项目进展/图片初步数字化/进度/总览/01-各步骤测试集合金标汇总审阅.md)。
  Step5-d 2026-09-11 起有了一份锚定判据回归集（`align-anchor`，见上表），但对齐
  金标本身仍是自动生成、不受此机制约束，所以 Step5-d 只能算"部分补齐"。
- 本表只做**路径映射**，不做**统计聚合**（每册每页输入输出量、多候选占比、performance）——
  这三类数字目前没有一键命令产出，仍需临时手写脚本，见上面链接的审阅文档第 3 条结论。
