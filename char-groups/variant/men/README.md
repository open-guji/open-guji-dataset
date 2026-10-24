# men（門族 間聞問閱閩闡…，形近不同义）训练集

2026-10-24，A24「强化门族与辶族形近判别」对话。组卡、判法与门槛见 open-guji-cv `doc/字组/men.md`（PR open-guji-cv#518）。

- `labels.jsonl`：一行一格。`form`＝标签字，`member`＝是否组员（否＝进库的陪衬字）。标签全是殿本 vol04–20 seed_admit 已放行格（无疑问、非人裁非印章）的放行字（`by=admit-label`），不是人裁；按册留出的错例看过图，都是判法错、标签对。
- `crops/`：字块图（`crop_patch` 原样，未去碎墨；建库时再 `clean_patch`）。
- `split.json`：按册分折，评某册时模板不含该册。
- `replay_2026-10-24.jsonl`：离线回放进组的格与结论；补放格带 `look`（看图确认，`by=claude-强化门族与辶族形近判别`）。
- 建库与评测：open-guji-cv `research/m7/glyph_expand/build_family.py men`；回放 `replay_family.py`。
