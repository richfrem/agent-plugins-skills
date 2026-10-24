#!/usr/bin/env python3
"""
Unit tests for scaffold_apm.py and validate_apm_package.py (packaging-with-apm skill).

Purpose:
    Validates the documented quick start of the create mode:
    1. `scaffold_apm.py --name <pkg>` works without --path and writes into the current directory
    2. The scaffolded package passes `validate_apm_package.py --path <pkg>`

Key Input Dependencies:
    - ../scripts/scaffold_apm.py (module under test)
    - ../scripts/validate_apm_package.py
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def run(script, *args, cwd):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args], cwd=cwd,
                          capture_output=True, text=True)


class ScaffoldQuickStartTests(unittest.TestCase):
    def test_name_only_scaffolds_into_current_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run("scaffold_apm.py", "--name", "demo-pkg", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((Path(tmp) / "demo-pkg" / "apm.yml").is_file())
            self.assertTrue((Path(tmp) / "demo-pkg" / "docs" / "governance.md").is_file())

    def test_scaffolded_package_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run("scaffold_apm.py", "--name", "demo-pkg", cwd=tmp).returncode, 0)
            result = run("validate_apm_package.py", "--path", "./demo-pkg", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
