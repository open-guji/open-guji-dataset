# 占位样本（collation）

本目录**不含真实数据**，只提供 schema 骨架供新增样本时拷贝。

本数据集不含图片：样本是**冻结的转写流 + 参考文本 + 金标对齐**，
全部在 `expected.json` 内。合成样本（`label_origin: "synth"`）可由脚本
从高质量参考注入可控替换噪声生成，`reference.noise_injected` 记录噪声率
x，`reference.rho` = 1 - x 即质量真值。

骨架中各列表只含一条全 `null` 的示意项；`info.json` 标记
`"placeholder": true`。

添加真实/合成样本的步骤见 [../../../doc/collation.md](../../../doc/collation.md)。
