# char-ocr —— 单字识别测试集

**一句话**：1,404 条 (冻结图块, 参考整理本金标字)，用来量「这一块图上是
哪个字」。格式说明见 [../doc/char-ocr.md](../doc/char-ocr.md)。

| | |
|---|---|
| 样本 | 1,404 条，来自 book9（《欽定四庫全書總目·卷首一》10 页）|
| 金标来源 | `align` —— 参考整理本对齐，**取值与任何 OCR 引擎无关** |
| 覆盖 | 9/10 页锚定；1,647 个实例里进集 1,404 条（85.2%）|
| 冻结 | 图块像素已拷进 `samples/*/crops/`，本集不随切分漂移 |
| 主指标 | `top1` / `top5` / `charset_ceiling`（三者必须一起读）|

## 当前基线（2026-08-23）

| 引擎 | top1 | top5 | 字表可达上界 |
|---|---|---|---|
| rapidocr + 简→繁扩展 | **88.75%** (1246/1404) | 94.02% (1320/1404) | 99.29% |
| rapidocr（关掉 s2t）| 82.91% (1164/1404) | 90.17% (1266/1404) | 99.29% |
| tesseract:chi_tra | 44.59% (626/1404) | — | — |

简→繁扩展值 **+5.84pp**：PP-OCR 是简体模型，繁体刻本上没有它就系统性
输出简体。

### 分层

| 分层 | n | rapidocr+s2t | tesseract |
|---|---|---|---|
| `opcode:equal`（建集时转写就对）| 1254 | 99.36% | 47.77% |
| `opcode:replace`（建集时转写错了）| 150 | **0.00%** | **18.00%** |
| `variant`（非本版常用表面形）| 15 | 53.33% | 26.67% |

`replace` 层上 rapidocr 恒为 0 **是定义使然**——那一层就是「rapidocr 当时
错的位置」。这一层只对**别的**引擎有意义：tesseract 在这 150 条上救回
18%，这才是「多引擎互补」的正确量法。

## 三条读数守则

**1. 先看天花板，再看差距。** `charset_ceiling` = 金标字有多少落在
「引擎字表 ∪ 简→繁扩展 ∪ 异体字扩展」之内。本书语料上 PP-OCR 原始字表
漏掉 **11.03% 的字次**（缺的是 說 則 謂 論 諸 這类繁体常用字，不是生僻
字），扩展后压到 1.20%。`top1` 与 ceiling 之差是重排能捞回来的部分，
`1 - ceiling` 是只能换字表才能动的部分。只看 top1 会把「字表不够」误诊
成「排序不好」。

**2. 本集的准确率是乐观的。** 锚不上参考本的页不进集，被排除的 243 条
正是切分出错的位置。同一册 `eval-align` 量到的全书准确率是 **80.08%**，
本集上是 89% 量级。差的这 9 个点就是偏置本身。**不要拿本集的数字对外
报「识别准确率」**，它只能用于同一批样本上比较不同算法。

**3. 比值连着分母读。** 表里每个比值都带 n/N，改动之后如果分母变了，
比值的升降与算法好坏无关。

## 已知局限

见 `metadata.json` 的 `known_limitation`。最要紧的三条：**单册、没有
train 集、没有跨册泛化数据**；异体字样本只有 15 条；`label_origin` 只有
`align` 一种，human/synth 的分层评测能力**至今没有样本验证过**。

## 重建

```bash
cd open-guji-cv
PYTHONPATH=. python scripts/build_char_ocr_dataset.py output/book9 \
    --corpus corpus/zongmu_wuyingdian_reference.txt \
    --dataset ../open-guji-dataset --shard book9
PYTHONPATH=. python scripts/eval_char_ocr.py ../open-guji-dataset/char-ocr \
    --engines rapidocr,tesseract
```

金标是自动对齐出来的，**重跑脚本即可重建整个集**，不需要重标。
