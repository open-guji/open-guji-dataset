import json,collections,re,sys
sys.path.insert(0,'.')
G=list("彝彛彜彞𢑱𢑴")
exec(open("pc.py",encoding="utf-8").read().split("def main")[0])
def cause(d):
    ds=codes(d); c=d.get("char") or ""
    for n,f in BUCKETS:
        if f(d,ds,c): return n
    return OTHER
books=["vol01","vol02","vol03","vol04","vol05","vol06","vol07"]
out={}
for b in books:
    R=[json.loads(l) for l in open(f"ex2/{b}.jsonl",encoding="utf-8")]
    for g in G:
        cells=[x for x in R if x["char"]==g]
        refc=[x for x in R if x.get("ref")==g]
        top=[x for x in R if x.get("lib_top2") and g in x["lib_top2"] and x["char"]!=g]
        pg=lambda xs: len({x["id"].split(":")[1] for x in xs})
        out[(b,g)]=dict(char=len(cells),char_pages=pg(cells),admit=sum(x["admit"] for x in cells),pend=sum(not x["admit"] for x in cells),
            ref=len(refc),ref_char_diff=sum(1 for x in refc if x["char"]!=g),lib_top_only=len(top),
            causes=dict(collections.Counter(cause(x) for x in cells if not x["admit"])))
json.dump({f"{b}|{g}":v for (b,g),v in out.items()},open("yi_count.json","w"),ensure_ascii=False,indent=1)
print("| 码位 | "+" | ".join(books)+" |")
for g in G:
    print(f"| {g} U+{ord(g):X} | "+" | ".join((lambda v:f"{v['char']}(放{v['admit']}/待{v['pend']},{v['char_pages']}页)" if v['char'] else "0")(out[(b,g)]) for b in books)+" |")
print()
for g in G:
    print(g,"ref同字但engine字不同:",{b:out[(b,g)]['ref_char_diff'] for b in books if out[(b,g)]['ref']},"ref总",{b:out[(b,g)]['ref'] for b in books if out[(b,g)]['ref']},"仅lib前二",{b:out[(b,g)]['lib_top_only'] for b in books if out[(b,g)]['lib_top_only']})
print()
for g in G:
    c=collections.Counter()
    for b in books:
        c.update(out[(b,g)]["causes"])
    print(g,dict(c))
