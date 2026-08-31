# -*- coding: utf-8 -*-
"""抬头框 inner_y 按真墨重拟（线心）。

用户定的口径：
- inner_y = **线心**（不是线的边缘）
- 墨量**只在这一列的窄窗口里**算——抬头框只存在于这一列
- 不能跟外边框弄混，两条判据：
  1. 内外边框间距全页基本一致（实测：上 36.3±6.2 / 下 38.2±5.1 / 侧 38.4±4.0 /
     抬头 40.3±3.2，四处都聚在 36~40）——所以候选的 inner-outer 间距必须落在
     GAP_MIN..GAP_MAX 内，这条专门用来把"外边框本身"和"下面第一个字的横画"
     两头都排掉
  2. 满足间距的候选里，取**最靠里**（y 最大）的那条，即使比较浅

关键：墨占比门槛必须是**绝对值**，不能用"峰值的一半"——外边框常常是满墨
(1.0)，相对门槛会被抬到 0.5，而真正的内边框只有 0.38~0.45，会被整批杀掉
（vol01/47 四例全中）。
"""
import collections
import json, os, sys
from pathlib import Path
import numpy as np, cv2

RAW = Path(os.environ.get("GUJI_RAW", "/home/user/rebuild_src")) / "vol01"
GOLD = Path(__file__).resolve().parent.parent / "border-detection" / "samples"
PAGES = ["137", "138", "32", "33", "49", "9", "14", "142", "24", "65", "141", "26", "47", "51"]

INSET = 0.12        # 列窗口两侧内缩比例，避开界行/墙线本身
BAND = 30           # 在金标 inner_y 上下这么多行里找
INK_FLOOR = 0.25    # 绝对墨占比门槛（浅的内边框实测 0.38~0.45，留余量）
MAX_RUN = 14        # 连通段太宽就不是一条线
GAP_MIN, GAP_MAX = 25.0, 52.0   # 内外间距先验（实测抬头 35.0~46.8，放宽）
MAX_SHIFT = 15.0    # 单次移动上限——"移动它不能过分"


def col_window(g, col, w, y):
    vr, vl = g["verticals_inner"][col - 1], g["verticals_inner"][col]
    xr = (w - 1) - (vr["x_at_top"] + vr["slope"] * y)
    xl = (w - 1) - (vl["x_at_top"] + vl["slope"] * y)
    a, b = sorted((xl, xr))
    pad = (b - a) * INSET
    return int(a + pad), int(b - pad)


def line_centers(prof, ys):
    """绝对门槛以上的连通段 -> 每段用"峰值半高以上"那截算线心。"""
    out, i, n = [], 0, len(prof)
    while i < n:
        if prof[i] >= INK_FLOOR:
            j = i
            while j + 1 < n and prof[j + 1] >= INK_FLOOR:
                j += 1
            if j - i + 1 <= MAX_RUN:
                seg, yy = prof[i:j + 1], ys[i:j + 1]
                pk = int(np.argmax(seg))
                a, b = pk, pk
                while a > 0 and seg[a - 1] >= seg[pk] * 0.5:
                    a -= 1
                while b < len(seg) - 1 and seg[b + 1] >= seg[pk] * 0.5:
                    b += 1
                s, y2 = seg[a:b + 1], yy[a:b + 1]
                out.append((float((y2 * s).sum() / s.sum()), float(seg[pk]), j - i + 1))
            i = j + 1
        else:
            i += 1
    return out


def process(page):
    g = json.loads((GOLD / f"vol01_{page}.json").read_text())
    if not g["head_raise"]:
        return g, []
    img = cv2.imread(str(RAW / f"{page}.tif"), cv2.IMREAD_GRAYSCALE)
    h, w = img.shape
    m = (img < 128).astype(np.uint8)
    rep = []
    base = g.get("head_raise_manual") or g["head_raise"]
    for hr in base:
        col, iy, oy = hr["col"], hr["inner_y"], hr["outer_y"]
        r = dict(col=col, old=iy, new=iy, ok=False, why="", ink_at_old=None,
                 cands=[], gap_new=None, shift=None)
        if hr.get("estimated"):
            r["why"] = "estimated=true（线被裁掉了，没有可测的墨）"
            rep.append(r); continue
        lo, hi = int(iy - BAND), int(iy + BAND)
        ys = np.arange(lo, hi + 1)
        prof = np.array([m[y, slice(*col_window(g, col, w, y))].mean()
                         if col_window(g, col, w, y)[1] > col_window(g, col, w, y)[0] else 0.0
                         for y in ys])
        r["ink_at_old"] = float(prof[int(round(iy)) - lo])
        cands = line_centers(prof, ys)
        r["cands"] = [(round(c[0], 1), round(c[1], 2)) for c in cands]
        okc = [c for c in cands if GAP_MIN <= c[0] - oy <= GAP_MAX]
        if not okc:
            r["why"] = "带内没有间距合规的候选"
        else:
            best = max(okc, key=lambda c: c[0])      # 最靠里
            shift = best[0] - iy
            r.update(new=best[0], gap_new=best[0] - oy, shift=shift)
            if abs(shift) > MAX_SHIFT:
                r["why"] = f"移动{shift:+.1f}px超限"
            else:
                r["ok"] = True
        rep.append(r)
    return g, rep


def apply_all():

    NOTE = ("head_raise.inner_y 已按真墨重拟为**线心**（墨量只在该列窄窗口里算，"
            "因为抬头框只存在于这一列）。人工原值留在 head_raise_manual。"
            "判据：绝对墨占比门槛(0.25，不能用峰值相对门槛——外框常是满墨会把浅的"
            "内框杀掉)找连通段 -> 峰值半高以上加权质心 = 线心；再要求 inner-outer "
            "间距落在 25~52px（拦掉外框本身和下面第一个字的横画），合规候选里取"
            "**最靠里**那条；单次移动 <=15px。outer_y 保持人工值未动。")

    changed = 0
    for page in PAGES:
        f = GOLD / f"vol01_{page}.json"
        d = json.loads(f.read_text(), object_pairs_hook=collections.OrderedDict)
        if not d["head_raise"]:
            continue
        g, rep = process(page)
        img = cv2.imread(str(RAW / f"{page}.tif"), cv2.IMREAD_GRAYSCALE)
        h, w = img.shape
        m = (img < 128).astype(np.uint8)
        base = d.get("head_raise_manual") or d["head_raise"]
        d.setdefault("head_raise_manual", [dict(x) for x in base])
        rmap = {r["col"]: r for r in rep}
        new_hr, lines = [], []
        for hr in base:
            r = rmap[hr["col"]]
            e = collections.OrderedDict(hr)
            if r["ok"]:
                e["inner_y"] = float(r["new"])
                changed += 1
            new_hr.append(e)
            # 记下金标 outer_y 处的墨占比：为 0 的说明外框根本没印上
            a, b = col_window(g, hr["col"], w, int(hr["outer_y"]))
            oink = float(m[int(round(hr["outer_y"])), a:b].mean()) if b > a else 0.0
            lines.append(collections.OrderedDict(
                col=hr["col"], refit=r["ok"],
                kept_manual_because=(r["why"] or None) if not r["ok"] else None,
                inner_shift_px=None if not r["ok"] else round(r["shift"], 2),
                ink_at_old_inner=None if r["ink_at_old"] is None else round(r["ink_at_old"], 3),
                gap_after=None if r["gap_new"] is None else round(r["gap_new"], 1),
                ink_at_outer=round(oink, 3)))
        out = collections.OrderedDict()
        for k, v in d.items():
            out[k] = new_hr if k == "head_raise" else v
        out["head_raise_manual"] = d["head_raise_manual"]
        out["head_raise_refit"] = collections.OrderedDict(
            method="ink_line_center_in_column", note=NOTE,
            accepted=sum(r["ok"] for r in rep), total=len(rep), lines=lines)
        f.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
        print(f"{page}: 重拟 {sum(r['ok'] for r in rep)}/{len(rep)}")
    print(f"共改动 {changed} 例")


if __name__ == "__main__":
    if "--apply" in sys.argv:
        apply_all()
        raise SystemExit
    n_ok = n_all = 0
    shifts, inks_old, inks_new = [], [], []
    for page in PAGES:
        g, rep = process(page)
        if not rep:
            continue
        print(f"\n=== vol01/{page} ===")
        for r in rep:
            n_all += 1
            if r["ok"]:
                n_ok += 1
                shifts.append(r["shift"])
                print(f"  c{r['col']}: {r['old']:7.1f} -> {r['new']:7.1f} ({r['shift']:+5.1f}px)  "
                      f"新间距={r['gap_new']:5.1f}  旧位置墨={r['ink_at_old']:.3f}  候选={r['cands']}")
            else:
                print(f"  c{r['col']}: 保留 {r['old']:7.1f}  [{r['why']}]  候选={r['cands']}")
    print(f"\n重拟 {n_ok}/{n_all} 例；移动量 均值={np.mean([abs(s) for s in shifts]):.1f}px "
          f"范围={min(shifts):+.1f}~{max(shifts):+.1f}")
