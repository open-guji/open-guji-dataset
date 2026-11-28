"""小型标注集挑选（A24，2026-11-23，按 Sheldon 11-23 三条）：一册的人裁 → 按原图框绑到现行切分 → 对参校本分类。

用法：python decide-bench/tools/select_gold.py <ws> <册> <产物根/册> --out gold.jsonl [--dataset unified.jsonl] [--bind bind.json]

`--bind`：用 cv 绑定表（`feedback.bindings.book_bindings` 的输出，{事件 id: 行}）代替自算 IoU。换过图源的册（殿本 vol01
11-08 换 Commons 图）必须用它：旧锚由迁移锚接上，页表 rev 不符的事件 cv 不采信、表里没有。只认 valid／rebound
（及 unanchored 有 bound 的），其余不绑。

只收「人在网页或 artifact 上裁定」的格级 confirm（actor=user、target.step=seed_admit），去掉 source 含 vision（会话看图）、
「代写」的。每格取最新一条。绑定同 count_sources.py（事件框或 anchors 表框，IoU≥0.5 且次格 <0.2）。

分类（cls）：
- `dataset`：dataset 已有金标（char-groups unified，status=ok）且与最新人裁同字。
- `agree_ref`：人裁字＝参校本对位字（align_ref.align_char）。
- `override_ref`：人裁字≠参校本字，且有「明确推翻」的痕迹：待审原因是参校本差异类（ref_*、group_ref_dissent），
  或来自网站精校意见（备注多是迁移说明，不算）。
- `differ_unclear`：人裁字≠参校本字但没有上面的痕迹（不进金标，先报数）。
- `no_ref`：这格没有参校本对位字（不进金标，先报数）。
- `defect`：人裁为切坏／非字（另列，不进字的金标）。
"""
import re
import collections, glob, json, sys
from pathlib import Path
from guji_manager.datastore.d1conn import connect
_vn = lambda v: str(int(re.search(r"\d+", str(v)).group())) if re.search(r"\d+", str(v)) else str(v)   # 册号按数值比（11-27 册号位数统一）

ws, vol, prod = sys.argv[1:4]
arg = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None
prod = Path(prod)
J = lambda v: json.loads(v) if isinstance(v, str) else (v or {})
REF_REASONS = {"ref_mismatch", "ref_ocr_diff", "ref_final_diff", "ref_replaced", "group_ref_dissent", "ref_gap", "ref_lacuna"}
c = connect()
anch = {e: J(d).get("anchor") for e, d in c.execute("select event, doc from anchors where ws=? and book=?", [ws, vol]).fetchall()}
rows = c.execute("select id, ts, batch, payload, target from events where ws=? and book=? and kind='confirm' and actor='user' "
                 "and json_extract(target,'$.step')='seed_admit' order by ts", [ws, vol]).fetchall()


def box(q):
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    return [min(xs), min(ys), max(xs), max(ys)]


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    i = ix * iy
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u > 0 else 0.0


_cells = {}


def page_cells(pg):
    if pg not in _cells:
        f, out = prod / "row_segment" / f"p{pg:04d}.json", []
        if f.exists():
            for col in json.load(open(f))["cells"]["columns"]:
                for cl in col.get("cells") or []:
                    if cl.get("quad_page") and cl.get("kind") not in ("blank", None):
                        out.append((f"{vol}:{pg}:{col['col']}:{cl['slot']}{cl.get('sub') or ''}", box(cl["quad_page"])))
        _cells[pg] = out
    return _cells[pg]


bind = json.load(open(arg("--bind"))) if arg("--bind") else None
stat = collections.Counter()
latest = {}
for eid, ts, batch, pl, tg in rows:
    pl, tg = J(pl), J(tg)
    src = str(pl.get("source") or "")
    if "vision" in src or "代写" in src:
        stat["去掉:看图或代写"] += 1
        continue
    key, v = tg.get("key"), pl.get("v")
    ch = pl.get("shape") or pl.get("reading")
    if not key or not v or (v == "confirm" and not ch):
        continue
    if bind is not None:
        r = bind.get(eid)
        k = r and r.get("bound") if r and (r["status"] in ("valid", "rebound") or r["status"] == "unanchored") else None
        if not k:
            stat["未绑:绑定表" + (r["status"] if r else "无（rev 不符等）")] += 1
            continue
        pg = int(k.split(":")[1])
        bb = dict(page_cells(pg)).get(k)
        latest[k] = dict(event=eid, ts=ts, batch=batch, v=v, char=ch, bbox=bb, from_key=key,
                         reason=pl.get("pending_reason"), note=pl.get("note") or "", source=src, via=pl.get("via"))
        continue
    a = (tg.get("anchor") or {}).get("bbox") or (anch.get(eid) or {}).get("bbox")
    if not a:
        stat["未绑:无框"] += 1
        continue
    pg = int(key.split(":")[1])
    cand = sorted(((iou(a, b), k, b) for k, b in page_cells(pg)), reverse=True)
    if not cand or cand[0][0] < 0.5 or (len(cand) > 1 and cand[1][0] >= 0.2):
        stat["未绑:框对不上"] += 1
        if cand:
            stat[f"  对不上:top{min(9,int(cand[0][0]*10))}"] += 1
            if cand[0][0] >= 0.5:
                stat["  对不上:次格≥0.2"] += 1
        continue
    latest[cand[0][1]] = dict(event=eid, ts=ts, batch=batch, v=v, char=ch, bbox=cand[0][2], from_key=key,
                              reason=pl.get("pending_reason"), note=pl.get("note") or "", source=src, via=pl.get("via"))

ds = {}
if arg("--dataset"):
    for ln in open(arg("--dataset")):
        d = json.loads(ln)
        if _vn(d.get("book")) == _vn(vol) and d.get("status") == "ok":
            ds[d["id"]] = d.get("form")
            if d.get("event"):
                ds[d["event"]] = d.get("form")

ref, algo = {}, {}
for f in glob.glob(str(prod / "align_ref" / "p*.json")):
    for x in json.load(open(f))["align_ref"].get("chars") or []:
        if x.get("align_char"):
            ref[x["id"]] = x["align_char"]
for f in glob.glob(str(prod / "seed_admit" / "p*.json")):
    for col in json.load(open(f))["seed_admit"]["columns"]:
        for x in col.get("chars") or []:
            algo[x["id"]] = (x.get("char"), x.get("channel"), x.get("admit"))

out = []
for k, h in sorted(latest.items()):
    r = ref.get(k)
    if h["v"] != "confirm":
        cls = "defect"
    elif ds.get(h["event"]) == h["char"] or ds.get(h["from_key"]) == h["char"]:
        cls = "dataset"
    elif r is None:
        cls = "no_ref"
    elif r == h["char"]:
        cls = "agree_ref"
    elif (h["reason"] in REF_REASONS) or "网站精校意见" in h["source"]:   # 备注多是迁移说明，不算推翻理由（11-23）
        cls = "override_ref"
    else:
        cls = "differ_unclear"
    stat[cls] += 1
    a = algo.get(k, (None, None, None))
    out.append({"id": k, "book_ws": ws, "vol": vol, "bbox": h["bbox"], "space": "raw_page_px@top-right", "char": h["char"] if h["v"] == "confirm" else None,
                "defect": h["v"] if h["v"] != "confirm" else None, "cls": cls, "ref": r, "pack_char": a[0], "pack_channel": a[1],
                "event": h["event"], "from_key": h["from_key"], "batch": h["batch"], "reason": h["reason"], "note": h["note"][:120], "source": h["source"][:80]})
if arg("--out"):
    Path(arg("--out")).write_text("".join(json.dumps(o, ensure_ascii=False) + "\n" for o in out))
print(json.dumps({"ws": ws, "vol": vol, "人裁事件": len(rows), "绑上的格": len(latest), **stat}, ensure_ascii=False))
