# char-groups — 字组测试集

**用户 10-06 定的思路**（overview#437）：在 Step5–7 的大算法下面接一批「小分类器」。待审格里最常见的是几组形近字
（己/已/巳、日/曰、人/入/八）和许多组异体字。一格认出属于某组，就交给这一组**专门的算法**去拆，每组单独积累数据、单独提升。
本目录**一组一个子目录**，每组的测试数据在里面单独积累。

先收三组形近字：

| 目录 | 组 | 类型 | 一句话 |
|---|---|---|---|
| [jys/](jys) | 己 已 巳 | 形近 near_form | 殿本三字基本同形，只能按文意；现行全族大半送审 |
| [ry/](ry) | 日 曰 | 形近 near_form | 字形分不开（#352 负结果），现行主依据是整理本；放行多，错例零星但真实存在 |
| [rr/](rr) | 入 人 八 | 形近 near_form | 几乎全放行（送审 ~2%），强真值极少，放行错率**量不出来** |
| [variant/](variant) | 异体对（按对登记） | 异体 variant | 放行字与候选互为异体、哪边是图上形；基线与三种误判原因见该目录 README（vol04/vol05，10-10 道 B） |

## 分工：分类器在 Step6，Step7 只判断（用户 10-06 更正）

- **Step6**：判这一格属于哪个字组，交给该组的分类器。分类器可以用 Step5 的字形结果，也可以用上下文、词组、大模型；
  产物里记三样：**组名、给的字、把握程度**（拿不准就弃权）。
- **Step7**：只把分类器的结论当作一路证据，决定放行还是送审，不在 Step7 里写按字组认字的逻辑。
- 现在 seed_admit（Step7）里按字组写的逻辑——己已巳 `_resolve_ji_yi_si` 与 `ji_yi_si_ctx_rule`、形近护栏 `iron_confusable_guard`、
  异体护栏 `lane_variant_guard`——等对应组的分类器在 Step6 做出来，「认字」部分挪到 Step6，Step7 只留放行/送审的闸。
- 所以本目录的评测分两层：**分类器**（Step6）报每组的「给字率 / 给字准确率 / 弃权率」，在强真值上按册算；
  **放行**（Step7）照 `baseline.json` 报放行、放行错、送审。`baseline.json` 是分类器接进来之前的现行数，之后每个新方法都跟它比。

登记表见 [groups.json](groups.json)；建集记录（取了哪几个快照、上游 sha 是否对得上）见 [_build_info.json](_build_info.json)。
之后的异体字组（#433 护栏拦下的 21 格、#431）照同一格式加新目录，在 `groups.json` 登记。

## 每组目录里有什么

| 文件 | 内容 |
|---|---|
| `README.md` | 这一组的现状、已试过的方法与结果（含负结果）、已知难点、还缺什么 |
| `items.jsonl` | 一行一格（字位 × 组），全量，不只难例 |
| `crops/` | 字块灰度图（原图按 `cell_shrink` 的 `bbox_page` 裁，`core.anchor.crop_patch`），文件名＝id 的 `:` 换 `_` |
| `baseline.json` | 现行管线在本组上的成绩：按册分，放行、放行错、送审各几格，按通道细分；强真值格上各来源首选字的错率 |
| `context_stats.json` | 成员字在外部语料（殆知阁，与《總目》无重叠）与域内语料（《總目》本身）里的前后字搭配统计，注明来源与 sha256 |

## 怎么判一格属于哪组

- **core**：放行字 / 整理本对位字（`align_ref.chars`）/ 坐标证人字（`align_ref.coord`）/ 库首位（`glyph_match`）/ 任一真值 落在组里。基线只数 core。
- **外围**（`core=false`）：只因库第二候选或上下文首选（`context_decide`）落在组里。留给分类器量「组路由」的召回，基线不计。
- 一格可同属两组（如库前二是 已/日），每组各一行；跨组做总数按 `id` 去重。

## 一行一格（`items.jsonl`）

字段沿用 N1 的 `near-form-groups`（overview#428），补了真值档、页型、划分、外围标记与更长的上下文：

- 位置：`id` `book` `page` `col` `slot` `sub`（夹注 a/b）· `group` `core` · `split`（见下）· `page_type`/`page_type_src` · `kind`（Step3 格类）
- 真值：`gold` `gold_tier` `label_origin` `gold_src` · `gold_conflict`（强真值来源之间不一致）· `golds`（**所有来源逐条**：字、档、来源、备注）
- 现行产物：`admit` `channel` `char` `provenance` `doubts` · `ref` `ref_op`（整理本对位）`coord_ref`（坐标证人）·
  `lib` `lib_verdict` `lib_cov`（库前三）· `rare`（5-b 前三）· `ctx` `ctx_ranked` `ctx_source` `ctx_margin`（Step6）· `ocr` · `ji_yi_si`（己已巳规则的字与理由）· `snap`（取自哪个快照）
- 上下文：`left`/`right` 刻本读序前/后各 30 字（G1 起，用户 10-06 定先多放，G0 是 8；跨列连读，到页首页尾为止；未放行格用整理本字补，再没有记「□」）；`ref_left`/`ref_right` 整理本对应位；`word`（前 2【本格】后 2）
- 图：`crop` `ink` `wh`
- vol01 的题（`split=extra`）没有快照，只有文本上下文与人裁金标，另带 `cc_tier` `cc_options` `cc_arms`（confusable-context 首轮各臂答案）

## 真值分档（`gold_tier`，一格多个来源时取最高档；全部来源都在 `golds` 里）

| 档 | `label_origin` | 来源（`gold_src`） | 能干什么 |
|---|---|---|---|
| **A_human** | human | 用户审查页人裁 `user_review_<组>`（G1，`review/<组>_verdicts.jsonl`，排在 A 档最前）；人裁事件 `human_event`（工作区 `feedback/events`，`human_chars`，后到覆盖）；快照里 Step7 已采信的人裁 `snap_channel_human`；muse 试点 truth 里的 human；#352 样本里的人裁 `r352_human`；confusable-context 题 | 强真值 |
| **B_vision** | vision | 看图结论事件 `vision_event:*`（`feedback/vision`，V1 通道，同格按 ts 取最新）；overview 看图清单 `look_v03_s8` `look_v03_jys` `look_v04_s8` `look_v04_jys`；#426 的 3 格 `card426`；muse 试点 truth 里 Z39 会话判的 | 强真值，但是模型判的，**单独分层报** |
| **C_weak** | align | 已放行、非人裁、放行字＝整理本对位字＝坐标证人字 `witness_agree`（己已巳不给） | **对 match_ref 是循环的**，只作参考，不拿来数放行错 |
| （无） | — | — | 只有现行产物 |

另有 `X_unclear`（只出现在 `golds` 里）：用户审查页里点了「看不清」、或点了「别的字」没填字的格，不当真值。
另有 `X_stale`（只出现在 `golds` 里）：人裁事件早于快照、快照却没采信它（Step7 当时过绑定表，判它挂错了格）——编号可能已漂，**不当真值**。
本次共 3 格（vol02 `75:1:12`、`75:6:9`，vol03 `105:4:3`），都是整列顺移后旧编号落到了别的字上。

强真值与弱真值重叠的 10 格日曰里，弱真值错了 2 格（`vol02:188:5:19`、`vol04:133:3:7`，证人与放行都作「日」，实为「曰」）——弱真值**不能**当金标用。

## 评测口径

1. **按册报，分开报**：dev / val / pool 三类册不合并；正文与非正文分开（`page_type`，vol02 有 page-type 人裁，其余册 p1–2 与 vol04 p129 推定非正文）。三组的非正文格合计不到 10 格。
2. **划分**（`split`）：
   - `dev` = vol02、vol03：调方法用（人裁最多，vol03 有 muse 试点）；
   - `val` = **vol04，留出验证**：现行代码最新的产物（含 I1、N1、#360、#433 各开关），真值全是看图；方法定型之前不看它的错例；
   - `pool` = vol05–vol10：只有现行产物与弱真值，量覆盖和人审率，不量错率；
   - `extra` = vol01 confusable-context 题：没有快照，只能考纯上下文。
3. **两个数一起报**：放行错（只在有强真值的放行格上数，是下界，分子分母都写）和送审率（＝(人裁+待审)/core 格）。目标是保准确率的前提下压送审率。
4. **强真值分层**：human 与 vision 分开报；vision 是模型看图判的，可能有错。
5. **偏差**：强真值格多是机器拿不准才送人看的难例，放行格上的强真值多来自 S8「放行错穷举」（专挑与证人不一致的）——**都不是随机样本**，错率比全书高。要量全书放行错率，得另抽随机样本看图（见各组 README「还缺什么」）。

## 用户人裁（`review/`，G1，用户 10-06 定）

G0 缺数据清单第 1 条（放行格随机抽样）改由用户亲自人裁，记 A 档。三批，一批一页（cv `research/char_groups/review_pages.py` 出页）：

| 批 | 抽样框（都只取正文页） | 抽几格 |
|---|---|---|
| `ry` 日曰 | vol02/03/04 机器放行格（core、admit、channel≠human） | 每册 100，vol03 框里只有 76 格全收，共 276 |
| `rr` 入人八 | 同上 | 每册 100 |
| `jys` 己已巳 | vol04 待审格（core、未放行）全收；vol05 core 格 | vol04 全部 + vol05 随机 50 |

- **种子 `20261006`**（`random.Random("20261006:<组>")`，框按 id 排序后 `sample`，再整批打散）。
- `review/<组>_cards.jsonl`：冻住的卡片 id，带 `stratum`（`<册>:<框>`）、`frame_n`（框内格数）、`stratum_weight`（框内格数 / 抽中格数）。重出页面照读这份，不重抽。
  放行错率按册估：抽中格里裁出的错数 × `stratum_weight`。
- `review/<组>_verdicts.jsonl`：收回的裁决，一行 `{id, verdict, t}`；`verdict` 是成员字、`other:<字>`、`other`（没填字）或 `unclear`。
  `build.py` 把它当 A 档来源收进 `golds`（src `user_review_<组>`），再跑 `baseline.py` 基线就带上了。
- 卡面不印机器判断：上下文里目标位挖空，放行字、整理本此处的字、通道收在折叠的「机器参考」里。

**第一轮收回（10-06）**：用户裁了一部分（太累没裁完；自己也难判的点了「看不清」），已裁的先进测试集。

| 批 | 抽了 | 已裁 | 记 A 档 | 看不清 | 放行格里裁出的错 | 整理本错 |
|---|---|---|---|---|---|---|
| `ry` 日曰 | 276 | 18 | 18 | 0 | 0/18 | 0/18 |
| `rr` 入人八 | 300 | 33 | 33 | 0 | 0/33 | 0/33 |
| `jys` 己已巳 | 120 | 53 | 46 | 7 | 1/3（`vol05:112:9:7` 巳→已） | 26/46 |

三页都留着（URL 见 cv `research/char_groups/README.md`），没裁完的可以接着裁，或按各组新开的道的需要换题重出（`review_pages.py --seed-verdicts` 续裁）。
用户对三组各自的判法写在各组 README 的「用户人裁与观察」一节。

## 快照与复现

| 册 | seed_admit 快照 | 上游快照 | 产物代码 |
|---|---|---|---|
| vol02 | `vol02/20260930T0339` | `20260929T1024`（切分 `T1023`） | 09-30，早于 I1/N1 |
| vol03 | `vol03/20260930T0457` | `20260929T0451`（切分 `T0450`） | 09-30，早于 I1/N1 |
| vol04 | `vol04/20261006T1208` | 同 | cv `579f2e9f0c`，含 I1、N1（`ji_yi_si_ctx_rule` 开）、#360、#433 开关 |
| vol05–10 | `vol05/20260928T1508`、`vol06/…T1509`、`vol07/…T1509`、`vol08/…T1455-full`、`vol09/…T1511-full`、`vol10/…T1455-full` | 同 | 09-28 |

各册 seed_admit 的 `_manifest.jsonl` 里记的上游 sha256 与所取上游快照逐页比对，**全部一致**（`_build_info.json`）。
（N1 建 vol03 时取的上游是 `20260928T1708-full`，与 0930 的 seed_admit 不配套；这里改用 `0929T0451`。）
vol02/03/05–10 的产物早于 I1、N1，各册重跑 seed_admit 后要换快照重建基线。

```bash
# 快照解到沙箱（只读，不碰正式 products）
git -C <bare> fetch --depth 1 origin snap/96mid1ogzk/<册>/<时间>:refs/s/<册>_<时间>
git -C <bare> archive refs/s/<册>_<时间> | tar -x -C <snap_root>/<册>_<时间>
cd open-guji-cv
python research/char_groups/build.py <snap_root> <dataset>/char-groups      # items.jsonl + crops/
python research/char_groups/baseline.py <dataset>/char-groups               # baseline.json
python research/char_groups/corpus_stats.py <dataset>/char-groups           # context_stats.json
python research/char_groups/summary.py <dataset>/char-groups                # metadata.json + 格数表
```
`common.py` 里 `SNAPS` 是快照表，换快照只改这一处。建集需要工作区（`feedback/events`、`feedback/vision`、`data_full`）、
overview（看图清单、muse 试点）与本仓 `confusable-context`。

## 来历

- N1 的 `near-form-groups/`（overview#428）整体并入：N1 的每一行（id × 组）在这里都有，只有 2 行例外（N1 的 vol03 上游快照不配套，误收进组，见 `../near-form-groups/README.md`）；原目录只留一个指过来的 README。
  并入时修了 N1 的一处解析错：vol03 放行错穷举表「图上是」一栏取首字，把「同形」「同上」「封口形…」读成 同/封，vol03 己已巳有 9 格的真值因此丢了；
  这里改成只收单字，这 9 格的文意判由「全族逐格文意建议」表收进来。
- 全量：vol02–vol10 九册有快照的都收；N1 只收 vol02–04。
