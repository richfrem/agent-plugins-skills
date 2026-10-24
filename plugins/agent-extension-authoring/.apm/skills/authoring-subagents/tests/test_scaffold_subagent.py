#!/usr/bin/env python3
"""
Regression tests for scaffold_subagent.py (authoring-subagents skill).

Purpose:
    1. `scaffold_subagent.py --name N --path DIR --desc D` writes DIR/N.md that passes validate_agent.py
    2. Invalid names exit non-zero (the former scaffold.py printed an error and exited 0)
    3. An existing agent file is never overwritten without --force

Key Input Dependencies:
    - ../scripts/scaffold_subagent.py, ../scripts/validate_agent.py, ../assets/templates/agent.md.jinja
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def run(script, *args, cwd):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)], cwd=cwd,
                          capture_output=True, text=True)


class ScaffoldSubagentTests(unittest.TestCase):
    def test_scaffolded_agent_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run("scaffold_subagent.py", "--name", "flag-stale-evals", "--path", Path(tmp) / "agents",
                         "--desc", "flag stale evals", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            agent = Path(tmp) / "agents" / "flag-stale-evals.md"
            self.assertTrue(agent.is_file())
            check = run("validate_agent.py", agent, cwd=tmp)
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_invalid_name_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run("scaffold_subagent.py", "--name", "Bad_Name", "--path", tmp, "--desc", "x", cwd=tmp)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(list(Path(tmp).glob("*.md")))

    def test_existing_agent_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            existing = Path(tmp) / "keep-me.md"
            existing.write_text("original", encoding="utf-8")
            result = run("scaffold_subagent.py", "--name", "keep-me", "--path", tmp, "--desc", "x", cwd=tmp)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(existing.read_text(encoding="utf-8"), "original")


if __name__ == "__main__":
    unittest.main()
