"""小型集写成 dataset 分片 decide-bench/small（CV4，2026-11-23）。

用法：python decide-bench/tools/build_shard.py <final-small.jsonl> <分片目录> --rerun 史記=<关人裁重跑产物/册> --rerun 全唐文=… --rerun 殿本=…

items.jsonl：每格一条（统一金标信封）；anchor 是原图框（raw_page_px@top-right，row_segment quad 外接框），按框对格，不随切分改号。
report.json：冻结时关人裁重跑的基线，按书×规则×结果计数（放对／放错字／放成异体／拦住·首选对／拦住·首选错）。
"""
import collections, glob, json, sys
from pathlib import Path

final, outdir = sys.argv[1], Path(sys.argv[2])
reruns = dict(sys.argv[i + 1].split("=", 1) for i, a in enumerate(sys.argv) if a == "--rerun")
BOOK = {"988g3f0wsu": "史記", "995ejelvk0": "全唐文", "siku-zongmu": "殿本", "99k3i35yww": "脉经"}
FOLD = [set("己已巳"), set("日曰")]
try:
    from open_guji_cv.variants import are_variants as _cv_var
except Exception:  # noqa: BLE001
    _cv_var = lambda a, b: False
# cv variants 图之外，再认 cv config/hanzi/core/edges.tsv 里 relation=variant 的对（變𬽠、策䇿 这类 cv 图里没有，11-23 Sheldon 复核）
_EDGES = set()
_ef = Path(__file__).resolve().parents[5] / "open-guji-cv/config/hanzi/core/edges.tsv"
for _p in [_ef, Path("/home/user/open-guji-cv/config/hanzi/core/edges.tsv")]:
    if _p.exists():
        for _l in open(_p, encoding="utf-8"):
            _t = _l.split("\t")
            if len(_t) > 2 and _t[2] == "variant":
                _EDGES.add((_t[0], _t[1])); _EDGES.add((_t[1], _t[0]))
        break
are_variants = lambda a, b: bool(a and b) and (_cv_var(a, b) or (a, b) in _EDGES)
same = lambda a, b: a == b or any(a in g and b in g for g in FOLD)

algo = {}
for bk, root in reruns.items():
    for f in glob.glob(str(Path(root) / "seed_admit" / "p*.json")):
        for col in json.load(open(f))["seed_admit"]["columns"]:
            for x in col.get("chars") or []:
                r = f"admit:{x.get('channel')}" if x.get("admit") else \
                    "review:" + str((((x.get("evidence") or {}).get("demoted_from") or {}).get("by")) or ((x.get("doubts") or ["?"])[0]))
                algo[(bk, x["id"])] = (x.get("char"), bool(x.get("admit")), r)

items, rep = [], collections.Counter()
for l in open(final):
    g = json.loads(l)
    if not g.get("final"):
        continue
    bk = BOOK[g["book_ws"]]
    _, pg, col, slot = g["id"].split(":", 3)
    reviewed = g["review"] != "未审"
    items.append({
        "id": f"{g['book_ws']}:{g['id']}",
        "anchor": {"ws": g["book_ws"], "book": g["vol"], "page": int(pg), "key_at_freeze": g["id"],
                   "space": "raw_page_px@top-right", "bbox": [round(v, 1) for v in g["bbox"]]},
        "input": {"ref_char": g.get("ref"), "cls": g["cls"], "batch": g.get("batch"), "reason": g.get("reason")},
        "expected": {"char": g["final"]},
        "label_origin": "human_audit" if reviewed or g.get("fix") else "human",
        "stratum": ("抽审·分层" if reviewed else "人裁·未抽审") + ("·书级改字" if g.get("fix") == "book_rule" else ""),
        "status": "active", "book_title": bk,
        "source_events": [g["event"]],
        "history": [{"ts": "2026-11-23", "change": "created",
                     "why": "decide-bench 小型集（CV4）；" + {"未审": "人裁与参校本一致或明确推翻", "ok": "Sheldon 抽审点对",
                             "page_ok": "Sheldon 抽审翻页认下", "fixed": "Sheldon 抽审改字"}[g["review"]]
                     + ("；按书规则改字（全唐文 內絕勳虛茲→内絶勲虚兹）" if g.get("fix") == "book_rule" else "")}],
    })
    a = algo.get((bk, g["id"]))
    if a:
        ch, adm, r = a
        oc = ("放对" if same(ch, g["final"]) else "放成异体" if ch and are_variants(ch, g["final"]) else "放错字") if adm else \
             ("拦住·首选对" if ch and same(ch, g["final"]) else "拦住·首选错")
        rep[(bk, r, oc)] += 1
outdir.mkdir(parents=True, exist_ok=True)
(outdir / "items.jsonl").write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items))
tab = collections.defaultdict(lambda: collections.defaultdict(dict))
for (bk, r, oc), n in rep.items():
    tab[bk][r][oc] = n
(outdir / "report.json").write_text(json.dumps({"baseline": "cv dev 73133d89（v0.9.0 前）关人裁重跑 seed_admit，2026-11-23",
                                                "by_book_rule": tab}, ensure_ascii=False, indent=1))
print(len(items), collections.Counter(i["book_title"] for i in items), collections.Counter(i["label_origin"] for i in items))
tot = collections.Counter()
for (bk, r, oc), n in rep.items():
    tot[(bk, oc)] += n
print(sorted(tot.items()))
