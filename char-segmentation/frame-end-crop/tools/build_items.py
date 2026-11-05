import json, random, os, sys, io, base64, hashlib
import numpy as np
from PIL import Image, ImageDraw
WS='/home/user/ws'
def b64(im, fmt='PNG', q=80):
    bio=io.BytesIO()
    if fmt=='JPEG': im.convert('RGB').save(bio,'JPEG',quality=q)
    else: im.save(bio,'PNG',optimize=True)
    return ('data:image/jpeg;base64,' if fmt=='JPEG' else 'data:image/png;base64,')+base64.b64encode(bio.getvalue()).decode()
def page_of(cid): return int(cid.split(':')[1])
def context(vol, c):
    pg=page_of(c['id'])
    im=Image.open(f"{WS}/data_full/qiefen/{vol}/{pg}.png").convert('L')
    W,H=im.size
    x0,y0,x1,y1=c['bbox_page']; X0,X1=W-1-x1,W-1-x0
    h=y1-y0; w=X1-X0
    if c['end']=='bot': cy0,cy1=y0-1.2*h,y1+0.9*h
    else: cy0,cy1=y0-0.9*h,y1+1.2*h
    cx0,cx1=X0-0.45*w,X1+0.45*w
    box=tuple(int(round(v)) for v in (max(0,cx0),max(0,cy0),min(W,cx1),min(H,cy1)))
    cr=im.crop(box).convert('RGB'); d=ImageDraw.Draw(cr)
    d.rectangle([X0-box[0]-1,y0-box[1]-1,X1-box[0]+1,y1-box[1]+1],outline=(220,40,40),width=1)
    return cr
def patch(vol,mode,key):
    p=f"{WS}/cache/{vol}/char_patch_{mode}/{key}.png"
    return Image.open(p).convert('L') if os.path.exists(p) else None
def same(a,b):
    return a is not None and b is not None and a.size==b.size and np.array_equal(np.asarray(a),np.asarray(b))
