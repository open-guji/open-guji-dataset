"""cut-frame 打分：score.py <items.jsonl> <产物根（含 <册>/cell_shrink/pNNNN.json）> [--split tune|blind]
预测框取 cell_shrink char_index 里同 (页,列,slot,sub) 的 bbox_page。只评 status in (ok, fixed)。"""
import json, sys, glob
from pathlib import Path
from collections import defaultdict
items = [json.loads(l) for l in open(sys.argv[1])]; root = Path(sys.argv[2])
split = sys.argv[sys.argv.index("--split") + 1] if "--split" in sys.argv else None
pred = {}
for f in glob.glob(str(root / "*/cell_shrink/p*.json")):
    vol = Path(f).parts[-3]; d = json.load(open(f))["char_index"]
    for c in d["columns"]:
        for ch in c["chars"]:
            if ch.get("bbox_page"): pred[(vol, d["page"], c["col"], ch["slot"], ch.get("sub"))] = ch["bbox_page"]
def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1])); i = ix * iy
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u else 0
vols = {k[0] for k in pred}
items = [r for r in items if r["vol"] in vols]  # 只评产物根里有的册
agg = defaultdict(lambda: [0, 0, 0.0, [0.0] * 4])
for r in items:
    if r["status"] not in ("ok", "fixed") or (split and r["split"] != split): continue
    p = pred.get((r["vol"], r["page"], r["col"], r["slot"], r["sub"])); g = r["tight"]
    for k in (r["book"], "all") + tuple("tag:" + t for t in r["tags"]) + ("end:" + r["end"],):
        a = agg[k]; a[0] += 1
        if p is None: continue
        a[1] += iou(p, g) >= 0.9; a[2] += iou(p, g)
        for i in range(4): a[3][i] += abs(p[i] - g[i])
for k, (n, ok, s, e) in sorted(agg.items()):
    print(f"{k:22s} 格 {n:4d}  IoU@0.9 {ok / n:.3f}  平均IoU {s / n:.3f}  边偏差px(左,上,右,下) " + ",".join(f"{v / n:.1f}" for v in e))
