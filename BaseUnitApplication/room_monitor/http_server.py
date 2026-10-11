"""Loopback-only read API; room labels are edited in the local JSON config."""
import ipaddress
import json
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

STATIC = Path(__file__).parent / "static"
ASSETS = {"/": ("index.html", "text/html; charset=utf-8"),
          "/app.js": ("app.js", "text/javascript; charset=utf-8"),
          "/style.css": ("style.css", "text/css; charset=utf-8")}


def make_server(store, host="127.0.0.1", port=8080, receiver=None):
    address = ipaddress.ip_address(host)
    if not address.is_loopback:
        raise ValueError("dashboard HTTP must bind to a loopback address")

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def log_message(self, fmt, *args):
            pass

        def respond(self, status, body, content_type="application/json"):
            if not isinstance(body, bytes):
                body = json.dumps(body, allow_nan=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def do_GET(self):
            expected = f"[{host}]" if address.version == 6 else host
            allowed = {f"{expected}:{self.server.server_port}", f"localhost:{self.server.server_port}"}
            if self.headers.get("Host", "") not in allowed:
                self.respond(403, {"error": "local Host header required"})
                return
            if self.headers.get("Sec-Fetch-Site") == "cross-site":
                self.respond(403, {"error": "cross-site request denied"})
                return
            try:
                target = urlsplit(self.path)
                query = parse_qs(target.query, max_num_fields=8)
                if target.path in ASSETS:
                    name, content_type = ASSETS[target.path]
                    self.respond(200, (STATIC / name).read_bytes(), content_type)
                elif target.path == "/api/status":
                    self.respond(200, store.summary())
                elif target.path == "/api/history":
                    self.respond(200, store.history(query.get("node_id", [""])[0],
                                                    float(query.get("hours", ["24"])[0]),
                                                    int(query.get("limit", ["240"])[0])))
                elif target.path == "/healthz":
                    health = {"status": "ok", "mode": store.mode}
                    if receiver is not None:
                        health["receiver"] = dict(receiver)
                    self.respond(200, health)
                else:
                    self.respond(404, {"error": "not found"})
            except ValueError as exc:
                self.respond(400, {"error": str(exc)})

    class Server(ThreadingHTTPServer):
        address_family = socket.AF_INET6 if address.version == 6 else socket.AF_INET
        daemon_threads = True

    return Server((host, port), Handler)
