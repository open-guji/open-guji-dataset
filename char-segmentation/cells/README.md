# char-segmentation / cells —— 格内净化

## 这个子集在测什么

刻本按刚性网格切出格位之后，图块里常常还混着两样东西：

1. **左右界行 / 版框**——列边界上的竖线、页边的横线；
2. **上下邻字的残余**——上一个字的竖尾拖过格线，下一个字的顶横探上来。

直觉做法是「按纵向间隙丢弃孤立小块」。**实测这条路走不通**：

```
污染块与主体的间隙   p10=2  p50=10  p90=16   (n=20，人工标注)
「高/卞/示」顶部部件 p10=4  p50=12  p90=30   (n=655)
```

两个分布完全重叠。任何间隙阈值，要么留下污染，要么把「高」的顶点、
「字」的宀、「范」的艹削掉。所以本子集用**两个互相拉扯的指标**同时约束，
逼算法换判别维度而不是调阈值：

| 指标 | 掉分的原因 |
|------|-----------|
| `keep_recall` | 削掉了本字的墨（顶部分离部件首当其冲）|
| `drop_precision` | 留下了界行 / 邻字残余 |
| `clean_rate` | 完全没有杂墨的格位占比 |

并且单独报 `detached_top` 子集的分——顶部部件与主体不连通的字，
是误伤的重灾区。

## 跑分

```bash
python -m open_guji_cv seg-bench char-segmentation/cells/samples
python -m open_guji_cv seg-bench <samples> --strategies padding_box,component_owner --out report.json
```

## 挂一个新算法

在 `open_guji_cv/clustering/seg_eval.py` 里实现签名并注册：

```python
def strat_mine(strip, cells, cell_h, col_w) -> dict[int, np.ndarray]:
    """返回 {格序号: 该格保留的墨迹布尔掩膜}（掩膜与 strip 同形）"""

STRATEGIES["mine"] = strat_mine
```

## 现有基线（60 样本 / 480 格）

| 策略 | keep_recall | drop_precision | f1 | clean_rate |
|------|------------|----------------|-----|-----------|
| `padding_box` 按格线裁框 + 固定外扩 | 0.9881 | 0.8027 | 0.8832 | 0.0125 |
| `gap_threshold` 裁框 + 间隙阈值 | 0.9364 | 0.7622 | 0.8379 | 0.0167 |
| `component_owner` 列级连通体归属 | 0.9863 | **0.9995** | **0.9926** | **0.9875** |

`gap_threshold` 是**故意收进来的反面教材**：它在两个指标上同时输给什么都不做的
`padding_box`——既误伤了真部件，又没换来干净。

## 样本怎么造的

见 `metadata.json` 的 `construction`。一句话：不造假墨，用**结构上确定干净**的
真实格位重新码列 + 抖动 + 画界行，逐像素金标由构造过程直接给出。
生成器：`open-guji-cv/scripts/build_seg_cases.py`。

关键正例（`detached_top`）按**结构**挑选（连通体数 ≥2 且纵向间隙 ≥4px），
刻意不按 OCR 标签挑——实测按标签挑「高/卞/示」，77.8% 的实例本身就带着
邻字残余，正例集先脏了，测出来的分数没有意义。
