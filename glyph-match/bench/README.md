# glyph-match/bench —— 5a 新图×字形库 比对基准

查询图不另存：直接用三书人裁冻结分片 `char-clustering/samples/00{4,5,6}-*-human`（crops + expected.json）。
本目录只放**分档标注**和**基线**：

| 文件 | 内容 |
|---|---|
| `tiers-<分片>.jsonl` | 每个实例一行：`id`、`flags`（clean/offset/edge/stain/heavy/thin，多标签）、`dx dy margin n_speck ink` 特征 |
| `baseline-2026-11-06.json` | 三书当前基线（cv dev 6a2aca8，库为中心库当天 main） |

分档由 64×64 归一图算出（分片自带 `tier` 全是 clean，分不出）；规则与阈值在 cv `scripts/eval_match_bench.py` 头部常量，
改规则要重出 tiers。heavy/thin 用**本书**墨比例最高/最低 10%。

跑法（登记表 id：`match_bench` 殿本、`match_bench_shiji`、`match_bench_qtw`；库按 `GUJI_GLYPH_DB` 取）：

    python scripts/eval_match_bench.py --book 004-siku-v2-human:<殿本 glyph.db> --perturb --out bench.json

指标、查询分类（answerable/novel）、扰动种类见脚本头与 ai-team `domain/CV/字形领域/5a比对基准-2026-11-06.md`。
局限同 char-clustering 人裁分片：人裁格是送审的难格，不能当全书准确率读。
