"""大型层分片 decide-bench/large（CV4，2026-11-24）：几整册的全部人裁当金标（允许少量错），按原图框对格。

用法：python decide-bench/tools/build_large.py <分片目录> gold-01.jsonl gold-02.jsonl … [--book-rule "全唐文=內:内,絕:絶,…"]

输入是 select_gold.py 的输出（--bind 用 cv 绑定表绑到冻结快照）。与小型层不同：
- 收全部有字的人裁（agree_ref／override_ref／dataset／no_ref／differ_unclear），不只「＝参校本或明确推翻」；切坏／非字不收。
- 不逐格人审，label_origin 一律 human；放行准不准另靠放行格随机抽查（char_grid）估。
"""
import collections, json, sys
from pathlib import Path

out = Path(sys.argv[1])
args = sys.argv[2:]
rule = {}
if "--book-rule" in args:
    i = args.index("--book-rule")
    bk, m = args[i + 1].split("=", 1)
    rule[bk] = dict(p.split(":") for p in m.split(","))
    del args[i:i + 2]
BOOK = {"988g3f0wsu": "史記", "995ejelvk0": "全唐文", "siku-zongmu": "殿本", "99k3i35yww": "脉经"}
items, cnt = [], collections.Counter()
for f in args:
    for l in open(f):
        g = json.loads(l)
        if not g.get("char") or g.get("defect"):
            continue
        bk = BOOK[g["book_ws"]]
        ch = g["char"]
        fixed = rule.get(bk, {}).get(ch)
        _, pg, col, slot = g["id"].split(":", 3)
        items.append({
            "id": f"{g['book_ws']}:{g['id']}",
            "anchor": {"ws": g["book_ws"], "book": g["vol"], "page": int(pg), "key_at_freeze": g["id"],
                       "space": "raw_page_px@top-right", "bbox": [round(v, 1) for v in g["bbox"]]},
            "input": {"ref_char": g.get("ref"), "cls": g["cls"], "batch": g.get("batch"), "reason": g.get("reason")},
            "expected": {"char": fixed or ch},
            "label_origin": "human",
            "stratum": (g["cls"] if g["cls"].startswith("包内") else "人裁·" + g["cls"]) + ("·书级改字" if fixed else ""),
            "status": "active", "book_title": bk,
            "source_events": [g["event"]] if g.get("event") else [],
            "history": [{"ts": "2026-11-24", "change": "created",
                         "why": "decide-bench 大型层（CV4）：整册全部人裁，未逐格抽审" + ("；按书规则改字" if fixed else "")}],
        })
        cnt[(bk, g["vol"], g["cls"])] += 1
out.mkdir(parents=True, exist_ok=True)
(out / "items.jsonl").write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items))
print(len(items))
for k, n in sorted(cnt.items()):
    print(*k, n)
