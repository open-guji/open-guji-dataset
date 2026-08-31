# -*- coding: utf-8 -*-
"""按真墨脊线重新拟合金标 verticals_inner。

人工拖的直线保留了最有价值的东西——**这一页有几条线、哪条是哪条**，那是
人核过的。但"一条直线在弯曲界行上摆在哪"人眼拖不准（实测金标离真墨
6.36px，最佳直线 4.27px）。所以只重拟几何，不动条数和顺序，原值留档。

脊线提取：
- 搜索窗口锚在**现有人工金标线**上（人核过的身份），半宽 HALF
- 每个 y 取上下 WINH 行的墨列和，峰值要 >= MIN_FRAC 比例的行有墨
- 亚像素：峰附近半高以上那段连通区间的加权质心
- 稳健拟合：LS → 按 MAD 剔外点 → 重拟，迭代 3 次

三道验收闸，任何一道不过就**原样保留人工值**，绝不冒险覆盖：
1. 内点数 >= MIN_PTS 且 y 跨度 >= MIN_SPAN_FRAC 的版框高度
2. 新线必须真的比旧线更贴真墨（d_new < d_old）
3. 拟合区间内位移 <= MAX_SHIFT

闸 3 是踩出来的：HALF 放到 35 时，最外那两条线（idx0/idx9，也就是左右
版框内边框）会跳到旁边 20~31px 的**外边框**上去，位移 16~40px、方向一律
朝外，`d_new` 看着还大幅"改善"——其实是换了一条线。HALF 收到 20（小于
内外边框间距）+ 位移闸，双保险。
"""
import json, os, sys
from pathlib import Path
import numpy as np
import cv2

RAW = Path(os.environ.get("GUJI_RAW", "/home/user/rebuild_src")) / "vol01"
GOLD = Path(__file__).resolve().parent.parent / "border-detection" / "samples"
PAGES = ["137", "138", "32", "33", "49", "9", "14", "142", "24", "65", "141", "26", "47", "51"]

STEP = 20            # 采样步长
HALF = 20            # 搜索半宽，必须 < 内外边框间距（实测 20~31px）
WINH = 24            # 每个采样点纵向合并的行数
MIN_FRAC = 0.55      # 峰值至少这么多行有墨
MAX_RIDGE_W = 25     # 半高宽超过这个就不是一条线（压到字了）
MARGIN = 70          # 版框内缩，避开抬头框/墙线和版框转角
MAD_K = 2.5
MIN_PTS = 40
MIN_SPAN_FRAC = 0.6
MAX_SHIFT = 14       # 真实修正实测 <=12.6px；更大的只出现在"跳线"情形


def ridge_points(m, gold_x_at, y0, y1, w):
    ys, xs = [], []
    for y in range(y0, y1, STEP):
        c = int(round(gold_x_at(y)))
        lo, hi = max(0, c - HALF), min(w, c + HALF + 1)
        if hi - lo < 10:
            continue
        band = m[max(0, y - WINH // 2):y + WINH // 2, lo:hi]
        if band.shape[0] < WINH // 2:
            continue
        prof = band.sum(axis=0).astype(np.float64)
        pk = int(np.argmax(prof))
        if prof[pk] < MIN_FRAC * band.shape[0]:
            continue
        half = prof[pk] / 2.0
        a = b = pk
        while a > 0 and prof[a - 1] >= half:
            a -= 1
        while b < len(prof) - 1 and prof[b + 1] >= half:
            b += 1
        if b - a > MAX_RIDGE_W:
            continue
        seg = prof[a:b + 1]
        ys.append(float(y))
        xs.append(lo + float((np.arange(a, b + 1) * seg).sum() / seg.sum()))
    return np.array(ys), np.array(xs)


def robust_fit(ys, xs):
    keep = np.ones(len(ys), bool)
    k = b = 0.0
    for _ in range(3):
        if keep.sum() < 10:
            break
        k, b = np.polyfit(ys[keep], xs[keep], 1)
        r = xs - (k * ys + b)
        med = np.median(r[keep])
        mad = np.median(np.abs(r[keep] - med)) or 1.0
        keep = np.abs(r - med) <= MAD_K * 1.4826 * mad
    return k, b, keep


def process(page):
    g = json.loads((GOLD / f"vol01_{page}.json").read_text())
    img = cv2.imread(str(RAW / f"{page}.tif"), cv2.IMREAD_GRAYSCALE)
    h, w = img.shape
    m = (img < 128).astype(np.uint8)
    y0 = int(g["top_inner"]["y_at_right"] + MARGIN)
    y1 = int(g["bottom_inner"]["y_at_right"] - MARGIN)
    frame_h = y1 - y0
    # 始终以**人工原值**为基线：已经重拟过的样本再跑一次也复现同样的结果，
    # refit.lines 里记的永远是"相对人工值改了多少"，不是"相对上一次改了多少"。
    base = g.get("verticals_inner_manual") or g["verticals_inner"]
    out, report = [], []
    for i, q in enumerate(base):
        gx = lambda y, q=q: (w - 1) - (q["x_at_top"] + q["slope"] * y)   # noqa: E731
        ys, xs = ridge_points(m, gx, y0, y1, w)
        rec = dict(idx=i, n=len(ys), ok=False, why="", d_old=None, d_new=None, shift=None)
        keep_manual = True
        if len(ys) >= MIN_PTS:
            k, b, keep = robust_fit(ys, xs)
            span = (ys[keep].max() - ys[keep].min()) if keep.sum() else 0.0
            if keep.sum() < MIN_PTS or span < MIN_SPAN_FRAC * frame_h:
                rec["why"] = f"样本不足(n={int(keep.sum())},span={span/frame_h:.0%})"
            else:
                yk, xk = ys[keep], xs[keep]
                d_old = float(np.mean(np.abs(xk - ((-q["slope"]) * yk + (w - 1) - q["x_at_top"]))))
                d_new = float(np.mean(np.abs(xk - (k * yk + b))))
                ns, nx = -k, (w - 1) - b
                shift = max(abs((nx + ns * y) - (q["x_at_top"] + q["slope"] * y))
                            for y in (y0, (y0 + y1) // 2, y1))
                rec.update(n=int(keep.sum()), d_old=d_old, d_new=d_new, shift=shift)
                if d_new >= d_old:
                    rec["why"] = "没更贴"
                elif shift > MAX_SHIFT:
                    rec["why"] = f"位移{shift:.0f}px超限(疑似跳到外边框)"
                else:
                    rec["ok"] = True
                    keep_manual = False
                    out.append(dict(x_at_top=float(nx), slope=float(ns)))
        else:
            rec["why"] = f"采样点太少(n={len(ys)})"
        if keep_manual:
            out.append(dict(x_at_top=q["x_at_top"], slope=q["slope"]))
        report.append(rec)
    xs_new = [o["x_at_top"] for o in out]
    ordered = all(xs_new[i] < xs_new[i + 1] for i in range(len(xs_new) - 1))
    return out, report, ordered


def apply_all():
    """把重拟结果写回样本 JSON；原人工值留档在 verticals_inner_manual。"""
    import collections
    note = ("verticals_inner 已按真墨脊线重拟。人工拖的原值留在 "
            "verticals_inner_manual。人核过的条数/顺序/身份原样保留，只重拟几何"
            "——人眼在弯曲界行上拖直线拖不准。三道闸任一不过就保留人工值："
            "样本量/跨度、必须真的更贴真墨、拟合区间内位移<=14px（防止最外两条"
            "跳到旁边的外边框上）。逐条结果见 refit.lines。")
    n = 0
    for page in PAGES:
        f = GOLD / f"vol01_{page}.json"
        d = json.loads(f.read_text(), object_pairs_hook=collections.OrderedDict)
        out, rep, ordered = process(page)
        assert ordered, f"{page} 保序被破坏，中止"
        assert len(out) == len(d["verticals_inner"])
        d.setdefault("verticals_inner_manual", d["verticals_inner"])
        new = collections.OrderedDict()
        for k, v in d.items():
            new[k] = out if k == "verticals_inner" else v
        new["verticals_inner_manual"] = d["verticals_inner_manual"]
        new["refit"] = collections.OrderedDict(
            method="ink_ridge_robust_fit", note=note,
            accepted=sum(r["ok"] for r in rep), total=len(rep),
            lines=[collections.OrderedDict(
                idx=r["idx"], refit=r["ok"],
                kept_manual_because=(r["why"] or None) if not r["ok"] else None,
                n_inliers=r["n"],
                dist_to_ink_before=None if r["d_old"] is None else round(r["d_old"], 2),
                dist_to_ink_after=None if r["d_new"] is None else round(r["d_new"], 2),
                shift_px=None if r["shift"] is None else round(r["shift"], 2),
            ) for r in rep])
        f.write_text(json.dumps(new, ensure_ascii=False, indent=1) + "\n")
        n += sum(r["ok"] for r in rep)
        print(f"{page}: 写入，重拟 {sum(r['ok'] for r in rep)}/10")
    print(f"共改动 {n} 条")


if __name__ == "__main__":
    if "--apply" in sys.argv:
        apply_all()
        raise SystemExit
    detail = "-v" in sys.argv
    old_all, new_all, nacc, allok = [], [], 0, True
    rejects = []
    for page in PAGES:
        out, rep, ordered = process(page)
        allok &= ordered
        acc = [r for r in rep if r["ok"]]
        nacc += len(acc)
        old_all += [r["d_old"] for r in acc]
        new_all += [r["d_new"] for r in acc]
        rejects += [(page, r) for r in rep if not r["ok"]]
        do = np.mean([r["d_old"] for r in acc]) if acc else 0
        dn = np.mean([r["d_new"] for r in acc]) if acc else 0
        mx = max((r["shift"] for r in acc), default=0)
        print(f"{page:>5}  重拟 {len(acc):2d}/10  离真墨 {do:5.2f}→{dn:5.2f}px  "
              f"最大位移 {mx:5.1f}px  保序={'OK' if ordered else '!!破坏'}")
        if detail:
            for r in rep:
                if r["ok"]:
                    print(f"        idx{r['idx']} n={r['n']:3d} {r['d_old']:5.2f}→{r['d_new']:5.2f}"
                          f"  位移{r['shift']:5.1f}")
    print(f"\n重拟 {nacc}/140 条：这些线上 离真墨 {np.mean(old_all):.2f} → {np.mean(new_all):.2f}px")
    print(f"保序全部 OK: {allok}")
    print(f"\n保留人工值的 {len(rejects)} 条：")
    for pg, r in rejects:
        print(f"  {pg}/idx{r['idx']}: {r['why']}"
              + (f"  (d {r['d_old']:.1f}->{r['d_new']:.1f}, 位移{r['shift']:.1f})"
                 if r["d_old"] is not None else ""))
