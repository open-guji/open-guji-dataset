#!/usr/bin/env python3
"""标注包本地小服务：把本文件放进标注包文件夹（pack.json 同级），双击或 `python serve.py`。

自动用「本文件所在文件夹」当工作目录：浏览器打开 http://127.0.0.1:8765/annotate.html 就自动载入
包里的 pack.json、drafts.json、页图；导出直接存回这个文件夹（items_<包id>.jsonl）。只监听本机。
"""
import json, os, sys, threading, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("ANNOTATE_PORT", "8765"))


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def do_GET(self):
        if urlparse(self.path).path == "/_list":
            names = sorted(f for f in os.listdir(ROOT) if os.path.isfile(os.path.join(ROOT, f)))
            b = json.dumps(names, ensure_ascii=False).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        else:
            super().do_GET()

    def do_POST(self):
        u = urlparse(self.path)
        name = (parse_qs(u.query).get("name") or [""])[0]
        if u.path != "/_save" or not (name.startswith("items_") and name.endswith(".jsonl")) or "/" in name or "\\" in name:
            self.send_error(400, "只允许保存 items_*.jsonl"); return
        data = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        with open(os.path.join(ROOT, name), "wb") as f:
            f.write(data)
        self.send_response(200); self.send_header("Content-Length", "2"); self.end_headers(); self.wfile.write(b"ok")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    srv = None
    for port in range(PORT, PORT + 20):      # 端口被占（比如上一个包的服务还开着）就顺延
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", port), H)
            break
        except OSError:
            continue
    if srv is None:
        sys.exit("8765 起的 20 个端口都被占用，请关掉之前的 serve.py 窗口再试")
    url = f"http://127.0.0.1:{srv.server_address[1]}/annotate.html"
    print("标注包文件夹：", ROOT, "\n打开：", url, "\n（关掉这个窗口即停止）")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
