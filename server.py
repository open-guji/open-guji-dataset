"""Benchmark 数据浏览与编辑服务器。

启动: python server.py
访问: http://localhost:8765
"""
import json
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote

PORT = 8765
BASE_DIR = Path(__file__).parent
BENCHMARK_DIR = BASE_DIR / "book-profile"
SAMPLES_DIR = BENCHMARK_DIR / "samples"
RESULTS_DIR = BENCHMARK_DIR / "results"

BASIC_FIELDS = [
    "layout", "banxin_position", "content_format", "lines_per_page",
]
ADVANCED_FIELDS = [
    "font_type", "fixed_chars_per_line", "chars_per_line", "has_marginal_notes",
    "color_mode", "background_color", "text_color",
    "border_color", "border_style", "border_wear",
    "interferences", "margin_color",
]
EVAL_FIELDS = BASIC_FIELDS + ADVANCED_FIELDS


def read_json(path: Path) -> dict | None:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def should_eval_field(expected: dict, field: str) -> bool:
    if field == "banxin_position":
        return expected.get("layout") == "cut_half"
    if field == "margin_color":
        return "margin" in (expected.get("interferences") or [])
    if field == "chars_per_line":
        return expected.get("fixed_chars_per_line", True) is not False
    return True


def check_fields_match(expected: dict, result: dict, fields: list) -> bool:
    """Check if specified fields match between expected and result."""
    for f in fields:
        if not should_eval_field(expected, f):
            continue
        ev = expected.get(f)
        rv = result.get(f)
        if f == "interferences":
            if sorted(ev or []) != sorted(rv or []):
                return False
        elif ev != rv:
            return False
    return True


def get_sample_list() -> list:
    """Get all samples with summary info."""
    samples = []
    for d in sorted(SAMPLES_DIR.iterdir()):
        if not d.is_dir():
            continue
        info = read_json(d / "info.json") or {}
        expected = read_json(d / "expected.json")
        result_path = RESULTS_DIR / f"{d.name}.json"
        result = read_json(result_path)

        has_result = result is not None
        basic_match = False
        advanced_match = False
        if expected and result:
            basic_match = check_fields_match(expected, result, BASIC_FIELDS)
            advanced_match = check_fields_match(expected, result, ADVANCED_FIELDS)

        samples.append({
            "id": d.name,
            "description": info.get("description", ""),
            "tags": info.get("tags", []),
            "has_expected": expected is not None,
            "has_result": has_result,
            "basic_match": basic_match,
            "advanced_match": advanced_match,
        })
    return samples


def get_sample_detail(sample_id: str) -> dict | None:
    sample_dir = SAMPLES_DIR / sample_id
    if not sample_dir.is_dir():
        return None

    info = read_json(sample_dir / "info.json") or {}
    expected = read_json(sample_dir / "expected.json") or {}
    result = read_json(RESULTS_DIR / f"{sample_id}.json") or {}

    return {
        "id": sample_id,
        "info": info,
        "expected": expected,
        "result": result,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress default logging

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path: Path):
        if not path.exists():
            self.send_error(404)
            return
        mime, _ = mimetypes.guess_type(str(path))
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(data))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = unquote(self.path)

        # Static files
        if path == "/" or path == "/index.html":
            self.send_file(BASE_DIR / "index.html")
            return

        # API: list samples
        if path == "/api/samples":
            self.send_json(get_sample_list())
            return

        # API: sample detail
        parts = path.split("/")
        if len(parts) == 4 and parts[1] == "api" and parts[2] == "samples":
            data = get_sample_detail(parts[3])
            if data:
                self.send_json(data)
            else:
                self.send_error(404)
            return

        # API: sample image
        if len(parts) == 5 and parts[1] == "api" and parts[2] == "samples" and parts[4] == "image":
            sample_dir = SAMPLES_DIR / parts[3]
            images = list(sample_dir.glob("image.*"))
            if images:
                self.send_file(images[0])
            else:
                self.send_error(404)
            return

        self.send_error(404)

    def do_PUT(self):
        path = unquote(self.path)
        parts = path.split("/")

        # API: update expected.json
        if len(parts) == 5 and parts[1] == "api" and parts[2] == "samples" and parts[4] == "expected":
            sample_id = parts[3]
            sample_dir = SAMPLES_DIR / sample_id
            if not sample_dir.is_dir():
                self.send_error(404)
                return

            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError:
                self.send_json({"error": "Invalid JSON"}, 400)
                return

            expected_path = sample_dir / "expected.json"
            expected_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            self.send_json({"ok": True, "id": sample_id})
            return

        self.send_error(404)


def main():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Server running at http://localhost:{PORT}")
    print(f"Samples: {SAMPLES_DIR}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped")


if __name__ == "__main__":
    main()
