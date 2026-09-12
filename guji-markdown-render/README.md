# guji-markdown-render —— Step9「结果整理」坐标转字符位回归集

## 这个分片在测什么

Step9（结果整理，见 `overview` 仓
`项目进展/图片初步数字化/进度/Step9-结果整理/01-结果排版.md`）三件事里的
第一件：把 Step3 `row_segment`（版面结构：抬头、夹注、空白）+ Step7
`seed_admit`（每字位的定字结果）拼成 `guji-markdown` 格式文本。执行体是
`open-guji-cv` 仓 `scripts/render_guji_markdown.py`。

这个分片测的不是"文字内容对不对"（那要靠人核对原图，Step9 三件事都还
没做到"人审过的最终文本"这一步），而是**渲染逻辑本身**：给定一页的
版面结构和定字结果，`render_column`/`render_page` 该拼出什么样的
guji-markdown 文本——列内读序对不对、夹注该不该转 `<…>`、抬头级数
`^`/`^^` 对不对、挪抬 `.`/`..` 对不对、阙文占位 `[[…]]` 触发对不对、
排除名单（excluded）该不该跳过不占位、以及**过期数据检测**这条防线
本身有没有被后续改动悄悄破坏。

## 2026-09-11 首次建档 ＋ 两轮修复

用户要求"挑几页做成测试集，定义好期望的输出，看看效果"。挑了 vol01
四页，覆盖脚本当时处理的四类版面现象＋一个已知的真实数据缺陷；随后
用户拿真实产出（vol02 第 1-20 页）核实效果，暴露出两处渲染逻辑本身的
问题，修复后追加了第五条用例：

| id | 页 | 覆盖 |
|---|---|---|
| `render:vol01:10` | 10 | 基线：纯正文 + 1 处阙文 + 行首挪抬，无夹注无抬头 |
| `render:vol01:33` | 33 | 多级抬头（一级 `^`／二级 `^^`）+ 3 处阙文 + 行首挪抬，无夹注 |
| `render:vol01:89` | 89 | 夹注 + **一处已知过期数据**（见下）+ 抬头与挪抬并存（`^^....`） |
| `render:vol01:146` | 146 | 夹注 + 转行 `\|`（两条独立小注）+ 大量 excluded + 行首挪抬 |
| `render:vol02:3` | 3 | excluded（7 处）与真阙文（1 处）混在同一页，专门守住两者的区分（见下） |

### 两处渲染逻辑修复（用户用 vol02 p1-20 效果核实发现）

1. **excluded 误标成阙文**：最初版本把 Step7 排除名单命中
   （`doubts=["excluded"]`，切坏图块/非字）也标成了 `[[]]`——用户核实
   vol02 前 20 页时发现 20 处 `[[]]` 里 19 处其实是 excluded，只有 1 处
   是真识别失败。两者语义完全不同："这一格本不该存在" vs "这格是字但
   认不出"，混在一个记号里会让人误判缺字规模。修复后 excluded 跟
   `blank` 一样直接跳过、不占位。
2. **挪抬完全没有产出**：最初判断"挪抬没有对应几何数据支撑"（把挪抬
   想成了必须跟具体敬语词绑定的偶发现象），实际上挪抬记号本来记的就是
   "字前空出 n 格"这个版面事实本身——用户核实效果时指出"每一行开头的
   空格没有显示出来"，裁定不需要先判定"是不是敬语"，行首确实空着就该
   标 `.`。调研确认 vol02/vol03 全书 85%+ 的列固定开头空 2 格（vol01
   固定 1 格），跟内容无关，是版框顶边到首字的固定间距——但不管几何
   成因是什么，版面上确实空着就该标，修复后新增 `_lead_blank_count()`，
   从 Step3 `cells` 直接数（**不能**从 Step7 `seed_admit` 数，见下）。

### `render:vol01:89` 是故意留的"脏"案例，不是干净金标

调试脚本时在这一页 col7 发现：Step7 `seed_admit` 在 `slot=1/8/10`
上有记录，但 Step3 `row_segment` 的 `cells` 里同 `(slot,sub)` 查不到
对应格子。查实是**真实的产物版本不一致**——这一列在
`open-guji-cv` `1d404fe0fa`（"切分缺陷按机制清账"）之后被重新切分并
整体平移过 slot 编号，但 `seed_admit` 消费链
（`ocr_candidates→context_decide→align_ref→seed_admit`）没有跟着重跑，
`python -m open_guji_cv status` 已经把这页标记为过期。全书 810 个
夹注字位里只有这一处（外加这次顺带发现的 `slot=8`，共 5 条）不匹配。

**没有清洗掉这个案例，反而特意收进来**：`render_guji_markdown.py` 遇到
这种"Step7 有记录但 Step3 查不到"的情况，不会静默把它当正文字吞掉，
而是记进 `expected.stale` 里、跑完在 stderr 报告。这个分片除了守住
渲染文本本身，**同时守住这条报错防线**——以后如果有人改坏了 stale
检测逻辑（比如误吞、误报、报告格式变了但没人注意），这条测试会炸。

`expected.text`／`expected.stale` 都是**脚本当前真实输出的固化快照**，
不是人工核对过原图的"标准答案"（跟 `align-anchor` 分片同一个定位，
见其 README）。p89 的输出因为过期数据混进了一些兜底猜测（"筵"、"學"、
"太"、"翰"被当独立正文字而非夹注一部分处理），**这是已知的、故意
保留的缺陷**，不要"修好"这条 expected——它测的正是"脚本在遇到这种
数据时的确定性行为"，而不是"最终应该长什么样"。真要修，要去
`open-guji-cv` 重跑这一页管线，而不是改这个分片。

### `render:vol02:3` 专门守住 excluded ≠ 阙文

见上面"两处渲染逻辑修复"第 1 条。这一页 col3~col6 前两格都是排除名单
命中（图上切坏的碎块/墨污），col3 slot13 才是真正的识别失败。改动
`_is_excluded` 或阙文判据后，如果这条测试炸了，先看是不是又把两者
混到一起——这个分片存在的目的之一就是让这种混淆没法悄悄溜过去。

### ⚠️ 快照必须带 `doubts` 字段，否则 excluded 判据的回归形同虚设

首次建档时快照只存了 `slot`/`sub`/`admit`/`char`/`reading`，**漏了
`doubts`**。`AdmitRec` 没给这个字段时默认 `doubts=[]`，`_is_excluded`
（内部就是 `"excluded" in rec.doubts`）永远返回 `False`——也就是说
**即使 excluded 判据本身写错了，这个分片的回归测试也测不出来**，
因为快照给不出任何一条 `doubts` 非空的记录。修 excluded 那处 bug 时
一并补上了这个字段，四条旧用例的快照跟着重新导出。**以后往这个分片
新增用例，`AdmitRec` 相关字段有增删时，先看新字段是不是某个判据
（`_is_excluded`、阙文判据……）用得到的输入，用不到才能安心漏。**

## 数据结构

```jsonc
{
  "id": "render:vol01:33",
  "input": {
    "book": "vol01", "page": 33,
    "cells": [                    // 对应 row_segment 产物的最小快照
      {"col": 7, "n_raised": 2,
       "cells": [{"slot": -2, "sub": null, "kind": "char"}, ...]}
    ],
    "seed_admit": [                // 对应 seed_admit 产物的最小快照
      {"col": 7,
       "chars": [{"slot": -2, "sub": null, "admit": true,
                  "char": "天", "reading": null, "doubts": []}, ...]}
    ]
  },
  "expected": {
    "text": "^^天天而\n...",        // render_column 逐列拼接后的完整页文本
    "stale": []                    // p{page}col{col}:slot{n}{a|b} 列表，见上
  },
  "note": "一句话说明这页测什么",
  "label_origin": "derived",        // 派生自当前脚本真实输出，不是人工金标
  "status": "active"
}
```

`input.cells`／`input.seed_admit` 只保留渲染逻辑用得到的字段（`slot`／
`sub`／`kind`／`n_raised`／`admit`／`char`／`reading`／`doubts`），不是
完整产物——足够离线跑，不需要 `products/`、不需要 `GUJI_WORKSPACE`。
`doubts` 是 excluded 判据的唯一依据，**必须带**，见上一节。

## 怎么跑

`open-guji-cv` 仓 `tests/test_render_guji_markdown.py` 读本分片
`items.jsonl`，用快照数据重建 `CellRec`/`AdmitRec` 直接调用
`open_guji_cv/render/guji_markdown.py::render_column`（渲染逻辑本体，
命令行入口 `scripts/render_guji_markdown.py` 与控制台路由都是薄封装，
import 同一份函数），断言输出与 `expected.text`/`expected.stale` 一致。
纯数据输入，跑在常规 `pytest` 回归里（`-s -p no:cacheprovider`，
这个仓的 pytest 怪癖见 `open-guji-cv` 自己的坑本）。

## 维护口径

- 这是回归集，不是"正确性金标"——`label_origin: "derived"` 全部条目
  都是脚本真实输出，不是人工核对过原图逐字确认的答案。
- 改 `render_guji_markdown.py` 的渲染逻辑后如果这条测试失败：先判断
  是"变好了"（比如修复了某个版式判断）还是"变坏了"（引入了新 bug）。
  变好了就更新对应的 `expected.text`／`expected.stale`，并在
  `history` 里写清楚为什么变、依据是什么（哪次改动、什么真实数据
  验证过），不要不声明就悄悄改基线。
- 新增案例只在"覆盖了一种新的版式现象，或者踩出一种新的边界情况"时
  才加，不要为了凑数堆无差别页面。
- p89 那条**不要因为看着"内容不对"就删掉或"修正"**——它测的是过期
  数据检测本身，见上面专门一节。
