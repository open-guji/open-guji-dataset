# -*- coding: utf-8 -*-
"""严格版「算法 vs 金标 vs 真墨」对比，替代之前那版过松的量法。

之前那版的问题：窗口 ±50px 锚在算法/金标中点、只取 argmax、无亚像素、
无剔外点、STEP=120——会捞到**外边框**和字的竖笔画，把两边的误差一起
抬高（当时报的 5.90/6.36/4.27 三个数都偏大）。

这版：
- **只量内部界行 idx1..8**，跳过最外两条（旁边 20~31px 就是外边框，
  任何窗口都可能跳过去，量不干净）
- 窗口锚在算法/金标中点、半宽 30，峰值要 >=55% 的行有墨、半高宽 <=25
- 亚像素质心 + MAD 剔外点稳健拟合，用**拟合后的脊线**当基准
"""
import json, os
from pathlib import Path
import numpy as np, cv2

RAW = Path(os.environ.get("GUJI_RAW", "/home/user/rebuild_src")) / "vol01"
GOLD = Path(__file__).resolve().parent.parent / "border-detection" / "samples"
CACHE = Path(os.environ.get("GUJI_BORDERS_CACHE", "borders_cache.json"))
PAGES = ["137","138","32","33","49","9","14","142","24","65","141","26","47","51"]
STEP, HALF, WINH, MIN_FRAC, MAXW, MARGIN = 20, 30, 24, 0.55, 25, 70

def ridge(m, xat, y0, y1, w):
    ys, xs = [], []
    for y in range(y0, y1, STEP):
        c = int(round(xat(y))); lo, hi = max(0, c-HALF), min(w, c+HALF+1)
        band = m[max(0,y-WINH//2):y+WINH//2, lo:hi]
        if band.shape[0] < WINH//2 or hi-lo < 10: continue
        prof = band.sum(axis=0).astype(float); pk = int(np.argmax(prof))
        if prof[pk] < MIN_FRAC*band.shape[0]: continue
        half = prof[pk]/2.0; a=b=pk
        while a>0 and prof[a-1]>=half: a-=1
        while b<len(prof)-1 and prof[b+1]>=half: b+=1
        if b-a > MAXW: continue
        seg = prof[a:b+1]
        ys.append(float(y)); xs.append(lo+float((np.arange(a,b+1)*seg).sum()/seg.sum()))
    return np.array(ys), np.array(xs)

def rfit(ys, xs):
    keep=np.ones(len(ys),bool); k=b=0.0
    for _ in range(3):
        if keep.sum()<10: break
        k,b=np.polyfit(ys[keep],xs[keep],1); r=xs-(k*ys+b)
        med=np.median(r[keep]); mad=np.median(np.abs(r[keep]-med)) or 1.0
        keep=np.abs(r-med)<=2.5*1.4826*mad
    return k,b,keep

bc=json.load(CACHE.open())
A,G,BEST,BOW=[],[],[],[]
rows=[]
for page in PAGES:
    g=json.loads((GOLD/f"vol01_{page}.json").read_text())
    img=cv2.imread(str(RAW/f"{page}.tif"),cv2.IMREAD_GRAYSCALE); h,w=img.shape
    m=(img<128).astype(np.uint8)
    y0=int(g["top_inner"]["y_at_right"]+MARGIN); y1=int(g["bottom_inner"]["y_at_right"]-MARGIN)
    pa_,pg_,pb_=[],[],[]
    for i in range(1,9):                     # 只量内部界行
        p=bc[page]["verticals"][i]; q=g["verticals_inner"][i]
        ax=lambda y,p=p: (w-1)-(p[0]+p[1]*y)
        qx=lambda y,q=q: (w-1)-(q["x_at_top"]+q["slope"]*y)
        mid=lambda y: (ax(y)+qx(y))/2
        ys,xs=ridge(m,mid,y0,y1,w)
        if len(ys)<40: continue
        k,b,keep=rfit(ys,xs)
        if keep.sum()<40: continue
        yk,xk=ys[keep],xs[keep]
        da=float(np.mean(np.abs(xk-np.array([ax(y) for y in yk]))))
        dg=float(np.mean(np.abs(xk-np.array([qx(y) for y in yk]))))
        db=float(np.mean(np.abs(xk-(k*yk+b))))
        r=xk-(k*yk+b)
        pa_.append(da); pg_.append(dg); pb_.append(db); BOW.append(float(r.max()-r.min()))
        A.append(da); G.append(dg); BEST.append(db)
    if pa_:
        rows.append((page,len(pa_),np.mean(pa_),np.mean(pg_),np.mean(pb_)))

print(f"{'页':>5} {'条':>3} {'算法离墨':>9} {'金标离墨':>9} {'最佳直线':>9} {'算法-金标':>10}")
for pg,n,a,gg,b in rows:
    d=a-gg
    tag="  算法更贴" if d<-0.3 else ("  金标更贴" if d>0.3 else "")
    print(f"{pg:>5} {n:>3} {a:9.2f} {gg:9.2f} {b:9.2f} {d:+10.2f}{tag}")
print(f"\n内部界行 {len(A)} 条：算法={np.mean(A):.2f}px  金标={np.mean(G):.2f}px  "
      f"最佳直线={np.mean(BEST):.2f}px  真墨弯曲(峰-峰)={np.mean(BOW):.1f}px")
