# 如何添加测试样本

各数据集会长期增补。这份文档固化**已经踩过坑的流程**，照做即可，不必
重新摸索。

通用铁律，三条：

1. **金标必须比被测算法可靠。** 不要用被测算法的输出当金标——那是循环
   论证。宁可样本少，也不能循环。
2. **判不准就标 `uncertain`，评测跳过。** 灌进金标的噪声会同时高估和
   低估算法（构建 column-layout 时错标 3 页，修正后 body 从 90.4% 升到
   96.3%、toc 从 62.2% 降到 58.7%——两个方向都被带偏了）。
3. **标注表集中在一处，重跑脚本即可重建数据集。** 改标注只改那张表。

---

## column-layout（行列识别：逐列刚性/弹性）

### 判别定义（标注与评测共用，不得含糊）

| 列型 | 定义 |
|---|---|
| `rigid` | 字距 = 1×格高 |
| `elastic` | 字距 ≠ 1×格高（拉开 ~3.5× 或压缩 ~0.5×）|
| `blank` | 整列无字，由墨量客观判定，不进分类指标 |
| `uncertain` | 人工也判不准，评测跳过 |

判据是**字距**，不是字数也不是相位：

- 目录页一列只有 6 个字、后面全空 → 仍是 `rigid`；
- 抬头列（「上」「朝」被抬到格线之上）整体相位偏移但字距未变 → 仍是
  `rigid`。相位偏移是另一个更易修正的问题，混进列型会让标签失去指导意义。

### 步骤

1. **抽样**：按页型均衡（body / toc / roster / edict / cover），两册均分。
   页型可用转写文本粗分（`臣` 多 → 职名；`卷X` 多 → 目录），仅用于
   保证覆盖，**不作为金标**。
2. **渲染判读图**：把**纯刚性格线**（书级 `cell_h` + 页相位）叠在列上。

   ```python
   # 关键：画的是等距刚性格线，不是算法切出来的 cell——否则又是循环论证
   y = page_phase
   while y < strip.shape[0]:
       cv2.line(strip, (0, int(y)), (strip.shape[1], int(y)), (0, 0, 255), 2)
       y += cell_h
   ```

3. **目视判读**：红线落在字与字之间 → `rigid`；红线穿字而过、或字数与
   格数对不上 → `elastic`。一页 9 列一次判完。
4. **写进标注表**：`open-guji-cv/scripts/build_layout_dataset.py` 的
   `PAGE_LABELS`。页级给 `all`，个别列用 `individual` 覆盖。
5. **重建 + 复测**：

   ```bash
   cd open-guji-cv
   python scripts/build_layout_dataset.py --out ../open-guji-dataset/column-layout/samples
   python scripts/eval_layout.py ../open-guji-dataset/column-layout/samples
   ```

### 复核提示

页型批量标完后**务必逐页复看一遍**。构建时把两页目录页错标成正文页、
一页题名页错标成正文，都是复看时才发现的。

---

## char-segmentation/instances（单字图块质量）

### 判定原则：只看墨，不看框

**图块多裁一点空白不算失败**——空白不影响下游归一化与识别。
混入 = 多了别人的墨；截断 = 少了自己的墨；与外接框大小无关。

| 标签 | 含义 |
|---|---|
| `clean` | 就是完整的本字，没有别人的墨 |
| `contaminated` | 混入界行竖线 / 版框 / 上下邻字残余 / 隔壁列的字 |
| `truncated` | 本字的墨被切掉了一部分 |
| `not_text` | 根本不是字（版框角、整条横线、空格位）|

细粒度的逐像素指标不在这里标——那由合成数据集
[`char-segmentation/cells`](../char-segmentation/cells) 承担，
它能造出逐像素金标，且天然对空白免疫。

### 步骤

1. **抽样**：一半从历史人工审查标记过的问题位置抽（值得复查），一半
   从各列型随机抽。**抽样偏置必须写进 metadata**——各类占比不是全书
   真实缺陷率。
2. **渲染判读图**：左右对照。

   - 左：原页图 + 图块边界（黄框）+ 上下各约 0.6 格高的**上下文**
     （没有上下文判不了截断）；
   - 右：图块内**连通体着色**（每个连通体一种颜色）。

3. **目视判读**：右图里有不属于本字的色块 → `contaminated`；
   左图里本字的墨越出黄框、框内缺了一部分 → `truncated`；
   整块是线/框/空 → `not_text`。
4. **写进标注表**：`open-guji-cv/scripts/build_instance_dataset.py` 的
   `LABELS`。
5. **重建 + 复测**：

   ```bash
   cd open-guji-cv
   python scripts/build_instance_dataset.py \
       --out ../open-guji-dataset/char-segmentation/instances \
       --sample-meta <抽样元数据.json>
   python scripts/eval_instance_quality.py ../open-guji-dataset/char-segmentation/instances
   ```

### 注意：实例 ID 会随切分变化而失效

历史审查标记只有约 60~67% 能对上当前切分的 `page:col:idx`（弹性列改成
顺序编号、切分本身也改过）。所以：

- 历史标记**只当抽样线索**，指出「哪些位置值得复查」；
- 金标一律对**当前输出**重新标注；
- 重跑切分后旧标签同样可能失效，需要复核而不是直接沿用。

这也是为什么这个数据集评的是**自检能力**（`CharInstance.flags` 能否
标出坏图块）而非切分质量本身——后者的人工标签重跑即失效，当不了可
自动重跑的回归基准。

### 重跑切分之后：先查漂移，再谈数字

跑完 `segment`/`chars` 之后**不要直接测**。2026-08 的教训：加了列型分类
重跑切分，2771 个图块内容变了，直接用旧标签测出来的报告自相矛盾
（官方 benchmark 说 truncated 检出 0%，离线分析说 100%），查下去才发现
一部分标签已经不对应当前图块了。

固定动作：

```python
# ① 哪些标注实例的图块变了 / ID 没了
import json, hashlib
from pathlib import Path
gold = json.loads(Path("<dataset>/expected.json").read_text(encoding="utf-8"))
idx = {}
for line in open("output/<book>/phase4_chars/index.jsonl", encoding="utf-8"):
    r = json.loads(line); idx[f"{r['page']}:{r['col']}:{r['idx']}"] = r
for g in gold:
    k = f"{g['page']}:{g['col']}:{g['idx']}"
    if k not in idx:
        print("ID 已消失", k, g["quality"])          # → 移出标注表
    else:
        cur = hashlib.md5(Path("<dataset>/patches"/...).read_bytes()).hexdigest()
        # 与数据集里存的图块比对；不一致 → 进重标名单
```

② 把重标名单渲染成判读图，**对着当前图块**重新目视定标；
③ 改 `LABELS`，重建数据集，再跑 eval；
④ 把这一轮的变动写进 `metadata.json` 的 `relabel_history` 与 README。

重标本身会带出有价值的信息：那一轮 12 个重标里，有 6 个是**切分变好了**
（原来的 truncated/not_text/contaminated 现在已是完整干净的本字），代价是
本批样本从此没有 truncated 实例，截断检测能力暂时无从验证——这条已经
记进 `known_limitation`。**样本覆盖不到的能力要留痕，不能当作已验证。**

漂移的规模取决于改了什么。改判据（只影响 flag）不动图块，一个都不用重标；
改**几何**就是全量重标：紧接着那一轮加了残余错切校正，坐标系整个变了，
67 个里 59 个内容变化、4 个 ID 消失。所以：

- 改判据/阈值 → 直接重跑 eval；
- 改几何（切分、相位、错切、列宽）→ 先查漂移，按上面的固定动作走一遍，
  **不要**指望「只有几个会变」。

顺带一条读数提醒：切分变好之后缺陷基数会变小，**精确率会跟着掉**
（0.71 → 0.52，误报绝对数没变，分母小了）。看这类比值一定要同时看分母，
否则会把上游的进步误读成检测器的退步。

---

## char-segmentation/cells（格内净化，合成）

逐像素金标，靠**合成**而非人工标注取得，可大批量生成：

从真实页面挑出「结构上确定干净」的格位（连通体全部落在格线内、不碰
列边），按书级格高重新码成一列，加 ±10% 抖动，再画界行竖线与版框横线、
加纸纹噪声。每个像素属于哪一格在构造时就知道。

```bash
cd open-guji-cv
python scripts/build_seg_cases.py output/<book> \
    --out ../open-guji-dataset/char-segmentation/cells/samples --cases 60
python -m open_guji_cv seg-bench ../open-guji-dataset/char-segmentation/cells/samples
```

关键正例（`detached_top`，顶部部件与主体不连通的「高/卞/示」类）按
**结构**筛选（连通体数 ≥2 且纵向间隙 ≥4px），**不按 OCR 标签挑**——
实测按标签挑，77.8% 的实例本身就带着邻字残余，正例集先脏了。

---

## 加完样本之后

1. 跑该数据集的 eval，把新基线更新进 `metadata.json` 的 `baseline`
   与 README 的基线表；
2. 样本量、类别分布同步更新；
3. 如果新样本暴露了新的失败模式，写进 `notes` / `known_limitation`——
   **没解决的问题要留痕**，比假装没看见有价值。
