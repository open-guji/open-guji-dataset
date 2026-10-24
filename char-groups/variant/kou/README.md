# 口框族 國圖圍園固圓圜 训练集（2026-10-24，A24「强化口框族形近判别」线程）

组卡与判法：cv 仓 `doc/字组/kou.md`；建库脚本 `research/m7/glyph_expand/build_shape_pair.py kou … --char-patch`。

- 范围：殿本 vol04–20 现有产物（vol04 rev-004-r9、vol05 freeze-1.0.1、vol06 rev-006-r5、vol07–10 cv0.5.7 full、vol11–20 cv0.5.9p42）里
  已放行字是 國圖圍園固圓圜 和陪衬 圃圈囿 的格（人裁与印章通道除外），加中心库人裁刻形。團 殿本 vol04–20 没有放行格，不收。
- `labels.jsonl` 一行一格：
  - `form` 标签字（`src=放行字`：放行字当标签；`src=central:人裁`：中心库人裁刻形；`src=看图`：本线程看图剔除的 5 格，`status` 写原因）；
  - `in_bank`：是否进了 cv `config/groups/kou/ids_bank.json` 模板库（每册每字 ≤12、每字总共 ≤30，人裁不限）；
  - `loo_pick`／`loo_margin`：按册留出（判某册时模板不含该册）用线上门槛前的判字与分差，门槛 1.0。
- `crops/`：线上同款 char_patch（`ctx.image("char_patch")`，未做 `clean_patch`），只存模板格、人裁格、看图格和留出判字与标签不同的格（303 张）；
  其余格可按 id 用 `guji cache get --kind char_patch` 重取。
- `split.json`：按册分折。
- 成绩：成员格 2,996，门槛 1.0 给字 2,304（77%）、0 错；0 错门槛 0.90。
