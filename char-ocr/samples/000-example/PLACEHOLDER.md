# 占位样本（char-ocr）

本目录**不含真实数据**，只提供 schema 骨架供新增样本时拷贝。

缺失的真实文件：

| 文件 | 说明 |
|------|------|
| `crops/` | 归一化图块（文件名即 instance_id，与 `items[].crop` 对应） |

`expected.json` 的 `items` 只含一条全 `null` 的骨架项，`split` 为 `null`
（真实样本必须显式填 `train` 或 `test`，且按册划分）；`info.json` 标记
`"placeholder": true`。

添加真实样本的步骤见 [../../../doc/char-ocr.md](../../../doc/char-ocr.md)。
