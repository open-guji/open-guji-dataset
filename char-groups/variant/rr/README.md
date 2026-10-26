# rr 入人八：vol02–99 L2 补表（2026-10-26，A24「压低入人八送审」）

不同义组，「不看上下文无法判，读上下文判」。cv 判法与回放结论见 cv `doc/字组/rr.md`。

## 这一轮做了什么
全 99 册统计里 rr 送审 124 格（vol02–20 22、21–50 45、51–99 57），其中 106 格是文意 L2 表查表落空——中心库
`config/groups/l2/rr.json`（`rr-l2-2`，只有 haiku 一遍）只覆盖 vol01–10 和 vol11–20 的十几格。
只给要用的格补表（不全量批跑）：124 格送审格，加回放中被新规则（`lift_img_ref_veto`）拦下、文意又落空的 35 格。

## 文件
| 文件 | 是什么 |
|---|---|
| `l2/rr.json` | **新表**（`group_clf/1`，ctx_ver 3，ver `rr-l2-2+v2199`）：中心库 rr.json（rev 105995 拉取）＋本轮 159 格。上线时换掉中心库那份 |
| `l2/vol02_99/rrp_*.txt` 等 | 124 格送审格的批（提示词＝cv `config/groups/rr/prompt.md`）、`manifest.json`、`cells.json`、`runs/{haiku,sonnet,opus}/` |
| `l2/vol02_99/extra*/` | 回放中被拦下的 7＋28 格，同上 |
| `labels.jsonl` | 本线程读上下文的判断（`by=claude-a24-rr`，与人裁分开计），每条写了依据词组 |

## 合表规则
同 cv `groups.l2_panel`（haiku 主、opus 强、sonnet 第二）。另外手工处理 5 格（`note` 里写明）：
- vol07:58:9:10、vol09:65:5:20、vol10:78:2:21：旧表 haiku 单遍给错，三模型重判一致，否决后照补字规则改正；
- vol09:94:6:17、vol94:127:4:6：强模型（opus）只有 mid，弃权；
- vol12:147:2:17：窗口键按中心库新码位（喪→䘮）重写。
`strong`：三遍同字、至少两遍 high（只给本轮新判的格；旧表格不动）。cv 新开关 `ctx_over`、`review_fix_strong` 只认 strong。

## 结果
离线回放 70 册（124 格所在各册＋人裁册 vol02 vol05），124 格 放行 102／送审 22；放行与改字 104 格与 `labels.jsonl` 0 不一致、逐格看过图；
人裁标签 59 格放行 0 错。
