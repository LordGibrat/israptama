"""Local-only HTTP app; uploaded CSV is processed in memory and never saved."""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from engine import FIELDS, analyze, export_csv, parse_csv, sample_rows

STATIC = Path(__file__).parent / "static"


class Handler(BaseHTTPRequestHandler):
    def send(self, status: int, content: bytes, kind: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; "
                         "script-src 'self'; img-src 'self' data:; connect-src 'self'; "
                         "object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(content)

    def json(self, status: int, data: dict) -> None:
        self.send(status, json.dumps(data, ensure_ascii=False, allow_nan=False).encode(),
                  "application/json; charset=utf-8")

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        if route == "/api/sample":
            self.json(200, analyze(sample_rows(), synthetic=True))
        elif route in ("/api/sample.csv", "/api/template.csv"):
            content = (export_csv(sample_rows()) if route.endswith("sample.csv")
                       else ",".join(FIELDS) + "\n2026-07-01,Нан,100,85,400,160\n")
            self.send(200, ("\ufeff" + content).encode(), "text/csv; charset=utf-8")
        elif route == "/favicon.ico":
            self.send(204, b"", "image/x-icon")
        else:
            allowed = {"/": ("index.html", "text/html"),
                       "/app.js": ("app.js", "application/javascript"),
                       "/style.css": ("style.css", "text/css"),
                       "/bakery.css": ("bakery.css", "text/css"),
                       **{f"/assets/{name}.svg": (f"assets/{name}.svg", "image/svg+xml")
                          for name in ("bakery-tray", "croissant", "bread", "samsa")}}
            if route not in allowed:
                self.json(404, {"error": "Бет табылмады."})
                return
            filename, kind = allowed[route]
            self.send(200, (STATIC / filename).read_bytes(), kind + "; charset=utf-8")

    def do_POST(self) -> None:
        if self.path != "/api/analyze":
            self.json(404, {"error": "Бет табылмады."})
            return
        origin = self.headers.get("Origin")
        allowed_origins = {f"http://localhost:{self.server.server_port}",
                           f"http://127.0.0.1:{self.server.server_port}"}
        if origin and origin not in allowed_origins:
            self.json(403, {"error": "Тек жергілікті қосымшаға рұқсат."})
            return
        if not self.headers.get("Content-Type", "").startswith("application/json"):
            self.json(415, {"error": "JSON қажет."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 2_100_000:
                self.json(413, {"error": "Файл тым үлкен немесе сұрау бос."})
                return
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError("Сұрау JSON объектісі болуы керек.")
            csv_text = body.get("csv")
            synthetic = csv_text is None
            rows = sample_rows() if synthetic else parse_csv(csv_text)
            result = analyze(rows, synthetic=synthetic, buffer=body.get("buffer", 0))
            # A sample CSV re-upload is still a fictional dataset, with observable-sales evaluation.
            if not synthetic and all(r.get("data_source") == "SYNTHETIC_DEMO" for r in rows):
                result["synthetic"] = True
                result["uploaded_sample"] = True
            self.json(200, result)
        except (ValueError, UnicodeDecodeError, TypeError, KeyError) as exc:
            self.json(400, {"error": str(exc)})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Israptama local bakery planning prototype")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Israptama: http://localhost:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
