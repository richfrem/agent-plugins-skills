"""Unit tests for check_plan_links.py script."""

import subprocess
import sys
from pathlib import Path
import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
CHECK_SCRIPT = SCRIPTS_DIR / "check_plan_links.py"


def test_check_plan_links_passes_for_valid_file(tmp_path):
    doc = tmp_path / "test.md"
    target = tmp_path / "target.md"
    target.write_text("# Target\n", encoding="utf-8")
    doc.write_text("[Target](target.md)\n[External](https://example.com)\n", encoding="utf-8")

    res = subprocess.run([sys.executable, str(CHECK_SCRIPT), str(doc)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    assert "All local links valid" in res.stdout


def test_check_plan_links_fails_for_broken_link(tmp_path):
    doc = tmp_path / "test.md"
    doc.write_text("[Missing](nonexistent.md)\n", encoding="utf-8")

    res = subprocess.run([sys.executable, str(CHECK_SCRIPT), str(doc)], capture_output=True, text=True)
    assert res.returncode != 0
    assert "nonexistent.md" in res.stderr or "nonexistent.md" in res.stdout
