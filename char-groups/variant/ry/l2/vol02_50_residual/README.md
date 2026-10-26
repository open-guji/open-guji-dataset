# vol02–50 日曰／日目残留送审补读（A24，2026-10-26）

全 99 册统计（`char-groups/status/2026-10-26-全册-main-vol02-99`）里 vol02–50 的 ry／rm 送审 281 格（vol06 3 格不碰，余 278）。
基线回放（main 包＋现表 `+v5199`）拆出来的原因：共字组 rm 没表态（ry 给了字、rm 表缺格）83、文意表缺或低把握 61、
文意与整理本／放行字相反但不 strong 49、字形与文意冲突 22、曰格进了 rm（库分差内只有日目）rm 说「其他」25 等。

- `batches/b00–b07.txt`：三字联读（日／曰／目／其他）的批，窗口前后各 60 字（表键仍按 20 字）。
- `runs/opus/`：逐格细读（opus，写依据）；`runs/haiku/`：第二家（haiku）。
- `cells.json`：表键用的 20 字窗口；`manifest.json`：批 → 格。
- 逐格标签在 `../../labels_1026.jsonl`（kind=reading，by=claude-A24-ry-1026，事件号 `ry-verify-20261026-NNNN`，不进中心库）。

合表（ver 加 `+v1026`，表内注记 `verify_1026`）：
- ry 记 日／曰／其他，rm 记 日／目／其他（读成曰或别的字 → rm 其他）。
- 细读按 `ctx_l2.add_verify` 并入（票名 `opus#1026`、第二家 `haiku#1026`）；至少两遍、都 high、同字才 strong。
- 表里没有的格、或表键是旧窗口（重落后邻格变了、漂移超限，53+35 格）按新格建：haiku 须与细读同字才给字，否则 `abstain:new_dissent`。
- 已放行格：细读与原表相反（`disagree:verify`）但原表的字本来就与放行字不同 → 保留原表的字照常降审；表弃权而细读以 high／mid 给了
  组内另一个字 → 记细读的字（`agree:verify_demote`，不 strong），照常降审。都是为了不把「降审」变成「照旧放行」。

回放（vol02–05、07–50 main 包，`replay_groups.py --groups ry,rm,mz --raw`，配 cv 同期流程改动）：本任务 278 格送审 → 171；
这些册 ry／rm／mz 流程内送审 317 → 219；新放行／改字 98 格逐格读过，未见错。人裁与 10-24 细读金标（221 格已放行）：
不一致 5 格与改动前相同，都是旧的两可格，没有新增。
