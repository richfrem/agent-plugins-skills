#!/usr/bin/env python3
"""
Purpose:
    Unit tests for swarm_run.py model loading and configuration functions.
    Verifies correct model resolution from cheapest_models.json with fallbacks.

Key Input Dependencies:
    - swarm_run.py module (_load_cheapest_model function)
    - Temporary JSON files for test fixtures

Key Functions:
    - _write_json(): Write test JSON fixture to temporary file

Tests cover:
    - _load_cheapest_model: JSON load, fallback, malformed JSON, missing engine key
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from swarm_run import _load_cheapest_model


class TestLoadCheapestModel(unittest.TestCase):

    def _write_json(self, data: dict) -> Path:
        """Write test data to temporary JSON file and return path."""
        f = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        json.dump(data, f)
        f.close()
        return Path(f.name)

    def test_returns_fallback_when_json_absent(self):
        absent = Path(tempfile.mkdtemp()) / "does_not_exist.json"
        result = _load_cheapest_model("copilot", "gpt-5-mini", ref_path=absent)
        self.assertEqual(result, "gpt-5-mini")

    def test_loads_model_for_requested_engine(self):
        ref = self._write_json({"copilot": {"model": "gpt-5-nano"}})
        try:
            result = _load_cheapest_model("copilot", "gpt-5-mini", ref_path=ref)
            self.assertEqual(result, "gpt-5-nano")
        finally:
            ref.unlink()

    def test_returns_fallback_when_engine_not_in_json(self):
        ref = self._write_json({"copilot": {"model": "gpt-5-mini"}})
        try:
            result = _load_cheapest_model("gemini", "gemini-fallback", ref_path=ref)
            self.assertEqual(result, "gemini-fallback")
        finally:
            ref.unlink()

    def test_returns_fallback_on_malformed_json(self):
        f = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        f.write("not valid json{{{")
        f.close()
        ref = Path(f.name)
        try:
            result = _load_cheapest_model("copilot", "gpt-5-mini", ref_path=ref)
            self.assertEqual(result, "gpt-5-mini")
        finally:
            ref.unlink()

    def test_returns_fallback_when_model_key_absent(self):
        ref = self._write_json({"copilot": {"description": "no model key"}})
        try:
            result = _load_cheapest_model("copilot", "gpt-5-mini", ref_path=ref)
            self.assertEqual(result, "gpt-5-mini")
        finally:
            ref.unlink()


if __name__ == "__main__":
    unittest.main()
