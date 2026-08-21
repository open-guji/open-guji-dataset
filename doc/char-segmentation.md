# char-segmentation 数据格式

## 概述

`char-segmentation` 数据集用于评估**单字分拆**（模块化路线图第 2 部分，
见 [modules-roadmap.md](modules-roadmap.md)）：把预处理后的半页图按刻本
栏格切成逐字 cell，要求不含边框、不含邻字残余，并正确处理职名拉开等
特殊排布。

对应命令：`guji-cv segment <book>`（刻本严格网格切分，输出
`<page>_char_grid.json`）。

## 处理流程

```
页图（book-profile / cut-page 之后的预处理产物）
  ↓
书级网格参数估计（格高共识、行相位、每列字数）   ← 接口的一部分，随样本冻结
  ↓
guji-cv segment        ← 本数据集评估的步骤
  ↓
逐字 cell 框 → 归一化（char-normalization）
```

## 输入

每个样本的输入有两份，**都要冻结**：

| 文件 | 说明 |
|------|------|
| `image.png` | 预处理后的半页页图 |
| `input.json` | 列带（每列 left_x / right_x）+ 书级网格参数包（cell_height / phase / chars_per_line） |

> **为什么书级参数属于输入**：格高与行相位是**书级量**，纯页内拟合在
> 稀疏页欠定（目录页、卷端页只有几个字，页内投影周期不可辨）。第 1/2
> 部分之间的接口就是「页几何 + 列带 + 书级网格参数包」，不把它冻结进
> 样本，评测结果不可复现。

## 金标 schema（expected.json）

```json
{
  "source_item": "06061301.cn",
  "pipeline_version": "…",
  "label_origin": "align",
  "page_id": "0042",
  "image_size": {"width": 1200, "height": 1800},
  "chars_per_line": 21,
  "book_grid": {"cell_height": 110.6, "phase": 0.03},
  "columns": [
    {
      "index": 0, "left_x": 96.0, "right_x": 208.0,
      "cells": [
        {"type": "char",  "index": 0, "y_top": 12.0,  "y_bottom": 122.6},
        {"type": "empty", "index": 1, "y_top": 122.6, "y_bottom": 233.2}
      ]
    }
  ],
  "special_layout": ["raised_head"],
  "negatives": [{"instance_id": "…", "flag": "truncated"}]
}
```

### 字段定义

| 字段 | 类型 | 说明 |
|------|------|------|
| `page_id` | str | 页标识，与 `image.png` 同名 stem |
| `image_size` | object | 页图尺寸 `width` / `height` |
| `chars_per_line` | int | 该页每列格位数（含空格位） |
| `book_grid` | object | 书级网格参数：`cell_height` 格高共识、`phase` 行相位 |
| `columns` | list | 列带列表 |
| `columns[].index` | int | 列序（从右到左，与 segment 输出一致） |
| `columns[].left_x` / `right_x` | float | 列带左右边界（页坐标） |
| `columns[].cells` | list | 该列格位列表 |
| `cells[].type` | str | `char`（有字）/ `empty`（空格位）。`margin` 型不入金标 |
| `cells[].index` | int | 格位序号（0 起，含空格位，用于每列字数守恒校验） |
| `cells[].y_top` / `y_bottom` | float | 格位上下边界（**列内局部坐标**，与 segment 输出一致） |
| `special_layout` | list[str] | 特殊排布标记，见下表 |
| `negatives` | list | 人工审查 flag 的负例实例，用于回归测试 |

### special_layout 取值

| 取值 | 说明 |
|------|------|
| `spread_column` | **职名拉开**：官衔名列字距被拉开（实测 3.4~3.7 格，**非整数倍**），刚性网格会错格 |
| `sparse_toc` | **目录稀疏列**：一列只有寥寥数字，页内周期证据不足 |
| `raised_head` | **卷端抬头空格**：列首留空占格位但无墨，按内容范围锚定会整体错一格 |

这三种排布是**必测**项：它们是刚性网格模型最容易失效的位置，任何
样本集都应保证覆盖。

### negatives — 负例集

来自 open-guji-cv 第 6 部分（人工审查）的 flag 事件，目前已积累约 500 例：

| flag | 说明 |
|------|------|
| `truncated` | 字被格线切断 |
| `contaminated` | 混入邻字残笔或边框残余 |
| `not_text` | 根本不是字（栏线、污渍、鱼尾） |

**回归约定**：修复后这些实例不得再现，`negative_recurrence` 指标硬约束为 0。

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
| `straddle_ratio` | 越低越好 | 骑线比 = 格线处墨量 / 格心处墨量，衡量格线是否压在笔画上 |
| `cell_iou` | 越高越好 | 预测 cell 与金标 cell 的纵向 IoU（按 `index` 对齐后平均） |
| `chars_per_column_conservation` | 越高越好 | 每列 `char` 型 cell 数与对齐参考列字数一致的列占比 |
| `negative_recurrence` | 硬约束 = 0 | 负例集中再次出现的实例数 |

## 样本目录布局

```
char-segmentation/
├── metadata.json
├── samples/
│   ├── 000-example/        # 占位样本（placeholder: true，仅 schema 骨架）
│   ├── 001/
│   │   ├── image.png
│   │   ├── input.json
│   │   ├── expected.json
│   │   └── info.json
│   └── …
└── results/                # segment 输出，不入库
```

## 如何添加样本

1. 新建 `samples/NNN/`（三位数字，从 `001` 起顺序编号）；
2. 放入 `image.png`（预处理后的半页图）与 `input.json`（列带 + 书级网格参数包）；
3. 写 `expected.json`：先用 `guji-cv segment` 产出 `<page>_char_grid.json`
   作草稿，再人工订正 cell 边界与 `char`/`empty` 判定；
4. 写 `info.json`：`id` / `source` / `source_item` / `description` / `tags`；
   非占位样本不要写 `placeholder` 字段（或写 `false`）；
5. 顶层三个溯源字段必填。对齐自动标注写 `align`，人工订正过的写 `human`；
6. 更新 `metadata.json` 的 `total_samples` 与 `sources`；
7. 覆盖度检查：`special_layout` 三类特殊排布应各有样本。
