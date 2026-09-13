"""Regression test for the 2026-09-13 background-document-priority fix: a referenced
local prompt/brief document must be surfaced by the intake tool's own output at the
moment intake starts, not left to be remembered from SKILL.md prose.
"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from interview_spec_engine import detect_referenced_background_document


def test_detects_temp_prompt_md(tmp_path):
    (tmp_path / "temp").mkdir()
    (tmp_path / "temp" / "prompt.md").write_text("background doc", encoding="utf-8")

    found = detect_referenced_background_document(search_dir=tmp_path)

    assert found == "temp/prompt.md"


def test_returns_none_when_no_candidate_exists(tmp_path):
    found = detect_referenced_background_document(search_dir=tmp_path)

    assert found is None
