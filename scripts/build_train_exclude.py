"""识字 benchmark 的训练隔离清单（A23，2026-11-23）：哪些格、哪些字不许进相似度 CNN 的训练。

评测格进了训练集，CNN 那一路的数就偏乐观（全唐文 glyph_sim_qtw 是全库训的，对抗集、残损集的格都见过）。
这里把各书识字评测分片里的查询格汇成 `glyph-match/train_exclude/<书>.cells.txt`，对抗集的留出字汇成
`<书>.held_chars.txt`（整字类都不许见，否则「库外字」在模型眼里不是库外）。训练时：

    python scripts/train_glyph_sim_cnn.py --db <书 glyph.db> \\
        --exclude ../open-guji-dataset/glyph-match/train_exclude/<书>.cells.txt \\
        --exclude-chars ../open-guji-dataset/glyph-match/train_exclude/<书>.held_chars.txt …

只读本仓文件、不连库。分片有增减就重跑：python scripts/build_train_exclude.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOKS = {
    "siku-v2": dict(expected=["char-clustering/samples/004-siku-v2-human/expected.json"],
                    jsonl=["glyph-match/advset-siku-v2/items.jsonl", "glyph-match/damaged-siku-v2/items.jsonl",
                           "char-clustering/samples/004-siku-v2-human/rare.jsonl"],
                    advset="glyph-match/advset-siku-v2"),
    "shiji": dict(expected=["char-clustering/samples/005-shiji-human/expected.json"],
                  jsonl=["glyph-match/advset-shiji/items.jsonl", "glyph-match/damaged-shiji/items.jsonl",
                         "char-clustering/samples/005-shiji-human/rare.jsonl"],
                  advset="glyph-match/advset-shiji"),
    "qtw": dict(expected=["char-clustering/samples/006-qtw-human/expected.json"],
                jsonl=["glyph-match/advset-qtw/items.jsonl", "char-clustering/samples/006-qtw-human/rare.jsonl",
                       "char-clustering/samples/007-qtw-firstseen/rare.jsonl"],
                advset="glyph-match/advset-qtw"),
}


def main():
    out = ROOT / "glyph-match" / "train_exclude"
    out.mkdir(parents=True, exist_ok=True)
    summary = {}
    for book, c in BOOKS.items():
        cells = set()
        for f in c["expected"]:
            cells |= {x["instance_id"] for x in json.loads((ROOT / f).read_text(encoding="utf-8"))["instances"]}
        for f in c["jsonl"]:
            for ln in (ROOT / f).read_text(encoding="utf-8").splitlines():
                if ln.strip():
                    x = json.loads(ln)
                    cells |= {x[k] for k in ("query_id", "id") if k in x}
        held = json.loads((ROOT / c["advset"] / "info.json").read_text(encoding="utf-8"))["held"]
        (out / f"{book}.cells.txt").write_text("\n".join(sorted(cells)) + "\n", encoding="utf-8")
        (out / f"{book}.held_chars.txt").write_text("\n".join(sorted(held)) + "\n", encoding="utf-8")
        summary[book] = dict(cells=len(cells), held_chars=len(held), sources=c["expected"] + c["jsonl"])
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: (v["cells"], v["held_chars"]) for k, v in summary.items()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
