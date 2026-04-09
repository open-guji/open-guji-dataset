"""迁移数据到 v3 schema:
1. 添加 font_type 字段 (printed/handwritten)
2. 添加 fixed_chars_per_line 字段 (true/false)
   - 已有 chars_per_line 非 null → true
   - chars_per_line 为 null → true (默认，待人工确认)
"""
import json
from pathlib import Path

BENCHMARK_DIR = Path("D:/workspace/open-guji-dataset/book-profile")
SAMPLES_DIR = BENCHMARK_DIR / "samples"

# book2 是手写本，其余都是印刷
HANDWRITTEN = {"002"}


def main():
    for d in sorted(SAMPLES_DIR.iterdir()):
        if not d.is_dir():
            continue
        path = d / "expected.json"
        if not path.exists():
            continue

        data = json.loads(path.read_text(encoding="utf-8"))

        # font_type
        if "font_type" not in data:
            data["font_type"] = "handwritten" if d.name in HANDWRITTEN else "printed"

        # fixed_chars_per_line
        if "fixed_chars_per_line" not in data:
            data["fixed_chars_per_line"] = True

        # 重新排序字段
        order = [
            "layout", "banxin_position", "content_format", "font_type",
            "lines_per_page", "fixed_chars_per_line", "chars_per_line",
            "has_marginal_notes",
            "color_mode", "background_color", "text_color",
            "border_color", "border_style", "border_wear",
            "interferences", "margin_color",
        ]
        ordered = {}
        for key in order:
            if key in data:
                ordered[key] = data[key]
        for key in data:
            if key not in ordered:
                ordered[key] = data[key]

        path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{d.name}] font={ordered['font_type']}, fixed_cpl={ordered['fixed_chars_per_line']}")

    print("\nDone")


if __name__ == "__main__":
    main()
