"""把「查询格清单」冻结成自带归一图、带固定候选池的分片（A23，2026-11-23）。

用于 3a 的 A5 退化（ai-team 残笔细笔真实残损集）等「库内刻例当查询」的集：查询是本书字形库里的刻例，
候选池按 cv `scripts/eval_sim_bench.py build_pool` 的规则从**按物理格留一**的库里取
（同字 HOG 前 8 例；HOG 最像的 8 个异字各 3 例；再补形近表对家），然后把查询与候选的归一图都落进 `crops/`，
此后打分只看分片、不碰字形库。

    python scripts/build_glyph_poolset.py <清单.tsv> <书名列值> <glyph.db> <输出目录> [--kind-col 类别]

清单 tsv 要有列：书、格（instance_id）、金标字、类别。金标字以清单为准（人裁），不取库标签。
"""
import argparse
import csv
import hashlib
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

CV = Path(__file__).resolve().parents[2] / "open-guji-cv"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tsv")
    ap.add_argument("book")
    ap.add_argument("db")
    ap.add_argument("out")
    ap.add_argument("--cv", default=str(CV))
    ap.add_argument("--source", default="")
    a = ap.parse_args()
    sys.path[:0] = [a.cv, a.cv + "/scripts"]
    import pickle
    from eval_sim_bench import build_pool  # noqa: E402

    rows = [r for r in csv.DictReader(open(a.tsv, encoding="utf-8"), delimiter="\t") if r["书"] == a.book]
    con = sqlite3.connect(a.db)
    out = Path(a.out)
    (out / "crops").mkdir(parents=True, exist_ok=True)
    kept, skipped = [], []
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "crops").mkdir()
        inst = []
        for r in rows:
            iid = r["格"]
            x = con.execute("SELECT data FROM derived WHERE instance_id=? AND kind='norm'", (iid,)).fetchone()
            if x is None:
                skipped.append(iid)
                continue
            name = iid.replace(":", "_") + ".png"
            (td / "crops" / name).write_bytes(x[0])
            inst.append(dict(instance_id=iid, char=r["金标字"], crop="crops/" + name))
            kept.append(r)
        (td / "expected.json").write_text(json.dumps(dict(instances=inst), ensure_ascii=False), encoding="utf-8")
        build_pool(a.db, td, td / "pool.pkl")
        D = pickle.load(open(td / "pool.pkl", "rb"))
    lib = D["lib"]
    used = set()
    items = []
    for r, q in zip(kept, D["qs"]):
        assert q["id"] == r["格"]
        cands = [dict(id=lib["ids"][j], char=q["gold"], same=True) for j in q["gold_rows"]]
        cands += [dict(id=lib["ids"][j], char=c, same=False) for c, js in q["rivals"].items() for j in js]
        items.append(dict(query_id=q["id"], gold=q["gold"], kind=r["类别"], candidates=cands))
        used.add(q["id"])
        used.update(c["id"] for c in cands)
    for iid in sorted(used):
        x = con.execute("SELECT data FROM derived WHERE instance_id=? AND kind='norm'", (iid,)).fetchone()
        (out / "crops" / (iid.replace(":", "_") + ".png")).write_bytes(x[0])
    with open(out / "items.jsonl", "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    sha = hashlib.sha256(Path(a.db).read_bytes()).hexdigest()
    import collections
    info = dict(schema_version=1, book=a.book, kind="poolset", source=a.source or a.tsv,
                crops_from=f"glyph.db sha256 {sha[:16]}（derived.norm；候选池按物理格留一）",
                n_items=len(items), n_crops=len(used), n_answerable=sum(any(c["same"] for c in i["candidates"]) for i in items),
                by_kind=dict(collections.Counter(i["kind"] for i in items)), skipped_no_norm=skipped)
    (out / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(info, ensure_ascii=False))


if __name__ == "__main__":
    main()
