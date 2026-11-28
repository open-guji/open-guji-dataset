"""收回抽审结果，定出小型集金标（CV4，2026-11-23）。

用法：python decide-bench/tools/apply_review.py <items-all.jsonl> <结果目录(labels/*.json)> <gold-*.jsonl …> --out final.jsonl [--book-rule 全唐文=內:内,絕:絶,勳:勲,虛:虚]

- 审过的格：点「对」或翻页认下（how=page_ok）→ 金标照旧；点「改作／填字」→ 金标改成填的字；「看不清」→ 剔除。
- `--book-rule`：Sheldon 按书定的整批改字（11-23：全唐文 內絕勳虛 一律作 内絶勲虚，「有的可能漏点了」），
  对该书全部金标格生效，记 `fix=book_rule`。
- 输出每格：原 gold 字段 ＋ final（最终金标字）、review（ok/page_ok/fixed/unclear/未审）、fix（来源）。
"""
import glob, json, sys
from pathlib import Path

arg = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None
items = {json.loads(l)["id"]: json.loads(l) for l in open(sys.argv[1])}
res = {}
for f in glob.glob(str(Path(sys.argv[2]) / "i_*.json")):
    d = json.load(open(f)); d = d.get("data", d)
    v, it = d.get("_v") or {}, items.get(d["id"])
    if not it:
        continue
    if v.get("sp") == "unclear":
        res[d["id"]] = ("unclear", None)
    elif v.get("wrong") or (v.get("pick") and v["pick"] != it["pre"]):
        res[d["id"]] = ("fixed", v.get("pick") or v.get("other"))
    else:
        res[d["id"]] = ("page_ok" if d.get("how") == "page_ok" else "ok", it["pre"])
BOOK = {"988g3f0wsu": "史記", "995ejelvk0": "全唐文", "siku-zongmu": "殿本"}
rules = {}
for r in ([arg("--book-rule")] if arg("--book-rule") else []):
    bk, m = r.split("=")
    rules[bk] = dict(p.split(":") for p in m.split(","))
golds = [a for a in sys.argv[3:] if a.endswith(".jsonl") and a != arg("--out")]
out, stat = [], {}
for gf in golds:
    for l in open(gf):
        g = json.loads(l)
        if g.get("defect") or g["cls"] not in ("agree_ref", "override_ref", "dataset"):
            continue
        st, ch = res.get(g["id"], ("未审", g["char"]))
        g.update(final=ch, review=st, fix="review" if st == "fixed" else None)
        bk = BOOK.get(g["book_ws"])
        m = rules.get(bk) or {}
        if ch in m:
            g.update(final=m[ch], fix="book_rule")
        if st == "unclear":
            g["final"] = None
        k = (bk, g["review"], g["fix"])
        stat[str(k)] = stat.get(str(k), 0) + 1
        out.append(g)
Path(arg("--out")).write_text("".join(json.dumps(o, ensure_ascii=False) + "\n" for o in out))
print(json.dumps(stat, ensure_ascii=False, indent=0))
