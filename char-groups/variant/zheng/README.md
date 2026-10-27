# zheng 徵徴 人裁

- `sheldon_labels-1027.jsonl`：sheldon 2026-10-27 在标注页点的 75 格（徴 46、徵 13、其他 16）。`model`／`margin` 是当时整字 HOG 的判法与 margin。
  格 id 是换图源前的旧页号（rev2），要用 cv#639 的转换表换到新页号。
- 用这些标注重训后按册留出仍做不到 0 错，sheldon 10-27 定 徵→徴 暂归一（cv doc/字组/README.md 第二节、zheng.md）。
  这些是日后拆分的训练数据：徵 攒够 20 例可靠人裁、看图能稳定指认 徵 中间的 一 横，再试字形判法。
