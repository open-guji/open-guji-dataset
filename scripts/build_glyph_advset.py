"""把 ai-team 的「库外形近字对抗集」冻结成自带图块的分片（A23，2026-11-23）。

原集（ai-team domain/CV/字形领域/5a相似度CNN深化-2026-11-15/advset/，11-15 建）只存刻例 id，
图块在当时的 glyph.db 里，库一长一撤就对不上。这里按**现行库**取归一图（`derived.norm`，64×64）
落进 `glyph-match/advset-<书>/crops/`，此后打分只看分片、不再碰库。

    python scripts/build_glyph_advset.py <书简称 qtw|sj|sk> <ai-team advset/data 目录> <glyph.db> <输出目录>

和原集的差别（都记进 info.json）：
- 已撤库（不在 exemplars）的刻例：查询丢掉、候选去掉；
- 查询刻例现标签折叠后不是留出字的：丢掉（库订正过，原题不成立）；
- 候选现标签折叠后等于留出字的：去掉（那是同字，不是对抗候选）；
- 候选字一律用现行库标签（折叠己已巳／日曰）；`var` 按 cv 的异体关系重算（同 advset_build.variant）。
"""
import argparse
import gzip
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

CV = Path(__file__).resolve().parents[2] / "open-guji-cv"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("book", choices=["qtw", "sj", "sk"])
    ap.add_argument("src")
    ap.add_argument("db")
    ap.add_argument("out")
    ap.add_argument("--cv", default=str(CV))
    a = ap.parse_args()
    sys.path[:0] = [a.cv, a.cv + "/scripts"]
    from eval_fold import fold  # noqa: E402
    from open_guji_cv.clustering.variants import VariantMap  # noqa: E402
    from open_guji_cv import variants as VG  # noqa: E402

    same_shape = {"歳": "歲", "𠋫": "侯", "廏": "廄", "两": "兩"}
    vm = VariantMap.load()
    fv = lambda c: fold(vm.semantic(same_shape.get(c, c)))  # noqa: E731

    def variant(x, y):
        return fv(x) == fv(y) or bool(set(VG._graph().sources_of(x, y)) & VG.HIGH_CONFIDENCE_SOURCES)

    src, out = Path(a.src), Path(a.out)
    (out / "crops").mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(a.db)
    lab = {iid: ch for iid, ch in con.execute(
        "SELECT e.instance_id, g.char FROM exemplars e JOIN glyphs g ON g.glyph_id=e.glyph_id")}
    prov = {iid: p for iid, p in con.execute("SELECT instance_id, provenance FROM admissions")}
    src_meta = json.loads((src / f"meta_{a.book}.json").read_text(encoding="utf-8"))
    layer_of = {}
    for ln in (src / f"pairs_{a.book}.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        h, _, p, _, source, hog, _det = ln.split("\t")
        layer_of[(h, p)] = (source, float(hog))

    items, used, drop = [], set(), dict(query_evicted=0, query_relabeled=0, cand_evicted=0, cand_same_char=0)
    vcache = {}
    for ln in list(gzip.open(src / f"items_{a.book}.tsv.gz", "rt", encoding="utf-8"))[1:]:
        qid, held, knn, prt = ln.rstrip("\n").split("\t")
        if qid not in lab:
            drop["query_evicted"] += 1
            continue
        if fold(lab[qid]) != fold(held):
            drop["query_relabeled"] += 1
            continue
        cands, seen = [], set()
        for role, field in (("partner", prt), ("knn", knn)):
            for x in field.split():
                _, iid = x.split("|", 1)
                if iid in seen:
                    continue
                seen.add(iid)
                if iid not in lab:
                    drop["cand_evicted"] += 1
                    continue
                c = fold(lab[iid])
                if c == fold(held):
                    drop["cand_same_char"] += 1
                    continue
                if (held, c) not in vcache:
                    vcache[(held, c)] = variant(held, c)
                cands.append(dict(id=iid, char=c, partner=role == "partner", variant=vcache[(held, c)]))
                used.add(iid)
        if not cands:
            continue
        used.add(qid)
        items.append(dict(query_id=qid, held=held, query_provenance=prov.get(qid, ""), candidates=cands))

    n_png = 0
    for iid in sorted(used):
        r = con.execute("SELECT data FROM derived WHERE instance_id=? AND kind='norm'", (iid,)).fetchone()
        if r is None:
            raise SystemExit(f"{iid} 没有 derived.norm，库不完整")
        (out / "crops" / (iid.replace(":", "_") + ".png")).write_bytes(r[0])
        n_png += 1
    with open(out / "items.jsonl", "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    sha = hashlib.sha256(Path(a.db).read_bytes()).hexdigest()
    info = dict(
        schema_version=1, book=a.book, kind="advset",
        title="库外形近字对抗集：留出字（库里没有）的刻例 vs 形近对家＋生产粗排候选，量匹配层误认",
        source="ai-team domain/CV/字形领域/5a相似度CNN深化-2026-11-15/advset（11-15 建，原库 sha "
               + src_meta.get("db_sha256", "")[:16] + "）",
        crops_from=f"glyph.db sha256 {sha[:16]}（derived.norm）",
        n_items=len(items), n_held=len({i['held'] for i in items}), n_crops=n_png,
        n_variant_cands=sum(c["variant"] for i in items for c in i["candidates"]),
        dropped=drop, pairs={f"{h}|{p}": v for (h, p), v in layer_of.items()},
        held=sorted({i["held"] for i in items}),
    )
    (out / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in info.items() if k not in ("pairs", "held")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
