# jys 己已巳：L1 规则册外回测与 L2 强模型复核（2026-10-24，A24「优化己已巳判别」）

不同义组，**只按文意定**。旧数据集（强真值、复审页）在 `../../jys/`、`../../review/jys*`；本目录是 10-24 这一轮的批跑原件、新表和标注。

## 这一轮做了什么
1. **L1 规则册外回测**：规则是从 vol01–10 挖的。用 Opus 对 vol04–20 全部进组格（约 1,240 格）重判一遍，查出新册里 L1 错改了 8 格（复核时把对的字改错）。规则改法见 cv `doc/字组/jys.md`。
2. **L2 表强模型复核**（cv `groups/l2_panel.py`）：vol11–20 的表只有 haiku 一遍，haiku 不是 high 的格全部送审。规则：Opus high 反对表里已给的字 → 否决；haiku 不是 high 时，Opus high 且 Sonnet 同字 → 补字。
3. 「而◎」规则收窄到句末（后面是 矣也乎哉耳焉、□ 或窗口尽头）；其余交文意表。sheldon 10-24 已同意（决定卡），连同下面 4 格争议金标改「己」。

## 文件
| 文件 | 是什么 |
|---|---|
| `batches/*.txt`、`batches/manifest.json`、`batches/cells.json` | 批（整条消息，提示词＝cv `config/groups/jys/prompt.md`），批 → 格，格 → 窗口。`jys_NN` 是旧金标批（vol01–10 强真值 226 格，同 cv `research/m7/ctx/l2_batches`）；`jysr_NN` 是表里弃权的 115 格；`jysv_NN`、`jysw_NN` 是 vol11–20、vol04–10 已由 L1 或表定字的格（审计用）；`jysx_NN` 是 L1 收窄后挪到表里的 106 格 |
| `runs/<模型>/<批>.json` | 各模型输出（opus＝全部批；sonnet＝金标、jysr、jysx；haiku＝jysx）。都是会话里开子代理按提示词原样跑的，没有给整理本 |
| `l2/jys.json` | **新表**（`group_clf/1`，ctx_ver 3）：中心库 `config/groups/l2/jys.json`（rev 99746）＋复核。上线时换掉中心库那份 |
| `l2/panel_manifest.json`、`l2/panel_cells.json` | 合表用的格单（表里的格＋挪进来的格） |
| `labels.jsonl` | 本线程的文意标注（`by=claude-a24-jys`，和人裁分开计）：回放里改了结论的格逐格读过，写了依据；原来与 sheldon 人裁不一致的 4 格，10-24 他已定为「己」（见 note） |
| `split.json` | 按册分折。规则和复核口径没有学来的参数，各折相同 |
| `eval.md` | 成绩：金标按册、册外回测、回放 |

重做：`python research/m7/ctx/l2_panel_book.py make <产物根> <册…> <现表> <目录>`，各模型跑完 `… ingest <目录> <现表> <新表>`。
