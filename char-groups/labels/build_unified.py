"""把 char-groups 里散在各处的形近字／异体字人裁，归并成一份统一格式 `labels/unified.jsonl`。

用法（幂等，可反复跑）：
    python char-groups/labels/build_unified.py [--events <feedback/events 目录>]

--events 缺省读 ~/.guji-data/main/siku-zongmu/feedback/events（`guji db pull` 拉下来的中心库人裁事件）。
给了才并入中心库的 confirm 事件；没给或目录不存在就只并本仓文件。

一行＝一格（id）× 一种标注（kind）。字段见 labels/README.md。
本脚本只读，不改任何源文件；源文件格式各异，规则写死在下面的 `parse_*` 里。
"""
from __future__ import annotations

import argparse
import collections
import datetime
import glob
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CG = HERE.parent
GROUPS = json.loads((HERE / "group_members.json").read_text(encoding="utf-8"))
MEMBER_GROUPS: dict[str, list[str]] = collections.defaultdict(list)
for gid, g in GROUPS.items():
    for ch in g["members"]:
        MEMBER_GROUPS[ch].append(gid)

ID_RE = re.compile(r"^(?:v2:)?(vol\d+):(\d+):(\d+):(-?\d+[ab]?)$")


def norm_id(i):
    if not i:
        return None
    m = ID_RE.match(i.strip())
    if not m:
        return None
    return f"{m.group(1)}:{m.group(2)}:{m.group(3)}:{m.group(4)}"


def date_of(*cands):
    for c in cands:
        if c is None:
            continue
        if isinstance(c, (int, float)) and c > 1e11:
            return datetime.datetime.fromtimestamp(c / 1000, datetime.timezone.utc).strftime("%Y-%m-%d")
        if isinstance(c, str) and re.match(r"\d{4}-\d{2}-\d{2}", c):
            return c[:10]
    return None


def groups_of(*chars):
    out = []
    for c in chars:
        for g in MEMBER_GROUPS.get(c, []):
            if g not in out:
                out.append(g)
    return out


def row(id_, kind, form, *, status="ok", groups=None, by=None, date=None, src=None, file=None, event=None, note=None,
        extra=None):
    nid = norm_id(id_)
    if nid is None:
        return None
    book, page, col, slot = nid.split(":")
    r = {"id": nid, "book": book, "page": int(page), "col": int(col), "slot": slot, "kind": kind, "form": form,
         "status": status, "groups": groups if groups is not None else groups_of(form),
         "by": by, "date": date, "src": src, "file": file}
    if event:
        r["event"] = event
    if note:
        r["note"] = note
    if extra:
        r.update(extra)
    return r


def jl(path):
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                yield json.loads(line)
            except ValueError:
                pass


def rel(p):
    return str(Path(p).relative_to(CG))


# ---- 各来源 ----
def parse_review_verdicts():
    """review/*verdicts.jsonl：verdict 是人点的字，idk／other 等表示没定。按文意定字（kind=reading）。"""
    for f in sorted(glob.glob(str(CG / "review" / "*verdicts.jsonl"))):
        grp_hint = {"jys": ["jys"], "jys2": ["jys"], "rr": ["rr"], "rr17": ["rr"], "ry": ["ry"], "ry_flag": ["ry"]}
        stem = Path(f).name.replace("_verdicts.jsonl", "")
        for r in jl(f):
            v = r.get("verdict")
            ok = isinstance(v, str) and len(v) == 1
            g = [r["group"]] if r.get("group") else (groups_of(v) if ok else grp_hint.get(stem, []))
            yield row(r.get("id"), "reading", v if ok else None, status="ok" if ok else (v or "unknown"),
                      groups=g, by=r.get("by", "sheldon"), date=date_of(r.get("date"), r.get("t")),
                      src=f"review:{stem}", file=rel(f), note=r.get("card_note") or r.get("note"))


def parse_long_tail():
    f = CG / "review" / "long-tail-1021" / "labels.jsonl"
    if f.exists():
        for r in jl(f):
            yield row(r.get("id"), "shape", r.get("pick"), by="sheldon", date="2026-10-21", src="review:long-tail-1021",
                      file=rel(f), extra={"lib": r.get("lib"), "ref": r.get("ref")})
    f = CG / "variant" / "same_variant_1021" / "labels.jsonl"
    if f.exists():
        for r in jl(f):
            yield row(r.get("cell"), "shape", r.get("char"), by="sheldon", date="2026-10-21", src="variant:same_variant_1021",
                      file=rel(f), note=r.get("kind"), extra={"lib": r.get("lib"), "ref": r.get("ref"), "choice": r.get("choice")})


def parse_variant_labels():
    """variant/<组>/labels.jsonl：form＝人裁刻形；有 cut 的另出一行 kind=cut。"""
    for f in sorted(glob.glob(str(CG / "variant" / "*" / "labels.jsonl"))):
        grp = Path(f).parent.name
        if grp == "same_variant_1021":
            continue
        for r in jl(f):
            by = r.get("by") or ("sheldon" if r.get("label_status") == "human" else None)
            yield row(r.get("id"), "shape", r.get("form"), status="ok" if r.get("form") else "other", by=by, date=r.get("date"),
                      src=f"variant:{grp}", file=rel(f), note=r.get("fixed") or r.get("src") or r.get("note"),
                      extra={"ref": r.get("ref")} if r.get("ref") else None)
            if r.get("cut"):
                yield row(r.get("id"), "cut", r.get("form"), by=by, date=r.get("date"), src=f"variant:{grp}", file=rel(f),
                          extra={"cut": {"line": r["cut"], "orient": r.get("orient"), "which": r.get("which")}})


def parse_pair_review():
    d = CG / "variant" / "pair_review"
    for f in sorted(glob.glob(str(d / "labels_*.jsonl"))):
        for r in jl(f):
            form = r.get("form")
            yield row(r.get("id"), "shape", form, status="ok" if form else (r.get("choice") or "unknown"),
                      groups=groups_of(*(r.get("opts") or [form or ""])), by=r.get("by", "sheldon"),
                      date=date_of(r.get("date"), r.get("t")), src=f"pair_review:{Path(f).stem}", file=rel(f),
                      note=r.get("card_note"))
    for f in sorted(glob.glob(str(d / "events_*.jsonl"))):
        for r in jl(f):
            yield row(r.get("id"), "shape", r.get("form"), by="sheldon", date=date_of(r.get("ts")),
                      src=f"pair_review:{Path(f).stem}", file=rel(f), event=r.get("event"), note=r.get("note"))


def parse_yi():
    d = CG / "variant" / "yi_560"
    f = d / "cut_labels.jsonl"
    if f.exists():
        for r in jl(f):
            yield row(r.get("id"), "cut", None, groups=["yi_560"], by=r.get("by"), date=date_of(r.get("hcuts_t")),
                      src="variant:yi_560", file=rel(f), extra={"cut": {"hcuts": r.get("hcuts"), "vcuts": r.get("vcuts")}})
    f = d / "user_parts_labels.jsonl"
    if f.exists():
        for r in jl(f):
            yield row(r.get("id"), "parts", r.get("target"), groups=["yi_560"], by=r.get("by"), date=None,
                      src="variant:yi_560", file=rel(f), note=r.get("note"),
                      extra={"parts": {k: r.get(k) for k in ("top", "mid", "bot")}})


def parse_central(events_dir):
    """中心库 confirm 事件（actor=user）：payload.shape＝人裁刻形，reading＝释读。只要落在已登记字组里的。"""
    if not events_dir or not Path(events_dir).is_dir():
        return
    latest = {}
    for f in sorted(glob.glob(str(Path(events_dir) / "*.jsonl"))):
        for e in jl(f):
            if e.get("kind") != "confirm" or e.get("actor") != "user":
                continue
            p = e.get("payload") or {}
            sh = p.get("shape")
            k = (e.get("target") or {}).get("key")
            if not sh or not norm_id(k) or not groups_of(sh):
                continue
            nk = norm_id(k)
            if nk not in latest or str(e.get("ts")) >= str(latest[nk][0].get("ts")):
                latest[nk] = (e, Path(f).name)
    for nk, (e, fn) in latest.items():
        p = e["payload"]
        yield row(nk, "shape", p["shape"], by="user", date=date_of(e.get("ts")), src=f"central:{e.get('batch')}",
                  file=f"central-events/{fn}", event=e.get("id"),
                  extra={"reading": p.get("reading")} if p.get("reading") else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", default=os.path.expanduser("~/.guji-data/main/siku-zongmu/feedback/events"))
    a = ap.parse_args()
    rows = []
    for gen in (parse_review_verdicts, parse_long_tail, parse_variant_labels, parse_pair_review, parse_yi):
        rows += [r for r in gen() if r]
    local_n = len(rows)
    central = [r for r in parse_central(a.events) if r]
    # 同格同类：本仓文件优先于中心库事件的"补录"，日期晚者胜；中心库独有的格补进来
    best = {}
    for r in rows + central:
        k = (r["id"], r["kind"])
        old = best.get(k)
        if old is None:
            best[k] = r
        else:
            old.setdefault("also", []).append(r["src"])
            if (r["date"] or "") > (old["date"] or "") and old["file"].startswith("central-events/") is False and r["file"].startswith("central-events/") is False:
                r["also"] = old.get("also", []) + [old["src"]]
                best[k] = r
    out = sorted(best.values(), key=lambda r: (r["book"], r["page"], r["col"], r["slot"], r["kind"]))
    (HERE / "unified.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), encoding="utf-8")
    by_group = collections.Counter(g for r in out if r["kind"] == "shape" or r["kind"] == "reading" for g in (r["groups"] or ["(无组)"]))
    by_kind = collections.Counter(r["kind"] for r in out)
    src_central = sum(1 for r in out if r["file"].startswith("central-events/"))
    print(f"本仓文件 {local_n} 行；中心库补录 {len(central)} 行；合并后 {len(out)} 行（其中只在中心库的 {src_central}）")
    print("按类型：", dict(by_kind))
    print("按组（shape+reading）：", dict(by_group.most_common()))


if __name__ == "__main__":
    main()
