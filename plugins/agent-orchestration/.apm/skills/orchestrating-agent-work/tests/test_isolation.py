#!/usr/bin/env python3
"""
Plug-and-Play Independence & Isolation Test for agent-orchestration
===================================================================

Verifies:
1. Copy with symlinks dereferenced into an isolated temporary directory.
2. Full execution of plugin test suite in isolation (no external sibling plugins present).
3. Static grep asserting ZERO matches for banned caller-coupling terms:
   agent-agentic-os | control_plane | evolution_state | TASK_PLAN | cli-agents
   (test_isolation.py excludes itself from the banned-term grep).
"""

import sys
import os
import re
import shutil
import tempfile
import subprocess
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent


class TestPluginIsolation(unittest.TestCase):

    def setUp(self):
        self.temp_isolated_dir = tempfile.mkdtemp(prefix="isolated_orchestration_")
        self.dest_plugin = Path(self.temp_isolated_dir) / "agent-orchestration"

        # Copy plugin with symlinks dereferenced (symlinks=False copies target file content)
        shutil.copytree(PLUGIN_ROOT, self.dest_plugin, symlinks=False)

    def tearDown(self):
        shutil.rmtree(self.temp_isolated_dir, ignore_errors=True)

    def test_run_tests_in_standalone_isolation(self):
        """Run the plugin's core test suites in the isolated directory."""
        tests_to_run = [
            "tests/test_loop_strategies.py",
            "tests/test_validate_manifest.py",
            "tests/test_graph_runner.py"
        ]
        cmd = [sys.executable, "-m", "pytest"] + tests_to_run + ["-v"]
        res = subprocess.run(
            cmd,
            cwd=self.dest_plugin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(
            res.returncode, 0,
            f"Test suite failed when running in isolated directory:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
        )

    def test_static_grep_zero_caller_coupling(self):
        """Assert zero occurrences of banned caller-coupling terms in code and refactored skills."""
        banned_pattern = re.compile(
            r"agent-agentic-os|control_plane|evolution_state|TASK_PLAN|cli-agents"
        )
        violations = []

        # Scan all .py files in plugin, plus all files in refactored skills and references
        for p in self.dest_plugin.rglob("*"):
            if not p.is_file():
                continue
            # test_isolation.py excludes itself from the banned-term grep
            if p.name == "test_isolation.py":
                continue

            rel_str = str(p.relative_to(self.dest_plugin))

            is_code = (p.suffix == ".py")
            is_refactored_asset = any(part in rel_str for part in [
                "graph-execution", "graph-planner", "select-loop-strategy",
                "orchestrator", "references", "scripts"
            ])

            if is_code or is_refactored_asset:
                text = p.read_text(encoding="utf-8", errors="ignore")
                for line_num, line in enumerate(text.splitlines(), start=1):
                    match = banned_pattern.search(line)
                    if match:
                        violations.append(
                            f"{rel_str}:{line_num}: matched '{match.group(0)}' -> {line.strip()}"
                        )

        self.assertEqual(
            violations, [],
            f"Found {len(violations)} banned caller-coupling reference(s):\n" + "\n".join(violations)
        )


if __name__ == "__main__":
    unittest.main()
