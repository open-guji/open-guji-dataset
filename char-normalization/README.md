# char-normalization —— 归一化 golden 回归（双层）

## 测什么

**切出来的原始字块 → 去残余、居中缩放、笔宽归一，得到 64×64 二值字形图。**

归一化是**纯函数**，本集是**回归门**：任一 verified 样本超出容差就算失败。

## 双层结构（2026-08 起）

上游切分做不到完美（正文页无标记率 vol01 78.9% / vol02 68.2%，管线手册 §1），
图块天然分两类，算法目标相应分两档，评测**必须**分开报：

| tier | 定义 | 对算法的要求 | 本集样本 |
|---|---|---|---|
| `clean` | 字完整、无外来残留 | **必须做得非常好**：缺陷零容忍，出现即 P0 | 19（缺陷 0）|
| `degraded` | 有邻字/界行残留，或本字被切 | 能不崩、残留尽量去掉；缺陷记账、按优先级修 | 13（缺陷 4）|

分层判据是 `open-guji-cv` 的 `crop_quality.assess_crop`：在**原始图块**上用
Otsu + 连通体结构量「完整性 / 残留」——

- `truncated`：主体连通体压图块外边界的墨 ≥14px（图块 = bbox + padding，
  完整的字连 padding 都不该穿透）；
- `residue`：**碰到图块边界且闯进核心区**（bbox 内）≥25px 的非主体连通体。
  两个条件缺一不可：只在 padding 带待着的邻字是常态；核心区里的非主体
  连通体多半是**本字自己的部件**（汉字本来就是多连通体的：門、百、卷…）。

判据对 [char-segmentation/instances](../char-segmentation/instances) 人工
quality 标签（第九轮 62 实例）校准：缺陷检出 5/7、clean 误报 2/55；漏掉的
两类是几何盲区（污染整体落在 bbox 内不碰边 / 图内自洽的截断），本集靠
**逐张目视**兜底——机器分级只是抽样线索，最终 tier 以目视为准
（`TIER_OVERRIDE` 记录改判，本轮 2 个：本字部件不连通又压边被误判残留）。

## verified / known_defect 两种状态（与 tier 正交）

golden = 当前归一化输出**逐张目视确认后**冻结。输出本身就错的绝不冻成
golden（那等于把缺陷焊死），改进 `known_defect` 层只记录行为、不进门。
目视发现**不是字**的样本直接剔除（本轮 3 个：四残字拼一格、版框横线块、
空格残迹——它们该由页型/切分层拦住，不该测归一化）。

## 抽样（每册对半，全部取自 page-type 金标 body 页）

| tier | 线索 | 数量 | 说明 |
|---|---|---|---|
| clean | `typical` | 6 | 无 flag、ink_ratio 0.10~0.22、机器分级 clean |
| clean | `ink_heavy` / `ink_light` | 5+6 | **墨迹像素平均灰度**两极（Otsu 分墨；`ink_ratio` 量到的是笔画数、最暗 15% 均值混进背景，都踩过坑）|
| degraded | `residue` | 5 | 机器判残留，按核心区残留墨量降序 |
| degraded | `truncated` | 5 | 机器判截断，按压边墨量降序 |
| degraded | `flagged` | 3 | extractor 确定层 flag（与 crop_quality 不同源的第二条线索）|
| degraded | `human_contaminated` | 2 | instances 人工缺陷标签（最硬的线索）|

## 基线（2026-08-23，pipeline 869f235 = P0 修复后的新切分）

```
回归门：28/28 通过
  [clean]    19 样本：verified 19  known_defect 0
  [degraded] 13 样本：verified 9   known_defect 4
已知缺陷层：4/4 行为未变
```

四个已知缺陷（全在退化层，共同点：**残留不贴图块边缘时
`remove_edge_specks` 完全够不着**——它只删贴边组件）：

| 样本 | 缺陷 |
|---|---|
| [022](samples/022) | 邻列字残片（左缘一条竖向笔画带）未去 |
| [026](samples/026) | 版框横线横穿图块**中部**（不贴上下边），未去 |
| [032](samples/032) | 底部横线残留未去（疑与「重」底横粘连）|
| [033](samples/033) | 邻字「一」整笔在图块下部核心区内，未去 |

上一版（旧切分）的 024 号缺陷——「界行竖线内缩 7px 漏网」——是同一个
根因的另一面：**贴边判据太字面**。修法大概率是一条：把「贴边」放宽成
「细长且主体在边缘带内」。

## 三个指标各管一件事

| 指标 | 容差 | 抓什么 |
|---|---|---|
| `pixel_diff_ratio` | ≤ 0.01 | 任何像素级改动 |
| `binary_iou` | ≥ 0.98 | 墨迹整体位置/大小（容忍抗锯齿边缘）|
| `skeleton_endpoint_delta` | ≤ 2 | 拓扑：断笔与虚连——断一笔只改几十个像素，只有它接得住 |

## 怎么跑

```bash
cd open-guji-cv
python scripts/eval_normalize.py ../open-guji-dataset/char-normalization
# 退出码非 0 = 回归门失败；报告按 tier 分层
```

重建（归一化**有意**改动后必须逐张重看再冻结；上游切分重跑后也必须
重建——本集样本取自工作区当前 output/，`pipeline_version` 记录版本）：

```bash
python scripts/build_normalization_dataset.py --dataset ../open-guji-dataset/char-normalization
```

## known_limitation

1. **回归门只保证「没变」，不保证「对」**——golden 是目视确认过的当前输出。
2. **断笔（broken_stroke）类没有确诊样本**：墨淡线索挑出的字没有明显断笔，
   「断笔容忍」这条能力仍未验证过。
3. 只覆盖两册同一版（武英殿刻本）；换版换刻工的墨色分布管不到。
4. `known_defect` 层不进门：缺陷修好时门不变红，报告里会出现「行为变了」，
   看到要去更新 golden 与 build 脚本的 `VERDICTS`。
5. **粘连盲区**：残留与本字笔画粘连时（样本 032），分级判据与去残余算法
   同时失效——这类只能靠人工。
6. clean 层 19 个样本没有一个出缺陷，是在**当前切分**上抽的；切分再变，
   clean 层要重抽重验（样本取自工作区 output/，与 `pipeline_version` 绑定）。
