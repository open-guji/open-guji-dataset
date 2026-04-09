"""迁移数据到 v2 schema:
1. white_margin -> margin (in interferences)
2. 添加 margin_color 字段 (white/black, 仅当有 margin 干扰时)
3. 移除 stains/water_damage (不再作为干扰项)
4. 为 cut_half 样本添加 banxin_position (left/right)
5. 同时更新 expected.json 和 results/*.json
"""
import json
from pathlib import Path

BENCHMARK_DIR = Path("D:/workspace/open-guji-dataset/book-profile")
SAMPLES_DIR = BENCHMARK_DIR / "samples"
RESULTS_DIR = BENCHMARK_DIR / "results"

# cut_half 样本的版心位置（人工判断）
# 版心在图片左侧 = left，右侧 = right
BANXIN_MAP = {
    "001": "left",   # 四库全书简明目录 - 版心在左
    "003": "left",   # 彩色橙底 - 版心在左
    "004": "left",   # 彩色橙底11行 - 版心在左
    "005": "left",   # 黑白刻本 - 版心在左
    "006": "left",   # 标准黑白 - 版心在左
    "007": "left",   # 表格版面 - 版心在左
    "010": "right",  # 天文圖說 - 版心在右
    "011": "right",  # 天文圖說插图 - 版心在右
}

# margin_color: 有 white_margin 的样本，页边距颜色
MARGIN_COLOR_MAP = {
    "001": "white",  # results 检测到 white_margin
    "002": "white",  # results 检测到 white_margin
    "005": "white",  # 白色页边距
    "007": "white",  # 白色页边距
}


def migrate_profile(data: dict, sample_id: str, is_result: bool = False) -> dict:
    """迁移单个 profile 数据。"""
    interferences = data.get("interferences", [])
    new_interferences = []

    has_margin = False
    for item in interferences:
        if item == "white_margin":
            new_interferences.append("margin")
            has_margin = True
        elif item in ("stains", "water_damage"):
            continue  # 移除
        else:
            new_interferences.append(item)

    data["interferences"] = new_interferences

    # margin_color
    if has_margin:
        data["margin_color"] = MARGIN_COLOR_MAP.get(sample_id, "white")
    elif "margin_color" not in data:
        data["margin_color"] = None

    # banxin_position (仅 cut_half 且非 result)
    layout = data.get("layout")
    if layout == "cut_half" and not is_result:
        if sample_id in BANXIN_MAP:
            data["banxin_position"] = BANXIN_MAP[sample_id]
        elif "banxin_position" not in data:
            data["banxin_position"] = "right"  # 默认

    return data


def reorder_fields(data: dict) -> dict:
    """按规范顺序排列字段。"""
    order = [
        "layout", "banxin_position", "content_format",
        "lines_per_page", "chars_per_line", "has_marginal_notes",
        "color_mode", "background_color", "text_color",
        "border_color", "border_style", "border_wear",
        "interferences", "margin_color",
        # result 特有字段
        "skip_pages", "skip_steps", "auto_detected", "detection_confidence",
    ]
    result = {}
    for key in order:
        if key in data:
            result[key] = data[key]
    # 保留未列出的字段
    for key in data:
        if key not in result:
            result[key] = data[key]
    return result


def main():
    # 迁移 expected.json
    print("=== 迁移 expected.json ===")
    for d in sorted(SAMPLES_DIR.iterdir()):
        if not d.is_dir():
            continue
        path = d / "expected.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        data = migrate_profile(data, d.name, is_result=False)
        data = reorder_fields(data)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  [{d.name}] OK")

    # 迁移 results/*.json
    print("\n=== 迁移 results/*.json ===")
    for path in sorted(RESULTS_DIR.glob("*.json")):
        sample_id = path.stem
        data = json.loads(path.read_text(encoding="utf-8"))
        data = migrate_profile(data, sample_id, is_result=True)
        data = reorder_fields(data)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  [{sample_id}] OK")

    # 更新 info.json tags
    print("\n=== 更新 info.json tags ===")
    for d in sorted(SAMPLES_DIR.iterdir()):
        if not d.is_dir():
            continue
        path = d / "info.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        tags = data.get("tags", [])
        new_tags = []
        for t in tags:
            if t == "white_margin":
                new_tags.append("margin")
            elif t in ("stains", "water_damage"):
                continue
            else:
                new_tags.append(t)
        data["tags"] = new_tags
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nDone")


if __name__ == "__main__":
    main()
