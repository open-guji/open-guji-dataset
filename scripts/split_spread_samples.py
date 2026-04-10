"""将 book-profile 中的 spread 样本切分为 cut_half。

奇数索引保留左半页（banxin=left），偶数索引保留右半页（banxin=right）。
更新 image 和 expected.json。
"""
import json
import cv2
from pathlib import Path

SAMPLES_DIR = Path("D:/workspace/open-guji-dataset/book-profile/samples")


def main():
    # 收集所有 spread 样本
    spread_ids = []
    for d in sorted(SAMPLES_DIR.iterdir()):
        if not d.is_dir():
            continue
        ep = d / "expected.json"
        if not ep.exists():
            continue
        exp = json.loads(ep.read_text(encoding="utf-8"))
        if exp.get("layout") == "spread":
            spread_ids.append(d.name)

    print(f"Found {len(spread_ids)} spread samples")

    for idx, sid in enumerate(spread_ids):
        sample_dir = SAMPLES_DIR / sid
        keep_left = (idx % 2 == 0)  # 0,2,4... → left; 1,3,5... → right
        side = "left" if keep_left else "right"

        # 读取图片
        img_path = None
        for ext in ["png", "jpg", "jpeg"]:
            p = sample_dir / f"image.{ext}"
            if p.exists():
                img_path = p
                break

        if not img_path:
            print(f"[{sid}] SKIP: no image")
            continue

        img = cv2.imread(str(img_path))
        if img is None:
            print(f"[{sid}] SKIP: cannot read image")
            continue

        h, w = img.shape[:2]
        mid_x = w // 2

        # 切分
        if keep_left:
            half = img[:, :mid_x]
        else:
            half = img[:, mid_x:]

        # 覆盖写入
        cv2.imwrite(str(sample_dir / "image.png"), half)
        # 删除旧格式图片（如果是 jpg）
        if img_path.suffix != ".png":
            img_path.unlink()

        # 更新 expected.json
        exp = json.loads((sample_dir / "expected.json").read_text(encoding="utf-8"))
        exp["layout"] = "cut_half"
        exp["banxin_position"] = side
        (sample_dir / "expected.json").write_text(
            json.dumps(exp, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        print(f"[{sid}] {w}x{h} -> {half.shape[1]}x{half.shape[0]} keep={side} banxin={side}")

    print(f"\nDone. All spread -> cut_half")


if __name__ == "__main__":
    main()
