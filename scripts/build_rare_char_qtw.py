"""全唐文（995ejelvk0）疑难字标注集：rare-char/qtw-995ejelvk0/。

来源：r9b 难认异体小审页两版（Sheldon 11-05 人裁 H-hv-1105 / H-hv-1105b），候选冻结为出页时的样子：
  page_v1：页上第一版候选（页上建议/整理本/参校/字形线/形近字线/Paddle/字体/本书库，≤10）
  a23：A23 多路候选 top12（异体表/部件检索/字统网族/形近表/IDS/5b-CNN/字体渲染/人裁字形 kNN）
  page_v2：第二版页上候选（前两路合并，多路同中排前）
另收认不出（unresolved）、切分有问题（seg）、不是字（notchar）三层。

重建：python scripts/build_rare_char_qtw.py --src <hard-variants-r9b 目录> --events <事件目录>
"""
import argparse, glob, json, os, re, shutil, unicodedata
from pathlib import Path

BLOCKS = [(0x4E00, 0x9FFF, "基本"), (0x3400, 0x4DBF, "扩A"), (0x20000, 0x2A6DF, "扩B"), (0x2A700, 0x2B73F, "扩C"),
          (0x2B740, 0x2B81F, "扩D"), (0x2B820, 0x2CEAF, "扩E"), (0x2CEB0, 0x2EBEF, "扩F"), (0x30000, 0x3134F, "扩G"),
          (0x31350, 0x323AF, "扩H"), (0x2EBF0, 0x2EE5F, "扩I"), (0xF900, 0xFAFF, "兼容"), (0x2F800, 0x2FA1F, "兼容补充")]


def block(ch):
    if not ch or len(ch) != 1:
        return "其他"
    o = ord(ch)
    return next((n for a, b, n in BLOCKS if a <= o <= b), "其他")


def rank(cands, ch):
    for i, c in enumerate(cands or []):
        if c[0] == ch:
            return i + 1
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="/mnt/project-files/qtw-tools/hard-variants-r9b")
    ap.add_argument("--events", default=os.path.expanduser("~/.guji-data/main/995ejelvk0/feedback/events"))
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "rare-char" / "qtw-995ejelvk0"))
    a = ap.parse_args()
    src, out = Path(a.src), Path(a.out)
    (out / "patches").mkdir(parents=True, exist_ok=True)
    v1 = {json.loads(l)["id"]: json.loads(l) for l in open(src / "小审页/items.jsonl", encoding="utf-8")}
    v2 = {json.loads(l)["id"]: json.loads(l) for l in open(src / "小审页v2/items.jsonl", encoding="utf-8")}
    a23 = {d["id"]: d for d in json.load(open(src / "A23候选/候选.json", encoding="utf-8"))["items"]}
    ev = {}
    for b in ("H-hv-1105", "H-hv-1105b"):
        for l in open(Path(a.events) / f"{b}.jsonl", encoding="utf-8"):
            e = json.loads(l)
            ev[e["target"]["key"]] = e
    extra = {  # 人没给字的格（Sheldon 11-05 thread 里说的），按 status 收
        "015:6:1:4": dict(status="unresolved", parts="人火又", note="Sheldon：人＋火＋又，查不到字，搁置；文意为「倓」（齊王倓）。A23 看作 亻厶夂＝俊（Paddle 首位也是），待 Sheldon 定"),
        "007:77:9:15": dict(status="unresolved", parts="王旦", note="左王右旦，无码位；A23 建议记 珇（approx）或按整理本 殂 讹写，待 Sheldon 定"),
        "010:182:8:21": dict(status="unresolved", parts="", note="裁图只有栏线碎片，等切分线重切后再判"),
        "010:162:9:12": dict(status="seg", note="Sheldon：切分有问题"),
        "012:186:9:11a": dict(status="seg", note="Sheldon：切分有问题"),
        "010:10:9:5": dict(status="seg", note="Sheldon：切分有问题"),
        "012:99:1:9": dict(status="notchar", note="Sheldon：不是字（卷题列里的淡污）"),
    }
    rows = []
    for i in sorted(set(ev) | set(extra)):
        it1, it2, ia = v1.get(i, {}), v2.get(i, {}), a23.get(i, {})
        img = it2.get("img") or it1.get("img")
        patch = None
        if img and os.path.exists(img):
            patch = f"patches/{i.replace(':', '_')}.png"
            shutil.copy(img, out / patch)
        ctx = it2.get("ctx") or it1.get("ctx") or ia.get("ctx", "")
        m = re.search("【(.)】", ctx)
        pre = it1.get("pre") or it2.get("pre") or ia.get("sug")
        cands = {k: v for k, v in (("page_v1", it1.get("cands")), ("a23", ia.get("cands")), ("page_v2", it2.get("cands"))) if v}
        e = ev.get(i)
        t = (e or {}).get("target", {})
        anc = t.get("anchor") or {}
        r = {"id": i, "anchor": {"book": i.split(":")[0], "page": int(i.split(":")[1]), "col": int(i.split(":")[2]),
                                 "slot": i.split(":")[3], "space": anc.get("space"), "bbox": anc.get("bbox"),
                                 "content_sha": anc.get("content_sha")},
             "input": {"patch": patch, "ctx": ctx, "ref": m.group(1) if m else None, "pre": pre,
                       "class_glyph_line": ia.get("分类"), "candidates": cands},
             "label_origin": "human", "status": "active"}
        if e:
            ch = e["payload"]["shape"]
            rk = {k: rank(v, ch) for k, v in cands.items()}
            r["expected"] = {"status": "char", "char": ch, "unicode_cp": f"U+{ord(ch):04X}" if len(ch) == 1 else None,
                             "block": block(ch), "same_as_pre": ch == pre, "same_as_ref": ch == r["input"]["ref"],
                             "rank": rk, "in_candidates": any(rk.values())}
            r["source_events"] = [e["id"]]
            r["stratum"] = "页上字对" if ch == pre else ("改字·候选有" if any(rk.values()) else "改字·候选无")
        else:
            x = extra[i]
            r["expected"] = {"status": x["status"], "char": None, **({"parts": x["parts"]} if x.get("parts") is not None else {})}
            r["note"] = x["note"]
            r["stratum"] = {"unresolved": "认不出", "seg": "切分或非字", "notchar": "切分或非字"}[x["status"]]
        rows.append(r)
    (out / "items.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    from collections import Counter
    st = Counter(r["stratum"] for r in rows)
    bl = Counter(r["expected"].get("block") for r in rows if r["expected"].get("char") and not r["expected"]["same_as_pre"])
    def hit(src_, n):
        xs = [r for r in rows if r["stratum"].startswith("改字") and src_ in r["input"]["candidates"]]
        return sum(1 for r in xs if (r["expected"]["rank"].get(src_) or 99) <= n), len(xs)
    meta = {"name": "rare-char/qtw-995ejelvk0", "version": "0.1.0", "schema_version": 1, "created": "2026-11-05",
            "description": "全唐文（995ejelvk0）r9b 难认异体格：Sheldon 人裁定字、认不出、切分/非字；候选按出页时冻结",
            "total_samples": len(rows), "sample_unit": "字位", "strata": dict(st), "changed_char_blocks": dict(bl),
            "metric": "改字层 top-12 召回（按候选来源分报）；切分或非字层：管线能否先判出不该找字",
            "baseline": {f"{s}_top{n}": "%d/%d" % hit(s, n) for s in ("page_v1", "a23", "page_v2") for n in (1, 3, 12)},
            "notes": ["参考答案全是 Sheldon 人点（H-hv-1105、H-hv-1105b），不用整理本当金标。",
                      "候选冻结：比较新算法时读 input.candidates，别用实时候选。",
                      "认不出层记 parts（人看得出的部件），用来测部件/IDS 检索；定字后挪到 char 层、版本加一。",
                      "patch 按 r11 cell_shrink 字框裁；anchor.bbox/content_sha 取自人裁事件锚，切分重跑后用它找回原格。"],
            "build_command": "python scripts/build_rare_char_qtw.py"}
    (out / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
