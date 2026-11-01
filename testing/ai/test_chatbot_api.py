"""HTTP API tests for the application-facing RetailAI chatbot."""

import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

from application.backend.chatbot import api


class ChatbotApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), api.ChatbotRequestHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def post(self, payload=None, raw=None):
        data = raw if raw is not None else json.dumps(payload).encode("utf-8")
        request = Request(
            self.base_url + "/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=3) as response:
                return response.status, json.loads(response.read())
        except HTTPError as error:
            return error.code, json.loads(error.read())

    def test_health_endpoint(self):
        with urlopen(self.base_url + "/api/health", timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.loads(response.read())["status"], "ok")

    def test_frontend_is_served(self):
        with urlopen(self.base_url + "/", timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get_content_type(), "text/html")
            self.assertIn(b"RetailAI Chatbot", response.read())

    def test_chat_routes_to_existing_service(self):
        expected = {"intent": "GREETING", "response": "Hello", "integration": {"live_data_connected": False}}
        with patch.object(api, "process_project_message", return_value=expected) as service:
            status, result = self.post({"message": "Hello"})
        self.assertEqual(status, 200)
        self.assertEqual(result, expected)
        service.assert_called_once_with("Hello")

    def test_invalid_json_is_rejected(self):
        status, result = self.post(raw=b"{invalid")
        self.assertEqual(status, 400)
        self.assertIn("valid JSON", result["error"])

    def test_invalid_messages_are_rejected(self):
        for payload in ({}, {"message": ""}, {"message": "   "}, {"message": 123}):
            with self.subTest(payload=payload):
                status, result = self.post(payload)
                self.assertEqual(status, 400)
                self.assertIn("message", result["error"].lower())

    def test_unknown_endpoint_returns_404(self):
        with self.assertRaises(HTTPError) as caught:
            urlopen(self.base_url + "/api/unknown", timeout=3)
        self.assertEqual(caught.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
