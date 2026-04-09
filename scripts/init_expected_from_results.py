"""将 recognize-profile 结果复制为 expected.json 初始值（仅对尚无 expected.json 的样本）。"""
import json
from pathlib import Path

BENCHMARK_DIR = Path("D:/workspace/open-guji-dataset/benchmark/book-profile")
SAMPLES_DIR = BENCHMARK_DIR / "samples"
RESULTS_DIR = BENCHMARK_DIR / "results"

# 从 result 中移除的字段（非评估字段）
REMOVE_FIELDS = ["auto_detected", "detection_confidence", "skip_pages", "skip_steps"]


def main():
    count = 0
    for sample_dir in sorted(SAMPLES_DIR.iterdir()):
        if not sample_dir.is_dir():
            continue

        sample_id = sample_dir.name
        expected_path = sample_dir / "expected.json"
        result_path = RESULTS_DIR / f"{sample_id}.json"

        if expected_path.exists():
            continue  # 已有 ground truth，跳过

        if not result_path.exists():
            continue

        profile = json.loads(result_path.read_text(encoding="utf-8"))
        for field in REMOVE_FIELDS:
            profile.pop(field, None)

        expected_path.write_text(
            json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        count += 1
        print(f"[{sample_id}] created expected.json")

    print(f"\nDone: {count} expected.json files created")


if __name__ == "__main__":
    main()
