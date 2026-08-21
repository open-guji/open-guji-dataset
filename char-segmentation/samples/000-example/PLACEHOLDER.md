# 占位样本（char-segmentation）

本目录**不含真实数据**，只提供 schema 骨架供新增样本时拷贝。

缺失的真实文件：

| 文件 | 说明 |
|------|------|
| `image.png` | 预处理后的半页页图 |
| `input.json` | 列带 + 书级网格参数包（格高共识、相位、每列字数） |

`expected.json` 中所有值为 `null` / 空列表，`info.json` 标记
`"placeholder": true`。评测脚本应跳过 `placeholder` 为 true 的样本。

添加真实样本的步骤见 [../../../doc/char-segmentation.md](../../../doc/char-segmentation.md)。
