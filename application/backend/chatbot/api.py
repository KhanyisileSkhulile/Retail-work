"""HTTP API for the RetailAI chatbot."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .service import process_project_message

REPO_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_FILE = REPO_ROOT / "application" / "frontend" / "index.html"
MAX_REQUEST_BYTES = 1_000_000


class ChatbotRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        if self.path == "/api/health":
            self._send_json(200, {"status": "ok", "service": "RetailAI chatbot"})
            return

        if self.path == "/":
            try:
                content = FRONTEND_FILE.read_bytes()
            except OSError:
                self._send_json(500, {"error": "Chatbot frontend is unavailable."})
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(content)
            return

        self._send_json(404, {"error": "Endpoint not found."})

    def do_POST(self):
        if self.path != "/api/chat":
            self._send_json(404, {"error": "Endpoint not found."})
            return

        try:
            length = int(self.headers.get("Content-Length", "-1"))
        except ValueError:
            length = -1

        if length < 0:
            self._send_json(400, {"error": "A valid Content-Length is required."})
            return
        if length > MAX_REQUEST_BYTES:
            self._send_json(413, {"error": "Request body is too large."})
            return

        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "Request body must contain valid JSON."})
            return

        if not isinstance(payload, dict):
            self._send_json(400, {"error": "Request body must be a JSON object."})
            return

        message = payload.get("message")
        if not isinstance(message, str) or not message.strip():
            self._send_json(400, {"error": "A non-empty message is required."})
            return
        if len(message) > 10_000:
            self._send_json(413, {"error": "Message is too long."})
            return

        try:
            result = process_project_message(message.strip())
            if not isinstance(result, dict) or not isinstance(result.get("response"), str):
                raise ValueError("Unexpected chatbot response format.")
            self._send_json(200, result)
        except Exception:
            self._send_json(500, {"error": "The chatbot could not process your message."})

    def log_message(self, format_string, *args):
        pass


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8000), ChatbotRequestHandler)
    print("RetailAI chatbot running at http://127.0.0.1:8000")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping RetailAI chatbot...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
