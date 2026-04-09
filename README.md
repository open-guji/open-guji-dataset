# open-guji-dataset

古籍计算机视觉 Benchmark 数据集，用于评估 [open-guji-cv](https://github.com/nichuanfang/open-guji-cv) 的识别准确率。

## 数据集

### book-profile — 版面识别 Benchmark

评估 `recognize-profile` 命令对古籍版面特征的自动识别能力。

**评估维度**：layout、content_format、lines_per_page、color_mode、border_style、border_wear、interferences、has_marginal_notes

**数据来源**：
1. open-guji-cv/data 测试数据（8 张）
2. AncientDoc 古籍图片数据集（~15 张）
3. 网络补充（缺失类型）

### 目录结构

```
benchmark/book-profile/
├── metadata.json          # 数据集元信息
├── samples/
│   └── 001/
│       ├── image.jpg      # 原始图片
│       ├── expected.json  # Ground truth (人工验证的 BookProfile)
│       └── info.json      # 来源、描述、标签
└── results/               # recognize-profile 输出 (gitignore)
```

## 使用

```bash
# 运行 benchmark
python scripts/run_benchmark.py

# 评估准确率
python scripts/evaluate.py
```
