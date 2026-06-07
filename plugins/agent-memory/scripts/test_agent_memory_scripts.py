#!/usr/bin/env python3
"""
test_agent_memory_scripts.py — unit tests for agent-memory script model resolution

Tests cover:
  swarm_run._load_cheapest_model  — per-engine JSON lookup with fallback
  distill_one._load_engine_defaults — full defaults dict loaded from JSON
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

DISTILL_ONE = Path(__file__).resolve().parent / "distill_one.py"
PLUGIN_REFS = DISTILL_ONE.parents[1] / "references"

sys.path.insert(0, os.path.dirname(__file__))


# ── swarm_run._load_cheapest_model ─────────────────────────────────────────────

from swarm_run import _load_cheapest_model


class TestSwarmRunLoadCheapestModel(unittest.TestCase):

    def _tmp_json(self, data: dict) -> Path:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(data, f)
        f.close()
        return Path(f.name)

    def test_returns_fallback_when_json_absent(self):
        absent = Path(tempfile.mkdtemp()) / "no_file.json"
        result = _load_cheapest_model("copilot", "gpt-5-mini", ref_path=absent)
        self.assertEqual(result, "gpt-5-mini")

    def test_loads_model_for_engine_from_json(self):
        ref = self._tmp_json({"copilot": {"model": "gpt-5-nano"}})
        try:
            result = _load_cheapest_model("copilot", "gpt-5-mini", ref_path=ref)
            self.assertEqual(result, "gpt-5-nano")
        finally:
            ref.unlink()

    def test_returns_fallback_when_engine_missing_from_json(self):
        ref = self._tmp_json({"copilot": {"model": "gpt-5-mini"}})
        try:
            result = _load_cheapest_model("gemini", "gemini-fallback", ref_path=ref)
            self.assertEqual(result, "gemini-fallback")
        finally:
            ref.unlink()

    def test_returns_fallback_on_malformed_json(self):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        f.write("{not valid")
        f.close()
        ref = Path(f.name)
        try:
            result = _load_cheapest_model("copilot", "gpt-5-mini", ref_path=ref)
            self.assertEqual(result, "gpt-5-mini")
        finally:
            ref.unlink()

    def test_returns_fallback_when_model_key_absent(self):
        ref = self._tmp_json({"copilot": {"description": "no model key here"}})
        try:
            result = _load_cheapest_model("copilot", "gpt-5-mini", ref_path=ref)
            self.assertEqual(result, "gpt-5-mini")
        finally:
            ref.unlink()


# ── distill_one._load_engine_defaults ─────────────────────────────────────────

from distill_one import _load_engine_defaults


class TestDistillOneLoadEngineDefaults(unittest.TestCase):

    def _tmp_json(self, data: dict) -> Path:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(data, f)
        f.close()
        return Path(f.name)

    def test_returns_dict_with_all_engines_when_json_absent(self):
        absent = Path(tempfile.mkdtemp()) / "no_file.json"
        result = _load_engine_defaults(ref_path=absent)
        self.assertIn("copilot", result)
        self.assertIn("gemini", result)
        self.assertIn("claude", result)

    def test_overrides_engine_model_from_json(self):
        ref = self._tmp_json({"copilot": {"model": "gpt-5-nano"}})
        try:
            result = _load_engine_defaults(ref_path=ref)
            self.assertEqual(result["copilot"], "gpt-5-nano")
        finally:
            ref.unlink()

    def test_unmentioned_engines_keep_hardcoded_fallback(self):
        ref = self._tmp_json({"copilot": {"model": "gpt-5-nano"}})
        try:
            result = _load_engine_defaults(ref_path=ref)
            self.assertIsNotNone(result["claude"])
            self.assertIsNotNone(result["gemini"])
        finally:
            ref.unlink()

    def test_returns_hardcoded_fallbacks_on_malformed_json(self):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        f.write("{not valid")
        f.close()
        ref = Path(f.name)
        try:
            result = _load_engine_defaults(ref_path=ref)
            self.assertIn("copilot", result)
            self.assertIsNotNone(result["copilot"])
        finally:
            ref.unlink()

    def test_defaults_match_cheapest_models_json_when_present(self):
        """When cheapest_models.json exists, loaded defaults must equal its values."""
        script_dir = Path(__file__).resolve().parent
        ref = script_dir.parent / "references" / "cheapest_models.json"
        if not ref.exists():
            self.skipTest("cheapest_models.json not present")
        with open(ref) as f:
            json_models = json.load(f)
        result = _load_engine_defaults(ref_path=ref)
        for engine, info in json_models.items():
            if "model" in info and engine in result:
                self.assertEqual(
                    result[engine], info["model"],
                    f"{engine} should match cheapest_models.json"
                )


# ── distill_one.py --mock subprocess tests ────────────────────────────────────
# Category B: real subprocess execution, no mocks.
# --mock resolves the engine model from cheapest_models.json and exits 0
# without needing --profile, --file, or a running CLI.

class TestDistillOneMockFlag(unittest.TestCase):

    def _run_mock(self, extra_args: list) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(DISTILL_ONE), "--mock"] + extra_args,
            capture_output=True, text=True,
        )

    def test_mock_exits_zero(self):
        result = self._run_mock(["--engine", "copilot"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_mock_output_is_valid_json(self):
        result = self._run_mock(["--engine", "copilot"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            self.fail(f"--mock stdout is not valid JSON: {e}\nGot: {result.stdout!r}")
        self.assertIn("engine", data)
        self.assertIn("model", data)

    def test_mock_copilot_model_matches_cheapest_models_json(self):
        ref = PLUGIN_REFS / "cheapest_models.json"
        if not ref.exists():
            self.skipTest("cheapest_models.json not present")
        expected = json.loads(ref.read_text())["copilot"]["model"]
        result = self._run_mock(["--engine", "copilot"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["model"], expected)

    def test_mock_claude_model_matches_cheapest_models_json(self):
        ref = PLUGIN_REFS / "cheapest_models.json"
        if not ref.exists():
            self.skipTest("cheapest_models.json not present")
        expected = json.loads(ref.read_text())["claude"]["model"]
        result = self._run_mock(["--engine", "claude"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["model"], expected)


if __name__ == "__main__":
    unittest.main()
