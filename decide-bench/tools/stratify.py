"""按判别规则分层（A24，2026-11-23）：金标候选（select_gold.py 的输出）× 关掉人裁重跑的 seed_admit → 每格是哪条规则放行或拦住、算法对不对。

用法：python decide-bench/tools/stratify.py <gold.jsonl> <关人裁重跑的产物根/册> --out strat.jsonl [--per-rule 30] [--seed 0]

规则名：放行格＝`admit:<channel>`；拦住的格＝`review:<降级来源或第一个疑问码>`（evidence.demoted_from.by 优先）。
等价：码位同字算对；己已巳、日曰组内任一字算对（Sheldon 定）。
挑样：每条规则里要看的（放错字、放成异体、拦住但首选其实对＝可救回）全收；算法对的按种子随机收 per-rule 个。
"""
import collections, glob, json, random, sys
from pathlib import Path

gold_f, run = sys.argv[1], Path(sys.argv[2])
arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
per_rule, seed = int(arg("--per-rule", 30)), arg("--seed", "0")
FOLD = [set("己已巳"), set("日曰")]


def same(a, b):
    return a == b or any(a in g and b in g for g in FOLD)


try:
    from open_guji_cv.variants import are_variants
except Exception:  # noqa: BLE001
    are_variants = lambda a, b: False


def outcome(x, gold):
    """放对／放错字／放成异体（异体选形不同）／拦住·首选对／拦住·首选错。"""
    a = x.get("char")
    if x.get("admit"):
        if same(a, gold):
            return "放对"
        return "放成异体" if a and are_variants(a, gold) else "放错字"
    return "拦住·首选对" if a and same(a, gold) else "拦住·首选错"


cells = {}
for f in glob.glob(str(run / "seed_admit" / "p*.json")):
    for col in json.load(open(f))["seed_admit"]["columns"]:
        for x in col.get("chars") or []:
            cells[x["id"]] = x


def rule_of(x):
    if x.get("admit"):
        return f"admit:{x.get('channel')}"
    ev = x.get("evidence") or {}
    by = (ev.get("demoted_from") or {}).get("by")
    if by:
        return f"review:{by}"
    d = (x.get("doubts") or ["?"])[0]
    return "review:" + str(d).split("(")[0].split(":")[0][:24]


by_rule = collections.defaultdict(list)
for ln in open(gold_f):
    g = json.loads(ln)
    if g["cls"] not in ("dataset", "agree_ref", "override_ref") or not g.get("char"):
        continue
    x = cells.get(g["id"])
    if not x:
        continue
    r = rule_of(x)
    oc = outcome(x, g["char"])
    ok = oc in ("放对", "拦住·首选错")
    g.update(rule=r, algo=x.get("char"), algo_ok=ok, outcome=oc, admit=bool(x.get("admit")), doubts=x.get("doubts"))
    by_rule[r].append(g)
rng = random.Random(seed)
out, table = [], []
for r, L in sorted(by_rule.items(), key=lambda kv: -len(kv[1])):
    bad = [g for g in L if not g["algo_ok"]]
    good = [g for g in L if g["algo_ok"]]
    pick = bad + rng.sample(good, min(per_rule, len(good)))
    out += pick
    oc = collections.Counter(g["outcome"] for g in L)
    table.append((r, len(L), len(bad), len(pick), " ".join(f"{k}{v}" for k, v in oc.most_common())))
if arg("--out"):
    Path(arg("--out")).write_text("".join(json.dumps(o, ensure_ascii=False) + "\n" for o in out))
print("规则\t金标格\t要看的\t入选\t结果")
for t in table:
    print("\t".join(map(str, t)))
print(f"合计入选 {len(out)}")
