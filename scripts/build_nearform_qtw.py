"""把 OCR 研究的「形近字组字形判别基准」（全唐文，11-18）冻结成 3a A6 分片（CV3，2026-11-23）。

来源（ai-team `domain/CV/字形领域/形近字组字形判别基准-2026-11-18/data/`）：
  meta.jsonl（一格一行：id=册:页:列:位、放行字 label、tier、dis 分歧）、boxes.jsonl（与 meta 逐行对应，
  页内框 x0..x1 从右起量）、pairs.json（122 对）、最终标签-逐格改标.json（{字对: {格: f 翻成另一字 | b 不计}}）。
原图：`guji source pull --book-id 995ejelvk0 --vol <册> --to <img>/<册>`（页号不补零）。

做法：按框从原图裁灰度块 im[y0:y1, W-1-x1 : W-1-x0]，cv `normalize_patch` 归一成 64×64 {0,1}，
打包进 `crops.npz`（ids、norm=packbits）；`items.jsonl` 一行一个「字对×格」。
最终标签规则同 OCR `code/build_labels.py`：己已／已巳／己巳／望朢 整对不用；千干／日曰／天夭 标签保持放行字（文意定）；
其余对按逐格改标翻或不计。dev/test 按册号奇偶（奇＝dev），另留 OCR 的三折 fold。

    python scripts/build_nearform_qtw.py <data 目录> <img 目录> <输出目录> [--cv ../open-guji-cv]
"""
import argparse
import collections
import json
import sys
from pathlib import Path

import numpy as np

DROP = {"己已", "已巳", "己巳", "望朢"}
CTX = {"千干", "日曰", "天夭"}


def _vol(job):
    """一册：按页读原图、裁、归一；结果存 <cache>/<册>.npz（中断后重跑跳过已做的册）。"""
    v, bs, img, cache, cv = job
    f = Path(cache) / f"{v}.npz"
    if f.exists():
        return v, f
    sys.path[:0] = [cv]
    from PIL import Image
    from open_guji_cv.clustering.normalize import normalize_patch
    bypg = collections.defaultdict(list)
    for b in bs:
        bypg[b["page"]].append(b)
    ids, norms, sizes = [], [], collections.Counter()
    for pg, xs in sorted(bypg.items()):
        im = np.array(Image.open(Path(img) / v / f"{pg}.png").convert("L"))
        W = im.shape[1]
        sizes[f"{im.shape[0]}x{W}"] += 1
        for b in xs:
            crop = im[max(b["y0"], 0):b["y1"], max(W - 1 - b["x1"], 0):W - 1 - b["x0"]]
            ids.append(b["id"])
            norms.append(normalize_patch(crop))
    np.savez(f, ids=np.array(ids), norm=np.stack(norms).astype(np.uint8), sizes=np.array(dict(sizes), dtype=object))
    return v, f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("img")
    ap.add_argument("out")
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--cv", default=str(Path(__file__).resolve().parents[2] / "open-guji-cv"))
    a = ap.parse_args()
    sys.path[:0] = [a.cv]
    from PIL import Image
    from open_guji_cv.clustering.normalize import normalize_patch

    d = Path(a.data)
    meta = [json.loads(x) for x in open(d / "meta.jsonl", encoding="utf-8")]
    boxes = [json.loads(x) for x in open(d / "boxes.jsonl", encoding="utf-8")]
    assert [b["id"] for b in boxes] == [m["id"] for m in meta], "boxes 与 meta 不逐行对应"
    pairs = json.load(open(d / "pairs.json", encoding="utf-8"))
    fix = json.load(open(d / "最终标签-逐格改标.json", encoding="utf-8"))

    by_char = collections.defaultdict(list)
    for pk, p in pairs.items():
        if pk in DROP:
            continue
        by_char[p["a"]].append(pk)
        by_char[p["b"]].append(pk)

    items, st = [], collections.Counter()
    for m in meta:
        for pk in by_char.get(m["label"], []):
            p = pairs[pk]
            other = p["b"] if m["label"] == p["a"] else p["a"]
            f = fix.get(pk, {}).get(m["id"])
            if f == "b":
                st["不计"] += 1
                continue
            gold = other if f == "f" else m["label"]
            st["翻" if f == "f" else "留"] += 1
            v = int(m["v"])
            items.append(dict(
                pair=pk, a=p["a"], b=p["b"], kind=p.get("kind"), ctrl=bool(p.get("ctrl")),
                id=m["id"], v=m["v"], split="dev" if v % 2 else "test", fold=m["fold"],
                released=m["label"], gold=gold, flipped=f == "f",
                label_src=("文意" if pk in CTX else "人裁" if pk in fix else "放行字"),
                tier=m["tier"], hard=pk in (m.get("dis") or {})))

    need = {it["id"] for it in items}
    byv = collections.defaultdict(list)
    for b in boxes:
        if b["id"] in need:
            byv[b["v"]].append(b)
    from multiprocessing import Pool
    cache = Path(a.out) / "_vols"
    cache.mkdir(parents=True, exist_ok=True)
    jobs = [(v, byv[v], a.img, str(cache), a.cv) for v in sorted(byv)]
    ids, norms, sizes = [], [], collections.Counter()
    with Pool(a.procs) as pool:
        for v, f in pool.imap(_vol, jobs):
            z = np.load(f, allow_pickle=True)
            ids += [str(x) for x in z["ids"]]
            norms += list(z["norm"])
            for k, n in z["sizes"].item().items():
                sizes[k] += n
            print(v, len(z["ids"]), flush=True)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    N = np.stack(norms).astype(np.uint8)
    np.savez_compressed(out / "crops.npz", ids=np.array(ids), norm=np.packbits(N, axis=-1), shape=np.array(N.shape))
    with open(out / "items.jsonl", "w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")
    info = dict(
        name="nearform-qtw", book="995ejelvk0", source="ai-team domain/CV/字形领域/形近字组字形判别基准-2026-11-18/data",
        built_by="open-guji-dataset scripts/build_nearform_qtw.py",
        n_cells=len(ids), n_items=len(items), n_pairs=len({it["pair"] for it in items}),
        labels=dict(st), page_sizes=dict(sizes),
        rules=dict(drop=sorted(DROP), context_only=sorted(CTX)))
    (out / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(info, ensure_ascii=False))


if __name__ == "__main__":
    main()
