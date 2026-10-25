# yr 一二：数横评测集与错放审计（2026-10-25，A24「优化一二判别」）

不同义组。cv 仓 `groups/bars.py::count_bars`（数横）的评测集，和这一轮看图审计的结论。做法与成绩见 cv `doc/字组/yr.md`。

| 文件 | 是什么 |
|---|---|
| `labels.jsonl` | `by=auto-admit`：殿本 vol04–20 现产物（vol11–15、17–20 v0.5.12，vol16 v0.5.9，vol04–10 各册 main 包）已放行、数横与放行字同字的格（7,144 行）。`by=claude-a24-yr`：看图审计的 15 格（错放 9、送审格看图 6），`form` 是看图定的字（「非字」＝切碎的半个字，`kind=cut`），`admitted` 是产物里的现状，`note` 写依据（上下文、列图） |
| `split.json` | 按册分折。数横没有学来的参数，各折同一套门槛 |
| `crops/` | 审计格的字块（线上同款 char_patch） |

字块取法：`guji products pack fetch` 取产物包，`guji source pull` 取原图，`RunContext.materialize("char_patch", "p<页>c<列>s<格>")`。
