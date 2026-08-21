# 占位样本（char-clustering）

本目录**不含真实数据**，只提供 schema 骨架供新增样本时拷贝。

缺失的真实文件：

| 文件 | 说明 |
|------|------|
| `crops/` | 归一化后的字块图（文件名即 instance_id） |
| `features.npz` | 可选，冻结的特征矩阵 |

`expected.json` 的 `instances` / `hard_pairs` 各含一条全 `null` 的骨架项，
仅示意字段，不是标注；`info.json` 标记 `"placeholder": true`。

添加真实样本的步骤见 [../../../doc/char-clustering.md](../../../doc/char-clustering.md)。
