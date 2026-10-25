# 變𠮓 刻形标注（2026-10-25）

下部 攵（左上多一短撇）＝變，又＝𠮓。sheldon 在标注页逐批标出：
- `sheldon_labels.jsonl`：733 行 `{id, form, by, date, src, note?}`。`src` 写每一批的约定：
  - 第一批只点 𠮓，没点的算 變；
  - 第二批只点 變，没点的算 𠮓；
  - 「其余」是 sheldon 口头说「剩下的下边都是又」，没有逐格点。
  - `form` 为空的 2 格是别的字（寢、凝）。
- `labels.jsonl`／`crops/`／`split.json`：cv `build_shape_pair.py bian --labels` 建库用的 345 格（「其余」每册 ≤12），crops 是线上同款 char_patch 清理后的字块。

计数：變 107（14 册，vol19 40 格最多）、𠮓 624。判法与评测见 cv `doc/字组/bian.md`。
