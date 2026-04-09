"""评估 recognize-profile 的识别准确率。

对比 expected.json (ground truth) 和 results/ 下的输出，
逐字段计算准确率。
"""
import json
from pathlib import Path

BENCHMARK_DIR = Path("D:/workspace/open-guji-dataset/benchmark/book-profile")
SAMPLES_DIR = BENCHMARK_DIR / "samples"
RESULTS_DIR = BENCHMARK_DIR / "results"

# 需要评估的字段
EVAL_FIELDS = [
    "layout",
    "banxin_position",
    "content_format",
    "lines_per_page",
    "chars_per_line",
    "has_marginal_notes",
    "color_mode",
    "background_color",
    "text_color",
    "border_color",
    "border_style",
    "border_wear",
    "interferences",
    "margin_color",
]


def should_eval_field(expected, field: str) -> bool:
    """判断是否需要评估该字段（条件字段）。"""
    if field == "banxin_position":
        return expected.get("layout") == "cut_half"
    if field == "margin_color":
        return "margin" in (expected.get("interferences") or [])
    return True


def compare_field(expected, result, field: str) -> bool:
    """比较单个字段是否匹配。"""
    ev = expected.get(field)
    rv = result.get(field)

    if field == "interferences":
        # 列表比较：排序后比较
        return sorted(ev or []) == sorted(rv or [])

    return ev == rv


def main():
    sample_dirs = sorted(SAMPLES_DIR.iterdir())

    # 统计
    field_correct = {f: 0 for f in EVAL_FIELDS}
    field_total = {f: 0 for f in EVAL_FIELDS}
    errors = []

    evaluated = 0

    for sample_dir in sample_dirs:
        if not sample_dir.is_dir():
            continue

        sample_id = sample_dir.name
        expected_path = sample_dir / "expected.json"
        result_path = RESULTS_DIR / f"{sample_id}.json"

        if not expected_path.exists():
            continue
        if not result_path.exists():
            print(f"[{sample_id}] SKIP: no result")
            continue

        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        result = json.loads(result_path.read_text(encoding="utf-8"))

        evaluated += 1
        sample_errors = []

        for field in EVAL_FIELDS:
            if field not in expected:
                continue
            if not should_eval_field(expected, field):
                continue

            field_total[field] += 1
            if compare_field(expected, result, field):
                field_correct[field] += 1
            else:
                sample_errors.append({
                    "field": field,
                    "expected": expected.get(field),
                    "got": result.get(field),
                })

        if sample_errors:
            info_path = sample_dir / "info.json"
            desc = ""
            if info_path.exists():
                info = json.loads(info_path.read_text(encoding="utf-8"))
                desc = info.get("description", "")
            errors.append({
                "id": sample_id,
                "description": desc,
                "errors": sample_errors,
            })

    # 输出报告
    print("=" * 60)
    print("古籍版面识别 Benchmark 评估报告")
    print("=" * 60)
    print(f"\n评估样本数: {evaluated}")
    print()

    print("字段准确率:")
    print("-" * 45)
    total_correct = 0
    total_count = 0
    for field in EVAL_FIELDS:
        t = field_total[field]
        if t == 0:
            continue
        c = field_correct[field]
        pct = c / t * 100
        total_correct += c
        total_count += t
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"  {field:<22s} {bar} {c:>3d}/{t:<3d} ({pct:5.1f}%)")

    if total_count > 0:
        overall = total_correct / total_count * 100
        print("-" * 45)
        print(f"  {'总体':<22s}                      {total_correct:>3d}/{total_count:<3d} ({overall:5.1f}%)")

    if errors:
        print(f"\n错误详情 ({len(errors)} 个样本有误):")
        print("-" * 45)
        for err in errors:
            print(f"\n  [{err['id']}] {err['description'][:50]}")
            for e in err["errors"]:
                print(f"    {e['field']}: 期望={e['expected']} 实际={e['got']}")

    # 保存报告 JSON
    report = {
        "evaluated": evaluated,
        "field_accuracy": {
            f: {"correct": field_correct[f], "total": field_total[f],
                "accuracy": field_correct[f] / field_total[f] if field_total[f] > 0 else None}
            for f in EVAL_FIELDS if field_total[f] > 0
        },
        "overall_accuracy": total_correct / total_count if total_count > 0 else None,
        "errors": errors,
    }
    report_path = BENCHMARK_DIR / "report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n报告已保存: {report_path}")


if __name__ == "__main__":
    main()
