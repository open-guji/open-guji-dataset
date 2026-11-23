# glyph-match —— 字形匹配基准

被测对象：`open-guji-cv` 的匹配栈（normalize_patch → 特征 →
verify_pair_cov 排序）。与 `char-clustering`（聚类 purity）互补：
这里量的是**单对排序**——同字形必须比形近异字更匹配。

| 分片 | 单元 | 数量 | 说明 |
|---|---|---|---|
| [triplets](triplets/) | 三元组 | 98（hard 38 / control 60）| 体检人裁产出的排序金标 |
| [pairs-siku-v2](pairs-siku-v2/) | 图块对 | 27,370 | 殿本人裁金标（char-clustering 004）派生的阈值标定集，2026-11-05 冻结 |
| [pairs-shiji](pairs-shiji/) | 图块对 | 23,884 | 史記人裁金标（005）派生 |
| [pairs-qtw](pairs-qtw/) | 图块对 | 26,587 | 全唐文人裁金标（006）派生 |
| [advset-siku-v2](advset-siku-v2/)、[advset-shiji](advset-shiji/)、[advset-qtw](advset-qtw/) | 题（留出字刻例＋候选） | 1,550／919／1,704 题 | 3a 子基准 A2「库外拒识」：库里没有的字 vs 形近对家与生产粗排候选，量匹配层误认（cv `scripts/eval_advset.py`；2026-11-23 冻结，见下节） |
| [bench](bench/) | 分档标注＋基线 | 3 书 | 新图×字形库 比对基准（查询用 char-clustering 三书人裁分片，2026-11-06） |


## advset-*：库外形近字对抗集（A23，2026-11-23 冻结）

来源：ai-team `domain/CV/字形领域/5a相似度CNN深化-2026-11-15/advset/`（11-15 建，做法见该目录 `code/advset_build.py` 模块头）。
原集只存刻例 id，图块在当时的 glyph.db 里；这里用 `scripts/build_glyph_advset.py` 按 11-22 中心库 main 的库取 `derived.norm`
（64×64 归一图）落进 `crops/`，**打分只看分片、不碰字形库**。

- `items.jsonl`：一行一题 `{query_id, held, query_provenance, candidates: [{id, char, partner, variant}]}`。
  `held` 是留出字（当库外字），`partner` 标形近对家（否则是生产粗排 HOG 前 15），`variant` 标同形异码／异体（逐码位判，单列一层）。
- `info.json`：来源库 sha、和原集的差别（已撤库刻例去掉、库订正过标签的题丢掉、候选现标签等于留出字的去掉）。
- 判官用生产的：殿本、史記覆盖分 `verify_pair_elastic`；全唐文 `sim_model: glyph_sim_qtw` + `fuse: mean`。
- **已知偏乐观**：现役 CNN 用全库训，留出字的刻例在训练集里；训练隔离的版本另做（识字 benchmark 第 2 期 c）。

基线（cv 21be710）：

| 分片 | 判官 | 形近误认（题） | 其中对家 | 异体下 same |
|---|---|---|---|---|
| advset-siku-v2 | 覆盖分 | 34／1,549 | 23 | 11／392 |
| advset-shiji | 覆盖分 | 7／919（与 11-15 原集一致） | 7 | 1／293 |
| advset-qtw | CNN+fuse | 0／1,691 | 0 | 0／189 |
