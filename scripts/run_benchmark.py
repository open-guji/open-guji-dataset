"""对所有 benchmark 样本运行 recognize-profile，生成结果。"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BENCHMARK_DIR = Path("D:/workspace/open-guji-dataset/book-profile")
SAMPLES_DIR = BENCHMARK_DIR / "samples"
RESULTS_DIR = BENCHMARK_DIR / "results"
GUJI_CV = "D:/workspace/open-guji-cv"


def run_recognize_profile(image_path: Path) -> dict | None:
    """对单张图片运行 recognize-profile，返回 profile dict。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 复制图片到临时目录
        shutil.copy2(image_path, Path(tmpdir) / image_path.name)

        result = subprocess.run(
            [sys.executable, "-m", "open_guji_cv", "recognize-profile", tmpdir],
            capture_output=True,
            text=True,
            cwd=GUJI_CV,
            encoding="utf-8",
        )

        if result.returncode != 0:
            print(f"  ERROR: {result.stderr.strip()}")
            return None

        # recognize-profile 会在输入目录生成 profile.json
        profile_path = Path(tmpdir) / "profile.json"
        if profile_path.exists():
            return json.loads(profile_path.read_text(encoding="utf-8"))
        else:
            print(f"  ERROR: profile.json not generated")
            return None


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    sample_dirs = sorted(SAMPLES_DIR.iterdir())
    total = len(sample_dirs)
    success = 0

    for sample_dir in sample_dirs:
        if not sample_dir.is_dir():
            continue

        sample_id = sample_dir.name
        # 找图片文件
        images = list(sample_dir.glob("image.*"))
        if not images:
            print(f"[{sample_id}] SKIP: no image file")
            continue

        image = images[0]
        info_path = sample_dir / "info.json"
        desc = ""
        if info_path.exists():
            info = json.loads(info_path.read_text(encoding="utf-8"))
            desc = info.get("description", "")

        print(f"[{sample_id}] {desc[:40]}...")
        profile = run_recognize_profile(image)

        if profile:
            result_path = RESULTS_DIR / f"{sample_id}.json"
            result_path.write_text(
                json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            success += 1
            print(f"  OK")
        else:
            print(f"  FAILED")

    print(f"\n完成: {success}/{total} 成功")


if __name__ == "__main__":
    main()
