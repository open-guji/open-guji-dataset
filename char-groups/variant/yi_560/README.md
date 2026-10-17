# #560 彝彛彜彞𢑱𢑴 取图点单（10-12）

`cells_to_crop.jsonl`：每码位最多 8 个候选格（按册轮流取），共 42 行。字段 `codepoint target id book admit_char admit ref lib_top2 channel crop`。

- `admit_char` 是引擎放行字，**没人核过，不是真值**；候选格不等于图上一定是该字。
- 彜只有 2 格放行（均 vol06），凑不满 3–5，如实保留。
- 切图请用引擎自己的 `char_patch`（`console/routers/products.py::_char_patch_binarized`，注意 bbox_page 是右上原点，需镜像 x），不要自己重切。
- 输出：`crops/<crop>`（id 的冒号换下划线，与 variant/crops 同命名）。
- 只出图，不判字。判字由 Lucian 看、用户定。
