"""从 AncientDoc 数据集挑选代表性图片创建 benchmark 样本。"""
import json
import shutil
from pathlib import Path

ANCIENTDOC = Path("D:/workspace/resource/AncientDoc/imgs")
SAMPLES_DIR = Path("D:/workspace/open-guji-dataset/benchmark/book-profile/samples")

# 从 009 开始编号（001-008 已被 open-guji-cv 占用）
SAMPLES = [
    {
        "category": "传记类",
        "book": "晏子春秋",
        "file": "page_23.png",
        "description": "晏子春秋卷首，未裁全页，黑白底红色圈点，单边框，约10行",
        "tags": ["uncut_full", "regular", "bw", "single", "10_lines", "red_punctuation"],
    },
    {
        "category": "天文算法类",
        "book": "天文圖說",
        "file": "page_17.png",
        "description": "天文圖說，半页扫描，黑白，密排约13行，单边框",
        "tags": ["cut_half", "regular", "bw", "single", "13_lines"],
    },
    {
        "category": "天文算法类",
        "book": "天文圖說",
        "file": "page_20.png",
        "description": "天文圖說插图页，含天文图和文字混排",
        "tags": ["cut_half", "illustration", "bw", "single"],
    },
    {
        "category": "儒家类",
        "book": "菜根譚",
        "file": "page_10.png",
        "description": "菜根譚，未裁全页，米黄底色，边角破损，双边框，约12行",
        "tags": ["uncut_full", "regular", "colored", "yellow", "double", "12_lines", "water_damage"],
    },
    {
        "category": "兵家类",
        "book": "兵鏡",
        "file": "page_10.png",
        "description": "兵鏡，未裁全页，白底红圈点，单边框，约10行",
        "tags": ["uncut_full", "regular", "bw", "single", "10_lines", "red_punctuation"],
    },
    {
        "category": "艺术类",
        "book": "乐记",
        "file": "page_10.png",
        "description": "乐记，未裁全页，米黄底色，密排有夹注，双边框",
        "tags": ["uncut_full", "regular", "colored", "yellow", "double", "marginal_notes"],
    },
    {
        "category": "小说家类",
        "book": "(新鐫)笑林廣記",
        "file": "page_10.png",
        "description": "笑林廣記，未裁全页，蓝色边框（特殊），白底，约10行",
        "tags": ["uncut_full", "regular", "bw", "single", "10_lines", "blue_border"],
    },
    {
        "category": "天文算法类",
        "book": "靈臺儀象志",
        "file": "page_10.png",
        "description": "靈臺儀象志，未裁全页，黑白，单边框，约10行，干净清晰",
        "tags": ["uncut_full", "regular", "bw", "single", "10_lines"],
    },
    {
        "category": "谱录类",
        "book": "文房十二友",
        "file": "page_10.png",
        "description": "文房十二友，未裁全页，黑白，单边框，密排约12行",
        "tags": ["uncut_full", "regular", "bw", "single", "12_lines"],
    },
    {
        "category": "类书类",
        "book": "册府元龜",
        "file": "page_10.png",
        "description": "册府元龜，未裁全页，黄色底色有污渍，大字少行(约5行)，单边框",
        "tags": ["uncut_full", "regular", "colored", "yellow", "single", "5_lines", "stains"],
    },
    {
        "category": "医家类",
        "book": "隂海陽海二圖",
        "file": "page_10.png",
        "description": "隂海陽海二圖，医学插图页（人体脏腑图），米色底",
        "tags": ["uncut_full", "illustration", "colored", "yellow", "single"],
    },
    {
        "category": "杂家类",
        "book": "同書",
        "file": "page_10.png",
        "description": "同書，未裁全页，米色底，单边框，约8行大字",
        "tags": ["uncut_full", "regular", "colored", "yellow", "single", "8_lines"],
    },
    {
        "category": "总集类",
        "book": "古樂府",
        "file": "page_10.png",
        "description": "古樂府目录+正文混排，未裁全页，黑白，单边框",
        "tags": ["uncut_full", "regular", "bw", "single", "mixed_layout"],
    },
    {
        "category": "楚辞类",
        "book": "楚辭新註",
        "file": "page_10.png",
        "description": "楚辭新註，未裁全页，黑白，单边框，密排约13行",
        "tags": ["uncut_full", "regular", "bw", "single", "13_lines"],
    },
    {
        "category": "诗文评类",
        "book": "六一詩話",
        "file": "page_10.png",
        "description": "六一詩話，未裁全页，米色底，双边框，约10行",
        "tags": ["uncut_full", "regular", "colored", "yellow", "double", "10_lines"],
    },
    {
        "category": "医家类",
        "book": "太醫院校註婦人良方大全",
        "file": "page_10.png",
        "description": "婦人良方大全，未裁全页，黄色底有夹注，双边框，密排",
        "tags": ["uncut_full", "regular", "colored", "yellow", "double", "marginal_notes"],
    },
]


def main():
    start_id = 9
    for i, sample in enumerate(SAMPLES):
        sample_id = f"{start_id + i:03d}"
        sample_dir = SAMPLES_DIR / sample_id
        sample_dir.mkdir(parents=True, exist_ok=True)

        # 复制图片
        src = ANCIENTDOC / sample["category"] / sample["book"] / sample["file"]
        suffix = src.suffix
        dst = sample_dir / f"image{suffix}"
        if src.exists():
            shutil.copy2(src, dst)
            print(f"[{sample_id}] {sample['book']}/{sample['file']}")
        else:
            print(f"[{sample_id}] WARNING: {src} not found")

        # info.json
        info = {
            "id": sample_id,
            "source": f"AncientDoc/imgs/{sample['category']}/{sample['book']}",
            "source_file": sample["file"],
            "description": sample["description"],
            "tags": sample["tags"],
        }
        (sample_dir / "info.json").write_text(
            json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    print(f"\nDone: {len(SAMPLES)} samples created (009-{start_id + len(SAMPLES) - 1:03d})")


if __name__ == "__main__":
    main()
