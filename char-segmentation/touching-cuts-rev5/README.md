# char-segmentation / touching-cuts-rev5：殿本粘连切线（迁到现行图源 rev5）

## 这是什么
`touching-cuts` 的旧条目把 y 记在**旧图（CADAL，页表 rev2）的列图坐标**里。殿本后来两次换图源（10-26 qiefen-v2、11-07 Commons），
旧条目在现行图上已经对不上。本子集把它们迁到**现行图源 rev5 的原图页面坐标**，并经人审（Sheldon，2026-11-23）。
另外收进控制台「切线」页 09-28～10-01 一批当时没收割的事件（页面坐标）。

## 两档
| 文件 | 档 | 条数 | 能不能当金标 |
|---|---|---|---|
| `items.jsonl` | `human_checked` | 603（vol01 200、vol02 240、vol03 163；折线 540） | 能。迁移后逐条出图给人看过，判「对」才收 |
| `migrated_unreviewed.jsonl` | `migrated_unreviewed` | 713（vol01 379、vol02 334；全是直线） | **不能当人核金标**。迁移后只过了墨谷筛（离最近墨谷 ≤3px），抽样估计约 4% 偏错；只当参考或弱监督用 |

人审判「不对」的 58 条、「看不出（背景印章）」的 12 条不收。

## 字段
- `anchor`：`{book, page, col, slot, space:"raw_page_px@top-right", source_rev:5}`，页号、格号都是 rev5 的。
  **格号只当提示**：迁移里有约 10 条格号差一格，定位以 `expected.page_y` 和上下字为准。
- `expected.page_y`、`expected.page_x_tr`：切线在原图页面上的位置（右上原点）。
- `expected.page_polyline_tr`：折线切法，`[[x_tr, y], …]`，页面坐标。直线条目没有这个字段。
- `expected.verdict`、`slot_above/below`、`char_above/below`、`tags`：沿用旧标注。
- `review`：人审记录 `{by, date, page, verdict}`（只有 `items.jsonl` 有）。
- `provenance.label_origin`：`human` 或 `migrated`。
- `qc.valley_dist`：只有未人核档有，表示离最近墨谷的距离（px）。

## 怎么迁的
旧列图 y → 旧页（cv 0.5.21 在 rev2 图上重跑 border_detect→column_warp 复原列图几何，按 `col_h` 对上才收）
→ pagemap 仿射 → rev4 `from_rev.H` → 新页 → 新图 ±25px 模板匹配精修。
脚本与逐步记录在 ai-team `domain/CV/A22/cut-bench/tc-migrate/`。

**已知坑**：`col_h` 对上不等于几何对上，列尾几格可能偏约 20px，所以未人核档不能直接当金标。
