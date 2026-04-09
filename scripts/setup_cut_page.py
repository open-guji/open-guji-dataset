"""创建 cut-page 数据集：从 book-profile 001-015 复制 + 添加 PDF 样本。"""
import json
import shutil
from pathlib import Path

BOOK_PROFILE_SAMPLES = Path("D:/workspace/open-guji-dataset/book-profile/samples")
CUT_PAGE_SAMPLES = Path("D:/workspace/open-guji-dataset/cut-page/samples")

# 001-015 的 cut_type 映射（基于 layout）
# spread → vertical_cut, uncut_full/cut_half → none
LAYOUT_TO_CUT = {
    "spread": "vertical_cut",
    "uncut_full": "none",
    "cut_half": "none",
}


def main():
    # 从 book-profile 001-015 复制
    for i in range(1, 16):
        sid = f"{i:03d}"
        src_dir = BOOK_PROFILE_SAMPLES / sid
        dst_dir = CUT_PAGE_SAMPLES / sid

        if not src_dir.exists():
            print(f"[{sid}] SKIP: source not found")
            continue

        dst_dir.mkdir(parents=True, exist_ok=True)

        # 复制图片
        for img in src_dir.glob("image.*"):
            shutil.copy2(img, dst_dir / img.name)

        # 读取 expected.json 获取 layout
        exp = json.loads((src_dir / "expected.json").read_text(encoding="utf-8"))
        layout = exp.get("layout", "cut_half")
        cut_type = LAYOUT_TO_CUT.get(layout, "none")

        # 复制并修改 info.json
        info = json.loads((src_dir / "info.json").read_text(encoding="utf-8"))
        info["id"] = sid
        (dst_dir / "info.json").write_text(
            json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # 创建 expected.json
        expected = {"cut_type": cut_type}
        (dst_dir / "expected.json").write_text(
            json.dumps(expected, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        print(f"[{sid}] layout={layout} -> cut_type={cut_type}")

    # 添加 PDF 样本
    pdf_samples = [
        {
            "id": "016",
            "source": "续修四库全书总目提要 稿本 32",
            "source_file": "page_3",
            "image": "D:/tmp/xuxiu_page_3.png",
            "description": "续修四库全书总目提要，上下两栏，需水平切分",
            "cut_type": "horizontal_cut",
            "tags": ["horizontal_cut", "two_columns"],
        },
        {
            "id": "017",
            "source": "续修四库全书总目提要 稿本 32",
            "source_file": "page_11",
            "image": "D:/tmp/xuxiu_page_11.png",
            "description": "续修四库全书总目提要，上下两栏，需水平切分",
            "cut_type": "horizontal_cut",
            "tags": ["horizontal_cut", "two_columns"],
        },
        {
            "id": "018",
            "source": "四库全书总目 上下 1965 北京中华书局",
            "source_file": "page_7",
            "image": "D:/tmp/sikuzongmu_page_7.png",
            "description": "四库全书总目（中华书局1965版），单栏，不需切分",
            "cut_type": "none",
            "tags": ["none", "single_column", "modern_print"],
        },
    ]

    for s in pdf_samples:
        sid = s["id"]
        dst_dir = CUT_PAGE_SAMPLES / sid
        dst_dir.mkdir(parents=True, exist_ok=True)

        src_img = Path(s["image"])
        shutil.copy2(src_img, dst_dir / f"image{src_img.suffix}")

        info = {
            "id": sid,
            "source": s["source"],
            "source_file": s["source_file"],
            "description": s["description"],
            "tags": s["tags"],
        }
        (dst_dir / "info.json").write_text(
            json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        expected = {"cut_type": s["cut_type"]}
        (dst_dir / "expected.json").write_text(
            json.dumps(expected, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        print(f"[{sid}] PDF: cut_type={s['cut_type']}")

    print(f"\nDone: {15 + len(pdf_samples)} samples")


if __name__ == "__main__":
    main()
