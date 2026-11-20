"""book-columns 打分：python score.py <items.jsonl> <预测.jsonl>
预测每行 {"id": 同 items, "cells": [{slot, sub, x0, x1, y0, y1}, …]}（列图坐标；只看有字格）。
一格算对：与某金标格 1 对 1 配上，且 IoU ≥ 0.75（按框算；a/b 半格同样按框）。
报：列全对率（金标每格都配上、预测没有多余格）、格级 P/R/F1、按类分。金标为空（none_overlap）的列跳过、单列计数。
不带预测文件时拿 items 里的 baseline 打分（即出问题那一版的切法）。"""
import json,sys
def iou(a,b):
    ix=max(0,min(a['x1'],b['x1'])-max(a['x0'],b['x0'])); iy=max(0,min(a['y1'],b['y1'])-max(a['y0'],b['y0']))
    i=ix*iy; u=(a['x1']-a['x0'])*(a['y1']-a['y0'])+(b['x1']-b['x0'])*(b['y1']-b['y0'])-i
    return i/u if u>0 else 0
def match(g,p,t=0.75):
    pairs=sorted(((iou(a,b),i,j) for i,a in enumerate(g) for j,b in enumerate(p)),reverse=True); ug,up=set(),set(); n=0
    for v,i,j in pairs:
        if v<t: break
        if i in ug or j in up: continue
        ug.add(i); up.add(j); n+=1
    return n
items=[json.loads(l) for l in open(sys.argv[1])]
pred={}
if len(sys.argv)>2:
    for l in open(sys.argv[2]): r=json.loads(l); pred[r['id']]=r['cells']
else:
    pred={r['id']:r['input']['baseline']['cells'] for r in items}
by={}; tot=[0,0,0,0,0]; skip=0
for r in items:
    g=r['expected']['cells']
    if not g: skip+=1; continue
    p=pred.get(r['id'],[]); n=match(g,p); ok=int(n==len(g)==len(p))
    for k,v in ((r['expected']['category'],None),('全部',None)):
        s=by.setdefault(k,[0,0,0,0,0]); s[0]+=1; s[1]+=ok; s[2]+=n; s[3]+=len(g); s[4]+=len(p)
for k,(c,ok,n,ng,np_) in sorted(by.items()):
    P=n/np_ if np_ else 0; R=n/ng if ng else 0; F=2*P*R/(P+R) if P+R else 0
    print(f"{k}\t列 {c}\t列全对 {ok}/{c}\t格 P {P:.3f} R {R:.3f} F1 {F:.3f}")
print(f"（金标留空、只作开放问题的列 {skip}）")
