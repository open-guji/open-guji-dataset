# triplets —— 匹配排序三元组

三元组 = (anchor 本例, same 同字刻例, other 形近异字刻例)。
金标性质：**cov(anchor, same) > cov(anchor, other)**。

## 来源（2026-08-24 首建）

字形库体检（`open-guji-cv` 的 `/glyphdb-audit`）出的 rival 案例 ×
审查页人工白名单：用户逐卡确认「本例标签没错，但算法把形近异字排得
比同字还近」——用户实审原话：「明明我看着第一个和第二个更像，你的
匹配率却显示和第三个更匹配」。这 38 条 hard 是**当时算法的已知失败**，
基线 ≈0 是设计使然；60 条 control 是未打旗良例抽样，护栏。

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
