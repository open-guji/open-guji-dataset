# column-warp / legacy-page-anchor —— 旧输入口径的存档

**这套不再扩充。** 现行口径见上一级目录。

## 它跟现行口径差在哪

差的不是参数，是**链路**：

| | 本目录（legacy） | 现行 `../samples` |
|---|---|---|
| 列的左右边线 | `border-detection` 的**人工金标** `verticals_inner` | `detect_borders()` **算法探测** |
| 矫正窗口上下界 | 整页共用一个标量 `top.y_at(0)`（页面右端锚点） | `page_column_windows()` **逐列**算 |
| 抬头列上界 | 该列 `head_raise.inner_y` | `head_raise.outer_y - 8px` |
| 列图从哪来 | 按样本 `geometry` 现算 | 读 `output/<book>/step2_columns/` 的 PNG |
| 量的是什么 | **Step2 自己**（Step1 误差被隔离） | **Step1+Step2 端到端** |

实测两条链路的边线差 **0.76~27.6px**，列图宽度差到 **38px**（vol01/47 c7）。
不是同一张图，标注不通用。

## 为什么归档而不是删

它仍然回答一个现行口径答不了的问题：**假设 Step1 完全正确，Step2 的收尾算法
有多准**。25 列 / 50 条界上 `column_text_band` 命中走廊 43/50、吃进字身
0.1px 均。跑法跟现行口径一样：

```bash
python scripts/eval_column_warp.py \
    ../open-guji-dataset/char-segmentation/column-warp/legacy-page-anchor
```

`eval_column_warp.rebuild()` 认样本里有没有 `input` 那一块：有就读列图 PNG
（现行），没有就按 `geometry` 现算（本目录）。

## 迁移到现行口径的结果

32 条原始标注**逐条复核**（重算列图、看人标点处的墨占比还是不是 ≤0.01）：

- **17 条可迁**，已写进 `../samples`；
- **15 条失效**（`vol01` 的 9c1 / 33c7 / 47c2,c4,c5,c6,c7,c8 / 137c6 /
  138c4,c5,c6 / 141c2,c3,c4），人标点处的墨占比最高到 0.22，界行整个挪进带里。
  47 那页 9 列失效 7 列——那页算法边线跟金标差最大（19~28px）。
- `border_class`（上下版框类别）**一条都没迁**：类别取决于"窗口裁到哪"，
  而窗口口径正是这次改掉的东西——新窗口故意把主版框线放在列图第 0 行，
  实测上端「没残墨」的列从 24 掉到 6，旧的 `none` 是**被口径作废**的，不是噪声。

值得记的一条：有 2 条（33 c5、137 c5）在上一轮 Step1 重拟竖直线时失效、
在这一轮新输入下**又变有效了**。所以复核要对**全部原始标注**跑，不能只
复核"当前还留在金标里"的那些——只查后者会永久丢掉这 2 条。
