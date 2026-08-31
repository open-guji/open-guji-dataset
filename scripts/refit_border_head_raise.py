# -*- coding: utf-8 -*-
"""抬头框 head_raise 按真墨重拟：inner_y = 线心，outer_y = 外延，并标注
每个坐标到底是不是观测值。

口径（用户 2026-08-31 定）：
- `inner_y` = **线心**（内框是一条 4~8px 的细锐线，取线心）
- `outer_y` = **外延**（外框常是一条 15~23px 的粗条，取朝外那一侧的边缘；
  上边框朝外就是 y 小的一侧）
- 墨量**只在该列的窄窗口里**算——抬头框只存在于这一列，按整行算会被邻列
  的墨污染

判定观测与否：
- `inner_observed` / `outer_observed` 两个字段分别记这两个坐标是不是量出来的
- `estimated` = `not (inner_observed and outer_observed)`，保持"这条记录不是
  全观测"的旧语义，跟 `border_geometry.HeadRaiseBorder.estimated` 对齐

踩过的坑：
- **墨占比门槛必须是绝对值**，不能用"峰值的一半"——外框常常是满墨(1.0)，
  相对门槛会被抬到 0.5，而真内框只有 0.33~0.47，会被整批杀掉（vol01/47
  四例全中）。
- 拦"跟外框/字混淆"靠间距先验：要求 inner-outer 落在 25~52px，把外框本身
  （间距太小）和下面第一个字的横画（实测在 y≈350 一带，间距太大）两头排掉；
  合规候选里取**最靠里**那条，即使比较浅。
- 重拟始终以 `head_raise_manual` 为基线，重复跑结果一致（幂等）。

跑法：
    python scripts/refit_border_head_raise.py          # 只打印，不写
    python scripts/refit_border_head_raise.py --apply  # 写回样本 JSON
原图路径用 GUJI_RAW 覆盖（默认 /home/user/rebuild_src）。
"""
import collections
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np

RAW = Path(os.environ.get("GUJI_RAW", "/home/user/rebuild_src")) / "vol01"
GOLD = Path(__file__).resolve().parent.parent / "border-detection" / "samples"
PAGES = ["137", "138", "32", "33", "49", "9", "14", "142", "24", "65", "141", "26", "47", "51"]

INSET = 0.12                  # 列窗口两侧内缩比例，避开界行/墙线本身
BAND = 30                     # 在人工值上下这么多行里找
INNER_FLOOR = 0.25            # 内框：绝对墨占比门槛（浅的内框实测 0.33~0.47）
OUTER_FLOOR = 0.30            # 外框：认一段"外框墨"的门槛
MAX_RUN = 14                  # 连通段超过这么宽就不是一条细线
GAP_MIN, GAP_MAX = 25.0, 52.0 # inner-outer 间距先验
MAX_SHIFT = 15.0              # 单次移动上限——"移动它不能过分"


def col_window(g, col, w, y):
    vr, vl = g["verticals_inner"][col - 1], g["verticals_inner"][col]
    xr = (w - 1) - (vr["x_at_top"] + vr["slope"] * y)
    xl = (w - 1) - (vl["x_at_top"] + vl["slope"] * y)
    a, b = sorted((xl, xr))
    pad = (b - a) * INSET
    return int(a + pad), int(b - pad)


def profile(m, g, col, w, ys):
    out = []
    for y in ys:
        a, b = col_window(g, col, w, int(y))
        out.append(m[int(y), a:b].mean() if b > a else 0.0)
    return np.array(out)


def _runs(prof, floor):
    idx = np.where(prof >= floor)[0]
    if len(idx) == 0:
        return []
    segs, s, p = [], idx[0], idx[0]
    for q in idx[1:]:
        if q == p + 1:
            p = q
        else:
            segs.append((s, p)); s = q; p = q
    segs.append((s, p))
    return segs


def line_centers(prof, ys):
    """细线的线心：连通段内"峰值半高以上"那截的加权质心。"""
    out = []
    for a, b in _runs(prof, INNER_FLOOR):
        if b - a + 1 > MAX_RUN:
            continue
        seg, yy = prof[a:b + 1], ys[a:b + 1]
        pk = int(np.argmax(seg))
        i, j = pk, pk
        while i > 0 and seg[i - 1] >= seg[pk] * 0.5:
            i -= 1
        while j < len(seg) - 1 and seg[j + 1] >= seg[pk] * 0.5:
            j += 1
        s, y2 = seg[i:j + 1], yy[i:j + 1]
        out.append((float((y2 * s).sum() / s.sum()), float(seg[pk])))
    return out


def outer_edge(prof, ys, near_y):
    """粗条的外延：墨占比跨过该段峰值一半的那个点（朝 y 小的一侧），线性插值。"""
    segs = _runs(prof, OUTER_FLOOR)
    if not segs:
        return None
    a, b = min(segs, key=lambda t: abs((ys[t[0]] + ys[t[1]]) / 2 - near_y))
    pk = float(prof[a:b + 1].max())
    half = pk * 0.5
    i = a
    while i > 0 and prof[i - 1] >= half:
        i -= 1
    if i == 0:
        edge = float(ys[i])
    else:
        y0, y1 = float(ys[i - 1]), float(ys[i])
        p0, p1 = float(prof[i - 1]), float(prof[i])
        edge = y1 if p1 == p0 else y1 - (p1 - half) / (p1 - p0) * (y1 - y0)
    return edge, pk, float(ys[a]), float(ys[b])


def process(page):
    g = json.loads((GOLD / f"vol01_{page}.json").read_text())
    if not g["head_raise"]:
        return g, []
    img = cv2.imread(str(RAW / f"{page}.tif"), cv2.IMREAD_GRAYSCALE)
    h, w = img.shape
    m = (img < 128).astype(np.uint8)
    base = g.get("head_raise_manual") or g["head_raise"]
    rep = []
    for hr in base:
        col, iy0, oy0 = hr["col"], hr["inner_y"], hr["outer_y"]
        r = dict(col=col, inner_old=iy0, inner_new=iy0, outer_old=oy0, outer_new=oy0,
                 inner_observed=False, outer_observed=False,
                 inner_why="", outer_why="", ink_at_old_inner=None,
                 ink_at_old_outer=None, bar=None, gap=None)

        # --- inner：线心，最靠里的合规候选 ---
        ys = np.arange(int(iy0 - BAND), int(iy0 + BAND) + 1)
        pr = profile(m, g, col, w, ys)
        r["ink_at_old_inner"] = float(pr[int(round(iy0)) - ys[0]])
        ok = [c for c in line_centers(pr, ys) if GAP_MIN <= c[0] - oy0 <= GAP_MAX]
        if not ok:
            r["inner_why"] = "带内没有间距合规的候选（线被裁掉或没印上）"
        else:
            best = max(ok, key=lambda c: c[0])
            if abs(best[0] - iy0) > MAX_SHIFT:
                r["inner_why"] = f"移动{best[0]-iy0:+.1f}px超限"
            else:
                r.update(inner_new=best[0], inner_observed=True)

        # --- outer：外延 ---
        ys2 = np.arange(int(oy0 - BAND), int(oy0 + BAND) + 1)
        pr2 = profile(m, g, col, w, ys2)
        r["ink_at_old_outer"] = float(pr2[int(round(oy0)) - ys2[0]])
        res = outer_edge(pr2, ys2, oy0)
        if res is None:
            r["outer_why"] = "带内没有任何墨（外框没印上）"
        else:
            edge, pk, sa, sb = res
            r["bar"] = (sa, sb, round(pk, 2))
            if edge >= r["inner_new"] - 8:
                r["outer_why"] = f"最近的墨段({sa:.0f}~{sb:.0f})就是内框本身，外框没印上"
            elif abs(edge - oy0) > MAX_SHIFT:
                r["outer_why"] = f"移动{edge-oy0:+.1f}px超限"
            else:
                r.update(outer_new=edge, outer_observed=True)

        if r["inner_observed"] and r["outer_observed"]:
            r["gap"] = r["inner_new"] - r["outer_new"]
        rep.append(r)
    return g, rep


def apply_all():
    note = ("head_raise 已按真墨重拟：inner_y=线心、outer_y=外延，墨量只在该列"
            "窄窗口里算（抬头框只存在于这一列）。人工原值留在 head_raise_manual。"
            "inner_observed/outer_observed 记这两个坐标是不是量出来的；"
            "estimated = not(inner_observed and outer_observed)。"
            "坑：墨占比门槛必须用绝对值，外框满墨时相对门槛会把浅的内框整批杀掉。")
    n_i = n_o = 0
    for page in PAGES:
        f = GOLD / f"vol01_{page}.json"
        d = json.loads(f.read_text(), object_pairs_hook=collections.OrderedDict)
        if not d["head_raise"]:
            continue
        g, rep = process(page)
        base = d.get("head_raise_manual") or d["head_raise"]
        d.setdefault("head_raise_manual", [dict(x) for x in base])
        rmap = {r["col"]: r for r in rep}
        new_hr, lines = [], []
        for hr in base:
            r = rmap[hr["col"]]
            e = collections.OrderedDict(hr)
            e["inner_y"] = float(r["inner_new"])
            e["outer_y"] = float(r["outer_new"])
            e["inner_observed"] = r["inner_observed"]
            e["outer_observed"] = r["outer_observed"]
            e["estimated"] = not (r["inner_observed"] and r["outer_observed"])
            new_hr.append(e)
            n_i += r["inner_observed"]; n_o += r["outer_observed"]
            lines.append(collections.OrderedDict(
                col=r["col"],
                inner_observed=r["inner_observed"], outer_observed=r["outer_observed"],
                inner_shift_px=round(r["inner_new"] - r["inner_old"], 2),
                outer_shift_px=round(r["outer_new"] - r["outer_old"], 2),
                inner_kept_because=r["inner_why"] or None,
                outer_kept_because=r["outer_why"] or None,
                ink_at_old_inner=round(r["ink_at_old_inner"], 3),
                ink_at_old_outer=round(r["ink_at_old_outer"], 3),
                outer_bar=r["bar"],
                gap_after=None if r["gap"] is None else round(r["gap"], 1)))
        out = collections.OrderedDict()
        for k, v in d.items():
            out[k] = new_hr if k == "head_raise" else v
        out["head_raise_manual"] = d["head_raise_manual"]
        out["head_raise_refit"] = collections.OrderedDict(
            method="ink_inner_center_outer_edge", note=note,
            inner_observed=sum(r["inner_observed"] for r in rep),
            outer_observed=sum(r["outer_observed"] for r in rep),
            total=len(rep), lines=lines)
        f.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
        print(f"{page}: inner 观测 {sum(r['inner_observed'] for r in rep)}/{len(rep)}, "
              f"outer 观测 {sum(r['outer_observed'] for r in rep)}/{len(rep)}")
    print(f"共 inner 观测 {n_i} 例、outer 观测 {n_o} 例")


if __name__ == "__main__":
    if "--apply" in sys.argv:
        apply_all()
        raise SystemExit
    gaps = []
    print(f"{'页/列':>9} | {'inner':>26} | {'outer':>28} | {'间距':>6}")
    for page in PAGES:
        g, rep = process(page)
        for r in rep:
            i = (f"{r['inner_old']:7.1f}->{r['inner_new']:7.1f} ({r['inner_new']-r['inner_old']:+5.1f})"
                 if r["inner_observed"] else f"{r['inner_old']:7.1f} 保留 [{r['inner_why'][:12]}]")
            o = (f"{r['outer_old']:7.1f}->{r['outer_new']:7.1f} ({r['outer_new']-r['outer_old']:+5.1f})"
                 f" 条宽{r['bar'][1]-r['bar'][0]:.0f}" if r["outer_observed"]
                 else f"{r['outer_old']:7.1f} 保留 [{r['outer_why'][:16]}]")
            if r["gap"] is not None:
                gaps.append(r["gap"])
            gap = f"{r['gap']:6.1f}" if r["gap"] is not None else "     -"
            print(f"{page + '/c' + str(r['col']):>9} | {i:>26} | {o:>28} | {gap}")
    print(f"\n外延->线心 间距 n={len(gaps)}: 均值={np.mean(gaps):.1f} 中位={np.median(gaps):.1f} "
          f"范围={min(gaps):.1f}~{max(gaps):.1f} σ={np.std(gaps):.2f}")
