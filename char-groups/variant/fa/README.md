# 發𤼵 刻形标注（2026-10-25/26）

右下 殳＝發，矢＝𤼵。vol21–50 main 包里放行字或整理本字在组里的全部格，sheldon 在标注页（https://claude.ai/artifact/9bbu5iubFNW9HgH3Hf4jCR，db 集合 fa）过了一遍：
- `sheldon_labels.jsonl`：`{id, form, by, date, src, note?, admitted_as?}`。`src`：
  - 「sheldon 逐格点」：他点过的格；
  - 「其余」：页上预填机器判的刻形，他看过没改，按预填算（建库每册每字 ≤12）；
  - 「复核（2026-10-26）」：建组后按册留出机器高把握判反的格，拿回去再点（`note` 记首轮标签）；
  - 「看图更正」：A24 看图改的（只 fa vol48:61:5:7 一格，预填误作 發）。
  - 「sheldon 逐格点（vol51–99 标注页）」「其余：sheldon…（2026-10-26 vol51–99 标注页）」：10-26 补 vol51–99，页 https://claude.ai/artifact/4vJouspkJXp3rYrJcYZ2i4 （db 集合 fa）放回放没把握的 60 格；
  - 「其余：A24 右下放大逐张看」：vol51–99 回放高把握改判 𤼵 的 99 格，没上页，A24 看过（by claude-a24）。
  - `form` 为空＝不清，不进模板。
- `labels.jsonl`／`crops/`／`split.json`：cv `build_shape_pair.py fa --char-patch --labels` 建库用的格（线上同款 char_patch 清理后字块），含陪衬 登務條 放行格各 60（10-26 起 660 格，vol21–99）。

判法与评测见 cv `doc/字组/fa.md`。
