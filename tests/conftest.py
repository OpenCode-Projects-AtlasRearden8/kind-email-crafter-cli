"""Shared test fixtures: a local mocked OpenAI-compatible endpoint."""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest


class _MockHandler(BaseHTTPRequestHandler):
    reply_content = None
    status = 200
    behave_badly = False

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)
        if self.behave_badly:
            out = b"not json at all"
        elif self.reply_content is None:
            out = json.dumps({"choices": []}).encode()
        else:
            out = json.dumps(
                {"choices": [{"message": {"content": self.reply_content}}]}
            ).encode()
        self.send_response(self.status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *args):
        pass


class _EndpointHandle:
    def __init__(self, handler_attrs):
        handler = type("EndpointHandler", (_MockHandler,), dict(handler_attrs))
        self.server = HTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    @property
    def base_url(self):
        return f"http://127.0.0.1:{self.server.server_port}/v1"

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


@pytest.fixture
def make_endpoint():
    handles = []

    def _make(**handler_attrs):
        handle = _EndpointHandle(handler_attrs)
        handles.append(handle)
        return handle

    yield _make
    for handle in handles:
        handle.close()


@pytest.fixture
def good_endpoint(make_endpoint):
    return make_endpoint(
        reply_content=(
            "Hi Pat,\n\nThank you for waiting so kindly.\n\nAll the best,\nMe\n"
            "\n--- SHORT VARIANT ---\nHi Pat,\n\nShort thanks.\n\nAll the best,\nMe"
        )
    )


@pytest.fixture
def broken_endpoint(make_endpoint):
    return make_endpoint(status=500)


@pytest.fixture
def nonsense_endpoint(make_endpoint):
    return make_endpoint(behave_badly=True)
