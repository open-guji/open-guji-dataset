# context-correction 数据格式

## 概述

`context-correction` 数据集用于评估**上下文 + LM 概率纠正**（模块化
路线图第 5 部分，见 [modules-roadmap.md](modules-roadmap.md)）：给定
一列的上下文与每个槽位的候选字及概率，用语言模型重排候选。

对应命令：`guji-cv refine <book> --corpus <本书语料> --general-corpus
<通用古文语料> --general-weight 0.1 --lam 0.65`。

**建集与评测（open-guji-cv 侧，成对提交）**

```bash
PYTHONPATH=. python scripts/build_context_correction_dataset.py output/book9 \
    --corpus corpus/zongmu_wuyingdian_reference.txt --dataset ../open-guji-dataset
PYTHONPATH=. python scripts/eval_context_correction.py \
    ../open-guji-dataset/context-correction \
    --general-corpus corpus/external/daizhige_zhaoling.txt \
    --book-corpus corpus/zongmu_wuyingdian_reference.txt \
    --sweep 0,0.25,0.5,0.75,0.9,1.0 --lam 0.65
```

样本里的**候选是冻结的**：本集测的是纠正层，不是 OCR 层。上游 OCR
一变指标就不可比，所以候选列表连同概率一起存进样本。

## 处理流程

```
char-ocr 的候选（字 + 概率 + 来源）
  ↓
冻结进样本                                ← 本数据集的输入
  ↓
guji-cv refine（簇级边缘化 + n-gram / 外部语料）   ← 本数据集评估的步骤
  ↓
参考校对（collation）/ 人工审查
```

## 输入与金标（expected.json）

本数据集**不含图片**，输入与金标都在 `expected.json` 里：

一个 `expected.json` = 一**页**，页内所有列放在 `columns` 数组里
（schema_version 2；框架期的骨架是一列一个文件，但一册就有几百列，
逐列建目录不可维护）。列本身的字段一个没变。

```json
{
  "source_item": "book9",
  "pipeline_version": "…",
  "label_origin": "align",
  "page": "10",
  "corpus": "corpus/zongmu_wuyingdian_reference.txt",
  "columns": [{
   "column_id": "book9:10:3",
   "context": {"prev": "…前一列金标文本…", "next": "…后一列金标文本…"},
   "slots": [
    {
      "index": 7,
      "candidates": [
        {"char": "日", "prob": 0.62, "source": "rapidocr"},
        {"char": "曰", "prob": 0.31, "source": "glyph"},
        {"char": "白", "prob": 0.07, "source": "prior"}
      ],
      "gold": "曰",
      "frozen": true,
      "instance_id": "book9:10:3:7",
      "cluster_id": "c00123",
      "cluster_size": 4
    }
   ]
  }]
}
```

### 字段定义

| 字段 | 类型 | 说明 |
|------|------|------|
| `column_id` | str | 列标识（`source_item` + 页 + 列序） |
| `corpus` | str\|null | 评测所用语料标识（open-guji-cv `corpus/`），随样本记录以保证可复现 |
| `context.prev` / `next` | str | 相邻列的**金标**文本，即「相邻列已确认好」的理想情形 |
| `slots[].instance_id` | str | 对应的图块实例，可与 char-ocr 交叉引用 |
| `slots[].cluster_id` / `cluster_size` | str / int | 所属簇，供簇级边缘化使用 |

### `context` 取金标是上界口径

真实流程里相邻列同样带错，本集给的是**理想上下文**。这样取是为了隔离
纠正算法本身的能力；「相邻列也带噪」是另一个问题，要另建集或另加一档。
所以本集的 `top1_gain` **不能**直接当作全书能拿到的增益。
| `slots[].index` | int | 列内槽位序号 |
| `slots[].candidates` | list | **冻结**的候选列表 |
| `candidates[].char` | str | 候选字 |
| `candidates[].prob` | float | 候选概率（同槽位归一） |
| `candidates[].source` | str | 候选来源：`prior` / `ocr` / `rapidocr` / `vlm` / `glyph` / `ref` |
| `slots[].gold` | str | 该槽位金标字 |
| `slots[].frozen` | bool | 恒为 `true`，标明候选不可由评测流程重新生成 |

### 字形层不可被语义层改写（硬约束）

这是**测试断言**，不是软指标。纠正层只允许在**候选集合内重排**：

- 不得引入候选列表之外的字；
- 不得修改字形层的 surface（本版实际用字）。

理由：参考文本与语料多为**正字化**文本，语义层的偏好会把本版的异体
用字"改正"掉，破坏字形库的真实性。语义层的产出是**读法**，字形层的
产出才是**这一版刻的是什么字**。评测脚本必须对每个被改动的槽位断言
新 top-1 仍在原候选集合内，违反即失败。

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
| `baseline_top1` | 参照 | 冻结候选的 top-1 基线（不做纠正） |
| `top1_gain` | 越高越好 | 纠正后 top-1 相对基线的**绝对提升**，本集主指标 |
| `harmful_flip_rate` | 越低越好 | 把原本正确的槽位改错的比例 |
| `glyph_layer_immutability` | 硬约束 = true | 字形层未被语义层改写的断言 |

`top1_gain` 必须与 `harmful_flip_rate` 一起看：净收益为正但有害翻转很高，
说明纠正过于激进——实测中同书自举 n-gram 在缺乏外部语料时净有害，
正是这样暴露出来的。

另外两个必看的量（建集时打印，写在 `info.json` / `report.json`）：

- `gold_in_candidates_rate`（本集 94.52%）：金标根本不在候选里的部分，
  **重排永远碰不到**，那是候选召回的问题；
- `headroom`（本集 5.20%）：金标在候选里但不是首选的比例 —— 重排能拿到
  的**全部**空间。报增益时要说清占了 headroom 的几成，否则 +2% 听起来
  像小改进，实际已经吃掉四成可用空间。

### 本书语料必须留出测试页

本书语料就是本书的整理本，测试页的金标也是从同一份整理本对齐来的。
不挖掉就是**背答案**。评测脚本会先把每个测试页的金标窗口（前后各多挖
200 字）从语料里剔除再训练，并打印挖掉了多少字；打印为 0 就说明挖漏了，
后面的数字一概不可信。通用语料同样要查泄漏：脚本会打印通用语料与测试页
金标的 8-gram 重合率（当前配置为 0.0）。

## 样本目录布局

```
context-correction/
├── metadata.json
├── samples/
│   ├── 000-example/        # 占位样本（placeholder: true，仅 schema 骨架）
│   ├── 001/
│   │   ├── expected.json
│   │   └── info.json
│   └── …
└── results/                # refine 输出，不入库
```

一个样本 = 一**页**（目录名 `<册>_<页>`），页内所有列在 `columns` 里。
纠正的作用域仍是列，跨列上下文由 `context.prev` / `next` 提供。

## 如何添加样本

1. 跑 `scripts/build_context_correction_dataset.py`，它会为每个锚定成功
   的页建一个 `samples/<册>_<页>/`；
2. 候选从 `phase6_labels/candidates.json` **原样冻结**进
   `slots[].candidates`，不要重新归一或裁剪；
3. 金标 `gold` 由整理本对齐给出（`label_origin: "align"`），分歧点
   人工裁决后改 `"human"`；
4. 记录 `corpus`：换语料等于换实验条件，不记录则结果不可比；
5. 写 `expected.json`（含三个溯源字段）与 `info.json`；
6. 更新 `metadata.json` 的 `total_samples` 与 `sources`；
7. 优先收录**难列**：候选 top-1 与 gold 不一致、或候选概率接近的列。
   全对的列对本集没有信息量。
