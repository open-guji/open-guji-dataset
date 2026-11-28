# glyph-near/bench3b：3b 形近字组整体 benchmark

2026-11-28 CV3 建（形近字组整体方案第八、十一节 D「3b 整体」）。评的是第三步 3b `glyph_near` 各方法**放在整册上**的表现：
触发多少格、该罩的格罩住没有、方法之间一致不一致、判得准不准、弃权多少、校准好不好（ECE）、每格多慢、指纹稳不稳。
3b 只吃「3a 候选＋字块图」，所以这里把 3a 记录和被触发格的字块图冻住，评测不必整册重跑，几分钟跑完。

- 冻结：open-guji-cv `scripts/build_near_bench.py`；评测：`scripts/eval_near.py`（脚本头与 cv `doc/3-识字/3b整体benchmark.md` 是细则）。
- manager：`guji eval run @near`（注册见 guji-manager #1257）。

## 三书

| 书 | 工作区 | test 册（报数） | fit 册（只拟合临时校准） | 组：方法 |
|---|---|---|---|---|
| 全唐文 `995ejelvk0` | 995ejelvk0 | 046 | 031 | rr：rr_shape；wu：wu_shape；hou：hou_shape；dt／wyu／yh：pair_shape；men：book_knn；qg（千干）：stroke_veto；`_guard`：near_knn |
| 史記 `988g3f0wsu` | 988g3f0wsu | 05 | 04 | zy（之矣）：pair_shape |
| 殿本總目 `96mid1ogzk` | siku-zongmu | vol04 | vol06 | gong（宫宮官）：cnn_small；men：book_knn |

各册格数、触发数、标签数见 `metadata.json`；每册 `meta.json` 有钉死的产物包标签。

## 文件

| 文件 | 内容 |
|---|---|
| `bench.json` | 每书：工作区 id、册（`role: test`／`fit`）、钉死的产物包标签、3b 书配置写法的 `groups`（按 cv 登记表展开 `ref`、守 `handling.methods`）、模型文件 sha256 与训练说明；`labels.circular_channels` |
| `<书>/<册>/cells.jsonl.gz` | 这一册**每一格**一行：`a`＝3a 首位／判档／护栏／全部候选；`label`＝放行字与通道、人裁 `gold_char`；`img`＝被触发格的字块图 |
| `<书>/<册>/img/` | `<key>.p.png`＝`char_patch`（灰度原样）；`<key>.r.png`＝原图按 `bbox_page` 裁的块（只给挂了 `patch: raw` 方法的组，即殿本 gong） |
| `<书>/<册>/meta.json` | 包标签、cv 版本、页数、格数、触发数、标签数 |
| `baseline.json` | 2026-11-28 基线报告（`eval_near.py --fit-calib`，含 `temp_calib` 一节） |

## 纪律与已知偏差

- **包标签钉死**：冻结时工作区产物根里这册的 `.pack.json` 标签对不上就拒。
- **标签**：人裁优先（`seed_admit` 的 `human` 通道；殿本另按格 id 对 `char-groups/labels/unified.jsonl` 的 `kind=shape`、`status=ok`）；
  否则用放行字，但去掉 3b 方法自己的放行通道（`circular_channels`），免得自己评自己。
- **3a 只用来触发**，不评 3a 本身：包里的 3a 是人裁入库后现跑的（候选字线 11-27 的坑）。
- **训练册泄漏**（报告照抄 `bench.json` 的 note）：rr_shape 训练册 04–15，test 046 与 fit 031 都在外面；史記 pair_shape 训练册 01–03；
  book_knn／near_knn 的刻例库是本书已放行格建的，**test 册可能在库里，准确率偏乐观**；殿本 cnn_small 用殿本现行文本 7447 格按册 5 折训练、推理取五折平均，vol04／vol06 多半在训练语料里，同样偏乐观（它的正式校准表是 5 折留出概率拟合的）。
- `_guard` 的 `gap` 一路（3a 没判 same 的格）量太大，只数不冻图、不判。
- 模型文件不进本仓：`models/…` 在 cv 仓，`config/groups/…` 读本书中心库数据目录（`guji db pull -w <工作区>`）。sha256 对不上照跑，报告里 `pin_ok: false`。
- `meta.json` 的 `render_cv` 是写 meta 时的 cv（046／vol04 的 meta 是事后 `--meta-only` 重写的）；字块图的生成代码这段时间没变。

## 2026-11-28 基线（test 册）

准确率＝方法判出字的格里对的比例（只数标签字在方法认得的字里的格）；覆盖＝放行字／人裁落在组内的格被这组触发的比例（silver）。
耗时是预热后的每格毫秒数（首批格含模型加载另计 `load_s`）。ECE 列：殿本 gong 是正式表；标 tmp 的是本次临时表在 test 册上的 holdout。

| 册 | 方法:组 | 触发 | 覆盖 | 准确率 | 弃权率 | ms/格 | ECE |
|---|---|---|---|---|---|---|---|
| 全唐文 046 | near_knn:_guard | 15571（gap 12709／guard 1334／near_form 1528；判 3237） | — | 0.906（2851/3148） | 0.013 | 19.1 | — |
| 全唐文 046 | rr_shape:rr | 259 | 251/252 | 0.996（231/232） | 0.097 | 1.5 | 0.0089 tmp |
| 全唐文 046 | pair_shape:dt | 279 | 183/183 | 1.0（178/178） | 0.229 | 0.8 | 0.0173 tmp |
| 全唐文 046 | pair_shape:wyu | 473 | 152/152 | 0.973（145/149） | 0.666 | 0.6 | 0.0364 tmp |
| 全唐文 046 | pair_shape:yh | 64 | 26/26 | 1.0（24/24） | 0.594 | 0.8 | — |
| 全唐文 046 | wu_shape:wu | 28 | 15/15 | 1.0（15/15） | 0.107 | 6.0 | — |
| 全唐文 046 | hou_shape:hou | 113 | 39/39 | 0.875（7/8，错的是人裁 𠋫） | 0.274 | 4.9 | — |
| 全唐文 046 | stroke_veto:qg | 229 | 57/57 | 0.904（47/52，千↔干） | 0.376 | 55.5 | — |
| 全唐文 046 | book_knn:men | 307 | 243/243 | 1.0（122/122） | 0.603 | 5.1 | — |
| 史記 05 | pair_shape:zy | 494 | 389/389 | 1.0（388/388） | 0.008 | 1.2 | 0.0022 tmp |
| 殿本 vol04 | cnn_small:gong | 85 | 78/91（人裁 17/30） | 0.987（77/78） | 0 | 15.0 | 0.013 |
| 殿本 vol04 | book_knn:men | 628 | 164/198（人裁 10/44） | 1.0（60/60） | 0.898 | 3.0 | — |

- 方法间一致率（046）：near_knn 对 rr_shape 0.987、对 book_knn 1.0、对 yh 1.0、对 stroke_veto 0.875、对 dt 0.711、对 wyu 0.731
  （只数两边的字都在对方认得的字里的格）。
- 同批格再打一遍逐位相同（`repeat_equal`）：全部方法 True；各书 `methods_sha` 两次运行相同。
- 殿本覆盖缺口：gong 有 13 格放行字在组内但 3a 首位不是组内字（`member` 只看首位，触发不到）；men（`cands` 触发）34 格放行字在组内而 3a 候选里没有够近的组内字。

## 临时校准表（`--fit-calib DIR`）

fit 册拟合（保序回归 PAV，段值 `(正例+0.5)/(n+1)`，至少 30 格且两类各 5 格），test 册报 holdout；表是 `near-calib/1`＋`version`、`temporary: true`、`fit_on`、`holdout`，
**只给排序展示、不用于自动放行**（Sheldon 11-28），不进本仓、不推中心库。2026-11-28 版本 `tmp-2026-11-28.1`：

| 书 | 方法:组 | fit n（正类） | holdout n | holdout ECE | Brier |
|---|---|---|---|---|---|
| 全唐文 | rr_shape:rr（031→046，另带 `rule.八`） | 219（入） | 200 | 0.0089 | 0.001 |
| 全唐文 | pair_shape:dt（031→046） | 127（太） | 183 | 0.0173 | 0.006 |
| 全唐文 | pair_shape:wyu（031→046） | 114（玉） | 152 | 0.0364 | 0.046 |
| 史記 | pair_shape:zy（04→05） | 643（矣 41） | 389 | 0.0022 | 0.0003 |

没出表的：hou_shape:hou（fit 031 只有 8 格在认得的字里）、wu_shape:wu（5）、pair_shape:yh（19）、stroke_veto:qg（22）样本不够；
book_knn、near_knn 不读校准表；殿本 cnn_small:gong 已有正式表。

## 命令

    # 冻结一册（GUJI_WORKSPACE 指书的工作区：产物根里是钉的包，原图、书级代码都在）
    PYTHONPATH=. python scripts/build_near_bench.py <dataset>/glyph-near/bench3b --book 995ejelvk0 --vol 046
    # 评测（--fit-calib 另出临时校准表；--calib-dir 拿一套校准表覆盖模型旁的表来评）
    PYTHONPATH=. python scripts/eval_near.py <dataset>/glyph-near/bench3b --out report.json [--fit-calib DIR] [--calib-dir DIR]
    guji eval run @near
