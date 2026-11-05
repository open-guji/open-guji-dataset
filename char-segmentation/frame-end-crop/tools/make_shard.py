import json, glob, os, shutil, collections
SH='/home/user/open-guji-dataset/char-segmentation/frame-end-crop'
WS='/home/user/ws'
TS='2026-11-05T01:10:00Z'
CV='open-guji-cv dev bc219f2（cell_shrink 1.25）'
rows=[]; stats=collections.Counter()
def lab(v): return v if v in ('clean','frame','cut','unsure') else None
def cp(vol,mode,key):
    src=f'{WS}/cache/{vol}/char_patch_{mode}/{key}.png'
    rel=f'crops/{vol}/{key}_{mode}.png'; os.makedirs(f'{SH}/crops/{vol}',exist_ok=True)
    shutil.copyfile(src,f'{SH}/{rel}'); return rel
for batch,mdir,hdir in (('b1','items','harvest/labels'),('b2','items2','harvest2/labels')):
    man={m['id'].replace(':','-'):m for m in json.load(open(f'/home/user/an/{mdir}/manifest.json'))}
    for f in sorted(glob.glob(f'/home/user/an/{hdir}/*.json')):
        k=os.path.basename(f)[:-5]; x=json.load(open(f)); m=man[k]
        off=lab(x.get('off')); on=lab(x.get('on'))
        if batch=='b1' and not m['changed']: on=off        # 开关前后字块逐像素相同，标签同一份
        crops={}
        if batch=='b1': crops['off']=dict(label=off,sha=m['off_sha'],file=cp(m['vol'],'off',m['key']))
        if on is not None or batch=='b2' or m['changed']:
            crops['on']=dict(label=on,sha=m['on_sha'],file=cp(m['vol'],'on',m['key']))
        if not any(c['label'] for c in crops.values()): continue
        parts=m['id'].split(':'); 
        rows.append(dict(id=m['id'], status='active', label_origin='human',
            anchor=dict(book=m['vol'],page=int(parts[1]),col=int(parts[2]),slot=m['slot'],sub=m['sub'],end=m['end'],patch_key=m['key'],bbox_page_tr=m['bbox_page']),
            expected=dict(char=m['char'],crops=crops),
            input=dict(batch=batch,stratum=m['why'],weight=m['weight'],ratio_off=m.get('ratio_off'),ratio_on=m.get('ratio_on'),changed=m['changed'],ref_id=m['ref_id'],
                       cv=CV,inner_frame_cut={'off':False,'on':True}),
            source_events=[f'artifact-db:{batch}:{k}'],
            history=[dict(change='created',ts=TS,why='Sheldon 11-04 看图单点选（A22-1 列端评测集）')]))
        for mode,c in crops.items(): stats[(batch,mode,c['label'])]+=1
with open(f'{SH}/items.jsonl','w') as fo:
    for r in sorted(rows,key=lambda r:r['id']): fo.write(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n')
samp={'b1':json.load(open('/home/user/an/items/sampling.json')),'b2':json.load(open('/home/user/an/items2/sampling.json'))}
json.dump(samp,open(f'{SH}/sampling.json','w'),ensure_ascii=False,indent=1)
print(len(rows)); 
for k,v in sorted(stats.items(),key=str): print(k,v)
