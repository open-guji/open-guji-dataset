# 于千子干等形近不同义组：zy 于千子干、yz 予子、guan 官宫宮、hou 侯候𠉀俟、liang 兩雨（2026-10-24，A24「强化于千子干等形近判别」）

不同义组，**按文意定**。千干 qg 并进 zy（cv `registry.RENAMED`）；宫宮 由 #5 线程交来，归 guan。

## 文件（五个目录同一布局）
| 文件 | 是什么 |
|---|---|
| `batches/<组>p_NN.txt`、`manifest.json`、`cells.json` | 给模型的批（整条消息，提示词＝cv `config/groups/<组>/prompt.md`），批 → 格，格 → 窗口。格＝回放里进了本组补放入口的全部格（L1 已给字的也进批，审计用） |
| `runs/<模型>/<批>.json` | haiku、sonnet、opus（high effort）各跑一遍的输出，会话里开子代理按提示词原样跑，不给整理本 |
| `l2/<组>.json` | **新表**（`group_clf/1`，ctx_ver 3）：空表起，按 cv `groups/l2_panel` 合：haiku high 且 Opus 没以 high 反对 → 给字；haiku 不是 high 时 Opus high 且 Sonnet 同字 → 给字。上线时放进中心库 `config/groups/l2/<组>.json`（「推」） |
| `labels.jsonl` | 本线程的文意标注（`by=claude-a24-xingjin`，和人裁分开计）：回放里新放行、降审的格逐格读过上下文、看过字块图，写依据、整理本字、原产物字；另记 L1 回测查出、回放没改的现有错放 |
| `split.json` | 按册分折 |
| `eval.md`（只在 zy） | 五组成绩 |

重做：cv `research/m7/ctx/replay_groups.py`（回放，`--redo zy,qg`）→ `l2_new_groups.py make`（出批）→ 各模型跑 → `l2_new_groups.py ingest`（合表）→ 带 `--tables` 再回放。L1 规则怎么挖见 cv `research/m7/ctx/mine_l1/README.md`。
