#!/usr/bin/env python3
"""
test_execute.py — unit tests for execute.py (optimization loop wrapper)

Tests cover:
  - _get_default_improve_model: JSON load, fallback, malformed JSON
"""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

sys.path.insert(0, os.path.dirname(__file__))
from execute import _get_default_improve_model


class TestGetDefaultImproveModel(unittest.TestCase):

    def test_returns_gpt5_mini_when_json_absent(self):
        with patch.object(Path, "exists", return_value=False):
            result = _get_default_improve_model()
        self.assertEqual(result, "gpt-5-mini")

    def test_loads_copilot_model_from_valid_json(self):
        json_data = json.dumps({"copilot": {"model": "gpt-5-nano"}})
        with patch.object(Path, "exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=json_data)):
            result = _get_default_improve_model()
        self.assertEqual(result, "gpt-5-nano")

    def test_returns_fallback_when_copilot_key_missing_from_json(self):
        json_data = json.dumps({"llama": {"model": "gemma-4-12b"}})
        with patch.object(Path, "exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=json_data)):
            result = _get_default_improve_model()
        self.assertEqual(result, "gpt-5-mini")

    def test_returns_fallback_on_malformed_json(self):
        with patch.object(Path, "exists", return_value=True), \
             patch("builtins.open", mock_open(read_data="not json{{{")):
            result = _get_default_improve_model()
        self.assertEqual(result, "gpt-5-mini")


if __name__ == "__main__":
    unittest.main()
