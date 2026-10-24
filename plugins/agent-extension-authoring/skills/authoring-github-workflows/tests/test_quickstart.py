#!/usr/bin/env python3
"""
Quick-start regression tests for the authoring-github-workflows scripts.

Purpose:
    Validates the commands documented in SKILL.md actually run:
    1. scaffold_github_agent.py --skill-dir <skill> --target B works without --name
       (the agent name defaults to the skill folder name)
    2. validate_github_agent.py accepts the generated workflow with --file/--target
    3. scaffold_github_action.py generates a parseable workflow YAML

Key Input Dependencies:
    - ../scripts/scaffold_github_agent.py, validate_github_agent.py, scaffold_github_action.py
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def run(script, *args, cwd):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)], cwd=cwd,
                          capture_output=True, text=True)


def make_skill(root: Path) -> Path:
    skill = root / "demo-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("---\nname: demo-skill\ndescription: Summarises issues. Use when triaging.\n---\n\n# Demo\n\nSummarise.\n",
                                    encoding="utf-8")
    return skill


class QuickStartTests(unittest.TestCase):
    def test_agent_scaffold_defaults_name_to_skill_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = make_skill(Path(tmp))
            result = run("scaffold_github_agent.py", "--skill-dir", skill, "--target", "B", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((Path(tmp) / ".github" / "workflows" / "demo-skill.md").is_file())

    def test_generated_workflow_validates_with_documented_flags(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = make_skill(Path(tmp))
            self.assertEqual(run("scaffold_github_agent.py", "--skill-dir", skill, "--target", "B", cwd=tmp).returncode, 0)
            result = run("validate_github_agent.py", "--file", ".github/workflows/demo-skill.md", "--target", "B", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_github_action_scaffold_outputs_valid_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run("scaffold_github_action.py", "--category", "test", "--name", "CI", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            files = list(Path(tmp).rglob("*.yml"))
            self.assertTrue(files, result.stdout)
            self.assertIsInstance(yaml.safe_load(files[0].read_text()), dict)


if __name__ == "__main__":
    unittest.main()
