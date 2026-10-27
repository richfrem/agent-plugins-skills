#!/usr/bin/env python3
"""
Regression tests for scaffold_plugin.py (authoring-plugins skill).

Purpose:
    1. A scaffolded plugin has valid JSON/YAML manifests, an author object, and no skills/agents/hooks arrays
    2. Optional hooks/MCP files are valid JSON under .apm/hooks/hooks.json and .mcp.json
    3. Invalid names and existing directories exit non-zero without writing
    4. The result passes audit_plugin_structure.py with zero errors or warnings

Key Input Dependencies:
    - ../scripts/scaffold_plugin.py, ../scripts/audit_plugin_structure.py, ../assets/templates/README.md.jinja
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def run(script, *args, cwd):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)], cwd=cwd, capture_output=True, text=True)


class ScaffoldPluginTests(unittest.TestCase):
    def test_manifest_is_clean_and_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run("scaffold_plugin.py", "--name", "demo-plugin", "--path", tmp, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            root = Path(tmp) / "demo-plugin"
            manifest = json.loads((root / ".claude-plugin" / "plugin.json").read_text())
            self.assertEqual(manifest["name"], "demo-plugin")
            self.assertIsInstance(manifest["author"], dict)
            for key in ("skills", "agents", "hooks"):
                self.assertNotIn(key, manifest)
            self.assertTrue((root / ".apm" / "skills").is_dir())
            self.assertTrue((root / "apm.yml").is_file())
            self.assertTrue((root / "README.md").is_file())

    def test_optional_files_are_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run("scaffold_plugin.py", "--name", "demo-plugin", "--path", tmp, "--with-hooks", "--with-mcp", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            root = Path(tmp) / "demo-plugin"
            self.assertEqual(json.loads((root / ".apm" / "hooks" / "hooks.json").read_text()), {"hooks": {}})
            self.assertEqual(json.loads((root / ".mcp.json").read_text()), {"mcpServers": {}})

    def test_invalid_name_and_existing_directory_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertNotEqual(run("scaffold_plugin.py", "--name", "Bad_Name", "--path", tmp, cwd=tmp).returncode, 0)
            self.assertEqual(run("scaffold_plugin.py", "--name", "dup", "--path", tmp, cwd=tmp).returncode, 0)
            self.assertNotEqual(run("scaffold_plugin.py", "--name", "dup", "--path", tmp, cwd=tmp).returncode, 0)

    def test_scaffold_passes_structure_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("scaffold_plugin.py", "--name", "demo-plugin", "--path", tmp, cwd=tmp)
            result = run("audit_plugin_structure.py", Path(tmp) / "demo-plugin", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("ERRORS", result.stdout, result.stdout)


if __name__ == "__main__":
    unittest.main()
