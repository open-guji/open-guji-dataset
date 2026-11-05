# rare-char / qtw-995ejelvk0（全唐文疑难字）

全唐文（book-text 995ejelvk0）r9b 统一字形审页六波审完后剩下的难认异体格，加上第二版小审页的补充格。Sheldon 在 11-05 用 char_card 难认字页逐格人点，人裁批次为 H-hv-1105 和 H-hv-1105b。

- `items.jsonl`：每格一条，统一金标信封。
  - `input.candidates` 按来源冻结：`page_v1`、`a23`、`page_v2`。
  - `expected` 字段：`status`，取值 char／unresolved／seg／notchar；`char`；`block`，即 Unicode 区；`rank`，即正确字在各路候选里排第几。
  - `stratum` 有五层：页上字对、改字·候选有、改字·候选无、认不出、切分或非字。
- `patches/`：字块图，按 r11 cell_shrink 字框裁。
- 重建：`python scripts/build_rare_char_qtw.py`。需要项目共享盘上的 hard-variants-r9b 目录，以及工作区事件日志。

0.1.0 基线见 `metadata.json`。改字层共 34 格，其中 18 格的正确字落在扩 B。A23 候选 top-12 召回 18/34，没召回的大多是扩 B 字。page_v2 是多路投票重排后的结果，top-1 是 0/14，比 A23 原序还差，说明「命中路数多」不适合当首位排序依据。
