# guan L2 补表：vol02–99 送审格（2026-10-26，A24「压低官宫送审」）

- 批：cv 改规则后离线回放（97 册 main 包，不含 vol06，码位 宮=宫），取补放入口仍待审的 44 格，`l2_new_groups.py make`（提示词 cv `config/groups/guan/prompt.md`，book_desc＝《四庫全書總目》殿本刻本）。
- 跑：haiku、sonnet、opus（high）各一遍，`runs/<模型>/guanp_00.json`。
- 合表：`l2_new_groups.py ingest`（`l2_panel` 规则）给字 33；vol16:143:6:11「縣之學【?】歟」学官／学宫两可、opus 与另两家不同，人工剔掉。并进 `../guan.json`（原 17 格保留，vol19:76:3:12 按新窗口覆盖），ver `guan-l2-1+v1026`。
- 补放格逐格读上下文的结论在 `../../labels.jsonl`（`by=claude-a24-guan`、date 2026-10-26 的行）。
