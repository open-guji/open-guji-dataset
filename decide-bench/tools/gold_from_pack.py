"""从冻结快照自己的人裁格取金标（CV4，2026-11-24，大型层用）。

用法：python decide-bench/tools/gold_from_pack.py <ws> <册> <快照/册> --out gold.jsonl

快照 seed_admit 里 channel=human 的格＝冻结时 cv 已采信、落到格上的人裁。殿本换过图源（11-08 起 vol01 等），
多数旧事件页表 rev 不符、现行绑定表绑不上（vol02 8,430 条只绑上 161），但冻结时的包里已经按当时的绑定落了字，
大型层允许少量错，就用它。框取快照 row_segment 的格框。输出格式同 select_gold.py（event 为空）。
"""
import glob, json, sys
from pathlib import Path

ws, vol, prod = sys.argv[1:4]
out = sys.argv[sys.argv.index("--out") + 1]
prod = Path(prod)


def box(q):
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    return [min(xs), min(ys), max(xs), max(ys)]


bb = {}
for f in glob.glob(str(prod / "row_segment" / "p*.json")):
    pg = int(Path(f).stem[1:])
    for col in json.load(open(f))["cells"]["columns"]:
        for cl in col.get("cells") or []:
            if cl.get("quad_page"):
                bb[f"{vol}:{pg}:{col['col']}:{cl['slot']}{cl.get('sub') or ''}"] = box(cl["quad_page"])
ref = {}
for f in glob.glob(str(prod / "align_ref" / "p*.json")):
    for x in json.load(open(f))["align_ref"].get("chars") or []:
        if x.get("align_char"):
            ref[x["id"]] = x["align_char"]
rows, n_nobox = [], 0
for f in sorted(glob.glob(str(prod / "seed_admit" / "p*.json"))):
    for col in json.load(open(f))["seed_admit"]["columns"]:
        for x in col.get("chars") or []:
            if x.get("channel") != "human" or not x.get("char"):
                continue
            k = x["id"]
            if k not in bb:
                n_nobox += 1
                continue
            r = ref.get(k)
            cls = "no_ref" if r is None else "agree_ref" if r == x["char"] else "differ_unclear"
            rows.append({"id": k, "book_ws": ws, "vol": vol, "bbox": bb[k], "space": "raw_page_px@top-right",
                         "char": x["char"], "defect": None, "cls": "包内人裁·" + cls, "ref": r, "event": None,
                         "batch": None, "reason": None, "source": "pack_human"})
open(out, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
import collections
print(json.dumps({"vol": vol, "包内人裁格": len(rows), "无框": n_nobox, **collections.Counter(r["cls"] for r in rows)}, ensure_ascii=False))
