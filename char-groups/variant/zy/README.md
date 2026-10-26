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

## 2026-10-27 全册补表（A24「压低于千子干送审」）
全 99 册统计里 zy 送审 89 格（vol02–20 15、21–50 28、51–99 46）。病根同 rr：中心库 `zy.json`（zy-l2-1）只有 vol04–20 的 64 格，vol21–99 查表全落空；另有 4 条 L1 规则在新册误判（见 cv `doc/字组/zy.md`）。
只给要用的格补表（不全量批跑）：离线回放里进了 zy／yz 补放入口、表里没有的 169 格（`l2/vol02_99/zy`、`l2/vol02_99/yz`），加上旧表窗口对不上的 2 格与共字组 予子 要表态的 5 格（`l2/vol02_99/extra`）。haiku／opus（high effort）／sonnet 各一遍，按 `l2_panel` 合表。
- `l2/zy.json`、`../yz/l2/yz.json`：**新表**，ver `zy-l2-1+v0299`／`yz-l2-1+v0299`（旧 64＋3 格原样保留，旧表窗口变了的 2 格用新窗口重判）。上线时换掉中心库 `config/groups/l2/{zy,yz}.json`。
- `strong`：三遍同字、至少两遍 high（只标本轮新判的格）。
- 三遍都说「其他」的格记 `abstain:other`（共字组联判要它：zy 定 于／干，yz 须明说不是 予子）。
- 手工处理 1 格：yz `vol70:115:6:11`「益字【?】謙」改弃权（刻形与同页「予咸」的 予 几乎一样，三模型都不 strong）。
- `labels.jsonl` 追加 183 行（`by=claude-a24-zy1027`）：回放里新放行、改判的每一格，逐格读过上下文、看过字块图，写依据、整理本字、原产物字。
