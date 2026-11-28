# page-survey —— 1a 页面预检（尺寸异常页）

CV1，2026-11-28。评测：open-guji-cv `open_guji_cv/eval/survey_bench.py`。信封见 layout/README。
`input.width/height` 是原图像素尺寸（冻结的上游输入，不需要图）。`expected.odd/kind` 是判据结论。
**种子 134 条全是 `label_origin: rule`**（按 cv d040498 判据快照，取自版面标注包原图），只能当回归，不是人核金标；
册内页数 <3 的册不放。缺：整册尺寸表、人核异常页名单。
