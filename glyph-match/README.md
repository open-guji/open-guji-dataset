# glyph-match —— 字形匹配基准

被测对象：`open-guji-cv` 的匹配栈（normalize_patch → 特征 →
verify_pair_cov 排序）。与 `char-clustering`（聚类 purity）互补：
这里量的是**单对排序**——同字形必须比形近异字更匹配。

| 分片 | 单元 | 数量 | 说明 |
|---|---|---|---|
| [triplets](triplets/) | 三元组 | 98（hard 38 / control 60）| 体检人裁产出的排序金标 |
