# jue（絕絶）U-Net 权重

- `unet_v1.npz`（sha256 `ec9e2983c8ffb3f1`）：絕絶 左右向 2 类 U-Net，只用本组 `labels.jsonl` 39 格人标切线训（60 epoch，seed 1），cv#397（10-22 通用 IDS 判法）。
- 线上用的是 CV 仓 `config/groups/jue/unet.npz`，与此份逐字节相同。
- R2 备份：`derived/ids-unet/jue/unet_v1.npz`（main 桶，`datastore.packs.fetch_file` 取）。
- 重训：`python -m open_guji_cv.groups.ids_online build jue --dataset <本仓>`（需要 torch）。
