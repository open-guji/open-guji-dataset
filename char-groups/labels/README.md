# labels/ — 形近字／异体字人裁：统一格式

2026-10-22 起。`unified.jsonl` 把散在 `review/`、`variant/*/`、`variant/pair_review/` 和中心库 `feedback/events` 里的人裁归并成同一格式。
**源文件不动**（它们各自的格式是历史原因）；本目录是汇总视图，由 `build_unified.py` 生成，可反复重跑（幂等）。

    python char-groups/labels/build_unified.py [--events <feedback/events 目录>] [--cv <open-guji-cv 仓>]

`--events` 缺省 `~/.guji-data/main/siku-zongmu/feedback/events`（`guji db pull` 拉下来的中心库人裁事件）。`group_members.json` 由 CV 仓注册表导出
（`--cv` 给了就先重新导出；2026-10-24 为 68 组），不手改。规范总入口：CV 仓 `doc/字组/README.md`。

## 一行一格一种标注

| 字段 | 含义 |
|---|---|
| `id` | `册:页:列:格号`，夹注格号带 `a`/`b`；去掉了 `v2:` 前缀 |
| `book` `page` `col` `slot` | 从 id 拆出 |
| `kind` | `shape` 人裁的**刻形**（图上刻的是哪个字）· `reading` 按**文意**定的字（己已巳、日曰、入人八 的复审页）· `cut` 切线 · `parts` 部件读法（彝上中下） |
| `form` | 人裁结论的字；没定时为 null |
| `status` | `ok` 或页面上的非字结论（`idk` 看不清、`other` 别的字等） |
| `groups` | `form` 属于哪些已注册字组（可多个，如 日／目）；空＝还不在任何已注册组里（备选单上的对，如 往徃、刪删） |
| `by` `date` | 谁、哪天（页面里只有毫秒时间戳的已换算成日期） |
| `src` | 来源：`review:<页>` / `variant:<组>` / `pair_review:<批>` / `central:<批名>` |
| `file` | 源文件（本仓相对路径；`central-events/…` 表示只在中心库，本仓之前没有） |
| `event` | 中心库事件 id（有时） |
| `cut` `parts` `reading` `lib` `ref` `note` | 按 kind 才有：切线、部件、释读、库形／整理本字、备注 |

同一格同一 `kind` 在多个来源出现时合并成一行（2026-10-24 起的规则）：
- 结论取**日期最晚**的一条（同日时中心库事件优先），所以更正写进中心库、重建后就生效；其余来源记在 `also`；
- `verified: {n, agree}`：独立来源数、结论是否一致；
- `corrected_from: [{form, src, date}]`：与最终结论不同的早先结论（被更正过）；
- `in_central`：有没有中心库来源；`central_form`：中心库最新一条与最终结论不同（本仓的更正还没写进中心库，流水线读到的是它）。
中心库事件每条都收（以前只留每格最新一条），`by` 记事件的 `reviewer`。**切线按 sheldon 要求必须存进数据集**：`kind=cut` 的行就是。

## 现状（2026-10-24 重建）

4,600 行：刻形 3,884 · 文意 382 · 切线 247 · 部件 87。多来源 1,814 行，其中来源之间结论不同（被更正过）96 行；结论与中心库不同 7 行。各组明细见 `../status/`。

### 2026-10-22 首次生成时

3,060 行：shape 2,385 · reading 341 · cut 247 · parts 87。其中 **736 行原来只在中心库、本仓没有**，这次补录进来
（主要是 即卽、一二、大太、子于、旨㫖、王玉、木本、論諭、象彖𧰼、曾會㑹、問間、而面、土士、十卜、千干、圓圖、未末 等组在 vol01–03 的人裁）。

按组的 shape+reading 行数见脚本输出；`groups` 为空的约 750 行是还没注册成组的候选对（往徃 160、刪删 116、抵扺 100、衛衞 55、郎郞 等）。

## 没有收进来、要留意

- `*/items.jsonl`（jys、ry、rr）里的金标是**由这些人裁和别的来源派生**出来的评测集，不当原始标注，没有收；它们的人裁来源（`review/*_verdicts`）已收。
- 中心库里的 `confirm` 事件只收了 `actor=user` 且 `payload.shape` 落在已注册字组里的；其余（非字、切分、校勘 `collate_verdict` 等）不是形近字标注，没收。
- 10-17 复审中有 14 格不在 items 里，只在 `review/`，这里收了。
- 判成"非字／看不清"的格 `form` 为 null，`status` 记原因。
- 写中心库事件是另一回事：这里的汇总**不回写**中心库。
