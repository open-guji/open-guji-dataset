# yi_560 U-Net 权重

- `unet_v1.npz`（sha256 `d2c32a4b87ca2e86`）：彝 三段 U-Net，cv#332
- 线上用的是仓里 `config/groups/yi_560/unet.npz`，与此份逐字节相同；这里是备份，免得重训。
- 训练数据：本目录 `labels.jsonl`（及 V_POOL 各组）。
- R2 备份（10-22）：`derived/ids-unet/yi_560/<文件名>`（main 桶，`datastore.packs.fetch_file` 取）。
