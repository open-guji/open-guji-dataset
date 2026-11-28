# decide-bench/tools：建 decide-bench 金标用的工具

2026-11-28 从 ai-team `domain/CV/A24/decide-bench/` 搬入（评测脚本 run／score／dyn／gate_bench 在 cv `open_guji_cv/eval/decide_bench/`，不在这里）。
都是单文件命令行脚本，在本仓根目录运行：`python decide-bench/tools/<名>.py …`，参数见各文件开头的用法。

建 small／large 的顺序（金标来源与分层规则见 [../README.md](../README.md)）：

| 步骤 | 脚本 | 作用 |
|---|---|---|
| 1 取金标 | `select_gold.py` | 从人裁（D1 events）、dataset 已有的格挑金标候选，按原图框绑格（殿本加 `--bind`） |
| | `gold_from_pack.py` | 从冻结包直接取金标 |
| | `count_sources.py` | 数各来源（人裁、AI 判定、book-text）能绑上多少格，选法前先量 |
| 2 分层抽审 | `stratify.py` | 按放行／拦住规则分层，每条规则挑例 |
| | `sample_admit.py` | 放行格随机抽查（银标人抽查用） |
| 3 出审阅 | `build_review.py` | 出审阅页输入（实际页型用 guji-manager `review-pages`，不手写网页） |
| 4 收回 | `apply_review.py`、`append_fill.py` | 把审阅结果收回金标／补进冻结集 |
| 5 成片 | `build_shard.py`、`build_large.py` | 写 `items.jsonl`、`metadata.json`、`report.json` |

cell-state 分片由 cv `python -m open_guji_cv.eval.decide_bench.build_cell_state --dataset .` 生成。
这些脚本要连中心库、工作区与产物目录，不在 CI 里跑。
