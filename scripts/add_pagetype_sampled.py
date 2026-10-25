"""page-type 金标增补（A21 2026-10-25）：
1) vol03–10 抽样 66 页入库（23 页逐页人标，其余按 Sheldon「跟着推荐」确认）；
2) blank 并入 body（空白页是正文的一种），3 个 vol01 blank 改 body；
3) 九列格子页加「字写到第几列」四个字段（机器测列带墨量，阈值 2.0%）。

用法：python scripts/add_pagetype_sampled.py <measure.jsonl>
measure.jsonl 每行：vol,page,n_verticals,col_ink（open-guji-cv 同口径测量，见 page-type/README.md「字写到第几列」）。
标注表只在本文件 LABELS；改标注改这里重跑。"""
import json, re, sys
from pathlib import Path

THR, WEAK = 2.0, 1.0
D = Path(__file__).resolve().parent.parent / "page-type"
TS = "2026-10-25T00:00:00Z"
PAGES = {"vol03": 110, "vol04": 221, "vol05": 188, "vol06": 150, "vol07": 135, "vol08": 69, "vol09": 265, "vol10": 175}

# (册, 页): (页型, 来源) 来源 human＝逐页人标；confirmed＝按推荐、Sheldon 确认
LABELS = {}
def put(v, ps, t, o): [LABELS.__setitem__((v, p), (t, o)) for p in ps]
HUMAN = {("vol03",1):"cover",("vol03",2):"label",("vol03",35):"body",("vol03",36):"body",("vol03",102):"body",("vol03",28):"body",
 ("vol04",1):"cover",("vol04",2):"label",("vol04",129):"label",("vol04",64):"body",
 ("vol05",1):"cover",("vol05",2):"label",("vol05",106):"body",("vol06",1):"cover",("vol06",2):"label",("vol06",88):"body",
 ("vol06",149):"body",("vol07",1):"cover",("vol07",91):"body",("vol08",1):"cover",("vol09",1):"cover",("vol09",224):"body",("vol10",1):"cover"}
for k, t in HUMAN.items(): LABELS[k] = (t, "human")
put("vol07", [90], "body", "human")   # Sheldon 10-25 明说：vol07/90 是正文
CONF = {"vol03":[71,48],"vol04":[150,96,8,107,22],"vol05":[105,55,82,91,78,154],"vol06":[69,94,14,107,8],
        "vol07":[38,120,100,39,76,15],"vol08":[38,30,54,35,49,47],"vol09":[170,22,17,141,130,80],"vol10":[134,162,130,157,150,173]}
for v, ps in CONF.items(): put(v, ps, "body", "confirmed")
assert len(LABELS) == 66, len(LABELS)

meas = {}
for l in open(sys.argv[1], encoding="utf-8"):
    r = json.loads(l)
    if r.get("n_verticals", 0) >= 10: meas[(r["vol"], r["page"])] = r["col_ink"]

def fields(ci):
    txt = [i + 1 for i, v in enumerate(ci) if v >= THR]
    return {"last_text_col": max(txt) if txt else 0, "text_col_count": len(txt), "col_ink": ci,
            "weak_cols": [i + 1 for i, v in enumerate(ci) if WEAK <= v < THR]}

MEASURE = {"measure": "列带(距两侧列线各22%)墨量%，右起1=最右；有字阈值2.0%，弱列1.0–2.0%；机器测量，非逐字目视"}
items = [json.loads(l) for l in open(D / "items.jsonl", encoding="utf-8")]
flat = json.loads((D / "expected.json").read_text(encoding="utf-8"))
byid = {i["id"]: i for i in items}

# 1) 新增 66 页
nrand = {}
for (v, p), (t, o) in LABELS.items():
    if t == "body": nrand[v] = nrand.get(v, 0) + 1
for (v, p), (t, o) in LABELS.items():
    iid = f"{v}:{p}"
    assert iid not in byid
    it = {"anchor": {"book": v, "page": p}, "expected": {"page_type": t},
          "history": [{"change": "added", "ts": TS, "why": "vol03–10 抽样入库（A21）；" + ("逐页人标" if o == "human" else "按推荐、Sheldon 确认")}],
          "id": iid, "input": {"note": None, "sample_batch": "vol03-10-2026-10-25"},
          "label_origin": "human", "source_events": [], "status": "active"}
    if t == "body":
        it["stratum"] = "抽样·随机"
        it["stratum_weight"] = round((PAGES[v] - 3) / nrand[v], 2)   # 近似：册页数去掉人选的封面/题签后的占比
    else:
        it["stratum"] = "人选·非正文"; it["stratum_weight"] = 1.0
    items.append(it); byid[iid] = it
    flat.append({"book": v, "page": str(p), "page_type": t, "label_origin": "human", "note": None, "schema_version": 1,
                 "stratum": it["stratum"], "stratum_weight": it["stratum_weight"]})

# 2) blank → body
for it in items:
    if it["expected"]["page_type"] == "blank":
        it["expected"]["page_type"] = "body"
        it["history"].append({"change": "relabel", "ts": TS, "why": "空白页是正文的一种（Sheldon 2026-10-25）：blank 并入 body，空白由 last_text_col=0 表示"})
for r in flat:
    if r["page_type"] == "blank": r["page_type"] = "body"

# 3) 新字段
fl = {(r["book"], str(r["page"])): r for r in flat}
n = 0
for it in items:
    k = (it["anchor"]["book"], it["anchor"]["page"])
    if k in meas and it["expected"]["page_type"] in ("body", "toc", "roster"):
        f = fields(meas[k]); it["expected"].update(f); it["input"].update(MEASURE)
        fl[(k[0], str(k[1]))].update(f); n += 1
(D / "items.jsonl").write_text("".join(json.dumps(i, ensure_ascii=False, sort_keys=True) + "\n" for i in items), encoding="utf-8")
txt = json.dumps(flat, ensure_ascii=False, indent=1)
txt = re.sub(r'\[\s+([-\d., \s]*?)\s+\]', lambda m: "[" + re.sub(r"\s+", " ", m.group(1)) + "]", txt)   # 数值列表压成一行
(D / "expected.json").write_text(txt + "\n", encoding="utf-8")
print("items", len(items), "with fields", n)
