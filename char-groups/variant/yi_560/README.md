# #560 彝彛彜彞𢑱𢑴 取图点单（10-12）

`cells_to_crop.jsonl`：每码位最多 8 个候选格（按册轮流取），共 42 行。字段 `codepoint target id book admit_char admit ref lib_top2 channel crop`。

- `admit_char` 是引擎放行字，**没人核过，不是真值**；候选格不等于图上一定是该字。
- 彜只有 2 格放行（均 vol06），凑不满 3–5，如实保留。
- 切图请用引擎自己的 `char_patch`（`console/routers/products.py::_char_patch_binarized`，注意 bbox_page 是右上原点，需镜像 x），不要自己重切。
- 输出：`crops/<crop>`（id 的冒号换下划线，与 variant/crops 同命名）。
- 只出图，不判字。判字由 Lucian 看、用户定。

## 补点 40 格（2026-10-20）
`user_parts_labels.jsonl` 由 42 格增至 82 格。新增 40 格取自殿本 vol01、04–10 产物里放行字或整理本字落在彝六字、且机器把握最低的格；机器按当时算法预填部件读法，sheldon 在手机审查页逐格看，改了 2 处（vol06:118:5:18 中段 分→糸，vol10:112:9:16 下段 大→廾），其余点「全部确认」。字段 `by`：`user`＝sheldon 点选／改过，`user_confirmed`＝机器预填、sheldon 确认；`src`＝`review_page_1020`。字块图在 `crops/`（产物原图裁切，x 已按右上原点镜像）。
切线标注见 `cut_labels.jsonl`、`CUT_README.md`。
