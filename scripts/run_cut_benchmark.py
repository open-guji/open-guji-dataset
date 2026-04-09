"""对 cut-page 数据集运行 cut 检测，生成结果。"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CUT_PAGE_DIR = Path("D:/workspace/open-guji-dataset/cut-page")
SAMPLES_DIR = CUT_PAGE_DIR / "samples"
RESULTS_DIR = CUT_PAGE_DIR / "results"
GUJI_CV = "D:/workspace/open-guji-cv"


def run_cut_detect(image_path: Path) -> dict | None:
    """对单张图片运行 cut 检测，返回 cut.json 内容。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        shutil.copy2(image_path, Path(tmpdir) / image_path.name)

        result = subprocess.run(
            [sys.executable, "-m", "open_guji_cv", "cut", tmpdir],
            capture_output=True,
            text=True,
            cwd=GUJI_CV,
            encoding="utf-8",
        )

        if result.returncode != 0:
            print(f"  ERROR: {result.stderr.strip()}")
            return None

        cut_path = Path(tmpdir) / "cut.json"
        if cut_path.exists():
            return json.loads(cut_path.read_text(encoding="utf-8"))
        return None


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    sample_dirs = sorted(SAMPLES_DIR.iterdir())
    total = 0
    success = 0
    correct = 0

    for sample_dir in sample_dirs:
        if not sample_dir.is_dir():
            continue

        sample_id = sample_dir.name
        images = list(sample_dir.glob("image.*"))
        if not images:
            continue

        total += 1
        info_path = sample_dir / "info.json"
        desc = ""
        if info_path.exists():
            info = json.loads(info_path.read_text(encoding="utf-8"))
            desc = info.get("description", "")

        print(f"[{sample_id}] {desc[:40]}...", end="")
        result = run_cut_detect(images[0])

        if result:
            result_path = RESULTS_DIR / f"{sample_id}.json"
            result_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            success += 1

            # 对比 expected
            exp_path = sample_dir / "expected.json"
            if exp_path.exists():
                expected = json.loads(exp_path.read_text(encoding="utf-8"))
                if result.get("cut_type") == expected.get("cut_type"):
                    correct += 1
                    print(f" OK ({result['cut_type']})")
                else:
                    print(f" FAIL: expected={expected['cut_type']} got={result['cut_type']}")
            else:
                print(f" OK (no expected)")
        else:
            print(f" FAILED")

    print(f"\n完成: {success}/{total} 成功, {correct}/{total} 正确")


if __name__ == "__main__":
    main()
