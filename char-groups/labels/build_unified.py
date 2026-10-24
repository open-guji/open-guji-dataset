"""把 char-groups 里散在各处的形近字／异体字人裁，归并成一份统一格式 `labels/unified.jsonl`。

用法（幂等，可反复跑）：
    python char-groups/labels/build_unified.py [--events <feedback/events 目录>] [--cv <open-guji-cv 仓>]

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
MEMBER_GROUPS: dict[str, list[str]] = collections.defaultdict(list)


def _load_groups():
    MEMBER_GROUPS.clear()
    for gid, g in json.loads((HERE / "group_members.json").read_text(encoding="utf-8")).items():
        for ch in g["members"]:
            MEMBER_GROUPS[ch].append(gid)


_load_groups()

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
    """中心库 confirm 事件（actor=user）：payload.shape＝人裁刻形，reading＝释读。只要落在已登记字组里的。
    同一格的每条事件都出一行（不只留最新的），合并时据此算复核与更正（2026-10-24）。"""
    if not events_dir or not Path(events_dir).is_dir():
        return
    for f in sorted(glob.glob(str(Path(events_dir) / "*.jsonl"))):
        for e in jl(f):
            if e.get("kind") != "confirm" or e.get("actor") != "user":
                continue
            p = e.get("payload") or {}
            sh = p.get("shape")
            nk = norm_id((e.get("target") or {}).get("key"))
            if not sh or not nk or not groups_of(sh):
                continue
            r = row(nk, "shape", sh, by=e.get("reviewer") or "user", date=date_of(e.get("ts")), src=f"central:{e.get('batch')}",
                    file=f"central-events/{Path(f).name}", event=e.get("id"),
                    extra={"reading": p.get("reading")} if p.get("reading") else None)
            if r:
                r["_ts"] = str(e.get("ts") or "")
                yield r


def merge(rows: list[dict]) -> list[dict]:
    """同格同类的多条来源合成一行（2026-10-24 起）：
    - 结论取**日期最晚**的一条（同日：中心库事件优先于本仓文件，事件之间取 ts 晚的）；更正写进中心库就会生效；
    - `also`：其余来源；`verified`：独立来源数 `n` 与结论是否一致 `agree`；
    - `corrected_from`：与最终结论不同的早先结论（`[{form, src, date}]`），即被更正过；`in_central`：有中心库来源；
    - `central_form`：中心库最新一条与最终结论不同（流水线读的是它，本仓的更正还没写进中心库）。"""
    by: dict = collections.defaultdict(list)
    for r in rows:
        by[(r["id"], r["kind"])].append(r)
    out = []
    for (_, _), rs in by.items():
        key = lambda r: (r["date"] or "", r["file"].startswith("central-events/"), r.get("_ts", ""))  # noqa: E731
        rs = sorted(rs, key=key)
        best = dict(rs[-1])
        best.pop("_ts", None)
        others = rs[:-1]
        srcs = []
        for r in others:
            if r["src"] not in srcs and r["src"] != best["src"]:
                srcs.append(r["src"])
        if srcs:
            best["also"] = srcs
        forms = {r["form"] for r in rs}
        best["verified"] = {"n": len({r["src"] for r in rs}), "agree": len(forms) == 1}
        corr = []
        for r in others:
            if r["form"] != best["form"] and not any(c["form"] == r["form"] and c["src"] == r["src"] for c in corr):
                corr.append({"form": r["form"], "src": r["src"], "date": r["date"]})
        if corr:
            best["corrected_from"] = corr
        cen = [r for r in rs if r["file"].startswith("central-events/")]
        best["in_central"] = bool(cen)
        if cen and cen[-1]["form"] != best["form"]:
            best["central_form"] = cen[-1]["form"]     # 流水线读到的是这个：本仓更新的结论还没写进中心库
        out.append(best)
    return out


def export_members(cv: Path) -> None:
    """从 CV 仓注册表导出 `group_members.json`（字组变了就重跑；不手改）。"""
    import subprocess
    code = ("import json; from open_guji_cv.groups import registry as R; "
            "print(json.dumps({g: {'name': s.name, 'kind': s.kind, 'members': ''.join(sorted(s.members))} "
            "for g, s in R.FLOW_GROUPS.items()}, ensure_ascii=False, indent=1))")
    txt = subprocess.run(["python3", "-c", code], cwd=cv, capture_output=True, text=True, check=True).stdout
    (HERE / "group_members.json").write_text(txt, encoding="utf-8")
    print("导出 group_members.json：", len(json.loads(txt)), "组")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", default=os.path.expanduser("~/.guji-data/main/siku-zongmu/feedback/events"))
    ap.add_argument("--cv", default="", help="CV 仓路径：先从注册表重新导出 group_members.json")
    a = ap.parse_args()
    if a.cv:
        export_members(Path(a.cv))
        _load_groups()
    rows = []
    for gen in (parse_review_verdicts, parse_long_tail, parse_variant_labels, parse_pair_review, parse_yi):
        rows += [r for r in gen() if r]
    local_n = len(rows)
    central = [r for r in parse_central(a.events) if r]
    out = sorted(merge(rows + central), key=lambda r: (r["book"], r["page"], r["col"], r["slot"], r["kind"]))
    (HERE / "unified.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), encoding="utf-8")
    by_group = collections.Counter(g for r in out if r["kind"] == "shape" or r["kind"] == "reading" for g in (r["groups"] or ["(无组)"]))
    by_kind = collections.Counter(r["kind"] for r in out)
    only_central = sum(1 for r in out if r["file"].startswith("central-events/"))
    multi = sum(1 for r in out if r["verified"]["n"] > 1)
    disagree = sum(1 for r in out if not r["verified"]["agree"])
    print(f"本仓文件 {local_n} 行；中心库事件 {len(central)} 条；合并后 {len(out)} 行（结论来自中心库的 {only_central}，"
          f"有中心库来源的 {sum(r['in_central'] for r in out)}）")
    print(f"多来源 {multi} 行，其中来源之间不一致（有更正）{disagree} 行；结论与中心库不同（更正没进中心库）"
          f"{sum(1 for r in out if r.get('central_form'))} 行")
    print("按类型：", dict(by_kind))
    print("按组（shape+reading）：", dict(by_group.most_common()))


if __name__ == "__main__":
    main()
