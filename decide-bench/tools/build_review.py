"""小型集人抽审页（CV4，2026-11-23）：stratify 的样本 → guji-manager gold_sample（check 模式）的 items。

用法：python decide-bench/tools/build_review.py <strat.jsonl> <产物根/册> <页图目录> <图输出目录> --out items.jsonl [--ok-sample 10] [--seed 0]

上页的格：算法与人裁不一致的（放错字、放成异体、拦住·首选对、拦住·首选错），推翻参校本的（override_ref），
再随机加几格「放对」当对照。`review:excluded` 不上页（是冻结输入里带进来的人裁排除名单，不是算法规则）。
页上显示的是**人裁金标字**（pre），人点「对」＝金标对；算法字不同时给「改作 算法字」一键。
裁图按 cell_shrink 字框（同 guji-manager review_pages/crop.py），邻格条左右各 2 格。
"""
import json, random, sys
from pathlib import Path
from guji_manager.review_pages import crop as crop_mod

strat, prod, pages, outdir = sys.argv[1:5]
arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
prod, pages, outdir = Path(prod), Path(pages), Path(outdir)
outdir.mkdir(parents=True, exist_ok=True)
R = [json.loads(l) for l in open(strat)]
rnd = random.Random(int(arg("--seed", 0)))
want = [r for r in R if r["rule"] != "review:excluded" and (r["outcome"] != "放对" or r["cls"] == "override_ref")]
ok = [r for r in R if r["rule"] != "review:excluded" and r["outcome"] == "放对" and r["cls"] != "override_ref"]
want += rnd.sample(ok, min(len(ok), int(arg("--ok-sample", 10))))

from PIL import Image
Image.MAX_IMAGE_PIXELS = None
_sh, _ref = {}, {}


def shrink(pg):
    if pg not in _sh:
        f = prod / "cell_shrink" / f"p{pg:04d}.json"
        d = json.loads(f.read_text()) if f.exists() else {}
        _sh[pg] = (d.get("char_index") or d.get("cell_shrink", {}).get("char_index") or {}).get("columns", [])
    return _sh[pg]


def refseq(pg):
    if pg not in _ref:
        f = prod / "align_ref" / f"p{pg:04d}.json"
        xs = json.loads(f.read_text())["align_ref"].get("chars") or [] if f.exists() else []
        _ref[pg] = [(x["id"], x.get("align_char") or "") for x in xs]
    return _ref[pg]


items, miss = [], []
for r in want:
    cid = r["id"]
    pg = int(cid.split(":")[1])
    chars = at = None
    for col in shrink(pg):
        ids = [c["id"] for c in col.get("chars", [])]
        if cid in ids:
            chars, at = col["chars"], ids.index(cid)
    img = pages / f"{pg}.png"
    if chars is None or not chars[at].get("bbox_page") or not img.exists():
        miss.append(cid)
        continue
    im = Image.open(img).convert("L")
    base = cid.replace(":", "_")
    f = outdir / f"{base}.png"
    im.crop(crop_mod.to_image_box(chars[at]["bbox_page"], im.width, 3)).save(f)
    strip, strip_at = [], 0
    for j in range(max(0, at - 2), min(len(chars), at + 3)):
        b = chars[j].get("bbox_page")
        if not b:
            continue
        t = im.crop(crop_mod.to_image_box(b, im.width, 3)); t.thumbnail((120, 120))
        sf = outdir / f"{base}_s{j - at:+d}.png"; t.save(sf)
        if j == at:
            strip_at = len(strip)
        strip.append(str(sf))
    seq = refseq(pg)
    k = next((i for i, (x, _) in enumerate(seq) if x == cid), None)
    left = "".join(c for _, c in seq[max(0, k - 12):k]) if k is not None else ""
    right = "".join(c for _, c in seq[k + 1:k + 13]) if k is not None else ""
    g, a = r["char"], r.get("algo")
    cands = {g: ["人裁"]}
    if r.get("ref"):
        cands.setdefault(r["ref"], []).append("整理本")
    if a:
        cands.setdefault(a, []).append("算法")
    items.append({"id": cid, "pre": g, "ref_char": r.get("ref") or "", "lib": a if a and a != g else None, "cands": cands,
                  "left": left, "right": right, "kind": f"{r['outcome']}｜{r['rule']}",
                  "fact": f"人裁 {g}｜算法 {a or '无'}（{r['rule']}）｜整理本 {r.get('ref') or '无'}｜{r['cls']}｜事件 {r['event']}",
                  "img": str(f), "strip": strip, "strip_at": strip_at})
Path(arg("--out")).write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items))
print(json.dumps({"上页": len(items), "缺图": len(miss), "缺图样例": miss[:5]}, ensure_ascii=False))
