# wyu 王玉：L1 规则收窄（2026-10-26，A24「压低王玉送审」）

- `labels.jsonl`：58 格逐格读上下文的判读（kind=reading，`by=claude-a24-wyu`），每条写依据（why）与原标注（note：整理本字、产物放行字）。不同义形近按文意，未看刻形。
- `回放-2026-10-26.jsonl`：`research/m7/ctx/replay_groups.py` 新规则＋中心库 L2 表（wyu-l2-1，只覆盖 vol04–10）对 97 册（vol02–99，不含 vol06）回放，只留全册任务表 59 格和判读格。

规则改动在 open-guji-cv `config/groups/wyu/rules.yaml`，结论与数字见 cv `doc/字组/wyu.md`。
