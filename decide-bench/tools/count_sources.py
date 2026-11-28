"""金标来源试点计数（A24，2026-11-23）：每书一册取 5 页，把人裁、AI 判定按原图框绑到现行切分，再按格数四类来源。

用法：python decide-bench/tools/count_sources.py <ws> <册> <产物根/册> <book-text char.json> [--pages 1,2,3] [--dump out.jsonl]
绑定：事件自带 target.anchor.bbox，或中心库 anchors 表（补锚档）里有框 → 与产物包 row_segment 的 quad_page 求 IoU，
最大的那格 IoU≥0.5 且第二格 <0.2 才绑上（同编号 valid，别的编号 rebound）；没有框的老事件不绑（unanchored）。
不给 --pages 时：绑上的人裁最密 3 页＋其余有 seed_admit 的页里按种子随机 2 页。
四类：① 有人裁；② 无人裁、AI 判定与 book-text 同字；③ 无人裁、有 AI 但与 book-text 不同；④ 只有算法（无人裁、无 AI）。
另报：人裁与算法字不同、book-text 与算法字不同、整理本对位字与算法字不同的格。
"""
import collections, glob, json, random, sys
from pathlib import Path
from guji_manager.datastore.d1conn import connect

ws, vol, prod, char_json = sys.argv[1:5]
arg = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None
prod = Path(prod)
c = connect()
J = lambda v: json.loads(v) if isinstance(v, str) else (v or {})
anch = {e: J(d).get("anchor") for e, d in c.execute("select event, doc from anchors where ws=? and book=?", [ws, vol]).fetchall()}
rows = c.execute("select id, actor, ts, payload, target from events where ws=? and book=? and kind='confirm' "
                 "and json_extract(target,'$.step')='seed_admit' order by ts", [ws, vol]).fetchall()


def box(q):
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    return min(xs), min(ys), max(xs), max(ys)


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    i = ix * iy
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u > 0 else 0.0


cells_cache = {}


def page_cells(pg):
    if pg not in cells_cache:
        f = prod / "row_segment" / f"p{pg:04d}.json"
        out = []
        if f.exists():
            for col in json.load(open(f))["cells"]["columns"]:
                for cl in col.get("cells") or []:
                    if cl.get("quad_page") and cl.get("kind") not in ("blank", None):
                        out.append((f"{vol}:{pg}:{col['col']}:{cl['slot']}{cl.get('sub') or ''}", box(cl["quad_page"])))
        cells_cache[pg] = out
    return cells_cache[pg]


stat = collections.Counter()
human, ai = {}, {}
for eid, actor, ts, pl, tg in rows:
    pl, tg = J(pl), J(tg)
    key = tg.get("key")
    v = pl.get("v")
    ch = pl.get("shape") or pl.get("reading")
    lab = ch if v == "confirm" and ch else (f"<{v}>" if v and v != "confirm" else None)
    if not key or lab is None:
        continue
    who = "人裁" if actor == "user" else "AI"
    a = (tg.get("anchor") or {}).get("bbox") or ((anch.get(eid) or {}).get("bbox"))
    if not a:
        stat[f"{who}:无框未绑"] += 1
        continue
    pg = int(key.split(":")[1])
    cand = sorted(((iou(a, b), k) for k, b in page_cells(pg)), reverse=True)
    if not cand or cand[0][0] < 0.5 or (len(cand) > 1 and cand[1][0] >= 0.2):
        stat[f"{who}:框对不上"] += 1
        continue
    bound = cand[0][1]
    stat[f"{who}:{'同号' if bound == key else '改号'}"] += 1
    (human if actor == "user" else ai)[bound] = (lab, eid)

have = sorted(int(Path(f).stem[1:]) for f in glob.glob(str(prod / "seed_admit" / "p*.json")))
if arg("--pages"):
    pages = [int(x) for x in arg("--pages").split(",")]
else:
    dens = collections.Counter(int(k.split(":")[1]) for k in human)
    hard = [p for p, _ in dens.most_common() if p in have][:3]
    rest = [p for p in have if p not in hard]
    pages = sorted(hard + random.Random(f"0:{vol}").sample(rest, 2))
bt = {}
for p in json.load(open(char_json))["pages"]:
    for col in p["columns"]:
        for cell in col["cells"]:
            bt[f"{vol}:{cell['a']}"] = cell.get("c")
cnt = collections.Counter()
dump = open(arg("--dump"), "w") if arg("--dump") else None
for pg in pages:
    sa = json.load(open(prod / "seed_admit" / f"p{pg:04d}.json"))["seed_admit"]
    try:
        ar = json.load(open(prod / "align_ref" / f"p{pg:04d}.json"))["align_ref"]
        ref = {x["id"]: x.get("align_char") for x in ar.get("chars") or []}
    except FileNotFoundError:
        ref = {}
    for col in sa["columns"]:
        for x in col.get("chars") or []:
            k, a = x["id"], x.get("char")
            b = bt.get(k)
            h, m = human.get(k, (None,))[0], ai.get(k, (None,))[0]
            cnt["格"] += 1
            cnt["放行" if x.get("admit") else "人审"] += 1
            if h:
                cls = "①人裁"
                if h != a:
                    cnt["①中人裁≠算法字"] += 1
            elif m:
                cls = "②AI=book-text" if b is not None and m == b else "③AI≠book-text"
            else:
                cls = "④只有算法"
            cnt[cls] += 1
            if b is not None and b != a:
                cnt["book-text≠算法字"] += 1
            if ref.get(k) and ref[k] != a:
                cnt["整理本≠算法字"] += 1
            if dump:
                dump.write(json.dumps({"id": k, "cls": cls, "algo": a, "admit": x.get("admit"), "channel": x.get("channel"),
                                       "human": h, "ai": m, "booktext": b, "ref": ref.get(k)}, ensure_ascii=False) + "\n")
print(json.dumps({"ws": ws, "vol": vol, "pages": pages, "绑定": dict(stat), **cnt}, ensure_ascii=False))
