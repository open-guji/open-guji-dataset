# BookProfile 数据格式

## 概述

`BookProfile` 描述一本古籍的版式特征。由 `guji-cv recognize-profile` 命令自动生成，存储为 `profile.json`。

本文档是 BookProfile 数据格式的完整定义。

## 字段一览

| 分类 | 字段 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| 基础 | `layout` | str | `"cut_half"` | 版面布局 |
| 基础 | `banxin_position` | str\|null | `null` | 版心位置（仅 cut_half） |
| 基础 | `content_format` | str | `"regular"` | 内容格式 |
| 基础 | `lines_per_page` | int | `8` | 每页行数 |
| 高级 | `font_type` | str | `"printed"` | 字体类型 |
| 高级 | `fixed_chars_per_line` | bool | `true` | 每行字数是否固定 |
| 高级 | `chars_per_line` | int\|null | `21` | 每行字数 |
| 高级 | `has_marginal_notes` | bool | `false` | 是否有夹注 |
| 高级 | `color_mode` | str | `"bw"` | 色彩模式 |
| 高级 | `background_color` | str | `"white"` | 底色 |
| 高级 | `text_color` | str | `"black"` | 文字颜色 |
| 高级 | `border_color` | str | `"black"` | 边框颜色 |
| 高级 | `border_style` | str | `"double"` | 边框类型 |
| 高级 | `border_wear` | str | `"medium"` | 边框磨损 |
| 高级 | `interferences` | list[str] | `[]` | 干扰项 |
| 高级 | `margin_color` | str\|null | `null` | 页边距颜色 |
| 配置 | `skip_pages` | list[int] | `[]` | 跳过页码 |
| 配置 | `skip_steps` | list[str] | `[]` | 跳过预处理步骤 |
| 元信息 | `auto_detected` | bool | `true` | 是否自动检测 |
| 元信息 | `detection_confidence` | dict | `{}` | 各字段置信度 |

---

## 基础参数

### layout — 版面布局

描述图片中古籍页面的物理拍摄/扫描方式。

| 取值 | 说明 |
|------|------|
| `cut_half` | **半页**：已剪切的单个半页，最常见的扫描方式 |
| `uncut_full` | **筒子页**：未剪切的完整筒子页，中间有版心，需从中缝分页 |

> 注：`spread`（对开拍照）应在 `cut` 命令阶段被切分为两个 `cut_half`，不应出现在 recognize-profile 的输入中。

### banxin_position — 版心位置

**条件字段**：仅当 `layout = "cut_half"` 时有意义。

版心是半页侧边的窄条带，包含书名、卷数、页码和鱼尾标记。

| 取值 | 说明 |
|------|------|
| `"left"` | 版心在图片左侧 |
| `"right"` | 版心在图片右侧 |
| `null` | 无法判断或非 cut_half |

### content_format — 内容格式

描述页面内容的排版方式。

| 取值 | 说明 |
|------|------|
| `regular` | **常规栏式（乌丝栏）**：竖线分隔的等宽列，古籍最常见的排版 |
| `no_line` | **无栏线**：有分栏但列之间没有竖线分隔 |
| `table` | **表格**：含内部横线的网格布局 |
| `illustration` | **插图**：以图片为主的页面 |
| `mixed` | **混合**：文字与插图混合排列（如上半部插图、下半部文字） |

### lines_per_page — 每页行数

每半页的文字列数（竖排古籍中"行"即"列"）。

- `regular`/`no_line`：文字列数，通常 4~12
- `table`：列数（表格的纵向分栏数）
- 对于 `uncut_full`：指单侧半页的行数（去掉版心后）

---

## 高级参数

### font_type — 字体类型

| 取值 | 说明 |
|------|------|
| `"printed"` | **印刷/刻本**：笔画均匀、字形规整 |
| `"handwritten"` | **手写/抄本**：笔画粗细变化、字形不规整 |

### fixed_chars_per_line — 每行字数是否固定

| 取值 | 说明 |
|------|------|
| `true` | 每列字数基本一致（如固定 21 字/列） |
| `false` | 每列字数不固定（如散文、诗词等），此时 `chars_per_line` 为 `null` |

### chars_per_line — 每行字数

**条件字段**：仅当 `fixed_chars_per_line = true` 时有意义。

每列的字符数，通常 15~25。`null` 表示未检测到或字数不固定。

### has_marginal_notes — 夹注

是否存在夹注（一列内包含双行小字注释）。

### color_mode — 色彩模式

| 取值 | 说明 |
|------|------|
| `"bw"` | 黑白（灰度扫描或黑白印刷） |
| `"colored"` | 彩色（宣纸底色、彩色边框等） |

### background_color — 底色

| 取值 | 说明 |
|------|------|
| `"white"` | 白色（黑白扫描的常见背景） |
| `"xuan"` | 宣纸色（米黄/橙色暖色调，四库全书等常见） |
| `"other"` | 其他颜色 |

### text_color — 文字颜色

| 取值 | 说明 |
|------|------|
| `"black"` | 黑色（最常见） |
| `"red"` | 红色（朱墨批注、红色印刷等） |
| `"other"` | 其他颜色 |

### border_color — 边框颜色

| 取值 | 说明 |
|------|------|
| `"black"` | 黑色 |
| `"red"` | 红色（常见于宣纸色古籍的边框） |
| `"other"` | 其他颜色 |

### border_style — 边框类型

| 取值 | 说明 |
|------|------|
| `"double"` | **双边框**：外粗内细两条线 |
| `"single"` | **单边框**：一条线 |
| `"hsingle_vdouble"` | **上下单左右双**：水平边为单线，垂直边为双线 |

### border_wear — 边框磨损

| 取值 | 说明 |
|------|------|
| `"none"` | 无磨损（边框完整清晰） |
| `"light"` | 轻微磨损 |
| `"medium"` | 中等磨损 |
| `"heavy"` | 严重磨损（边框大面积断裂） |

### interferences — 干扰项

图片中影响识别的干扰因素列表。

| 取值 | 说明 |
|------|------|
| `"spine_shadow"` | **书脊阴影**：页面侧边的纵向暗条纹，由装订处产生 |
| `"margin"` | **页边距**：版心外围的均匀区域（白色或黑色），与 `margin_color` 配合使用 |

### margin_color — 页边距颜色

**条件字段**：仅当 `interferences` 包含 `"margin"` 时有意义。

| 取值 | 说明 |
|------|------|
| `"white"` | 白色页边距（扫描件常见的白色留白） |
| `"black"` | 黑色页边距（拍摄时的黑色背景） |
| `"other"` | 其他颜色 |
| `null` | 无页边距干扰 |

---

## 配置字段

### skip_pages

跳过的页码列表（按文件名末尾数字匹配）。用于标记不需要处理的页面（如封面、空白页）。

### skip_steps

跳过的预处理步骤列表。可选值：`remove_watermark`, `normalize`, `crop`, `enhance_lines`, `split`, `binarize`

---

## 元信息

### auto_detected

`true` 表示由 `recognize-profile` 自动生成，`false` 表示人工编辑。

### detection_confidence

各字段的检测置信度（0.0~1.0），键名为字段名或干扰项名。仅自动检测时有此字段。

---

## 向后兼容

加载旧版 profile.json 时自动迁移：

| 旧值 | 新值 |
|------|------|
| `page_type: "table"` | `layout: "cut_half"` + `content_format: "table"` |
| `page_type: "cut_half"/"uncut_full"/"spread"` | `layout` 对应值 |
| `background_color: null` | `"white"` |
| `background_color: "orange"/"yellow"` | `"xuan"` |
| `border_color: "orange"` | `"red"` |
| interferences 中的 `"white_margin"` | `"margin"` |
| interferences 中的 `"stains"` | 移除 |

## 示例

```json
{
  "layout": "cut_half",
  "banxin_position": "right",
  "content_format": "regular",
  "font_type": "printed",
  "lines_per_page": 9,
  "fixed_chars_per_line": true,
  "chars_per_line": 21,
  "has_marginal_notes": false,
  "color_mode": "colored",
  "background_color": "xuan",
  "text_color": "black",
  "border_color": "red",
  "border_style": "double",
  "border_wear": "medium",
  "interferences": ["spine_shadow", "margin"],
  "margin_color": "black"
}
```
