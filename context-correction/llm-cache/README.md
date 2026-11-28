# llm-cache：llm_context 评测的大模型答案快照（GM3，2026-11-28）

`2026-11-28.jsonl`：从 open-guji-cv `output/llm_context_evalset/report_<provider>_<model>_<prompt>.json` 的逐题 `rows` 抽出的**已有真实答案**（glm-4-flash／glm-4-plus／qwen-plus，candidates 与 direct 两种提示词；mock 不收，解析失败的题不收）。没有为此重新在线问过。
题＝cv `output/llm_context_evalset/evalset.json` 的 100 题（殿本 vol01，现有策略判错的槽位），键是格号 `cell`（`vol01:页:列:格`），**还没有字格永久编号 u**；换图源重切后格号会变，需要时再按 (册,u) 补。
字段：kind=ctx_ruling、source=llm、cell、char（模型答的字）、model、provider、prompt_ver、in_candidates、raw（模型原文）。**无 conf**（当时的提示词不要求置信度）。
跑时请记本文件的 sha256（见 PR 描述）。
