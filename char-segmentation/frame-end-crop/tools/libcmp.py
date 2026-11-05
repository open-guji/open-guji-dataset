"""同字对照：列端字块墨高 vs 同册同字列中字块墨高中位数。"""
import json, glob, os, sys, statistics as st
import numpy as np
from PIL import Image
WS='/home/user/ws'
CPL=21
def ink_rows(path, thr=160):
    a=np.asarray(Image.open(path).convert('L'))
    m=(a<thr)
    r=np.where(m.sum(1)>=2)[0]
    if len(r)==0: return None
    return int(r[-1]-r[0]+1), a.shape
def load(vol, mode):
    chars={}
    for f in glob.glob(f'/home/user/prod_main/{vol}/seed_admit/p*.json'):
        for col in json.load(open(f))['seed_admit']['columns']:
            for c in col['chars']:
                chars[c['id']+(c['sub'] or '')]=(c.get('char'),c.get('admit'))
    cells=[]
    for f in sorted(glob.glob(f'/home/user/sb_{mode}/{vol}/cell_shrink/p*.json')):
        ci=json.load(open(f))['char_index']
        for col in ci['columns']:
            cs=[c for c in col['chars'] if c['cell_type']=='char']
            if not cs: continue
            smin=min(c['slot'] for c in cs); smax=max(c['slot'] for c in cs)
            for c in cs:
                end=None
                if c['slot']==smin and smin<=1: end='top'
                elif c['slot']==smax and smax>=CPL: end='bot'
                ch,ad=chars.get(c['id']+(c['sub'] or ''),(None,None))
                cells.append(dict(id=c['id'],sub=c['sub'],slot=c['slot'],end=end,char=ch,admit=ad,
                    key=c['patch_key'],bbox_page=c['bbox_page'],h=c['height'],w=c['width'],page=ci['page'] if 'page' in ci else None))
    return cells
def measure(vol, mode, cells):
    d=f'{WS}/cache/{vol}/char_patch_{mode}'
    for c in cells:
        p=f"{d}/{c['key']}.png"
        r=ink_rows(p) if os.path.exists(p) else None
        c['ink_h']=r[0] if r else None
    return cells
def refs(cells):
    g={}
    for c in cells:
        if c['end'] is None and c['admit'] and c['ink_h'] and 3<=c['slot']<=CPL-2:
            g.setdefault((c['char'],c['sub'] is not None),[]).append(c['ink_h'])
    return {k:(st.median(v),len(v)) for k,v in g.items() if len(v)>=3}
if __name__=='__main__':
    vol=sys.argv[1]
    out={}
    for mode in ('off','on'):
        cells=measure(vol,mode,load(vol,mode))
        R=refs(cells)
        for c in cells:
            if c['end'] and c['ink_h']:
                r=R.get((c['char'],c['sub'] is not None))
                c['ratio']=round(c['ink_h']/r[0],3) if r else None
                c['nref']=r[1] if r else 0
        out[mode]=[c for c in cells if c['end']]
    json.dump(out,open(f'/home/user/an/{vol}_ends.json','w'),ensure_ascii=False)
    for mode in out:
        e=out[mode]; cmp=[c for c in e if c.get('ratio')]
        for end in ('top','bot'):
            x=[c for c in cmp if c['end']==end]
            print(vol,mode,end,len([c for c in e if c['end']==end]),'可比',len(x),'偏高',sum(c['ratio']>1.12 for c in x),'偏矮',sum(c['ratio']<0.85 for c in x))
