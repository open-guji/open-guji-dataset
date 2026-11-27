# char-candidates：识字候选测试集

第三步「识字」的 3c（按图给候选）、第四步的 4b（按上下文排序并补字）和待审卡的候选按钮，都用这个集来量。
改了其中任何一步，跑一次评测就能知道有没有变好，**不用整册重跑**。
规格见 Claude Doc「候选字线：待审格格式、3c／4b 接口与 benchmark」第五、六节。负责人：CV3。

## 两层

| 层 | 是什么 | 字块图 |
|---|---|---|
| 甲 A 难格 | 三书人裁的生僻字格，取自 `char-clustering/samples/004–007/rare.jsonl` | 按路径引用那边的 64×64 归一图（`crop.kind=norm64`） |
| 乙 B 卡片回放 | 中心库里发过的待审卡，且发卡之后有人裁 | `crops/` 里卡上那张 96×96 单格图（`crop.kind=sprite96`，评测时照产线 `normalize_patch`） |

每格还冻结了：
- 前后文：本页按读序，接前后各一页，左右各 24 字，本格不放进去。
- 产线候选池：3a glyph_match 前 5、3b rare_candidates、4b context_decide 的 ranked。
- 参校字（align_ref）。

这些都取自各册的现行主版（★）产物包，包名写在 `input.pack`，汇总在 `packs.json`。
乙层另冻结了卡本身（`input.card`），含 lib_top、alt、ref、ctx 和待审原因。
`shown_approx` 是网站按钮的近似：参校字加上库前 3，去重后取 3 个。网站的 `cand` 来自校样文件，这里没有。

## 金标
- **只收人裁**：事件 `actor=user`，并且 reviewer、批次、来源里都不带 AI。史記 11-27 的 AI 看图落定批不收。
- 同一格裁了多次，取最后一次。
- `expected.status`：
  - `char` 是字；
  - `seg` 是切坏；
  - `figure`、`notchar`、`damaged` 不是字，或者残损。
  不是字的格不算命中率，只单报个数。
- 甲层带 `selfcheck_flag` 的格，评测时不计分。

## 行格式（items.jsonl）
```
{id, layer: A|B, book, book_title, vol, cell, u?, anchor?{bbox, space},
 crop{path, kind, src?}, input{ctx{left,right}, pool{lib, lib_verdict, rare, ctx_ranked}, ref, pack, now, card?, card_rev?, item?, vote?},
 expected{status, char}, label_origin: human, source_events?, stratum{set, tags?, rel?, block, gold_eq_ref?, selfcheck_flag?}, history, notes?}
```
`stratum.rel`（只乙层）记金标和卡的关系，取值如下：
- `lib1`：金标就是库首选；
- `ref`：金标就是参校字；
- `lib2-5`：在库的第 2 到第 5 名；
- `alt`：在相似字里；
- `none`：卡上哪里都没有。

`block` 是金标所在的 Unicode 区：basic、extA、extB+、compat。

## 跑
```
guji eval run @cands                       # manager 总入口
PYTHONPATH=. python scripts/eval_cands.py <dataset>/char-candidates --out r.json [--against 旧r.json] [--part 3c,4b,card]
```
要 torch、r5 权重和 SikuRoBERTa（HF 缓存，钉了 revision）。全集在 CPU 上跑几分钟。

## 重建
```
PYTHONPATH=. python scripts/build_char_candidates_set.py --dataset ../open-guji-dataset --packs <包缓存目录> \
    --ws-root <guji-workspace> --pack-list 988g3f0wsu=<pack list> --pack-list 995ejelvk0=… --pack-list siku-zongmu=…
```
运行前先 `guji db pull --no-glyph --no-rebuild` 三本书；`--pack-list` 填 `guji products pack list` 的输出。
人点的卡多了，就重建一次，扩大乙层。

## 已知偏差
- 两层都是审查流程挑出来的难格，数字不能当全书准确率读。
- 乙层里人多半按参校字点，所以卡片指标要按「金标 = 参校字」和「金标 ≠ 参校字」分开报，后者才是真难题。
- 前后文取自现行主版包，邻格的字可能已经吃进了后来的人裁，偏乐观一点。本格自己不进前后文。
- 甲层是生僻字格，库里这个字已经有人裁刻例。所以 3a 前 5 的冻结数是建库前那一轮产线的结果，不能拿来和现场 3a 比。
