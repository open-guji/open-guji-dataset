# decide-bench/cell-state：4c 格况评测集（起步）

4c `cell_state`（负责 CV4）判一格有没有字、被印章／墨点／切坏占了没有。本分片量它的护栏：**有字判无字（漏字）必须为 0**。
构建脚本：cv `open_guji_cv/eval/decide_bench/build_cell_state.py`（只用已有人裁，不新增标注）。

| 子目录（工作区 id） | 书 | char | non_char |
|---|---|---|---|
| `988g3f0wsu/` | 史記 03 | 2,951 | 0 |
| `995ejelvk0/` | 全唐文 004 | 5,357 | 0 |
| `siku-zongmu/` | 殿本 vol01（char）；vol01、vol02（non_char） | 1,114 | 38 |

- `items.jsonl` 用统一信封：`id`、`anchor`、`input`、`expected.state`、`label_origin`（human／human_audit）、`stratum`、`status`、`source_events`、`history`。
- **char**：来自 `decide-bench/small`，人裁定了字的格，锚点是原图框（IoU≥0.5 对现行格）。
- **non_char**：来自 `char-segmentation/instances` 的人标 `not_text`，锚点只有产物键（页、列、槽），无 bbox，切分改过可能失效。
- 都不是随机样本（char 层易格偏多，non_char 层是难例），不能估全册率。

## 已知缺口（S12）

- 没有 seal／occluded／seg_bad／blank 的金标；史記、全唐文没有 non_char；non_char 无 bbox。
- 11-28 起 Sheldon 定标注暂停，补标等恢复后用 guji-manager review-pages 做，由 CV4 负责。
- 打分接入：`score.py` 现从 seed_admit evidence 反推 4c 漏字，待 4c 独立产物（cell_state）接上后读本分片的 `expected.state`。
