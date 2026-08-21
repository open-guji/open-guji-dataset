# char-clustering 数据格式

## 概述

`char-clustering` 数据集用于评估**保守聚类**（模块化路线图第 3b 部分，
见 [modules-roadmap.md](modules-roadmap.md)）：把一册的归一化字块按字形
合并成簇，同一个字尽量进同一簇，**但绝不允许不同字混进一簇**。

对应命令：`guji-cv cluster <book> --feature hog`。

保守聚类的取向是**宁可碎，不可脏**：脏簇会把错误标签批量扩散到整簇
实例，碎簇只是多花人工审查成本。因此 purity 是硬约束，fragmentation
只在 purity 达标的前提下才有意义。

## 处理流程

```
char-normalization 的归一化字块
  ↓
特征（hog / raw）
  ↓
guji-cv cluster        ← 本数据集评估的步骤
  ↓
簇识别 OCR（char-ocr）
```

## 输入

| 文件 | 说明 |
|------|------|
| `crops/` | 归一化后的字块图目录，文件名即 `instance_id` |
| `features.npz` | 可选：冻结的特征矩阵 |

> 冻结特征的理由：3b 的质量几乎完全由 3a 归一化决定。若归一化改动后
> 直接重跑聚类，指标变化分不清是聚类还是归一化引起的。要单独评测
> 聚类，就把特征冻结；要端到端评测，就同时记录 `pipeline_version`。

## 金标 schema（expected.json）

```json
{
  "source_item": "06061301.cn",
  "pipeline_version": "…",
  "label_origin": "align",
  "shard_id": "06061301.cn/p001-p030",
  "feature_backend": "hog",
  "instances": [
    {"instance_id": "06061301.cn/0042/c03/s07", "char": "曰", "label_origin": "align"},
    {"instance_id": "06061301.cn/0043/c01/s02", "char": "日", "label_origin": "human"}
  ],
  "hard_pairs": [
    {"a": "…/s07", "b": "…/s02", "relation": "diff", "origin": "human"}
  ]
}
```

### 字段定义

| 字段 | 类型 | 说明 |
|------|------|------|
| `shard_id` | str | 分片标识（同一册内的一批实例） |
| `feature_backend` | str | 冻结的特征后端（如 `hog`），保证可复现 |
| `instances` | list | 实例→字标签映射 |
| `instances[].instance_id` | str | 实例标识，与 `crops/` 文件名对应 |
| `instances[].char` | str | 金标字（**语义层**字，字形层差异见下） |
| `instances[].label_origin` | str | 可逐实例覆盖顶层值：同一分片里 align 与 human 标签常常混杂 |
| `hard_pairs` | list | 难例对，单独报告 |
| `hard_pairs[].relation` | str | `same`（应同簇）/ `diff`（不可同簇） |
| `hard_pairs[].origin` | str | 该对的来源，一般是人工 `impure` / `split` 反馈事件 |

### 难例对（hard_pairs）

来自第 6 部分人工审查的两类反馈：

| 反馈 | 产生的对 | 含义 |
|------|---------|------|
| `impure`（簇里混了别的字） | `diff` | 这两个实例**不得**再进同一簇 |
| `split`（同一个字被拆成多簇） | `same` | 这两个实例**应当**合并 |

难例对准确率单独报告：它们是分布外的困难样本，混进总体 purity 会
掩盖真实进展。

## 溯源字段（必填）

每份 `expected.json` 顶层必须含三个溯源字段，缺一不可：

| 字段 | 类型 | 说明 |
|------|------|------|
| `source_item` | str | 来源册标识（如 `06061301.cn`） |
| `pipeline_version` | str | 生成该样本时 open-guji-cv 的版本 / commit |
| `label_origin` | str | 标注来源：`align` / `human` / `synth` |

| `label_origin` | 含义 |
|------|------|
| `align` | 整理本对齐自动标注（页内 n-gram 锚定 + 局部序列对齐，取高置信页） |
| `human` | 人工标注，或人工审查确认过 |
| `synth` | 合成 / 注入噪声构造 |

**为什么不可省略**：手工逐字标注不可持续，规模化标注只能来自整理本
对齐（整理本覆盖卷首~卷 27 约前 11 册，估计可自动标出 20 万+ 字级样本）。
但 align 标注**有噪声**——对齐错位、参考本与底本用字不同、参考本自身
讹误都会混进标签。没有 `label_origin` 就无法：

1. **清洗**：发现某批系统性错误时，按来源批量回滚或重标；
2. **分层评测**：align 与 human 子集必须分开报告，否则指标被噪声标签
   污染，模型在噪声上过拟合也看不出来；
3. **加权使用**：human > align > synth 的可信度差异要能表达。

`source_item` 另外支撑**按册划分** train/test（分册混淆分布差异很大，
跨册泛化是真实需求）；`pipeline_version` 支撑管线升级后判断哪些样本
需要重新生成。


## 指标

| 指标 | 方向 | 说明 |
|------|------|------|
| `purity` | **硬约束 >= 0.999** | 簇内同字比例（按簇大小加权平均） |
| `fragmentation` | 越低越好 | 簇数 / 金标字类数；仅在 purity 达标时有意义 |
| `hard_pair_accuracy` | 越高越好 | 难例对 same/diff 判定准确率，单独报告 |

**分层报告**：purity 必须按 `label_origin` 分层——align 标签本身有噪声，
用它算出的 purity 天然带一个误差底噪；human 子集上的 purity 才是可以
当硬约束卡的那个数。

open-guji-cv 的合成 bench（`guji-cv bench`）保留作冒烟测试，本集是真实
数据上的 purity 集，两者不互相替代。

## 样本目录布局

```
char-clustering/
├── metadata.json
├── samples/
│   ├── 000-example/        # 占位样本（placeholder: true，仅 schema 骨架）
│   ├── 001/
│   │   ├── crops/
│   │   ├── features.npz    # 可选
│   │   ├── expected.json
│   │   └── info.json
│   └── …
└── results/                # cluster 输出，不入库
```

一个样本 = 一个**册分片**（同册的一批实例），不是单个字块：聚类指标
只有在成批实例上才有定义。

## 如何添加样本

1. 新建 `samples/NNN/`（三位数字，从 `001` 起顺序编号）；
2. 导出该分片的归一化字块到 `crops/`，文件名用 `instance_id`；
3. 用整理本对齐产出 `instances` 的字标签草稿（`label_origin: "align"`），
   人工审过的实例改为 `"human"`；
4. 从人工审查的 `impure` / `split` 事件导出 `hard_pairs`；
5. 写 `expected.json`（含三个溯源字段与 `feature_backend`）与 `info.json`；
6. 更新 `metadata.json` 的 `total_samples` 与 `sources`；
7. 一个分片只放**同一册**的实例：跨册字形差异是另一个问题（刻工差异
   真实存在，如同版不同册格高 113.8px vs 110.6px），别混进 purity。
