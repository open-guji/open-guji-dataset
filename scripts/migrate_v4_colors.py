"""迁移颜色字段到新选项体系:
- background_color: null -> white, orange -> xuan
- border_color: orange -> red
- text_color: 保持 black
"""
import json
from pathlib import Path

SAMPLES_DIR = Path("D:/workspace/open-guji-dataset/book-profile/samples")

BG_MAP = {None: "white", "orange": "xuan", "yellow": "xuan", "red": "other"}
BORDER_MAP = {"orange": "red"}


def main():
    for d in sorted(SAMPLES_DIR.iterdir()):
        if not d.is_dir():
            continue
        path = d / "expected.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        changed = False

        bg = data.get("background_color")
        if bg in BG_MAP:
            data["background_color"] = BG_MAP[bg]
            changed = True

        bc = data.get("border_color")
        if bc in BORDER_MAP:
            data["border_color"] = BORDER_MAP[bc]
            changed = True

        if changed:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[{d.name}] bg={data['background_color']} border={data['border_color']}")

    print("Done")


if __name__ == "__main__":
    main()
