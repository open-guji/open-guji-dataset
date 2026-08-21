# char-ocr 数据格式

## 概述

`char-ocr` 数据集用于评估**单字识别**（模块化路线图第 4 部分，见
[modules-roadmap.md](modules-roadmap.md)）：给定一个归一化字块，输出
候选字及概率。样本形式是 (归一化图块, 金标字)，因此该集**可直接用于
Kraken / PaddleOCR 微调**，不只是评测集。

对应命令：`guji-cv label <book> --sources rapidocr,glyph,prior`
（候选生成 + 排序），多引擎对比另见 `guji-cv bench-ocr`。

## 处理流程

```
char-clustering 的簇（同字实例归并）
  ↓
候选生成：prior / rapidocr / vlm / glyph（字形库 kNN）    ← 本数据集评估的步骤
  ↓
上下文纠正（context-correction）
```

## 输入

| 文件 | 说明 |
|------|------|
| `crops/` | 归一化图块目录，文件名即 `instance_id`，与 `items[].crop` 对应 |

## 金标 schema（expected.json）

```json
{
  "source_item": "06061301.cn",
  "pipeline_version": "…",
  "label_origin": "align",
  "shard_id": "06061301.cn/p001-p030",
  "split": "train",
  "items": [
    {
      "instance_id": "06061301.cn/0042/c03/s07",
      "crop": "06061301.cn_0042_c03_s07.png",
      "char": "爻",
      "label_origin": "align",
      "is_variant": false,
      "column_id": "06061301.cn/0042/c03",
      "slot_index": 7
    }
  ]
}
```

### 字段定义

| 字段 | 类型 | 说明 |
|------|------|------|
| `shard_id` | str | 分片标识 |
| `split` | str | `train` / `test`，**按册划分**，见下 |
| `items[].instance_id` | str | 实例标识 |
| `items[].crop` | str | `crops/` 下的图块文件名 |
| `items[].char` | str | 金标字 |
| `items[].label_origin` | str | 可逐条覆盖顶层值 |
| `items[].is_variant` | bool | 是否异体字样本 |
| `items[].column_id` | str | 所属列，供 context-correction 交叉引用 |
| `items[].slot_index` | int | 列内槽位序号 |

### split 必须按册划分

`train` / `test` 的划分单位是**册**（`source_item`），同一册不得跨 split。

理由是实测的：第二册（06061301.cn，卷一，易类）冷启动准确率 82.07%，
卷首册 84.16%——跨册稳定，但**混淆分布差异极大**。卷一的混淆头部全是
易学专名：日→曰、益→葢、交→爻、解→辭、象→彖、繁→繫。这些领域高频字
是 OCR 字表与语料先验的系统盲区。按实例随机切分会让同册的这些字同时
出现在 train 和 test 里，测出来的是记忆而不是泛化。

### 异体字全留不采样

`is_variant: true` 的样本**不参与降采样**：异体字本来就稀少，采样会
把它们抹平。这类样本单独报告 `variant_top1`。

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
| `top1` | 越高越好 | top-1 命中率，**须按 `label_origin` 分层报告** |
| `top5` | 越高越好 | top-5 命中率，衡量候选召回上限（决定下游纠正的天花板） |
| `variant_top1` | 越高越好 | 异体字子集的 top-1，单独报告 |

**为什么必须分层**：align 标签的错误会同时污染训练与评测。若不分层，
在 align 噪声上过拟合的模型会拿到虚高的 top-1，而在 human 子集上原地
踏步——这正是 `label_origin` 存在的意义。

## 样本目录布局

```
char-ocr/
├── metadata.json
├── samples/
│   ├── 000-example/        # 占位样本（placeholder: true，仅 schema 骨架）
│   ├── 001/
│   │   ├── crops/
│   │   ├── expected.json
│   │   └── info.json
│   └── …
└── results/                # label / bench-ocr 输出，不入库
```

一个样本 = 一个**册分片**（一批 (图块, 金标字) 对）。不给每个字建一个
目录：字级样本量在 20 万+ 量级，逐字建目录不可维护。

## 如何添加样本

1. 新建 `samples/NNN/`（三位数字，从 `001` 起顺序编号）；
2. 导出归一化图块到 `crops/`；
3. 由整理本对齐闸门产出 `items`（对齐置信高 ∧ ρ̂ 高 ∧ top1==ref 或
   ref 在候选中且概率不低 → `label_origin: "align"`），人工裁决过的
   改为 `"human"`；
4. 显式填 `split`：同一 `source_item` 的所有分片必须同属一个 split；
5. 标注 `is_variant`：异体字映射表见 open-guji-cv `config/dicts/variants.tsv`；
6. 写 `expected.json`（含三个溯源字段）与 `info.json`；
7. 更新 `metadata.json` 的 `total_samples` 与 `sources`（按册记录计数与 split）。
