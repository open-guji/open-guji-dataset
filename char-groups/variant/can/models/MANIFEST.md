# can（參㕘叅）U-Net 留出模型
按册留出对照（10-22）：每个文件是**不含该册**的人标切线训出的 2 类 U-Net（水平切，40 epoch，seed 1），训练数据 = 本目录 labels.jsonl 中其余册的 88 格切线。
- `unet_holdout_vol04.npz`（sha256 `8b30651afa7a12fe`）
- `unet_holdout_vol08.npz`（sha256 `fc17ce4d4e76033b`）
- `unet_holdout_vol09.npz`（sha256 `decb6a75a2939569`）

线上用自动缝，没有用 U-Net（见 CV 仓 doc/research/形近字组实验记录.md）；这些权重只是留出评测的结果，存着免得重训。
- R2 备份（10-22）：`derived/ids-unet/can/<文件名>`（main 桶，`datastore.packs.fetch_file` 取）。
