#!/usr/bin/env python3
"""frame-end-crop 评测：拿一版新切出来的列端字块，对照人点过的字块，数带框、切笔还剩多少。

用法：
    python eval_frame_end_crop.py --patches <工作区>/cache/{vol}/char_patch [--json]

`--patches` 里的 `{vol}` 换成册号，目录下是 `guji step cell_shrink` 写的字块 `<patch_key>.png`。

判法：每条金标存了它被点时的字块指纹（sha）。新字块和某个已点字块逐像素相同，就沿用那个标签；
都不同就记「变了、没标」，要补看（看图单或人工），不猜。所以这把尺子能直接回答：
- 已知带框／切笔的字块，新版还剩几个一模一样的（没修好）；
- 已知干净的字块，新版有几个变了（可能弄坏，要补看）。
指纹算法与建集时一致：sha1(灰度像素字节 + str((宽, 高)))[:16]。
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent.parent


def sha_of(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    im = Image.open(path).convert("L")
    return hashlib.sha1(np.asarray(im).tobytes() + bytes(str(im.size), "ascii")).hexdigest()[:16]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--patches", required=True, help="字块目录模板，含 {vol}")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    items = [json.loads(l) for l in open(HERE / "items.jsonl", encoding="utf-8") if l.strip()]
    tally = collections.Counter()
    detail = []
    for it in items:
        if it.get("status") != "active":
            continue
        anc = it["anchor"]
        known = {c["sha"]: c["label"] for c in it["expected"]["crops"].values() if c.get("label")}
        prior = {c["label"] for c in it["expected"]["crops"].values() if c.get("label")}
        s = sha_of(os.path.join(a.patches.format(vol=anc["book"]), anc["patch_key"] + ".png"))
        if s is None:
            lab = "missing"
        else:
            lab = known.get(s, "changed")
        tally[lab] += 1
        if lab == "changed" and prior & {"clean"} and not prior & {"frame", "cut"}:
            tally["changed_from_clean"] += 1
        if lab in ("frame", "cut", "changed", "missing"):
            detail.append({"id": it["id"], "result": lab, "prior": sorted(prior)})
    n = sum(tally[k] for k in ("clean", "frame", "cut", "unsure", "changed", "missing"))
    out = {"n": n, **{k: tally[k] for k in ("clean", "frame", "cut", "unsure", "changed", "changed_from_clean", "missing")}, "detail": detail}
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        print(f"共 {n} 格：干净 {out['clean']}、带框 {out['frame']}、切笔 {out['cut']}、说不准 {out['unsure']}、"
              f"变了没标 {out['changed']}（其中原来干净的 {out['changed_from_clean']}）、缺字块 {out['missing']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
