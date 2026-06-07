#!/usr/bin/env python3
"""
test_routing_proxy.py — unit tests for routing_proxy internals

Tests cover:
  - _extract_cache_key: empty-system-message cache collision guard (P0 fix)
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(__file__))


def _make_raw_body(messages: list) -> bytes:
    return json.dumps({"messages": messages}).encode("utf-8")


class TestExtractCacheKey(unittest.TestCase):
    """_extract_cache_key must not return a hash when no non-empty system message exists.

    Without this guard all system-prompt-free requests collide on the same
    empty-string SHA-256 — a slot save from one call would corrupt a different
    call's state via a spurious restore.
    """

    def setUp(self):
        import routing_proxy as rp
        self.rp = rp
        self._orig_kv = rp._kv_cache
        mock = MagicMock()
        mock.cache_key.return_value = "abc123"
        rp._kv_cache = mock

    def tearDown(self):
        self.rp._kv_cache = self._orig_kv

    def test_no_messages_returns_none_key(self):
        raw = _make_raw_body([])
        key, body = self.rp._extract_cache_key(raw)
        self.assertIsNone(key)
        self.assertIsNotNone(body)

    def test_only_user_message_returns_none_key(self):
        raw = _make_raw_body([{"role": "user", "content": "hello"}])
        key, body = self.rp._extract_cache_key(raw)
        self.assertIsNone(key)
        self.assertIsNotNone(body)

    def test_empty_string_system_content_returns_none_key(self):
        raw = _make_raw_body([{"role": "system", "content": ""}])
        key, body = self.rp._extract_cache_key(raw)
        self.assertIsNone(key)
        self.assertIsNotNone(body)

    def test_whitespace_only_system_content_returns_none_key(self):
        raw = _make_raw_body([{"role": "system", "content": "   "}])
        key, body = self.rp._extract_cache_key(raw)
        self.assertIsNone(key)
        self.assertIsNotNone(body)

    def test_no_system_message_does_not_call_cache_key(self):
        raw = _make_raw_body([{"role": "user", "content": "ping"}])
        self.rp._extract_cache_key(raw)
        self.rp._kv_cache.cache_key.assert_not_called()

    def test_non_empty_system_message_returns_key(self):
        raw = _make_raw_body([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"},
        ])
        key, body = self.rp._extract_cache_key(raw)
        self.assertEqual(key, "abc123")
        self.assertIsNotNone(body)

    def test_kv_cache_none_returns_none_none(self):
        self.rp._kv_cache = None
        raw = _make_raw_body([{"role": "system", "content": "sys"}])
        key, body = self.rp._extract_cache_key(raw)
        self.assertIsNone(key)
        self.assertIsNone(body)

    def test_invalid_json_returns_none_none(self):
        key, body = self.rp._extract_cache_key(b"not json at all")
        self.assertIsNone(key)
        self.assertIsNone(body)


if __name__ == "__main__":
    unittest.main()
