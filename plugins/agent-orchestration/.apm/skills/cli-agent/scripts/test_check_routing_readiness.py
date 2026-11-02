#!/usr/bin/env python3
"""Tests for check_routing_readiness.py probe script."""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(__file__))

import check_routing_readiness as crr


class TestCheckRoutingReadiness(unittest.TestCase):

    def test_check_env_redirects_default_empty(self):
        with patch.dict(os.environ, {}, clear=True):
            res = crr.check_env_redirects()
            self.assertFalse(res["is_routed"])
            self.assertEqual(res["ANTHROPIC_BASE_URL"], "Not set (direct cloud API)")

    def test_check_env_redirects_active(self):
        with patch.dict(os.environ, {"ANTHROPIC_BASE_URL": "http://localhost:4000"}, clear=True):
            res = crr.check_env_redirects()
            self.assertTrue(res["is_routed"])
            self.assertEqual(res["ANTHROPIC_BASE_URL"], "http://localhost:4000")

    def test_check_cli_binaries(self):
        res = crr.check_cli_binaries()
        self.assertIn("claude", res)
        self.assertIn("codex", res)
        self.assertIn("agy", res)
        self.assertIn("copilot", res)
        self.assertIn("subscription", res["claude"])

    @patch("check_routing_readiness.probe_http_gateway")
    @patch("check_routing_readiness.check_cli_binaries")
    def test_evaluate_routing_readiness_active_proxy(self, mock_binaries, mock_gateway):
        mock_gateway.return_value = {"port": 4000, "status": "ACTIVE", "details": "mocked active"}
        mock_binaries.return_value = {
            "claude": {"installed": True, "path": "/path/claude", "subscription": "Claude Pro"},
            "codex": {"installed": True, "path": "/path/codex", "subscription": "ChatGPT Plus"},
            "agy": {"installed": True, "path": "/path/agy", "subscription": "Gemini Pro"},
            "copilot": {"installed": False, "path": None, "subscription": "Copilot"}
        }

        res = crr.evaluate_routing_readiness(port=4000)
        self.assertEqual(res["posture"], "LOCAL_PROXY_ACTIVE")
        self.assertEqual(len(res["active_cloud_subscriptions"]), 3)
        self.assertIn("Apple Silicon (M1/M2/M3) Optimized", res["hardware_profile"])


if __name__ == "__main__":
    unittest.main()
