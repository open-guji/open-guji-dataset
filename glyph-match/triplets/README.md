# triplets —— 匹配排序三元组

三元组 = (anchor 本例, same 同字刻例, other 形近异字刻例)。
金标性质：**cov(anchor, same) > cov(anchor, other)**。

## ⚠️ 读数须知：`hard` 的 rank_acc 会随集子变大而**下降**

这个集的 `hard` 档**按定义就是「当前算法排反的那些」**，
所以每次扩集 rank_acc 都会掉——**那是集子变难，不是算法退化**。

| 日期 | hard n | rank_acc | 说明 |
|---|---|---|---|
| 2026-08-24 建集 | 38 | 0.079 | coverage 判据 |
| 2026-08-24 elastic 上线 | 38 | **0.763** | 判据换 elastic（`glyph_match_stack.md` 记的就是这个数）|
| 2026-09-17 实测 | 65 | 0.492 | 集子中途扩过，文档没同步 |
| **2026-09-17 扩集后** | **142** | **0.250** | 新挖 67 条按定义全是排反的 |

**比较只在同一份集子内部有意义**：改判据前后各跑一遍比，别跟历史数字比。
`control`（1.000）与 `nearmiss`（1.000）是护栏，**任何改动都不得让它们回退**。

## 来源

### 一、human 193 条（2026-08-24 首建 ＋ 后续人裁）

字形库体检（`open-guji-cv` 的 `/glyphdb-audit`）出的 rival 案例 ×
审查页人工白名单：用户逐卡确认「本例标签没错，但算法把形近异字排得
比同字还近」——用户实审原话：「明明我看着第一个和第二个更像，你的
匹配率却显示和第三个更匹配」。这 38 条 hard 是**当时算法的已知失败**，
基线 ≈0 是设计使然；60 条 control 是未打旗良例抽样，护栏。
后续由 `add_inversion_triplets.py` / `add_labelconf_triplets.py` 扩充过。

### 二、mined 67 条（2026-09-17，`scripts/mine_hard_triplets.py`）

从字形库直接挖：对每个有 ≥2 刻例的字，`same` 取**同字且不同页**里最像的，
`other` 取异字里最像的（f1 ≥ 0.93）。`--hard-only` 只留当前排反的，
`--no-variants` 剔掉 `other` 是异体字的组。

来源册：vol01 50 / v2 11 / bxgb 6（**北行日錄刻本**——跨册样本，
防止集子只反映四庫一家刻工的风格）。

挖到的字对都是「差一笔或一笔挪位」这类：材/林、杜/柱、崇/祟、壁/璧、
九/丸、子/予、工/王、木/水、八/入、己/已。

⚠️ 这批是**算法挖的，不是人裁的**。标签本身来自库里的 `label`
（四庫那批是整理本对齐 + 人裁，北行那批含 `align` 档），未逐条复核字形。
当靶子用没问题（排序性质由「同字 vs 异字」这个定义保证），
但若某条被反复用来解释算法行为，该单独看一眼图。

## 量法

```bash
cd open-guji-cv
PYTHONPATH=. python scripts/eval_match_triplets.py \
    ../open-guji-dataset/glyph-match/triplets   # --report 逐条
```

图块是**原始灰度 patch**：归一化属于被测算法的一部分，冻结原图才能
让归一化层的改进也被量到。指标 = 各子集排序正确率 + 平均 margin。

## 基线（构建当日，coverage 判据 + hog 特征）

| 子集 | n | rank_acc | mean_margin |
|---|---|---|---|
| hard | 38 | **0.079** | -0.016 |
| control | 60 | 1.000 | +0.068 |

优化纪律：hard 是靶子；**control 不得回退**——为修 hard 把良例改坏
是净亏。改归一化/特征/verify 任何一层都要重跑。

## 扩充

后续每轮体检里新出现的 rival×白名单案例都可回流进来
（`scripts/build_match_triplets_shard.py` 重跑即重建，注意 seed 固定
control 抽样）。anchor 标签均为 human 二次确认。
