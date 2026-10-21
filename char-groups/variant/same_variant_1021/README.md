# 同字异体审查（2026-10-21）

殿本 vol04–10（cv0.5.4、corpus 12）送审格里，库首选与整理本字互为异体的 45 格：影子门否决 37、简繁错位 8。
sheldon 在审查页里选「库形 / 整理本形 / 其它」。

`labels.jsonl` 字段：`cell`（格号）、`lib`（库首选）、`ref`（整理本字）、`choice`（lib/ref/other）、`char`（定下的字，other 且未记具体字为 null）、`kind`、`src`、`note`。

- `src=click`：sheldon 在页面里点过（7 格）。
- `src=prefill_accepted`：页面按机器判断预选，sheldon 说「其他都标完了」，按接受预选记（38 格）。比 click 弱一档，用作评测金标时要注意。
- vol09:75:7:17 的字由 sheldon 在对话里更正为 𫝔。

结论：影子门 pick（整理本字）在这 37 格里对 33、错 4（𦌐罹 2、堯→𫝔、尸），没有可区分的特征，不能据此放行。
