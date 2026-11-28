"""规则补例的抽审结果追加进 small/items.jsonl（CV4，2026-11-23）。

用法：python decide-bench/tools/append_fill.py <ritems-all.jsonl> <结果 labels 目录> <items.jsonl> --prod 03=<产物根/03> --prod 004=… --prod vol01=…
这批格没有旧人裁：页上显示算法字，Sheldon 点对＝金标就是算法字，改字＝填的字，看不清＝不收。
anchor.bbox 取产物根 row_segment 的 quad_page 外接框。stratum＝「规则补例」，label_origin＝human_audit。
"""
import glob, json, sys
from pathlib import Path

ritems, resdir, items = sys.argv[1:4]
prods = dict(sys.argv[i + 1].split("=", 1) for i, a in enumerate(sys.argv) if a == "--prod")
WS = {"03": ("988g3f0wsu", "史記"), "004": ("995ejelvk0", "全唐文"), "vol01": ("siku-zongmu", "殿本")}
its = {json.loads(l)["id"]: json.loads(l) for l in open(ritems)}
have = {json.loads(l)["id"] for l in open(items)}
_box = {}


def bbox(vol, key):
    pg = int(key.split(":")[1])
    if (vol, pg) not in _box:
        d = json.load(open(Path(prods[vol]) / "row_segment" / f"p{pg:04d}.json"))
        m = {}
        for col in d["cells"]["columns"]:
            for c in col.get("cells") or []:
                if c.get("quad_page"):
                    q = c["quad_page"]; xs, ys = [p[0] for p in q], [p[1] for p in q]
                    m[f"{vol}:{pg}:{col['col']}:{c['slot']}{c.get('sub') or ''}"] = [round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1)]
        _box[(vol, pg)] = m
    return _box[(vol, pg)].get(key)


new = []
for f in glob.glob(str(Path(resdir) / "i_*.json")):
    d = json.load(open(f)); d = d.get("data", d); v = d.get("_v") or {}
    it = its.get(d["id"])
    if not it or v.get("sp") == "unclear":
        continue
    ch = (v.get("pick") or v.get("other")) if (v.get("wrong") or (v.get("pick") and v["pick"] != it["pre"])) else it["pre"]
    if not ch:
        continue
    key = it["id"]; vol = key.split(":")[0]; ws, title = WS[vol]
    _, pg, col, slot = key.split(":", 3)
    rid = f"{ws}:{key}"
    if rid in have:
        continue
    rule = it["kind"].split("｜", 1)[1]
    new.append({"id": rid, "anchor": {"ws": ws, "book": vol, "page": int(pg), "key_at_freeze": key,
                                      "space": "raw_page_px@top-right", "bbox": bbox(vol, key)},
                "input": {"ref_char": it.get("ref_char") or None, "cls": "rule_fill", "rule_at_freeze": rule, "algo_at_freeze": it["pre"]},
                "expected": {"char": ch}, "label_origin": "human_audit", "stratum": "规则补例",
                "status": "active", "book_title": title, "source_events": [],
                "history": [{"ts": "2026-11-23", "change": "created",
                             "why": "decide-bench 规则补例（CV4）：例子不足的规则从算法结果随机补，Sheldon 抽审" + ("改字" if ch != it["pre"] else "点对")}]})
with open(items, "a") as fo:
    fo.write("".join(json.dumps(n, ensure_ascii=False) + "\n" for n in new))
print("追加", len(new), "缺框", sum(1 for n in new if not n["anchor"]["bbox"]))
