"""从 open-guji-cv/data 中选取代表性图片创建 benchmark 样本。"""
import json
import shutil
from pathlib import Path

OPEN_GUJI_CV_DATA = Path("D:/workspace/open-guji-cv/data")
SAMPLES_DIR = Path("D:/workspace/open-guji-dataset/book-profile/samples")

# 每个 book 选取的图片和描述
BOOKS = [
    {
        "book": "book1",
        "image": "3.png",
        "description": "四库全书简明目录，标准黑白半页扫描，8行，双边框",
        "tags": ["cut_half", "regular", "bw", "double", "8_lines"],
    },
    {
        "book": "book2",
        "image": "3.png",
        "description": "未裁全页（蝴蝶装），手写批注，有夹注，8行",
        "tags": ["uncut_full", "regular", "bw", "double", "8_lines", "marginal_notes"],
    },
    {
        "book": "book3",
        "image": "3.png",
        "description": "彩色（橙底），9行，有污渍干扰",
        "tags": ["cut_half", "regular", "colored", "orange", "double", "9_lines", "stains"],
    },
    {
        "book": "book4",
        "image": "3.png",
        "description": "彩色（橙底），11行密排，有书脊阴影",
        "tags": ["cut_half", "regular", "colored", "orange", "double", "11_lines", "spine_shadow"],
    },
    {
        "book": "book5",
        "image": "3.png",
        "description": "黑白刻本，8行15字，边框严重磨损，有白边",
        "tags": ["cut_half", "regular", "bw", "double", "8_lines", "heavy_wear", "white_margin"],
    },
    {
        "book": "book6",
        "image": "v01_025.jpg",
        "description": "标准黑白半页扫描，8行，有夹注区域",
        "tags": ["cut_half", "regular", "bw", "double", "8_lines"],
    },
    {
        "book": "book7",
        "image": "06054854.cn_page_112.png",
        "description": "表格版面（天文历法），非常规列式，书脊阴影+白边",
        "tags": ["cut_half", "table", "bw", "double", "spine_shadow", "white_margin"],
    },
    {
        "book": "book8",
        "image": "page_026.png",
        "description": "跨页摊开扫描（前汉书），彩色橙底，12行，有夹注，书脊阴影",
        "tags": ["spread", "regular", "colored", "orange", "double", "12_lines", "marginal_notes", "spine_shadow"],
    },
]


def main():
    for i, book_info in enumerate(BOOKS, start=1):
        sample_id = f"{i:03d}"
        sample_dir = SAMPLES_DIR / sample_id
        sample_dir.mkdir(parents=True, exist_ok=True)

        # 复制图片
        src_image = OPEN_GUJI_CV_DATA / book_info["book"] / book_info["image"]
        suffix = src_image.suffix
        dst_image = sample_dir / f"image{suffix}"
        if src_image.exists():
            shutil.copy2(src_image, dst_image)
            print(f"[{sample_id}] 复制 {src_image.name} -> {dst_image.name}")
        else:
            print(f"[{sample_id}] 警告: {src_image} 不存在")

        # 生成 info.json
        info = {
            "id": sample_id,
            "source": f"open-guji-cv/data/{book_info['book']}",
            "source_file": book_info["image"],
            "description": book_info["description"],
            "tags": book_info["tags"],
        }
        (sample_dir / "info.json").write_text(
            json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # 复制 profile.json 作为 expected.json
        src_profile = OPEN_GUJI_CV_DATA / book_info["book"] / "profile.json"
        if src_profile.exists():
            profile = json.loads(src_profile.read_text(encoding="utf-8"))
            # 移除 auto_detected 和 detection_confidence，ground truth 不需要
            profile.pop("auto_detected", None)
            profile.pop("detection_confidence", None)
            profile.pop("skip_pages", None)
            profile.pop("skip_steps", None)
            (sample_dir / "expected.json").write_text(
                json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8"
            )

    print(f"\n完成: 共创建 {len(BOOKS)} 个样本")


if __name__ == "__main__":
    main()
