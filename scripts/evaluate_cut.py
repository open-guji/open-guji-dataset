"""评估 cut-page 的筒子页切分判定准确率。

对比 expected.json (ground truth) 与 results/ 下的 cut.json 输出。
只比 cut_type 一个字段——它决定后续是否把整页劈成两个半页，
判错的代价是整页版面全错，没有部分正确可言。
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CUT_PAGE_DIR = REPO / "cut-page"
SAMPLES_DIR = CUT_PAGE_DIR / "samples"
RESULTS_DIR = CUT_PAGE_DIR / "results"


def main() -> None:
    correct = total = 0
    errors = []
    for sd in sorted(SAMPLES_DIR.iterdir()):
        exp_p, res_p = sd / "expected.json", RESULTS_DIR / f"{sd.name}.json"
        if not exp_p.exists():
            continue
        if not res_p.exists():
            print(f"[{sd.name}] SKIP: no result")
            continue
        expected = json.loads(exp_p.read_text(encoding="utf-8")).get("cut_type")
        result = json.loads(res_p.read_text(encoding="utf-8")).get("cut_type")
        total += 1
        if expected == result:
            correct += 1
        else:
            info_p = sd / "info.json"
            desc = ""
            if info_p.exists():
                desc = json.loads(info_p.read_text(encoding="utf-8")).get("description", "")
            errors.append((sd.name, expected, result, desc))

    print("=" * 60)
    print("筒子页切分 Benchmark 评估报告")
    print("=" * 60)
    print(f"\n评估样本数: {total}")
    if total:
        print(f"cut_type 准确率: {correct}/{total} = {correct / total:.1%}")
    if errors:
        print("\n错误样本:")
        for name, exp, res, desc in errors:
            print(f"  [{name}] 期望={exp} 实际={res}  {desc}")

    report = {"evaluated": total,
              "accuracy": correct / total if total else 0.0,
              "correct": correct,
              "errors": [{"sample": n, "expected": e, "actual": r}
                         for n, e, r, _ in errors]}
    out = CUT_PAGE_DIR / "report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"\n报告已保存: {out}")


if __name__ == "__main__":
    main()
