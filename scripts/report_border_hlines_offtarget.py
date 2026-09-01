# -*- coding: utf-8 -*-
"""体检：找出 `top_inner`/`bottom_inner` 金标里**整条画在白纸上**的边。

**只报告，不改金标。** 见文末「为什么不自动重拟」。

背景：14 页金标里有 3 页的 `bottom_inner` 整条脱靶（vol01/137、/138、/141），
金标线上的行墨占比只有 0.011/0.028/0.057，而算法线上是 0.185/0.248/0.417。
这三页把 Step1 的 bottom 均值误差从 ~2px 拉到 6.96px、最大 38.9px——那不是
探测误差，是标注脱靶。

量法（**先验证过再用**，这条是踩出来的）：
上一版 `eval_border_hlines_vs_ink` 只拿金标当脊线种子，金标离"自己的"脊线
永远 <=HALF，结构上不可能输；金标压根不在墨上时还直接"样本不足"跳过——那是
个偏心的尺子，会把「金标更贴」这个结论凭空造出来。这里改成**中立量法**：
对每条候选线各自统计
    覆盖率 = 采样列里能在 ±HALF 内找到合格版框峰的比例（线在不在墨上）
    离墨   = 找到的那些峰的平均距离（在墨上时贴得多准）
**覆盖率是主判据**——不在墨上的线覆盖率会塌，离墨再小也没意义。
换成中立量法后，28 条边里 23 条金标与算法本来就重合，算法赢 3、金标赢 2；
偏心量法报出来的「vol01/47 top 算法差 23.9px」「vol01/51 bottom 差 15.5px」
两条都是量法造出来的假象，不是真缺陷。

为什么不自动重拟（两次都栽在同一件事上）：
1. 「取最黑的一行」必然选中**外版框**——外框比这几页磨损的内框黑 3 倍。
   搜索范围 SEARCH 一旦 >= 内外框间距（实测 38.4±4.0px），vol01/137、/138
   的重拟就正好落到算法线下方 +58.8/+57.5px，那就是外框。
2. 想拿金标自己的 `*_outer_offset` 把外框挖掉也不行——**它是相对于同一条
   misplaced 的内框量的**，内框错了它就跟着错，挖不准。vol01/138 挖完还是
   落在 +57.5px。
所以这三页得人工裁决：内框到底是印糊了还是根本没印上。

跑法：
    python scripts/report_border_hlines_offtarget.py
原图路径用 GUJI_RAW 覆盖（默认 /home/user/rebuild_src）。
"""
import json
import os
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "border-detection" / "samples"
RAW = Path(os.environ.get("GUJI_RAW", "/home/user/rebuild_src"))

STEP, HALF, WINW = 20, 11, 24     # HALF 必须 < 内外版框间距(实测 36~40px)，
MIN_FRAC, MAXW = 0.55, 14         # 否则脊线会跳到外框上——竖直线那边栽过
COV_BAD = 0.15                    # 覆盖率低于这个就算"整条脱靶"


def _y_at(rec, x_new):
    return rec["y_at_right"] + rec["slope"] * x_new


def probe(m, y_of, w, h, x_lo, x_hi):
    """沿 x 采样，返回 (覆盖率, 平均|距离|)。`y_of(x_old) -> y`。

    合格版框峰的条件：峰值处 >=MIN_FRAC 的列有墨，且半高宽 <=MAXW（排掉字
    的横画）。亚像素取半高以上加权质心。
    """
    hits, n = [], 0
    for x in range(x_lo, x_hi, STEP):
        c = int(round(y_of(x)))
        lo, hi = max(0, c - HALF), min(h, c + HALF + 1)
        if hi - lo < 10:
            continue
        band = m[lo:hi, max(0, x - WINW // 2):x + WINW // 2]
        if band.shape[1] < WINW // 2:
            continue
        n += 1
        prof = band.sum(axis=1).astype(float)
        pk = int(np.argmax(prof))
        if prof[pk] < MIN_FRAC * band.shape[1]:
            continue
        half = prof[pk] / 2.0
        a = b = pk
        while a > 0 and prof[a - 1] >= half:
            a -= 1
        while b < len(prof) - 1 and prof[b + 1] >= half:
            b += 1
        if b - a > MAXW:
            continue
        seg = prof[a:b + 1]
        y = lo + float((np.arange(a, b + 1) * seg).sum() / seg.sum())
        hits.append(abs(y - y_of(x)))
    if n == 0:
        return 0.0, float("nan")
    return len(hits) / n, (float(np.mean(hits)) if hits else float("nan"))


def row_ink(m, rec, w, h, x_lo, x_hi):
    """线所经过的那一行的墨占比——最直白的"在不在墨上"。"""
    xs = np.arange(x_lo, x_hi, 2)
    yy = np.rint([_y_at(rec, (w - 1) - x) for x in xs]).astype(int)
    ok = (yy >= 0) & (yy < h)
    return float(m[yy[ok], xs[ok]].mean()) if ok.any() else 0.0


def main() -> int:
    bad = []
    print(f"{'页':>10}{'边':>9} | {'覆盖率':>7}{'离墨':>7}{'行墨':>7} | 判")
    for path in sorted(SAMPLES.glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        book, page = d["book"], d["page"]
        img = cv2.imread(str(RAW / book / f"{page}.tif"), cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"{book + '/' + str(page):>10}  原图缺失，跳过")
            continue
        m = (img < 128).astype(np.uint8)
        h, w = m.shape
        vx = sorted(v["x_at_top"] + v["slope"] * (h / 2) for v in d["verticals_inner"])
        x_lo, x_hi = int((w - 1) - vx[-1] + 30), int((w - 1) - vx[0] - 30)
        if x_hi - x_lo < 200:
            continue
        for kind in ("top", "bottom"):
            rec = d[f"{kind}_inner"]
            cov, dist = probe(m, lambda x: _y_at(rec, (w - 1) - x), w, h, x_lo, x_hi)
            ink = row_ink(m, rec, w, h, x_lo, x_hi)
            if cov < COV_BAD:
                bad.append((book, page, kind, cov, ink))
                verdict = "**整条脱靶，需人工裁决**"
            else:
                verdict = ""
            print(f"{book + '/' + str(page):>10}{kind:>9} | {cov:7.2f}{dist:7.2f}{ink:7.3f} | {verdict}")
    print()
    if not bad:
        print("没有脱靶的边。")
    else:
        print(f"{len(bad)} 条边整条画在白纸上，需要人工裁决"
              f"（内框是印糊了还是根本没印上）：")
        for book, page, kind, cov, ink in bad:
            print(f"  - {book}/{page} {kind}_inner：覆盖率 {cov:.2f}、线上行墨 {ink:.3f}")
        print("  自动重拟已试过两版、都被外版框骗走，见模块 docstring。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
