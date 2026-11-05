import json, random, sys, os
sys.path.insert(0,'/home/user/an')
from build_items import *
import libcmp
random.seed(20261105)
VOLS=sys.argv[1].split(',')
HI=int(sys.argv[2]); LO=int(sys.argv[3])
OUT='/home/user/an/items2'; os.makedirs(OUT,exist_ok=True)
done={m['id'] for m in json.load(open('/home/user/an/items/manifest.json'))}
allitems=[]; sampling={}
for vol in VOLS:
    d=json.load(open(f'/home/user/an/{vol}_ends.json'))
    off={c['id']+(c['sub'] or ''):c for c in d['off']}
    E=[]
    for c in d['on']:
        k=c['id']+(c['sub'] or '')
        if k in done: continue
        p0=patch(vol,'off',c['key']); p1=patch(vol,'on',c['key'])
        if p1 is None: continue
        c['changed']=not same(p0,p1); c['ratio_off']=(off.get(k) or {}).get('ratio'); E.append(c)
    lo=[c for c in E if (c.get('ratio') or 9)<0.85]
    hi=[c for c in E if (c.get('ratio') or 0)>1.12]
    random.shuffle(lo); random.shuffle(hi)
    pick=[(c,'lo2') for c in lo[:LO]]+[(c,'hi2') for c in hi[:HI]]
    sampling[vol]=dict(lo2=dict(pop=len(lo),picked=min(LO,len(lo))),hi2=dict(pop=len(hi),picked=min(HI,len(hi))))
    cells=libcmp.measure(vol,'on',libcmp.load(vol,'on')); grp={}
    for c in cells:
        if c['end'] is None and c['admit'] and c['ink_h'] and 3<=c['slot']<=19:
            grp.setdefault((c['char'],c['sub'] is not None),[]).append(c)
    for c,why in pick:
        k=c['id']+(c['sub'] or '')
        g=grp.get((c['char'],c['sub'] is not None),[]); ref=None
        if len(g)>=3:
            med=sorted(x['ink_h'] for x in g)[len(g)//2]; ref=min(g,key=lambda x:abs(x['ink_h']-med))
        p1=patch(vol,'on',c['key']); p0=patch(vol,'off',c['key'])
        st=sampling[vol][why]
        it=dict(id=k,vol=vol,end=c['end'],char=c['char'],slot=c['slot'],sub=c['sub'],why=why,weight=round(st['pop']/st['picked'],3),
                ratio_off=c['ratio_off'],ratio_on=c.get('ratio'),changed=c['changed'],key=c['key'],bbox_page=c['bbox_page'],ref_id=ref['id'] if ref else None,
                off_sha=hashlib.sha1(np.asarray(p0).tobytes()+bytes(str(p0.size),'ascii')).hexdigest()[:16] if p0 is not None else None,
                on_sha=hashlib.sha1(np.asarray(p1).tobytes()+bytes(str(p1.size),'ascii')).hexdigest()[:16])
        img=dict(ctx=b64(context(vol,c)), on=b64(p1))
        if ref: img['ref']=b64(patch(vol,'on',ref['key']))
        it['img']=img; allitems.append(it)
    print(vol, sampling[vol])
random.shuffle(allitems)
json.dump(dict(seed=20261105,vols=VOLS,rule='第二批：只看开 inner_frame_cut 后的字块；lo2=新字块墨高/同字列中中位数<0.85，hi2=>1.12；去掉第一批已抽的格',strata=sampling),open(f'{OUT}/sampling.json','w'),ensure_ascii=False,indent=1)
json.dump([{k:v for k,v in it.items() if k!='img'} for it in allitems],open(f'{OUT}/manifest.json','w'),ensure_ascii=False,indent=0)
for i in range(0,len(allitems),50):
    json.dump([dict(id=it['id'],vol=it['vol'],end=it['end'],char=it['char'],img=it['img']) for it in allitems[i:i+50]],open(f'{OUT}/chunk-{i//50:02d}.json','w'),ensure_ascii=False)
print('items',len(allitems))
