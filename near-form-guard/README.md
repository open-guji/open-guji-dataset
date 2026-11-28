# near-form-guard：N01 形近字放行规则基准金标（GM3，2026-11-28）

按书一份 `<书id>/gold.tsv`（殿本 siku-zongmu、史記 988g3f0wsu、全唐文 995ejelvk0），共 1,905 格，全是人裁过的格。
列：书、册、格（页:列:格号）、类（A–E，库候选与参校字的关系）、参校字、库首位、库候选前3、真字(人裁)、真字=参校、真字=库首位。

来源：guji-manager `doc/参考/待审原因/near_form_guard/benchmark/gold_human.tsv`（2026-11 N01 放行规则研究，A24 建）按书拆开；
金标是人裁，不随算法变。用法：cv `eval/benches/near_form_admit.py`，`guji bench run near-form-admit --book <书id>`。
