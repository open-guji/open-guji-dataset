# char-normalization 数据格式

## 概述

`char-normalization` 数据集是**归一化 golden 集**（模块化路线图第 3a 部分，
见 [modules-roadmap.md](modules-roadmap.md)）：把切出的原始字块去边框残余、
去邻字侵入、笔画宽度归一并骨架化。

归一化是**纯函数**——同样的输入必须得到同样的输出，因此本集用 golden
图对做逐像素 / 容差回归，而不是统计指标。

> 3b 聚类的质量几乎完全由 3a 决定（实测：骨架化使同字 F1 从 0.4~0.6
> 提升到 0.63~0.93）。所以这一层的回归必须是像素级的。
>
> 骨架是**匹配特征**，不是存储格式：字形库的真源永远是原始图。

## 处理流程

```
char-segmentation 切出的原始字块
  ↓
normalize（去残余 / 笔画归一 / 骨架化）    ← 本数据集回归的纯函数
  ↓
char-clustering（特征与聚类）
```

## 输入与金标

| 文件 | 角色 | 说明 |
|------|------|------|
| `input.png` | 输入 | 原始字块图（segment 直接切出，未处理） |
| `golden.png` | 金标 | 期望的归一化输出，人工确认后冻结 |
| `golden_skeleton.png` | 金标 | 期望的骨架输出 |

## 金标 schema（expected.json）

```json
{
  "source_item": "06061301.cn",
  "pipeline_version": "…",
  "label_origin": "human",
  "instance_id": "06061301.cn/0042/c03/s07",
  "input": "input.png",
  "golden": "golden.png",
  "golden_skeleton": "golden_skeleton.png",
  "tolerance": {"pixel_diff_ratio": 0.01, "binary_iou_min": 0.98},
  "cover": ["border_residue", "ink_heavy"],
  "char": "曰"
}
```

### 字段定义

| 字段 | 类型 | 说明 |
|------|------|------|
| `instance_id` | str | 字块实例标识（来自 `phase4_chars` / `glyph_store`） |
| `input` | str | 原始图块文件名 |
| `golden` | str | 期望归一化图文件名 |
| `golden_skeleton` | str | 期望骨架图文件名 |
| `tolerance` | object | 容差：`pixel_diff_ratio` 上限、`binary_iou_min` 下限 |
| `cover` | list[str] | 该样本覆盖的难点类别，见下表 |
| `char` | str\|null | 该字块对应的字，可选，仅供人工检视，不参与本集指标 |

### cover — 覆盖类别

| 取值 | 说明 |
|------|------|
| `ink_heavy` | 墨重（笔画粘连、字口糊） |
| `ink_light` | 墨淡（笔画断续、灰阶弱） |
| `border_residue` | 边框残余（栏线、鱼尾切进图块） |
| `neighbor_intrusion` | 邻字侵入（上下左右邻字的残笔） |
| `broken_stroke` | 断笔（原刻或扫描导致的笔画断裂） |

每类应有若干组样本；`metadata.json` 的 `sources` 记录各类计数。

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
| `pixel_diff_ratio` | 越低越好 | 输出与 golden 逐像素不一致比例，须 <= `tolerance.pixel_diff_ratio` |
| `binary_iou` | 越高越好 | 二值前景 IoU，容忍抗锯齿边缘的细微差异 |
| `skeleton_endpoint_delta` | 越低越好 | 骨架端点 / 交叉点数量差，捕捉断笔与虚连回归 |

任一样本超出容差即判回归失败——本集是**回归门**，不是排行榜。

## 样本目录布局

```
char-normalization/
├── metadata.json
├── samples/
│   ├── 000-example/        # 占位样本（placeholder: true，仅 schema 骨架）
│   ├── 001/
│   │   ├── input.png
│   │   ├── golden.png
│   │   ├── golden_skeleton.png
│   │   ├── expected.json
│   │   └── info.json
│   └── …
└── results/                # 归一化输出，不入库
```

## 如何添加样本

1. 新建 `samples/NNN/`（三位数字，从 `001` 起顺序编号）；
2. 放入 `input.png`；跑一次当前归一化得到候选输出，**人工逐张确认**
   后另存为 `golden.png` / `golden_skeleton.png`——未经确认的输出不能当金标；
3. 写 `expected.json`：文件名映射、容差、`cover` 类别、三个溯源字段。
   人工确认的 golden 一律 `label_origin: "human"`；
4. 写 `info.json`（`id` / `source` / `source_item` / `description` / `tags`）；
5. 更新 `metadata.json` 的 `total_samples` 与 `sources`；
6. 归一化算法**有意**改动时，重新生成并人工复核受影响的 golden，
   同时更新样本的 `pipeline_version`。
