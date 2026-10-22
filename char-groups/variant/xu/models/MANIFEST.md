# xu U-Net 权重

- `unet_v1.npz`（sha256 `ed1146886df25657`）：叙敘 左右向 2 类 U-Net（叙敘+教敎+絕絶 共 106 格左右切线训，100 epoch，seed 1），cv#345
- 线上用的是仓里 `config/groups/xu/unet.npz`，与此份逐字节相同；这里是备份，免得重训。
- 训练数据：本目录 `labels.jsonl`（及 V_POOL 各组）。
