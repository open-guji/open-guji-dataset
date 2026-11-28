"""大型层放行精度抽查（CV4，2026-11-24）：关人裁重跑里算法放行、又没有人裁金标的格，每册随机抽 N 格 → char_grid 页 items。

用法：python decide-bench/tools/sample_admit.py --items <分片>/items.jsonl --run <册>=<重跑产物/册>:<原图目录> … --img <图输出目录> --out items.jsonl [--n 30] [--seed 0]

人点错的格＝算法放错；放行精度≈1−错格/抽样格（按册、按放行通道报）。抽样按册等量，册内按格随机（大通道 match_ref 自然占多数）。
裁图按 cell_shrink 字框（同 build_review.py）。
"""
import argparse, glob, json, random
from pathlib import Path
from PIL import Image
from guji_manager.review_pages import crop as crop_mod

Image.MAX_IMAGE_PIXELS = None
ap = argparse.ArgumentParser()
ap.add_argument("--items", required=True)
ap.add_argument("--run", action="append", required=True)
ap.add_argument("--img", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--n", type=int, default=30)
ap.add_argument("--seed", type=int, default=0)
a = ap.parse_args()
gold = {json.loads(l)["anchor"]["key_at_freeze"] for l in open(a.items)}
img_dir = Path(a.img); img_dir.mkdir(parents=True, exist_ok=True)
rnd = random.Random(a.seed)
items = []
for spec in a.run:
    vol, rest = spec.split("=", 1)
    root, pages = (Path(p) for p in rest.split(":", 1))
    pool = []
    for f in sorted(glob.glob(str(root / "seed_admit" / "p*.json"))):
        for col in json.load(open(f))["seed_admit"]["columns"]:
            for x in col.get("chars") or []:
                if x.get("admit") and x.get("char") and x["id"] not in gold:
                    pool.append((x["id"], x["char"], x.get("channel")))
    got = 0
    for cid, ch, chan in rnd.sample(pool, len(pool)):
        if got >= a.n:
            break
        pg = int(cid.split(":")[1])
        sf = root / "cell_shrink" / f"p{pg:04d}.json"
        if not sf.exists():
            sf = Path(str(root).replace("/exp/", "/snap/").rsplit("/", 2)[0]) / vol / "cell_shrink" / f"p{pg:04d}.json"
        d = json.loads(sf.read_text()) if sf.exists() else {}
        cols = (d.get("char_index") or d.get("cell_shrink", {}).get("char_index") or {}).get("columns", [])
        b = next((c.get("bbox_page") for col in cols for c in col.get("chars", []) if c["id"] == cid), None)
        im_f = pages / f"{pg}.png"
        if not b or not im_f.exists():
            continue
        im = Image.open(im_f).convert("L")
        out = img_dir / (cid.replace(":", "_") + ".png")
        im.crop(crop_mod.to_image_box(b, im.width, 3)).save(out)
        items.append({"id": cid, "pre": ch, "kind": chan, "img": str(out)})
        got += 1
    print(vol, "可抽", len(pool), "抽", got)
Path(a.out).write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items))
