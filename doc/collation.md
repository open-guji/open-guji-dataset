# collation 数据格式

## 概述

`collation` 数据集用于评估**参考校对**（模块化路线图第 5.5 部分，见
[modules-roadmap.md](modules-roadmap.md)）：把管线转写与外部参考文本
（整理本）对齐，估计参考质量 ρ，按质量加权注入候选与语言模型，并挖出
分歧点送人工审查。

对应命令：`guji-cv collate <book> --reference <ref>`（**规划中**，
数据集先行）。

参考校对位于自动识别与人工审查之间，处理三种现实情境：

| 情境 | 说明 | 模块行为 |
|------|------|---------|
| A 无参考 | 冷启动 | 退化为直通（ρ̂ = 0 的特例） |
| B 有参考、质量未知 | 常态 | 先估质量，再按质量加权使用 |
| C 有参考、质量高 | 如本项目的整理本 | 强先验 |

## 处理流程

```
转写流（context-correction 之后）+ 参考文本
  ↓
① 对齐：页内 n-gram 锚定 + 局部序列对齐
② 参考质量估计 ρ̂（用自己的高置信槽位作探针，分段估计）
③ 注入候选（权重 ∝ ρ̂ × 对齐置信）与 LM
④ 分歧挖掘 → ref_conflict 审查队列
  ↓
人工审查 / 自动标注闸门（产 align 级标签，回流其他数据集）
```

## 输入与金标（expected.json）

本数据集**不含图片**：样本是冻结的转写流 + 参考文本 + 金标对齐。

```json
{
  "source_item": "06061301.cn",
  "pipeline_version": "…",
  "label_origin": "synth",
  "case_id": "06061301.cn/0042/noise-10",
  "transcript": [
    {"slot_id": "06061301.cn/0042/c03/s07", "top1": "日", "prob": 0.62, "confidence": 0.58}
  ],
  "reference": {
    "text": "…参考文本…",
    "origin": "整理本/卷一",
    "rho": 0.90,
    "noise_injected": 0.10
  },
  "alignment": [
    {"slot_id": "06061301.cn/0042/c03/s07", "ref_index": 231, "ref_char": "曰"}
  ],
  "reference_quality": {
    "rho": 0.90,
    "segments": [{"start": 0, "end": 400, "rho": 0.96}, {"start": 400, "end": 820, "rho": 0.84}]
  },
  "divergences": [
    {"slot_id": "…/s07", "ours": "日", "ref": "曰", "verdict": "ref_right"}
  ]
}
```

### 字段定义

| 字段 | 类型 | 说明 |
|------|------|------|
| `case_id` | str | 样本标识 |
| `transcript` | list | 冻结的转写流：`slot_id` / `top1` / `prob` / `confidence` |
| `reference.text` | str | 参考文本 |
| `reference.origin` | str | 参考来源标识（哪一部整理本、哪一卷） |
| `reference.rho` | float\|null | 参考真实质量。**合成样本才有真值**（= 1 - `noise_injected`） |
| `reference.noise_injected` | float\|null | 注入的替换噪声率 x（0~0.30），非合成样本为 `null` |
| `alignment` | list | 金标对齐：`slot_id` → `ref_index` / `ref_char`；`null` 表示无对应（脱漏 / 衍文） |
| `reference_quality.rho` | float | 整体金标质量 |
| `reference_quality.segments` | list | **分段** ρ：参考可能局部差（某卷换底本、某段脱漏），只报整体会掩盖 |
| `divergences` | list | 金标分歧点：`ours` / `ref` / `verdict` |

### verdict 取值

| 取值 | 说明 |
|------|------|
| `ours_right` | 我们对、参考错——可反哺整理本修订 |
| `ref_right` | 参考对、我们错——难例金矿，回流 char-ocr / char-clustering |
| `both_wrong` | 两边都错——最高价值的人工样本 |

### 合成构造：注入可控噪声

本集**可人造**，这是它区别于其他数据集的地方：拿一段高质量参考，
按替换噪声率 x（x = 0 ~ 30%）随机替换字符，则 ρ = 1 - x 是**已知真值**。
由此可以验证：

1. ρ̂ 的响应曲线是否随 x 单调下降、偏差是否可接受；
2. 候选注入权重（∝ ρ̂ × 对齐置信）是否随质量下降而**平滑退化**——
   高噪声参考不该把正确的转写带偏；
3. x = 1.0（等价情境 A 无参考）时是否退化为直通。

合成样本一律 `label_origin: "synth"`，并填 `reference.noise_injected`。

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
| `alignment_accuracy` | 越高越好 | 槽位→参考字映射与金标对齐一致的比例 |
| `rho_mae` | 越低越好 | 参考质量估计误差 \|ρ̂ - ρ\| 的平均绝对值（合成样本上 ρ 已知） |
| `rho_response_monotonic` | 硬约束 = true | ρ̂ 随注入噪声率单调下降、注入权重随之退化 |
| `divergence_precision` | 越高越好 | 分歧挖掘（我们高置信 ∧ 参考不同）的查准率 |

**字形层纪律**（与 context-correction 同一条硬约束）：参考多为正字化
文本，对齐与注入一律在**语义层**比较；落字形层标签时 surface 由
「本版用字习惯 + 字形库 kNN」决定，定不了就标 `surface_uncertain` 交
人工审查。**参考文本无权改写字形层。**

## 样本目录布局

```
collation/
├── metadata.json
├── samples/
│   ├── 000-example/        # 占位样本（placeholder: true，仅 schema 骨架）
│   ├── 001/
│   │   ├── expected.json
│   │   └── info.json
│   └── …
└── results/                # collate 输出，不入库
```

一个样本 = 一**页或一段**：ρ 是分段量，样本粒度太大会把局部质量差异
平均掉。

## 如何添加样本

1. 新建 `samples/NNN/`（三位数字，从 `001` 起顺序编号）；
2. **真实样本**：冻结该页的转写流与对应参考文本，人工确认对齐与分歧
   裁决（`label_origin: "human"`），`reference.rho` 留 `null`（无真值）；
3. **合成样本**：取高质量参考，按 x 注入替换噪声，填
   `reference.noise_injected: x`、`reference.rho: 1 - x`，
   `label_origin: "synth"`。同一段参考建议做一组 x（如
   0 / 0.05 / 0.10 / 0.20 / 0.30）以画出响应曲线；
4. 写 `expected.json`（含三个溯源字段）与 `info.json`；
5. 更新 `metadata.json` 的 `total_samples` 与 `sources`；
6. 合成样本与真实样本**分开统计**：`rho_mae` 只在合成子集上有定义。
