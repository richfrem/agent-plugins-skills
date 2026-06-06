#!/usr/bin/env python3
"""
routing_proxy.py (CLI)
=====================================

Purpose:
    Global routing proxy for all local LLM CLI bridges. Intercepts requests
    on port 4000 and dispatches by model ID and endpoint:

    POST /v1/messages (Anthropic protocol):
      - claude-*      → transparent passthrough to Anthropic API (real key forwarded)
      - claude-local  → local llama-server :8089/v1/messages
      - gemma-* / *   → local llama-server :8089/v1/messages (strips thinking + temperature)

    POST /v1/chat/completions (OpenAI protocol):
      - gemma-*, local-*, claude-local → local llama-server :8089/v1/chat/completions
      - cloud models  → 501 Not Implemented

    GET /v1/models:
      - Fetches Anthropic model list, prepends gemma-4-12b so all CLI tools
        accept the local model at validation time.

    Both paths are pure relays — no format translation. llama-server speaks
    both Anthropic Messages API and OpenAI Chat Completions API natively.

    KV Cache Orchestrator (June 2026):
    Inspired by antirez/ds4's ds4_kvstore.c — SHA-keyed disk-persistent
    KV cache management with hit-frequency tracking and budget-based eviction.
    Before forwarding local requests, the proxy checks for a cached KV state
    matching the system prompt hash. On hit, it restores the slot from disk
    (~instant) instead of re-prefilling (~minutes). On miss, it saves the
    slot state after the response completes (background thread).

Layer: Infrastructure / Proxy

Usage Examples:
    python3 routing_proxy.py
    python3 routing_proxy.py --local-only
    python3 routing_proxy.py --port 4001

Supported Object Types:
    None

CLI Arguments:
    --local-only: Route ALL requests to local llama-server (ignore model name)
    --port: Port to listen on (default: 4001 if --local-only, else 4000)

Input Files:
    None

Output:
    Standard HTTP response streams, console logs

Key Functions:
    RoutingProxy.do_GET(): Handle GET /v1/models to expose local model info
    RoutingProxy.do_POST(): Handle POST /v1/messages and /v1/chat/completions
    RoutingProxy._route_to_local(): Strip thinking params and forward to llama-server
    RoutingProxy._route_to_local_openai(): Forward OpenAI-format request to llama-server
    RoutingProxy._forward_to_anthropic(): Forward request to Anthropic cloud

Script Dependencies:
    urllib, http.server, json, socketserver, ssl, threading

Consumed by:
    run_claude.py, run_copilot.py, run_agy.py, run_codex.py
    Claude Code, GitHub Copilot CLI, Antigravity, Aider, Goose, and any
    OpenAI-compatible CLI client routed through ANTHROPIC_BASE_URL or OPENAI_BASE_URL
"""

import json
import os
import socket
import sys
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import ssl
from typing import Any

_SSL_CONTEXT = ssl._create_unverified_context()

LLAMA_SERVER_URL: str = "http://localhost:8089/v1/messages"
ANTHROPIC_API_URL: str = "https://api.anthropic.com/v1/messages"
LOCAL_MODEL: str = "gemma-4-12b"

# Hop-by-hop headers must not be forwarded between proxy hops (RFC 7230)
_HOP_HEADERS: set[str] = {
    "transfer-encoding", "connection", "keep-alive",
    "proxy-authenticate", "proxy-authorization", "te", "trailers", "upgrade",
}


# ---------------------------------------------------------------------------
# KV Cache Orchestrator (antirez/ds4-inspired)
# ---------------------------------------------------------------------------
# Lazy-init: only created if kv_cache_orchestrator module is available and
# --slot-save-path is configured on llama-server. Gracefully degrades to
# no-op if the module is missing or the cache dir doesn't exist.
_kv_cache = None

def _init_kv_cache() -> None:
    """Attempt to initialize the KV cache orchestrator. No-op on failure."""
    global _kv_cache
    cache_dir = os.path.expanduser("~/.claude/proxy/kv_cache")
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        from kv_cache_orchestrator import KVCacheOrchestrator
        os.makedirs(cache_dir, exist_ok=True)
        _kv_cache = KVCacheOrchestrator(
            cache_dir=cache_dir,
            llama_base_url="http://localhost:8089",
            budget_bytes=4 * 1024 * 1024 * 1024,  # 4 GB disk budget
            quant_config={"ctk": "q8_0", "ctv": "q8_0"},  # matches run_server.py -ctk/-ctv
        )
        print(f"[kv-cache] Orchestrator initialized (dir={cache_dir}, budget=4GB)")
    except ImportError:
        print("[kv-cache] kv_cache_orchestrator.py not found — running without cache")
    except Exception as e:
        print(f"[kv-cache] Init failed: {e} — running without cache")


def _extract_cache_key(raw_body: bytes) -> tuple[str | None, dict | None]:
    """Extract system messages from request body and compute cache key.

    Returns (cache_key, parsed_body) or (None, None) on failure.
    """
    if _kv_cache is None:
        return None, None
    try:
        body = json.loads(raw_body.decode("utf-8"))
        messages = body.get("messages", [])
        if not messages:
            return None, body
        key = _kv_cache.cache_key(messages)
        return key, body
    except Exception:
        return None, None


def _try_restore(key: str) -> bool:
    """Attempt to restore a cached KV slot. Returns True on hit."""
    if _kv_cache is None or key is None:
        return False
    if _kv_cache.check_cache(key):
        success = _kv_cache.restore_slot(key)
        if success:
            print(f"[kv-cache] HIT {key[:8]}... restoring slot")
            return True
        else:
            print(f"[kv-cache] HIT {key[:8]}... restore FAILED, treating as miss")
    return False


def _estimate_tokens(parsed_body: dict | None) -> int:
    """Rough token count from message content (4 chars ≈ 1 token). Handles str and part arrays."""
    if not parsed_body:
        return 0
    total = 0
    for m in parsed_body.get("messages", []):
        content = m.get("content", "")
        if isinstance(content, str):
            total += len(content)
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict):
                    total += len(str(part.get("text", "")))
    return max(total // 4, 1)


def _save_in_background(key: str, tokens: int = 0) -> None:
    """Save KV slot to disk in a background thread (non-blocking)."""
    if _kv_cache is None or key is None:
        return
    def _do_save():
        success = _kv_cache.save_slot(key, tokens=tokens)
        if success:
            print(f"[kv-cache] MISS {key[:8]}... saved")
        else:
            print(f"[kv-cache] MISS {key[:8]}... save FAILED")
    threading.Thread(target=_do_save, daemon=True).start()


# Routes /v1/messages by model ID to Anthropic API or local llama-server
class RoutingProxy(BaseHTTPRequestHandler):
    """
    HTTP request handler that routes Anthropic API requests by model name.

    Handles POST /v1/messages only. Both claude-* and gemma-* paths are
    pure transparent relays — no format translation needed since llama-server
    speaks native Anthropic Messages API.
    """

    # Required for Claude Code's Node.js HTTP client — without HTTP/1.1, the
    # client closes keep-alive connections before SSE headers are sent (BrokenPipeError)
    protocol_version = "HTTP/1.1"

    # Suppress default access log; emit a structured line with model and destination
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        """Log each request with model name and resolved destination."""
        model = getattr(self, "_last_model", "?")
        dest = "local" if not model.startswith("claude-") else "anthropic"
        print(f"[proxy] {self.command} {self.path} model={model} → {dest}")

    # Handle GET requests — /v1/models returns merged list so Claude Code accepts gemma-4-12b
    def do_GET(self) -> None:
        """
        Handle GET /v1/models.

        Fetches the real Anthropic models list and injects gemma-4-12b so
        Claude Code's model validation accepts the local model at launch time.
        Falls back to a minimal static list if Anthropic is unreachable.
        """
        path_clean = self.path.split("?")[0]
        if path_clean != "/v1/models":
            self.send_error(404, "Only /v1/models and POST /v1/messages are supported")
            return

        api_key = self.headers.get("x-api-key", "")
        try:
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/models",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": self.headers.get("anthropic-version", "2023-06-01"),
                },
            )
            response = urllib.request.urlopen(req, context=_SSL_CONTEXT)
            models_data: dict[str, Any] = json.loads(response.read().decode("utf-8"))
        except Exception:
            models_data = {"data": [], "has_more": False, "first_id": None, "last_id": None}

        # Prepend local Gemma model so Claude Code sees it as valid
        local_entry: dict[str, Any] = {
            "type": "model",
            "id": LOCAL_MODEL,
            "display_name": "Gemma 4 12B (Local GPU)",
            "created_at": "2026-01-01T00:00:00Z",
        }
        models_data["data"] = [local_entry] + models_data.get("data", [])

        body = json.dumps(models_data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # Entry point for all POST requests — parse body and dispatch by model
    def do_POST(self) -> None:
        """
        Handle POST /v1/messages and /v1/chat/completions.

        Reads and parses the request body, extracts the model field,
        and dispatches to the corresponding endpoint or protocol handler.
        """
        path_clean = self.path.split("?")[0]
        if path_clean not in ("/v1/messages", "/v1/chat/completions"):
            self.send_error(404, f"Supported endpoints are /v1/messages and /v1/chat/completions. Got: {self.path}")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)

        try:
            req_body: dict[str, Any] = json.loads(raw_body.decode("utf-8"))
        except Exception as e:
            self.send_error(400, f"Invalid JSON: {e}")
            return

        model: str = req_body.get("model", "")
        self._last_model = model

        if path_clean == "/v1/chat/completions":
            # Sanitize the model parameter to match the local model expected by llama-server
            if model != LOCAL_MODEL:
                req_body["model"] = LOCAL_MODEL
                raw_body = json.dumps(req_body).encode("utf-8")
            self._route_to_local_openai(raw_body)
        # claude-local is a built-in Claude Code model alias (hardcoded in binary)
        # Route it to the local llama-server instead of Anthropic
        elif model.startswith("claude-local"):
            self._route_to_local(raw_body)
        elif model.startswith("claude-"):
            self._forward_to_anthropic(raw_body)
        else:
            self._route_to_local(raw_body)

    # ------------------------------------------------------------------ #
    # Anthropic passthrough                                                #
    # ------------------------------------------------------------------ #

    # Forward the raw request to Anthropic, preserving headers and streaming body back
    def _forward_to_anthropic(self, raw_body: bytes) -> None:
        """Transparently relay the request to the Anthropic API."""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.headers.get("x-api-key", ""),
            "anthropic-version": self.headers.get("anthropic-version", "2023-06-01"),
        }
        # Beta flags enable prompt caching, extended tool use, etc.
        if "anthropic-beta" in self.headers:
            headers["anthropic-beta"] = self.headers["anthropic-beta"]

        req = urllib.request.Request(
            ANTHROPIC_API_URL, data=raw_body, headers=headers, method="POST"
        )

        try:
            response = urllib.request.urlopen(req, context=_SSL_CONTEXT)
        except urllib.error.HTTPError as e:
            error_body = e.read()
            self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() not in _HOP_HEADERS:
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(error_body)
            return
        except Exception as e:
            self.send_error(502, f"Anthropic API unreachable: {e}")
            return

        self.send_response(response.status)
        for k, v in response.headers.items():
            if k.lower() not in _HOP_HEADERS:
                self.send_header(k, v)
        self.end_headers()

        try:
            while True:
                line = response.readline()
                if not line:
                    break
                self.wfile.write(line)
                self.wfile.flush()
        except BrokenPipeError:
            pass

    # ------------------------------------------------------------------ #
    # Local llama-server passthrough — WITH cache orchestration            #
    # ------------------------------------------------------------------ #

    # Forward the Anthropic request to llama-server — stripping thinking parameters
    def _route_to_local(self, raw_body: bytes) -> None:
        """Relay the request to the local llama-server, with KV cache restore/save."""
        # --- KV cache: extract key and attempt restore ---
        cache_key, parsed_body = _extract_cache_key(raw_body)
        kv_hit = _try_restore(cache_key)

        try:
            body = json.loads(raw_body.decode("utf-8"))
            body.pop("thinking", None)  # Claude Code sends this unconditionally
            # Pop temperature if it is default 1 to prevent template confusion
            if body.get("temperature", 1.0) == 1.0:
                body.pop("temperature", None)
            sanitized_body = json.dumps(body).encode("utf-8")
        except Exception:
            sanitized_body = raw_body

        req = urllib.request.Request(
            LLAMA_SERVER_URL,
            data=sanitized_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            error_body = e.read()
            self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() not in _HOP_HEADERS:
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(error_body)
            return
        except OSError:
            self._send_local_offline_error()
            return

        self.send_response(response.status)
        for k, v in response.headers.items():
            if k.lower() not in _HOP_HEADERS:
                self.send_header(k, v)
        self.send_header("Connection", "close")
        self.end_headers()

        try:
            while True:
                line = response.readline()
                if not line:
                    break
                self.wfile.write(line)
                self.wfile.flush()
        except BrokenPipeError:
            pass

        # --- KV cache: save on miss (background, non-blocking) ---
        if not kv_hit and cache_key:
            _save_in_background(cache_key, tokens=_estimate_tokens(parsed_body))

    def _route_to_local_openai(self, raw_body: bytes) -> None:
        """Relay OpenAI Chat Completions requests to llama-server, with KV cache."""
        llama_openai_url = "http://localhost:8089/v1/chat/completions"

        # --- KV cache: extract key and attempt restore ---
        cache_key, parsed_body = _extract_cache_key(raw_body)
        kv_hit = _try_restore(cache_key)

        req = urllib.request.Request(
            llama_openai_url,
            data=raw_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            error_body = e.read()
            self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() not in _HOP_HEADERS:
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(error_body)
            return
        except OSError:
            self._send_local_offline_error()
            return

        self.send_response(response.status)
        for k, v in response.headers.items():
            if k.lower() not in _HOP_HEADERS:
                self.send_header(k, v)
        self.send_header("Connection", "close")
        self.end_headers()

        try:
            while True:
                line = response.readline()
                if not line:
                    break
                self.wfile.write(line)
                self.wfile.flush()
        except BrokenPipeError:
            pass

        # --- KV cache: save on miss (background, non-blocking) ---
        if not kv_hit and cache_key:
            _save_in_background(cache_key, tokens=_estimate_tokens(parsed_body))

    # Emit a 503 with start instructions when the local server is unreachable
    def _send_local_offline_error(self) -> None:
        """Send a format-aware 503 error when llama-server is unreachable."""
        msg = (
            "Local llama-server is offline (port 8089). "
            "Start it with: python3 run_server.py  (or ./run_server.sh in local-llm-bench)"
        )
        path_clean = self.path.split("?")[0]
        if path_clean == "/v1/chat/completions":
            error_data = {
                "error": {
                    "message": msg,
                    "type": "api_error",
                    "param": None,
                    "code": None
                }
            }
            error_body = json.dumps(error_data).encode("utf-8")
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(error_body)))
            self.end_headers()
            self.wfile.write(error_body)
        else:
            error_data = {
                "type": "error",
                "error": {"type": "api_error", "message": msg},
            }
            error_body = json.dumps(error_data).encode("utf-8")
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(error_body)))
            self.end_headers()
            self.wfile.write(error_body)


# Probe llama-server health at proxy startup to surface online/offline status early
def _check_llama_server() -> bool:
    try:
        urllib.request.urlopen("http://localhost:8089/health", timeout=2)
        return True
    except Exception:
        return False


# Start the routing proxy HTTP server and log initial llama-server status
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle each request in a dedicated thread — avoids HEAD/keepalive blocking streaming."""
    daemon_threads = True


def _port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def run_server(port: int = 4000) -> None:
    # Initialize KV cache orchestrator (graceful degradation if unavailable)
    _init_kv_cache()

    if _port_in_use(port):
        print(f"[Routing Proxy] Port {port} is already in use.")
        print(f"  The proxy is likely already running (launchd daemon or another session).")
        print(f"  Check with:  lsof -i :{port}")
        print(f"  Proxy logs:  tail -f ~/.claude/proxy/logs/proxy.log")
        sys.exit(0)

    httpd = ThreadedHTTPServer(("localhost", port), RoutingProxy)
    print(f"[Routing Proxy] Listening on http://localhost:{port}")
    print(f"  claude-*           → Anthropic API  (api.anthropic.com)")
    print(f"  gemma-* /v1/messages        → llama-server :8089/v1/messages  (Anthropic protocol)")
    print(f"  gemma-* /v1/chat/completions → llama-server :8089/v1/chat/completions  (OpenAI protocol)")

    status = "ONLINE ✓" if _check_llama_server() else "OFFLINE — gemma requests return 503 until started"
    print(f"  llama-server status: {status}")
    print()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Routing Proxy] Stopped.")
        sys.exit(0)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Claude Code routing proxy")
    parser.add_argument("--local-only", action="store_true",
                        help="Route ALL requests to local llama-server (ignore model name)")
    parser.add_argument("--port", type=int, default=None,
                        help="Port to listen on (default: 4001 if --local-only, else 4000)")
    args = parser.parse_args()

    port = args.port or (4001 if args.local_only else 4000)

    if args.local_only:
        # Patch dispatch so every request goes to local regardless of model
        def _local_only_do_POST(self: RoutingProxy) -> None:
            path_clean = self.path.split("?")[0]
            if path_clean not in ("/v1/messages", "/v1/chat/completions"):
                self.send_error(404, f"Supported endpoints are /v1/messages and /v1/chat/completions. Got: {self.path}")
                return
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length)
            try:
                req_body: dict[str, Any] = json.loads(raw_body.decode("utf-8"))
            except Exception as e:
                self.send_error(400, f"Invalid JSON: {e}")
                return
            self._last_model = req_body.get("model", "?")
            if path_clean == "/v1/chat/completions":
                self._route_to_local_openai(raw_body)
            else:
                self._route_to_local(raw_body)
        RoutingProxy.do_POST = _local_only_do_POST  # type: ignore[method-assign]

    run_server(port)
