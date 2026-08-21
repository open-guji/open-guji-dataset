# 占位样本（char-normalization）

本目录**不含真实数据**，只提供 schema 骨架供新增样本时拷贝。

缺失的真实文件：

| 文件 | 说明 |
|------|------|
| `input.png` | 原始字块图 |
| `golden.png` | 期望归一化输出（人工确认后冻结） |
| `golden_skeleton.png` | 期望骨架输出 |

`expected.json` 中的容差与覆盖类别均为 `null` / 空列表，
`info.json` 标记 `"placeholder": true`。

添加真实样本的步骤见 [../../../doc/char-normalization.md](../../../doc/char-normalization.md)。
