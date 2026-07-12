#!/usr/bin/env python3
"""
test_run_agent.py — unit tests for the multi-LLM task router

Purpose:
    Tests cover:
      - Prompt assembly (build_prompt)
      - Command builders for each CLI backend (including isolated= security contract)
      - Default model table completeness
      - llama HTTP payload structure and max_tokens default
      - LLAMA_SERVER_URL constant

Key Input Dependencies:
    - run_agent.py module (in the same directory)
    - references/cheapest_models.json (optional, for the model-parity test)
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, mock_open, patch

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
    _load_default_models,
    build_prompt,
)


# ── Prompt assembly ───────────────────────────────────────────────────────────

class TestBuildPrompt(unittest.TestCase):

    def test_instruction_only(self):
        """Verify an instruction-only prompt omits SOURCE/INSTRUCTION section markers."""
        result = build_prompt("", "", "Do this.", False)
        self.assertIn("Do this.", result)
        self.assertNotIn("---SOURCE---", result)
        self.assertNotIn("---INSTRUCTION---", result)

    def test_source_plus_instruction(self):
        """Verify source + instruction includes an INSTRUCTION marker but no SOURCE marker."""
        result = build_prompt("", "Source content", "Do this.", False)
        self.assertIn("Source content", result)
        self.assertIn("---INSTRUCTION---", result)
        self.assertNotIn("---SOURCE---", result)

    def test_persona_plus_instruction(self):
        """Verify persona + instruction includes the persona text and INSTRUCTION marker."""
        result = build_prompt("You are a reviewer.", "", "Do this.", False)
        self.assertIn("You are a reviewer.", result)
        self.assertIn("---INSTRUCTION---", result)

    def test_all_parts(self):
        """Verify persona + source + instruction includes all section markers and content."""
        result = build_prompt("Persona", "Source", "Instruction", False)
        self.assertIn("Persona", result)
        self.assertIn("---SOURCE---", result)
        self.assertIn("Source", result)
        self.assertIn("---INSTRUCTION---", result)
        self.assertIn("Instruction", result)

    def test_isolated_footer_appended(self):
        """Verify the isolated sub-agent footer is appended when isolated=True."""
        result = build_prompt("", "", "Do this.", True)
        self.assertIn("isolated sub-agent", result)

    def test_no_isolated_footer_when_false(self):
        """Verify the isolated sub-agent footer is absent when isolated=False."""
        result = build_prompt("", "", "Do this.", False)
        self.assertNotIn("isolated sub-agent", result)


# ── Default model table ───────────────────────────────────────────────────────

class TestDefaultModels(unittest.TestCase):

    ALL_BACKENDS = ("copilot", "gemini", "claude", "agy", "codex", "llama")

    def test_all_six_backends_present(self):
        """Verify _DEFAULT_MODELS has an entry for every supported backend."""
        for backend in self.ALL_BACKENDS:
            self.assertIn(backend, _DEFAULT_MODELS, f"Missing backend: {backend}")

    def test_defaults_match_cheapest_models_json(self):
        """Loaded defaults must equal what cheapest_models.json declares.

        When you update cheapest_models.json the test self-updates — no
        model name is hardcoded here.
        """
        script_dir = os.path.dirname(os.path.realpath(__file__))
        ref_path = os.path.join(script_dir, "..", "references", "cheapest_models.json")
        if not os.path.exists(ref_path):
            self.skipTest("cheapest_models.json not present")
        with open(ref_path) as f:
            json_models = json.load(f)
        for engine, info in json_models.items():
            if "model" in info and engine in _DEFAULT_MODELS:
                self.assertEqual(
                    _DEFAULT_MODELS[engine],
                    info["model"],
                    f"{engine} default should match cheapest_models.json",
                )


# ── Command builders ──────────────────────────────────────────────────────────

class TestCommandBuilders(unittest.TestCase):

    def test_copilot_includes_model_and_file_ref(self):
        """Verify the copilot command includes the binary name, model, and prompt file reference."""
        cmd = _build_cmd_copilot("gpt-5-mini", "/tmp/prompt.txt")
        self.assertIn("copilot", cmd)
        self.assertIn("gpt-5-mini", cmd)
        self.assertTrue(any("prompt.txt" in arg for arg in cmd))

    def test_copilot_file_ref_has_at_prefix_on_posix(self):
        """Verify the copilot file reference uses the '@' prefix on POSIX platforms."""
        if sys.platform != "win32":
            cmd = _build_cmd_copilot("gpt-5-mini", "/tmp/prompt.txt")
            self.assertIn("@/tmp/prompt.txt", cmd)

    def test_copilot_includes_yolo_when_not_isolated(self):
        """Verify --yolo is included when isolated=False."""
        if sys.platform != "win32":
            cmd = _build_cmd_copilot("gpt-5-mini", "/tmp/prompt.txt", isolated=False)
            self.assertIn("--yolo", cmd)

    def test_copilot_excludes_yolo_when_isolated(self):
        """Verify --yolo is excluded when isolated=True."""
        if sys.platform != "win32":
            cmd = _build_cmd_copilot("gpt-5-mini", "/tmp/prompt.txt", isolated=True)
            self.assertNotIn("--yolo", cmd)

    def test_gemini_with_gemini_binary(self):
        """Verify the gemini command uses the installed binary when present."""
        with patch("shutil.which", return_value="/usr/bin/gemini"):
            cmd = _build_cmd_gemini("gemini-flash", "hello world")
        self.assertIn("gemini", cmd[0])
        self.assertIn("gemini-flash", cmd)
        self.assertIn("hello world", cmd)

    def test_gemini_falls_back_to_npx_when_no_binary(self):
        """Verify the gemini command falls back to npx when no binary is installed."""
        def _which(name: str) -> str | None:
            """Simulate shutil.which returning npx but not gemini."""
            return None if name == "gemini" else "/usr/bin/npx"
        with patch("shutil.which", side_effect=_which):
            cmd = _build_cmd_gemini("gemini-flash", "hello")
        self.assertIn("npx", cmd)
        self.assertIn("@google/gemini-cli@latest", " ".join(cmd))

    def test_gemini_excludes_yolo_when_isolated(self):
        """Verify --yolo is excluded from the gemini command when isolated=True."""
        with patch("shutil.which", return_value="/usr/bin/gemini"):
            cmd = _build_cmd_gemini("gemini-flash", "hello", isolated=True)
        self.assertNotIn("--yolo", cmd)

    def test_agy_includes_file_ref(self):
        """Verify the agy command includes the binary name and prompt file reference."""
        cmd = _build_cmd_agy("agy-3.5-sonnet", "/tmp/prompt.txt")
        self.assertIn("agy", cmd)
        self.assertTrue(any("prompt.txt" in arg for arg in cmd))

    def test_agy_includes_dangerous_flag_when_not_isolated(self):
        """Verify --dangerously-skip-permissions is included when isolated=False."""
        cmd = _build_cmd_agy("agy-3.5-sonnet", "/tmp/prompt.txt", isolated=False)
        self.assertIn("--dangerously-skip-permissions", cmd)

    def test_agy_excludes_dangerous_flag_when_isolated(self):
        """Verify --dangerously-skip-permissions is excluded when isolated=True."""
        cmd = _build_cmd_agy("agy-3.5-sonnet", "/tmp/prompt.txt", isolated=True)
        self.assertNotIn("--dangerously-skip-permissions", cmd)

    def test_claude_includes_model_and_prompt(self):
        """Verify the claude command includes the binary name, model, and prompt text."""
        cmd = _build_cmd_claude("haiku-4.5", "Review this.")
        self.assertIn("claude", cmd)
        self.assertIn("haiku-4.5", cmd)
        self.assertIn("Review this.", cmd)

    def test_claude_includes_dangerous_flag_when_not_isolated(self):
        """Verify --dangerously-skip-permissions is included when isolated=False."""
        cmd = _build_cmd_claude("haiku-4.5", "Review this.", isolated=False)
        self.assertIn("--dangerously-skip-permissions", cmd)

    def test_claude_excludes_dangerous_flag_when_isolated(self):
        """Verify --dangerously-skip-permissions is excluded when isolated=True."""
        cmd = _build_cmd_claude("haiku-4.5", "Review this.", isolated=True)
        self.assertNotIn("--dangerously-skip-permissions", cmd)

    def test_codex_includes_model(self):
        """Verify the codex command includes the binary name and model."""
        cmd = _build_cmd_codex("gpt-5-codex")
        self.assertIn("codex", cmd)
        self.assertIn("gpt-5-codex", cmd)

    def test_codex_includes_exec_subcommand(self):
        """Verify the codex command uses the 'exec' subcommand, not --quiet."""
        cmd = _build_cmd_codex("gpt-5-codex")
        self.assertIn("exec", cmd)
        self.assertNotIn("--quiet", cmd)

    def test_codex_uses_stdin_dash(self):
        """Verify the codex command includes the '-' stdin marker."""
        cmd = _build_cmd_codex("gpt-5-codex")
        self.assertIn("-", cmd)

    def test_codex_prompt_not_in_command_args(self):
        """Verify the prompt is piped via stdin, not passed as a positional command arg."""
        # Prompt is piped via stdin, NOT passed as a positional arg
        cmd = _build_cmd_codex("gpt-5-codex")
        self.assertNotIn("Refactor this function.", cmd)


# ── llama HTTP payload ────────────────────────────────────────────────────────

class TestLlamaHTTPPayload(unittest.TestCase):

    def _make_mock_response(self, content: str) -> MagicMock:
        """Build a mock HTTP response object mimicking a llama-server chat completion."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "choices": [{"message": {"content": content}}]
        }).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    def _capture_payload(self, prompt: str, model: str = "gemma-4-12b",
                         max_tokens: int = _LLAMA_MAX_TOKENS_DEFAULT) -> dict:
        """Call _call_llama_direct with a mocked urlopen and capture the request body/URL."""
        captured: dict = {}

        def fake_urlopen(req, timeout):
            """Capture the outgoing request body and URL, then return a mock response."""
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
        """Verify the request URL matches the configured llama-server endpoint."""
        captured = self._capture_payload("Capital of France?")
        self.assertEqual(captured["url"], _LLAMA_SERVER_URL)

    def test_payload_model_field(self):
        """Verify the request payload's model field matches the passed model."""
        captured = self._capture_payload("Capital of France?", model="gemma-4-12b")
        self.assertEqual(captured["body"]["model"], "gemma-4-12b")

    def test_payload_stream_is_false(self):
        """Verify the request payload disables streaming."""
        captured = self._capture_payload("Capital of France?")
        self.assertIs(captured["body"]["stream"], False)

    def test_payload_default_max_tokens(self):
        """Verify the request payload uses the default max_tokens when not overridden."""
        captured = self._capture_payload("Capital of France?")
        self.assertEqual(captured["body"]["max_tokens"], _LLAMA_MAX_TOKENS_DEFAULT)

    def test_payload_custom_max_tokens(self):
        """Verify the request payload uses a custom max_tokens value when provided."""
        captured = self._capture_payload("Capital of France?", max_tokens=50)
        self.assertEqual(captured["body"]["max_tokens"], 50)

    def test_payload_user_message_role(self):
        """Verify the request payload has exactly one message with role 'user'."""
        captured = self._capture_payload("Capital of France?")
        messages = captured["body"]["messages"]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["role"], "user")

    def test_payload_user_message_content(self):
        """Verify the request payload's user message contains the prompt text."""
        captured = self._capture_payload("Capital of France?")
        self.assertIn("France", captured["body"]["messages"][0]["content"])

    def test_output_written_to_file(self):
        """Verify the response content is written to the output file."""
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
        """Verify the configured llama-server URL constant."""
        self.assertEqual(_LLAMA_SERVER_URL, "http://localhost:8089/v1/chat/completions")

    def test_llama_max_tokens_default(self):
        """Verify the default max_tokens constant for llama calls."""
        self.assertEqual(_LLAMA_MAX_TOKENS_DEFAULT, 120)


# ── _load_default_models JSON override behavior ───────────────────────────────

class TestLoadDefaultModels(unittest.TestCase):

    def test_returns_all_six_backends_when_json_absent(self):
        """Verify all six backend keys are present in the fallback defaults."""
        with patch("os.path.exists", return_value=False):
            result = _load_default_models()
        self.assertEqual(set(result.keys()), {"copilot", "gemini", "claude", "agy", "codex", "llama"})

    def test_returns_hardcoded_llama_model_when_json_absent(self):
        """Verify the hardcoded llama default model is used when the JSON file is absent."""
        with patch("os.path.exists", return_value=False):
            result = _load_default_models()
        self.assertEqual(result["llama"], "gemma-4-12b")

    def test_overrides_default_from_valid_json(self):
        """Verify a valid JSON override replaces the hardcoded default model."""
        json_data = json.dumps({"llama": {"model": "custom-model-1b"}})
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=json_data)):
            result = _load_default_models()
        self.assertEqual(result["llama"], "custom-model-1b")

    def test_ignores_entry_without_model_key(self):
        """Verify an entry missing the 'model' key falls back to the hardcoded default."""
        json_data = json.dumps({"llama": {"description": "no model key"}})
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=json_data)):
            result = _load_default_models()
        self.assertEqual(result["llama"], "gemma-4-12b")

    def test_returns_hardcoded_defaults_on_malformed_json(self):
        """Verify malformed JSON falls back to hardcoded defaults for all backends."""
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data="not valid json{{{")):
            result = _load_default_models()
        self.assertEqual(result["llama"], "gemma-4-12b")
        self.assertEqual(set(result.keys()), {"copilot", "gemini", "claude", "agy", "codex", "llama"})


if __name__ == "__main__":
    unittest.main()
