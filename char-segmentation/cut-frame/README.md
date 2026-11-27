# cut-frame：字与框切分评测集（只看列首、列尾字）

归属：CV2（Sheldon 11-26 定切字分两方向：①字间 cut-lattice，②字与框 本集）。只做史記 42、全唐文 053；殿本不动，脉经不做。**只看每列首字、尾字**（上下版框处），左右界行不看（Sheldon 11-26 12:17 PT 定）。

## 量什么
给定第二步切好的格，算法（cell_shrink）给的字紧框：不带框线、不切掉笔画、不带邻字的墨。

## 口径（Sheldon 11-26 确认）
- 紧框＝字的**全部笔画**（含越过内下框的勾），**不含**框线残段（虚线、粗框条）。
- 越过框的字记 `crosses_frame`：评测时不当「带框」，要看补丁里越框的笔画有没有被抹掉。
- 框圈进框线残段记 `frame_residue`（算法框偏大，金标已改成只包字）。
- `truncated_char`（字被截断）不是框的问题，已排除，归字间方向；`invalid_card` 卡本身无字。

## 样本
每书 60 列、列首尾各一张卡（夹注 a/b 各一格）：风险高的 40 列（cell_shrink 在首尾格有 boundary_ink／tail_junk／lost_patch 等标记，或紧框贴着格边），对照 20 列（风险最低的一批里随机）；全唐文另加 053:128:9（QTW 报告，CV1 复核后页边右挪一说撤回）。盲测按列键 sha1 整除 3 余 0。数量见 `counts.json`。

## 字段（items.jsonl 一行一格）
`key`（书:册:页:列:end:slot[:sub]）、`end`（head 列首／tail 列尾）、`kind`、`stratum`（tb 风险／ctl 对照／known）、`split`、`status`（ok／fixed／excluded）、`tight`（金标紧框，excluded 为 null）、`algo_tight`（冻结时算法框）、`tags`。

## 局限
- ok＝人看了没标错，**不是人画框**；几个像素的精度人眼看不出，只保证无明显带框切笔。
- 金标按原图几何存。字格永久编号 u 到位后可再挂 u。
- 样本少（每书 60 列），样本 <20 的错型只报数，不据此调参。

## 评测
`score.py <items.jsonl> <cell_shrink 产物根>`：按格比预测 bbox_page 与金标 tight，报每边偏差、IoU@0.9、越框格数，按书、按 split、按 tags 分报。算法提升另开会话，用 tune 调、blind 只做上线前验证。

## 基线（v0.1，cv dev 现役 cell_shrink，不带人钉；`score.py`）
- 史記 136 格 IoU@0.9 0.985，全唐文 119 格 1.000。
- **这组数是同义反复**：ok 格的金标就是算法框（人只确认没标错），所以只有 fixed 格（史記 4、全唐文 1）有区分力。以后改算法，看的是 fixed 格和翻转格（ok 格改了之后是否仍不带框、不切笔），翻转格要出图人看，不看 IoU 总数。

## 版本
- 0.2.0（11-27）：全唐文 7 个 ok 格（053:28:1、28:8、49:5、77:3、94:1、95:5、116:4 尾字）金标原是旧算法框、带内框线抹后的毛边，换成 cv `cell_shrink.end_dash_row` 的新紧框（Sheldon 人审 28 格全对），tags 加 `rechecked_1127`。
