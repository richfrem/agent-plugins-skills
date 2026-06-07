#!/usr/bin/env python3
"""
test_run_agent.py — unit tests for the multi-LLM task router

Tests cover:
  - Prompt assembly (build_prompt)
  - Command builders for each CLI backend (including isolated= security contract)
  - Default model table completeness
  - llama HTTP payload structure and max_tokens default
  - LLAMA_SERVER_URL constant
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(__file__))
from run_agent import (
    _DEFAULT_MODELS,
    _LLAMA_MAX_TOKENS_DEFAULT,
    _LLAMA_SERVER_URL,
    _build_cmd_agy,
    _build_cmd_claude,
    _build_cmd_codex,
    _build_cmd_copilot,
    _build_cmd_gemini,
    _call_llama_direct,
    build_prompt,
)


# ── Prompt assembly ───────────────────────────────────────────────────────────

class TestBuildPrompt(unittest.TestCase):

    def test_instruction_only(self):
        result = build_prompt("", "", "Do this.", False)
        self.assertIn("Do this.", result)
        self.assertNotIn("---SOURCE---", result)
        self.assertNotIn("---INSTRUCTION---", result)

    def test_source_plus_instruction(self):
        result = build_prompt("", "Source content", "Do this.", False)
        self.assertIn("Source content", result)
        self.assertIn("---INSTRUCTION---", result)
        self.assertNotIn("---SOURCE---", result)

    def test_persona_plus_instruction(self):
        result = build_prompt("You are a reviewer.", "", "Do this.", False)
        self.assertIn("You are a reviewer.", result)
        self.assertIn("---INSTRUCTION---", result)

    def test_all_parts(self):
        result = build_prompt("Persona", "Source", "Instruction", False)
        self.assertIn("Persona", result)
        self.assertIn("---SOURCE---", result)
        self.assertIn("Source", result)
        self.assertIn("---INSTRUCTION---", result)
        self.assertIn("Instruction", result)

    def test_isolated_footer_appended(self):
        result = build_prompt("", "", "Do this.", True)
        self.assertIn("isolated sub-agent", result)

    def test_no_isolated_footer_when_false(self):
        result = build_prompt("", "", "Do this.", False)
        self.assertNotIn("isolated sub-agent", result)


# ── Default model table ───────────────────────────────────────────────────────

class TestDefaultModels(unittest.TestCase):

    ALL_BACKENDS = ("copilot", "gemini", "claude", "agy", "codex", "llama")

    def test_all_six_backends_present(self):
        for backend in self.ALL_BACKENDS:
            self.assertIn(backend, _DEFAULT_MODELS, f"Missing backend: {backend}")

    def test_llama_default_is_gemma(self):
        self.assertEqual(_DEFAULT_MODELS["llama"], "gemma-4-12b")

    def test_codex_default_set(self):
        self.assertIsNotNone(_DEFAULT_MODELS["codex"])

    def test_agy_default_is_none(self):
        self.assertIsNone(_DEFAULT_MODELS["agy"])


# ── Command builders ──────────────────────────────────────────────────────────

class TestCommandBuilders(unittest.TestCase):

    def test_copilot_includes_model_and_file_ref(self):
        cmd = _build_cmd_copilot("gpt-5-mini", "/tmp/prompt.txt")
        self.assertIn("copilot", cmd)
        self.assertIn("gpt-5-mini", cmd)
        self.assertTrue(any("prompt.txt" in arg for arg in cmd))

    def test_copilot_file_ref_has_at_prefix_on_posix(self):
        if sys.platform != "win32":
            cmd = _build_cmd_copilot("gpt-5-mini", "/tmp/prompt.txt")
            self.assertIn("@/tmp/prompt.txt", cmd)

    def test_copilot_includes_yolo_when_not_isolated(self):
        if sys.platform != "win32":
            cmd = _build_cmd_copilot("gpt-5-mini", "/tmp/prompt.txt", isolated=False)
            self.assertIn("--yolo", cmd)

    def test_copilot_excludes_yolo_when_isolated(self):
        if sys.platform != "win32":
            cmd = _build_cmd_copilot("gpt-5-mini", "/tmp/prompt.txt", isolated=True)
            self.assertNotIn("--yolo", cmd)

    def test_gemini_with_gemini_binary(self):
        with patch("shutil.which", return_value="/usr/bin/gemini"):
            cmd = _build_cmd_gemini("gemini-flash", "hello world")
        self.assertIn("gemini", cmd[0])
        self.assertIn("gemini-flash", cmd)
        self.assertIn("hello world", cmd)

    def test_gemini_falls_back_to_npx_when_no_binary(self):
        def _which(name: str) -> str | None:
            return None if name == "gemini" else "/usr/bin/npx"
        with patch("shutil.which", side_effect=_which):
            cmd = _build_cmd_gemini("gemini-flash", "hello")
        self.assertIn("npx", cmd)
        self.assertIn("@google/gemini-cli@latest", " ".join(cmd))

    def test_gemini_excludes_yolo_when_isolated(self):
        with patch("shutil.which", return_value="/usr/bin/gemini"):
            cmd = _build_cmd_gemini("gemini-flash", "hello", isolated=True)
        self.assertNotIn("--yolo", cmd)

    def test_agy_includes_file_ref(self):
        cmd = _build_cmd_agy("/tmp/prompt.txt")
        self.assertIn("agy", cmd)
        self.assertTrue(any("prompt.txt" in arg for arg in cmd))

    def test_agy_includes_dangerous_flag_when_not_isolated(self):
        cmd = _build_cmd_agy("/tmp/prompt.txt", isolated=False)
        self.assertIn("--dangerously-skip-permissions", cmd)

    def test_agy_excludes_dangerous_flag_when_isolated(self):
        cmd = _build_cmd_agy("/tmp/prompt.txt", isolated=True)
        self.assertNotIn("--dangerously-skip-permissions", cmd)

    def test_claude_includes_model_and_prompt(self):
        cmd = _build_cmd_claude("haiku-4.5", "Review this.")
        self.assertIn("claude", cmd)
        self.assertIn("haiku-4.5", cmd)
        self.assertIn("Review this.", cmd)

    def test_claude_includes_dangerous_flag_when_not_isolated(self):
        cmd = _build_cmd_claude("haiku-4.5", "Review this.", isolated=False)
        self.assertIn("--dangerously-skip-permissions", cmd)

    def test_claude_excludes_dangerous_flag_when_isolated(self):
        cmd = _build_cmd_claude("haiku-4.5", "Review this.", isolated=True)
        self.assertNotIn("--dangerously-skip-permissions", cmd)

    def test_codex_includes_model(self):
        cmd = _build_cmd_codex("gpt-5-codex")
        self.assertIn("codex", cmd)
        self.assertIn("gpt-5-codex", cmd)

    def test_codex_includes_exec_subcommand(self):
        cmd = _build_cmd_codex("gpt-5-codex")
        self.assertIn("exec", cmd)
        self.assertNotIn("--quiet", cmd)

    def test_codex_uses_stdin_dash(self):
        cmd = _build_cmd_codex("gpt-5-codex")
        self.assertIn("-", cmd)

    def test_codex_prompt_not_in_command_args(self):
        # Prompt is piped via stdin, NOT passed as a positional arg
        cmd = _build_cmd_codex("gpt-5-codex")
        self.assertNotIn("Refactor this function.", cmd)


# ── llama HTTP payload ────────────────────────────────────────────────────────

class TestLlamaHTTPPayload(unittest.TestCase):

    def _make_mock_response(self, content: str) -> MagicMock:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "choices": [{"message": {"content": content}}]
        }).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    def _capture_payload(self, prompt: str, model: str = "gemma-4-12b",
                         max_tokens: int = _LLAMA_MAX_TOKENS_DEFAULT) -> dict:
        captured: dict = {}

        def fake_urlopen(req, timeout):
            captured["body"] = json.loads(req.data.decode())
            captured["url"] = req.full_url
            return self._make_mock_response("Paris")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            out_path = f.name
        try:
            with patch("urllib.request.urlopen", fake_urlopen):
                _call_llama_direct(prompt, model, out_path, max_tokens=max_tokens)
        finally:
            if os.path.exists(out_path):
                os.unlink(out_path)
        return captured

    def test_url_is_llama_server(self):
        captured = self._capture_payload("Capital of France?")
        self.assertEqual(captured["url"], _LLAMA_SERVER_URL)

    def test_payload_model_field(self):
        captured = self._capture_payload("Capital of France?", model="gemma-4-12b")
        self.assertEqual(captured["body"]["model"], "gemma-4-12b")

    def test_payload_stream_is_false(self):
        captured = self._capture_payload("Capital of France?")
        self.assertIs(captured["body"]["stream"], False)

    def test_payload_default_max_tokens(self):
        captured = self._capture_payload("Capital of France?")
        self.assertEqual(captured["body"]["max_tokens"], _LLAMA_MAX_TOKENS_DEFAULT)

    def test_payload_custom_max_tokens(self):
        captured = self._capture_payload("Capital of France?", max_tokens=50)
        self.assertEqual(captured["body"]["max_tokens"], 50)

    def test_payload_user_message_role(self):
        captured = self._capture_payload("Capital of France?")
        messages = captured["body"]["messages"]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["role"], "user")

    def test_payload_user_message_content(self):
        captured = self._capture_payload("Capital of France?")
        self.assertIn("France", captured["body"]["messages"][0]["content"])

    def test_output_written_to_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            out_path = f.name
        try:
            with patch("urllib.request.urlopen", lambda req, timeout: self._make_mock_response("Paris")):
                _call_llama_direct("Capital of France?", "gemma-4-12b", out_path)
            with open(out_path) as f:
                self.assertEqual(f.read(), "Paris")
        finally:
            if os.path.exists(out_path):
                os.unlink(out_path)


# ── Constants ─────────────────────────────────────────────────────────────────

class TestConstants(unittest.TestCase):

    def test_llama_server_url(self):
        self.assertEqual(_LLAMA_SERVER_URL, "http://localhost:8089/v1/chat/completions")

    def test_llama_max_tokens_default(self):
        self.assertEqual(_LLAMA_MAX_TOKENS_DEFAULT, 120)


if __name__ == "__main__":
    unittest.main()
