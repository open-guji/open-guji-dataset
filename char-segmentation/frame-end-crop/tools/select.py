import json, random, sys, os
sys.path.insert(0,'/home/user/an')
from build_items import *
import libcmp
random.seed(20261104)
VOLS=sys.argv[1].split(',')
PER=int(sys.argv[2]) if len(sys.argv)>2 else 100
OUT='/home/user/an/items'; os.makedirs(OUT,exist_ok=True)
allitems=[]
sampling={}
for vol in VOLS:
    d=json.load(open(f'/home/user/an/{vol}_ends.json'))
    on={c['id']+(c['sub'] or ''):c for c in d['on']}
    E=[]
    for c in d['off']:
        k=c['id']+(c['sub'] or ''); o=on.get(k)
        p0=patch(vol,'off',c['key']); p1=patch(vol,'on',c['key'])
        if p0 is None: continue
        c['ratio_on']=o.get('ratio') if o else None
        c['changed']=not same(p0,p1)
        E.append(c)
    hi=[c for c in E if (c.get('ratio') or 0)>1.12]
    lo=[c for c in E if (c.get('ratio') or 9)<0.85 or (c.get('ratio_on') or 9)<0.85]
    ch=[c for c in E if c['changed']]
    pick={}
    K=lambda c:c['id']+(c['sub'] or '')
    seen=set(); strata={}
    for name,lst in (('lo',lo),('hi',hi),('changed',ch),('rest',E)):
        strata[name]=[c for c in lst if K(c) not in seen]; seen|={K(c) for c in strata[name]}
    W={}
    def take(name,n):
        lst=list(strata[name]); random.shuffle(lst); got=lst[:n]
        for c in got: pick[K(c)]=(c,name)
        W[name]=(len(strata[name])/len(got)) if got else 0
    take('lo',15); take('hi',40); take('changed',20); take('rest',PER-len(pick))
    sampling[vol]={n:dict(pop=len(strata[n]),picked=sum(1 for _,(c,x) in pick.items() if x==n)) for n in strata}
    # 参照字块：同字列中墨高最接近中位数的
    cells=libcmp.measure(vol,'off',libcmp.load(vol,'off'))
    grp={}
    for c in cells:
        if c['end'] is None and c['admit'] and c['ink_h'] and 3<=c['slot']<=19:
            grp.setdefault((c['char'],c['sub'] is not None),[]).append(c)
    for k,(c,why) in pick.items():
        g=grp.get((c['char'],c['sub'] is not None),[])
        ref=None
        if len(g)>=3:
            med=sorted(x['ink_h'] for x in g)[len(g)//2]
            ref=min(g,key=lambda x:abs(x['ink_h']-med))
        it=dict(id=k, vol=vol, end=c['end'], char=c['char'], slot=c['slot'], sub=c['sub'], why=why,
                weight=round(W[why],3), ratio_off=c.get('ratio'), ratio_on=c.get('ratio_on'), changed=c['changed'], key=c['key'],
                bbox_page=c['bbox_page'], ref_id=ref['id'] if ref else None)
        p0=patch(vol,'off',c['key']); p1=patch(vol,'on',c['key'])
        it['off_sha']=hashlib.sha1(np.asarray(p0).tobytes()+bytes(str(p0.size),'ascii')).hexdigest()[:16]
        it['on_sha']=hashlib.sha1(np.asarray(p1).tobytes()+bytes(str(p1.size),'ascii')).hexdigest()[:16] if p1 is not None else None
        img=dict(ctx=b64(context(vol,c)), off=b64(p0))
        if c['changed'] and p1 is not None: img['on']=b64(p1)
        if ref: img['ref']=b64(patch(vol,'off',ref['key']))
        it['img']=img
        allitems.append(it)
    print(vol, {w:sum(1 for _,(c,x) in pick.items() if x==w) for w in ('lo','hi','changed','rest')}, 'hi总',len(hi),'lo总',len(lo),'changed总',len(ch),'端格',len(E), 'top',sum(1 for _,(c,x) in pick.items() if c['end']=='top'))
random.shuffle(allitems)
json.dump(dict(seed=20261104,vols=VOLS,per=PER,rule='端格=列首(最小 slot<=1)/列尾(最大 slot>=21)；ratio=字块墨高/同册同字列中(slot3-19、已放行)墨高中位数；lo=<0.85(关或开)，hi=>1.12(关)，changed=开 inner_frame_cut 后字块变了，rest=其余；各层不重叠，按 lo→hi→changed→rest 先到先得',strata=sampling),open(f'{OUT}/sampling.json','w'),ensure_ascii=False,indent=1)
meta=[{k:v for k,v in it.items() if k!='img'} for it in allitems]
json.dump(meta,open(f'{OUT}/manifest.json','w'),ensure_ascii=False,indent=0)
CH=50
for i in range(0,len(allitems),CH):
    json.dump([dict(id=it['id'],vol=it['vol'],end=it['end'],char=it['char'],img=it['img']) for it in allitems[i:i+CH]],open(f'{OUT}/chunk-{i//CH:02d}.json','w'),ensure_ascii=False)
print('items',len(allitems), 'size MB', sum(os.path.getsize(f'{OUT}/'+f) for f in os.listdir(OUT))/1e6)
