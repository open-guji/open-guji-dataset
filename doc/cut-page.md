# CutPage 数据格式

## 概述

`cut-page` 数据集用于评估 `guji-cv cut` 命令的页面切分检测能力。该命令检测古籍图片是否需要切分，以及切分方向。

切分是古籍数字化的第一步，在 `recognize-profile`（版面识别）之前执行。

## 处理流程

```
原始图片
  ↓
guji-cv cut         ← 本数据集评估的步骤
  ↓
切分后的半页图片
  ↓
guji-cv recognize-profile
  ↓
...
```

## 输出格式

`cut.json`：

```json
{
  "cut_type": "vertical_cut"
}
```

## 字段定义

### cut_type — 切分类型

| 取值 | 说明 | 典型场景 |
|------|------|---------|
| `"none"` | **不切分**：图片已经是单个半页，或不需要切分的格式 | `cut_half` 半页扫描、`uncut_full` 筒子页、现代单栏排版 |
| `"vertical_cut"` | **垂直切分**：从中缝纵向切分为左右两半 | `spread` 对开页（两个独立页框左右排列） |
| `"horizontal_cut"` | **水平切分**：从中部横向切分为上下两半 | 影印本上下两栏排列 |

## 切分后的输出文件

| 切分类型 | 输出文件 |
|---------|---------|
| `none` | 不生成新文件 |
| `vertical_cut` | `{name}_left.png`, `{name}_right.png` |
| `horizontal_cut` | `{name}_top.png`, `{name}_bottom.png` |

## 检测算法

### vertical_cut 检测

在图片中央 40%-60% 宽度范围内，逐列计算墨迹密度。`spread` 页面的两个页框之间存在纵向间隙（墨迹密度接近零），而 `uncut_full` 的版心区域有持续的文字/装饰。

前提条件：宽高比 > 0.95（太窄的图片不可能是 spread）。

### horizontal_cut 检测

在图片中部 30%-70% 高度范围内，逐行计算墨迹密度。上下两栏之间存在连续的低密度水平带（间隙高度 >= 图片高度的 2%）。

前提条件：宽高比 < 1.2（太宽的图片不太可能是上下两栏）。

## 数据来源

| 来源 | 样本数 | cut_type |
|------|--------|----------|
| book-profile 001-007, 009-011 | 9 | none |
| book-profile 008, 012-015 | 6 | vertical_cut |
| 续修四库全书总目提要（PDF p3, p11） | 2 | horizontal_cut |
| 四库全书总目 1965 版（PDF p7） | 1 | none |

## 示例

### none（不切分）

```json
{
  "cut_type": "none"
}
```

适用于已经是半页的扫描件、筒子页、现代排版等。

### vertical_cut（垂直切分）

```json
{
  "cut_type": "vertical_cut"
}
```

适用于对开页扫描——两个独立的半页左右排列，中间有装订缝。

### horizontal_cut（水平切分）

```json
{
  "cut_type": "horizontal_cut"
}
```

适用于影印本——同一页上印刷了上下两个原始页面。
