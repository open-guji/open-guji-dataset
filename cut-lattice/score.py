"""cut-lattice 逐线打分（A 层的现役切法，CV2 2026-11-26）：拿一份 row_segment 产物量金标切线对上几条。

    python cut-lattice/score.py --pred <产物根> [--books shiji,qtw] [--split tune|blind|all] [--against <另一产物根>] [--json out.json]

产物根下按册放：<产物根>/<vol>/row_segment/pNNNN.json（cv 工作区的 products/<book>/、产物包、cut-bench 跑出的 ws/products 都是这个样子）。
只依赖本文件与 items.jsonl，不要 cut-bench。

口径：
- 逐轨（main／夹注 a、b）把预测格（kind 不是 blank）按 y 排好合成切线：首格上沿、相邻两格（上格下沿＋下格上沿）中点、末格下沿。
  正文格两轨共用；金标 main 线在有夹注的列里 a、b 两轨都要对上。
- 金标线 y＝`page_ends` 两端 y 的均值（L2 直线）。容差＝0.15×该轨金标线间距中位（≈字高）。一条预测线只配一条金标线。
- 线对＝对上的金标线数；**列线全对**＝该列金标线全对上、且金标范围内没有多出来的预测线。
- 字数对＝预测正文格位数（夹注一对算一格，同 `gold_n`）＝`gold_n`。
- 报「错列修回」（group=wrong 的列线全对）和「好列保住」（group=good 的列线全对），按书分列。
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOL = 0.15


def _box(q):
    xs = [p[0] for p in q]; ys = [p[1] for p in q]
    return min(xs), min(ys), max(xs), max(ys)


def _cells(pred: Path, vol: str, page: int, col: int) -> list[dict] | None:
    f = pred / vol / "row_segment" / f"p{page:04d}.json"
    if not f.exists():
        return None
    for c in json.loads(f.read_text(encoding="utf-8"))["cells"]["columns"]:
        if c["col"] == col:
            return [x for x in c.get("cells", []) if x.get("kind") not in ("blank", None)]
    return []


def pred_lines(cells: list[dict]) -> dict[str, list[float]]:
    tr = {"a": [], "b": []}
    for c in cells:
        _, y0, _, y1 = _box(c["quad_page"])
        if str(c.get("kind", "")).startswith("jiazhu"):
            tr["a" if c.get("sub") in ("a", "r", 0, "0") else "b"].append((y0, y1))
        else:
            tr["a"].append((y0, y1)); tr["b"].append((y0, y1))
    out = {}
    for t, seq in tr.items():
        seq.sort()
        ys = [seq[0][0]] + [(seq[i - 1][1] + seq[i][0]) / 2 for i in range(1, len(seq))] + [seq[-1][1]] if seq else []
        out[t] = ys
    return out


def score_col(item: dict, cells: list[dict]) -> dict:
    pl = pred_lines(cells)
    tracks = {l["track"] for l in item["lines"]}
    jz = sorted(tracks & {"a", "b"})
    okmap: dict = {}
    extra = 0
    for t in (jz or ["main"]):
        gl = sorted((sum(p[1] for p in l["page_ends"]) / 2, l["track"], l["k"]) for l in item["lines"]
                    if l["track"] in (t, "main"))
        if not gl:
            continue
        gaps = [b[0] - a[0] for a, b in zip(gl, gl[1:])]
        tol = TOL * (statistics.median(gaps) if gaps else 100.0)
        cand = pl["a"] if t == "main" else pl[t]
        used: set[int] = set()
        for y, tt, k in gl:
            d, i = min(((abs(y - p), i) for i, p in enumerate(cand) if i not in used), default=(1e9, -1))
            ok = d <= tol
            if ok:
                used.add(i)
            okmap[(tt, k)] = okmap.get((tt, k), True) and ok
        lo, hi = gl[0][0] - tol, gl[-1][0] + tol
        extra += sum(1 for i, p in enumerate(cand) if i not in used and lo < p < hi)
    n_ok = sum(okmap.values())
    return {"lines": len(okmap), "ok": n_ok, "extra": extra, "line_exact": n_ok == len(okmap) and extra == 0,
            "count_ok": len({c.get("slot") for c in cells}) == item.get("gold_n"), "n_pred": len({c.get("slot") for c in cells})}


def run(items: list[dict], pred: Path, books: list[str], split: str) -> dict[str, dict]:
    out = {}
    for it in items:
        if it["book"] not in books or (split != "all" and it["split"] != split):
            continue
        cells = _cells(pred, it["vol"], it["page"], it["col"])
        if cells is None:
            continue
        r = score_col(it, cells)
        r.update(group=it["group"], split=it["split"])
        out[it["key"]] = r
    return out


def summary(res: dict) -> dict:
    s: dict = {}
    for k, r in res.items():
        for key in (k.split(":")[0], "all"):
            d = s.setdefault(key, dict(cols=0, line_exact=0, count_ok=0, lines=0, lines_ok=0,
                                       wrong_cols=0, wrong_fixed=0, good_cols=0, good_kept=0))
            d["cols"] += 1; d["line_exact"] += r["line_exact"]; d["count_ok"] += r["count_ok"]
            d["lines"] += r["lines"]; d["lines_ok"] += r["ok"]
            g = "wrong" if r["group"] == "wrong" else "good"
            d[f"{g}_cols"] += 1; d["wrong_fixed" if g == "wrong" else "good_kept"] += r["line_exact"]
    return s


def main() -> None:
    ap = argparse.ArgumentParser(description="cut-lattice 逐线打分")
    ap.add_argument("--items", default=str(HERE / "items.jsonl"))
    ap.add_argument("--pred", required=True); ap.add_argument("--against")
    ap.add_argument("--books", default="shiji,qtw,dianben,maijing"); ap.add_argument("--split", default="tune")
    ap.add_argument("--json")
    a = ap.parse_args()
    items = [json.loads(l) for l in open(a.items, encoding="utf-8") if l.strip()]
    books = a.books.split(",")
    res = run(items, Path(a.pred), books, a.split)
    for b, d in summary(res).items():
        print(f"{b:8s} 列 {d['cols']:3d}｜列线全对 {d['line_exact']:3d}｜字数对 {d['count_ok']:3d}｜线 {d['lines_ok']}/{d['lines']}"
              f"｜错列修回 {d['wrong_fixed']}/{d['wrong_cols']}｜好列保住 {d['good_kept']}/{d['good_cols']}")
    if a.against:
        base = run(items, Path(a.against), books, a.split)
        for k in sorted(res):
            b0, b1 = base.get(k), res[k]
            if b0 and (b0["line_exact"], b0["ok"]) != (b1["line_exact"], b1["ok"]):
                print(f"  {k:18s} {b1['group']:5s} 列线全对 {int(b0['line_exact'])}→{int(b1['line_exact'])}  "
                      f"线 {b0['ok']}→{b1['ok']}/{b1['lines']}  格 {b0['n_pred']}→{b1['n_pred']}")
    if a.json:
        Path(a.json).write_text(json.dumps({"summary": summary(res), "cols": res}, ensure_ascii=False, indent=1),
                                encoding="utf-8")


if __name__ == "__main__":
    main()
