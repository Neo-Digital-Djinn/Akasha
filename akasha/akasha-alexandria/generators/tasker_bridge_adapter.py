"""
HTTP Bridge Adapter — Debian Port

Originally: Android Tasker HTTP bridge (Termux).
Ported to: standard Python HTTP server, compatible with Debian/Linux.

Listens on localhost:8080 for a single POST request containing a
Hypothesis JSON payload, then returns it to the kernel for evaluation.

Usage (external):
    curl -X POST http://localhost:8080 \
         -H "Content-Type: application/json" \
         -d '{"domain":"fin","claim":"A","constraints":[],"parameters":{},"derivation":"","confidence":1.0,"meta":{}}'
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from alexandria.hypothesis import Hypothesis
from generators.interface import GeneratorAdapter


class HTTPBridgeAdapter(GeneratorAdapter):
    """
    Generic HTTP bridge adapter for Debian/Linux environments.

    Replaces the Android Tasker bridge. Accepts one POST request,
    extracts the Hypothesis payload, and returns it to the kernel.

    host: interface to bind (default '127.0.0.1' for localhost-only)
    port: TCP port to listen on (default 8080)
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.host = host
        self.port = port

    def propose(self) -> Hypothesis:
        received = {}

        class _Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
                received.update(json.loads(body))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"received"}')

            def log_message(self, *args):  # suppress access log noise
                pass

        server = HTTPServer((self.host, self.port), _Handler)
        print(f"[HTTPBridgeAdapter] Waiting for POST on {self.host}:{self.port} ...")
        server.handle_request()
        server.server_close()

        return Hypothesis(**received)


# Keep the old name as an alias so any existing references don't break
TaskerBridgeAdapter = HTTPBridgeAdapter
