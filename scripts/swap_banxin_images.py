"""替换 banxin_position=left 的样本图片为相邻页（版心在右侧）。"""
import json
import shutil
from pathlib import Path

SAMPLES_DIR = Path("D:/workspace/open-guji-dataset/book-profile/samples")

# 每个样本的替换源：(新图片路径, 新 source_file)
SWAPS = {
    "001": ("D:/workspace/open-guji-cv/data/book1/4.png", "4.png"),
    "003": ("D:/workspace/open-guji-cv/data/book3/4.png", "4.png"),
    "004": ("D:/workspace/open-guji-cv/data/book4/4.png", "4.png"),
    "005": ("D:/workspace/open-guji-cv/data/book5/4.png", "4.png"),
    "006": ("D:/workspace/open-guji-cv/data/book6/v01_026.jpg", "v01_026.jpg"),
    "007": ("D:/workspace/open-guji-cv/data/book7/06054854.cn_page_113.png", "06054854.cn_page_113.png"),
    "010": ("D:/workspace/resource/AncientDoc/imgs/天文算法类/天文圖說/page_18.png", "page_18.png"),
}


def main():
    for sid, (src_path, new_source_file) in SWAPS.items():
        sample_dir = SAMPLES_DIR / sid
        src = Path(src_path)

        if not src.exists():
            print(f"[{sid}] WARNING: {src} not found")
            continue

        # 删除旧图片
        for old in sample_dir.glob("image.*"):
            old.unlink()

        # 复制新图片
        suffix = src.suffix
        dst = sample_dir / f"image{suffix}"
        shutil.copy2(src, dst)

        # 更新 info.json
        info_path = sample_dir / "info.json"
        info = json.loads(info_path.read_text(encoding="utf-8"))
        info["source_file"] = new_source_file
        info_path.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")

        # 更新 expected.json: banxin_position → right
        exp_path = sample_dir / "expected.json"
        exp = json.loads(exp_path.read_text(encoding="utf-8"))
        exp["banxin_position"] = "right"
        exp_path.write_text(json.dumps(exp, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"[{sid}] swapped to {new_source_file}, banxin=right")

    print("\nDone")


if __name__ == "__main__":
    main()
