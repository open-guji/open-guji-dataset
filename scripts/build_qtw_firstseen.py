"""全唐文首次字头格（3b 子基准 B2）冻结成 rare.jsonl 分片（A23，2026-11-23）。

来源：ai-team `domain/CV/字形领域/首次字头格-2026-11-18/数据/低把握卡-Sheldon结果.tsv`——016–045 册层 2、
库例 0–2 的首次字头格，Sheldon 一格一卡按刻形选字（`pick:<字>`；切分问题的格不收）。
字块按格号到全唐文字形库里取（Sheldon 选完已进库为人裁刻例），归一口径同 cv `scripts/build_book_human_shards.py`
（`normalize_patch(gray)*255`），行格式同 006 的 `rare.jsonl`，`eval_oov.py --items rare.jsonl` 直接能评。

strata：`firstseen` 全部；另按 cv CNN 类表加 `oov`，码位在扩 B 及以后的加 `extB+`。

    python scripts/build_qtw_firstseen.py <Sheldon结果.tsv> <全唐文 glyph.db> <输出目录>
"""
import csv
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

CV = Path(__file__).resolve().parents[2] / "open-guji-cv"
sys.path[:0] = [str(CV), str(CV / "scripts")]


def main():
    import cv2
    import numpy as np
    from open_guji_cv.clustering.normalize import normalize_patch
    from build_book_human_shards import cnn_classes
    tsv, db, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    classes = cnn_classes()
    con = sqlite3.connect(str(db))
    (out / "crops").mkdir(parents=True, exist_ok=True)
    rare, skipped = [], []
    for r in csv.DictReader(open(tsv, encoding="utf-8"), delimiter="\t"):
        if not r["Sheldon"].startswith("pick:"):
            skipped.append(dict(cell=r["cell"], why=r["Sheldon"]))
            continue
        ch = r["Sheldon"][5:]
        iid = "v2:" + r["cell"]
        x = con.execute("SELECT patch_png FROM instances WHERE instance_id=?", (iid,)).fetchone()
        if x is None:
            skipped.append(dict(cell=r["cell"], why="库里没有这格"))
            continue
        gray = cv2.imdecode(np.frombuffer(x[0], np.uint8), cv2.IMREAD_GRAYSCALE)
        name = iid.replace(":", "_") + ".png"
        cv2.imwrite(str(out / "crops" / name), (normalize_patch(gray) * 255).astype(np.uint8))
        strata = ["firstseen"] + (["oov"] if ch not in classes else []) + (["extB+"] if ord(ch) >= 0x20000 else [])
        rare.append(dict(char=ch, png=f"crops/{name}", src="human", book="995ejelvk0", id=iid, strata=strata,
                         tier="clean", card=dict(ref=r["参校本"], lib_top=r["库首位"], top3_5b=r["5b前三"])))
    with open(out / "rare.jsonl", "w", encoding="utf-8") as f:
        for x in rare:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    info = dict(id=out.name, book="995ejelvk0", created="2026-11-23",
                description="全唐文 016–045 首次字头格（库例 0–2），Sheldon 按刻形逐格选字；3b 子基准 B2",
                source="ai-team domain/CV/字形领域/首次字头格-2026-11-18（11-18 人审卡）",
                bias="是人审流程挑出的低把握卡，比全书首见字难；81 格只有约 60 个不同的字（倐 8、玘 5），按字去重另看",
                glyph_db_sha256=hashlib.sha256(db.read_bytes()).hexdigest(),
                n=len(rare), n_chars=len({x['char'] for x in rare}),
                strata={s: sum(s in x["strata"] for x in rare) for s in ("firstseen", "oov", "extB+")},
                skipped=skipped, build_command="python scripts/build_qtw_firstseen.py …")
    (out / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in info.items() if k != "skipped"}, ensure_ascii=False), len(skipped))


if __name__ == "__main__":
    main()
