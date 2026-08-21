# 占位样本（context-correction）

本目录**不含真实数据**，只提供 schema 骨架供新增样本时拷贝。

本数据集不含图片：样本是**冻结的候选**（列上下文 + 候选列表及概率 +
金标字），全部在 `expected.json` 内。骨架里的 `slots[0]` 与
`candidates[0]` 均为 `null` 占位，仅示意字段，不是标注；
`info.json` 标记 `"placeholder": true`。

添加真实样本的步骤见 [../../../doc/context-correction.md](../../../doc/context-correction.md)。
