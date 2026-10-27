# xjz（形近不同字对族，22 对）训练集

2026-10-27，A24「组外异体对未定码位」。组卡、判法与门槛见 open-guji-cv `doc/字组/xjz.md`。

- `labels.jsonl`：模板库用到的格（一行一格）。`form`＝标签字，`member`＝是否组员（否＝陪衬字）。标签全是 vol02–99 已放行格（无疑问、非人裁非印章）的放行字（`by=admit-label`）；按册留出的错例看过图。釆 的 4 格已放行刻例都是 采 的刻形，剔除。
- `replay_2026-10-27.jsonl`：vol02–99（除 vol06）离线回放进组的格与结论；补放 7 格看图全对（by=claude-a24-任务01）。
- 建库：open-guji-cv `research/m7/glyph_expand/build_family.py xjz <原图根> <产物根> --size 48 --cap 12 --write`。
