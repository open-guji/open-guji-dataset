# decide-bench：第四步「定字」评测集

第四步定字＝cv 大步 `decide`：4a 整理本对位 `align_ref`、4b 上下文 `context_decide`、4c 放行 `seed_admit`（负责：CV4）。
三层设计（Sheldon 2026-11-23 定）：

| 层 | 目录 | 内容 |
|---|---|---|
| 小型 | [small/](small) | 几千格，固定输入输出，金标 100% 对 |
| 大型 | [large/](large) | 几册冻结现数据，标注可稍错，定期更新 |
| 动态 | （不进本仓） | 随时跑现行数据看结果 |

## small（v0.2.0，9,422 格）

| 书 | 册 | 格 | 其中抽审 |
|---|---|---|---|
| 史記 | 03 | 2,951 | 28＋56 |
| 全唐文 | 004 | 5,357 | 113＋24 |
| 殿本（四库总目） | vol01 | 1,114 | 82＋19 |

- **金标来源**：人在网页／artifact 上的定字裁决（D1 `events`，kind=confirm、actor=user、step=seed_admit），只收与参校本一致、明确推翻参校本、或 dataset 已有的格。
- **锚定**：`anchor.bbox` 是原图框（raw_page_px@top-right）。评测时按框找现行切分里 IoU 最大的格（≥0.5，次格 <0.2），不按格号。`key_at_freeze` 只供参考。
- **抽审**：按放行／拦住规则分层，算法与人裁不一致的全上页，Sheldon 用 guji-manager gold_sample 审了 223 格（改字 50 格）。
- **规则补例**（v0.2.0）：金标里不到 8 例的 19 条放行／拦住规则，从算法结果随机补到 8 例，Sheldon 抽审 102 格（改字 20、看不清 3 不收），`stratum=规则补例`。
- **书级改字**（Sheldon 11-23）：全唐文 內絕勳虛茲 一律作 内絶勲虚兹。抽审还显示全唐文的 愼、荆、淸、宫、隷 等也是刻形，旧人裁写成了通行字。
- **判对**：己已巳、日曰组内任一字算对；放行字与金标只差异体选形，单独记为「放成异体」，不算错字。异体对认 cv `variants` 图，外加 cv `config/hanzi/core/edges.tsv` 里 relation=variant 的对（變／𬽠、策／䇿 不在 variants 图里，11-23 复核时补）。
- **放成异体都经人看过**：算法字与金标不同的格全部上过抽审页，金标字是 Sheldon 按刻形定的。

`report.json` 是冻结时的基线：cv dev（v0.9.0 前）关人裁重跑，按书×规则×结果计数。基线合计（v0.2.0）：

| 书 | 放对 | 放错字 | 放成异体 | 拦住·首选对 | 拦住·首选错 |
|---|---|---|---|---|---|
| 史記 | 2,922 | 0 | 14 | 3 | 12 |
| 全唐文 | 5,326 | 0 | 21 | 9 | 1 |
| 殿本 | 958 | **1**（vol01:88:6:9b 管→總，match_solo） | 19 | 20 | 116（含 77 格人裁排除名单带入，非算法） |

## large（v0.1.0，9,873 格）

| 书 | 册 | 金标来源 |
|---|---|---|
| 史記 | 01、02 | 整册人裁，按 cv 绑定表绑到快照 |
| 全唐文 | 005、008 | 同上 |
| 殿本（四库总目） | vol02、vol04 | 冻结包里已落到格上的人裁（旧事件多因换图绑不上：vol02 8,430 条只绑上 161） |

- **金标**：整册全部有字人裁，不逐格审，允许少量错。`stratum` 记来源与和参校本的关系。
- **复核**：基线放错字 27 格全部给 Sheldon 看过（11-24）：14 格改金标（史記私用码 U+EF6E 是 Unicode 未收字，最像「揚」，按揚算），1 格看不清移出，12 格确认是算法错。
- **放行抽查**：从算法放行、又没有人裁的格里每册随机抽 30 格（共 180），char_grid 页上 Sheldon 没点出放错的格（框带边框墨迹不算错）。0/180，放行错率 95% 上限约 1.7%。

基线（cv dev 73133d89 关人裁重跑）：

| 书 | 放对 | 放错字 | 放成异体 | 拦住·首选对 | 拦住·首选错 | 放行率 |
|---|---|---|---|---|---|---|
| 史記 | 4,640 | 0 | 10 | 10 | 33 | 99.1% |
| 全唐文 | 2,788 | 0 | 27 | 32 | 3 | 98.8% |
| 殿本 | 2,181 | **12** | 35 | 53 | 49 | 95.6% |

殿本 12 格放错字：note_lexicon 把 𨽾 放成 𨽻 6 格；match_solo 撫→廵、鶴→號、一→二 等 3 格；ref_lib 髣→髴、災→𠮓 2 格；match_ref 徙→徒 1 格。

跑法同 small，`--shard <本仓>/decide-bench/large`。

## 怎么跑（一键跑分）

脚本在 ai-team `domain/CV/A24/decide-bench/`：`run.py`（取快照、跑第四步、打分）、`score.py`（只打分）。

```bash
# 现行代码对上次结果，出翻转清单
python run.py --shard <本仓>/decide-bench/small \
  --ws 988g3f0wsu=<史記工作区> --ws 995ejelvk0=<全唐文工作区> --ws siku-zongmu=<殿本工作区> \
  --work <工作目录> --name <名字> --against <上次的 <名字>-A.jsonl>
# 改参数：A（现行）与 B（A＋参数）都跑，B 对 A 出翻转清单
python run.py … --params '{"seed_admit": {"某参数": 值}}'
```

- 快照按 `small/bench.yaml` 的包标签从 R2 取（`guji products pack fetch --label`），取回核 digest。只重跑第四步（align_ref→context_decide→seed_admit），关人裁，不在线问 AI（只读裁定缓存）。
- 输出：按书一行（放对／放成异体／放错字／拦住·首选对／拦住·首选错、放行率、人审首选对率），`wrong_admit` 必须为 0；`--against` 时列翻转格（好转／变坏／其它）并写 `*-flips.tsv`。
- 只打分（已有产物）：`python score.py --items small/items.jsonl --run 03=<产物根/03> … --out r.jsonl [--against 上次.jsonl]`。
- 耗时（4 核、装 torch）：史記 03 约 6 分钟，全唐文 004、殿本 vol01 各几分钟。

### 备工作区（每书一次）
空目录写 `workspace.yaml`（`id: <工作区 id>`）和 `.central.json`（`{"ws": "<id>", "branch": "main"}`），然后：
`guji db pull -w . --exclude run`（设 `GUJI_DATA_HOME`）→ 拷书仓 `code/` 进来 → `guji model fetch -w .`（全唐文再跑一次不带 `-w` 的）→
`guji glyph-db pin-build -w . --pin <册 yaml 的钉版号>` → `guji source pull <册> -w .`。要装 torch，否则文意 L2 静默弃权。
cv 是 dev 版、册钉旧语料时设 `GUJI_CORPUS_DRIFT=warn`（run.py 已设）。

### 已知限制
- 册配置、模型、字形库、裁定缓存取工作区现行（钉版的照钉版），没有整包冻结；这些变了，基线要重跑一次再比。
- 第四步不改切分，金标按冻结格号（`anchor.key_at_freeze`）对格；切分改了要按 `anchor.bbox` 重绑。
