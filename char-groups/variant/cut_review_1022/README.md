# 切分对比错例核对（2026-10-22，IDS 与切分线程）

按册留出时，人标切线／自动缝／先验折线三种切法里任一判错的 25 格（叙敘 7、教敎 7、參㕘叅 6、絕絶 5）。
sheldon 看过核对页后答复：**标注是对的，切线也都是对的，错在部件识别**（整页确认，没有逐格改）。
`labels.jsonl` 每行：`id`、`group`、`form`（现标注，确认无误）、`label_ok`/`cut_ok`、`machine`（各切法当时判成的字）。
原图与切线在 `variant/<group>/crops/`、`variant/<group>/labels.jsonl`。

中心库：sheldon 10-22 说「推」后写成 `confirm` 事件，批次 `H-M7-cutreview-confirm-1022`（24 条，siku-zongmu rev 92044），副本见 `events_H-M7-cutreview-confirm-1022.jsonl`。
vol03:80:3:21 没写：R2 没有 vol03 产物包，造不了锚，怕重切后挂错格。事件尚未 route／消费（下次 `guji events route` 时进金标与字形库）。
