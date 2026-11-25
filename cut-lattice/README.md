# cut-lattice：切分多备选评测集

量「切字给多个备选、下游挑一条」这件事：候选够不够（A 层，CV2）、挑得对不对（B 层，CV4）、换了以后定字错不错（C 层，CV4）。schema 与三层指标的定义见 ai-team `domain/CV/A24/切分多备选-schema与benchmark-草案-2026-11-25.md`。

## v1.0.0（2026-11-25，154 列）
来自 cut-bench（第二步切字固定样本，原图与冻结输入见 ai-team `domain/CV/A22/cut-bench/`）：现役算法（cv dev 64b8d9aa）切错的列全部，加每本书随机 10 列切对的作对照。金标切线由 CV2 预填，Sheldon 在 guji-manager review-pages（col_check）逐屏确认。

| 书 | 错列（调参／盲测） | 其中夹注列 | 好列（调参／盲测） |
|---|---|---|---|
| 史記 42 | 29（18／11） | 10 | 8（5／3） |
| 殿本 vol01 | 10（6／4） | 3 | 10（6／4） |
| 全唐文 053 | 33（21／12） | 28 | 10（6／4） |
| 脉经 01 | 46（30／16） | 23 | 8（4／4） |
| 合计 | 118（75／43） | 64 | 36（21／15） |

- 不收：金标被点出有错的 12 列（修好、再确认后作 v1.1 追加）；殿本 p88 职名页 3 列（非正文）。
- `err_tags` 是启发式预标（规则见 cutset-1125/README），确认页上可点「不确定」否掉，但没有逐项核。按错型分报时要注明这一点。错型分布见 `counts.json`。

## 字段（items.jsonl 一行一列）
- `key`＝`book:vol:page:col`；`group` wrong（现役切错）／good（现役切对，对照）；`split` tune／blind。
- `lines[]`：金标切线，`track` main 或夹注 a／b，`between` 上下格号，`k` 切点序号，`page_ends` 原图坐标 raw_page_px@top-right 的［右端点, 左端点］，`y_col` 列图 y。
- `col_img_sha`：该页 column_warp 产物 sha256 前 16 位。对不上时（第二步重跑过）用 `page_ends` 经新 quad 重投回列图，不要直接用 `y_col`。
- `gold_n`／`pred_n`／`ref_n`：金标、现役、参校本的格数；`ref_ok` 参校本字数与金标一致（目前只有史記有配页表）。
- `review`：`status` 恒为 ok，`how` click（点过格）／page_ok（整屏全对），`has_jiazhu`。

## 规矩
- 盲测集只在方案定稿和上线前跑，不用来调参；样本少于约 20 列的错型只报数，不调参。
- 以后加列只追加新版本，不改旧版本的行。
