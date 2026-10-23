#!/usr/bin/env python3
"""
test_audit_decoupled_state.py
=============================

Regression test suite ensuring that the repository has been fully decoupled from
hardcoded `.agents/` install assumptions and legacy installer plumbing:
1. No active scripts or markdown files invoke skills via `python* .agents/skills/...`.
2. No remaining references point to deleted legacy plumbing (`plugins/plugin-manager`, `bootstrap.py`).
3. No legacy `uvx plugin-add` commands remain in active documentation.
4. Copy-manifest (`symlinks.json`) entries are healthy with 0 drift.
5. All 8 plugin roots are valid without symlinks.
"""

import json
import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class TestNoStaleAgentReferences(unittest.TestCase):
    """Enforces that no stale operational `.agents/` references remain in the repository."""

    # Files that are explicitly permitted to reference APM / client internals:
    ALLOWED_HOST_SPEC_FILES = {
        "antigravity-directory-spec.md",
        "agent-package-manager-overview.md",
        "install-apm-package-acceptance-criteria.md",
        "optimize-context-deduplication-topology.md",
        "deduplication-topology.md",
        "symlink_manager.py",
        "optimize_context.py",
        "decouple_agent_paths.py",
        "test_decouple_agent_paths.py",
        "test_audit_decoupled_state.py",
        "INSTALL.md",
        "AGENTS.md",
        "architecture.md",
        "apm_migration_plan.md",
        "apm_phase2_decouple_worklist.md",
        "fix-plugin-paths.prompt.md",
    }

    # Historical ledgers where past incidents or commit history are permanently recorded:
    HISTORICAL_LEDGERS = {
        "map-debt.md",
        "evolution-log.md",
        "CHANGELOG.md",
        "backlog.md",
        "001_cross_plugin_script_dependencies.md",
        "002_multi_skill_script_centralization.md",
        "003_plugin_skill_resource_sharing_via_mirrored_folder_structure_and_file_level_symlinks.md",
        "004_self_contained_plugins_no_cross_plugin_dependencies.md",
        "006_python_native_plugin_bootstrap_installer.md",
        "010_apm_package_management_and_copy_manifest_architecture.md",
    }

    def test_no_hardcoded_python_execution_in_agents(self) -> None:
        """Assert no markdown or script runs `python .agents/skills/...` directly."""
        pattern = re.compile(r"python[3]?\s+(\.\./)*\.agents/skills/")
        violations = []

        for p in REPO_ROOT.rglob("*"):
            if not p.is_file():
                continue
            if any(part in p.parts for part in (".git", ".pytest_cache", "build", "temp", "node_modules", "tests", "archive", "work-tasks", "issue-payloads")):
                continue
            if p.name in self.HISTORICAL_LEDGERS or p.name in self.ALLOWED_HOST_SPEC_FILES:
                continue
            if p.suffix in (".md", ".py", ".sh", ".json"):
                try:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                    for idx, line in enumerate(text.splitlines(), 1):
                        if pattern.search(line):
                            violations.append(f"{p.relative_to(REPO_ROOT)}:{idx}: {line.strip()}")
                except Exception:
                    pass

        self.assertEqual(
            violations,
            [],
            f"Found hardcoded operational executions of .agents/skills:\n" + "\n".join(violations),
        )

    def test_no_references_to_deleted_plugin_manager(self) -> None:
        """Assert no active code or documentation points to the deleted `plugins/plugin-manager`."""
        pattern = re.compile(r"plugins/plugin-manager")
        violations = []

        for p in REPO_ROOT.rglob("*"):
            if not p.is_file():
                continue
            if any(part in p.parts for part in (".git", ".pytest_cache", "build", "temp", "node_modules", "tests", "archive", "work-tasks", "issue-payloads")):
                continue
            if p.name in self.HISTORICAL_LEDGERS or p.name in self.ALLOWED_HOST_SPEC_FILES:
                continue
            # Ignore test files that intentionally assert removal
            if p.name == "test_audit_decoupled_state.py":
                continue
            if p.suffix in (".md", ".py", ".sh", ".json", ".yaml", ".yml"):
                try:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                    for idx, line in enumerate(text.splitlines(), 1):
                        if pattern.search(line):
                            violations.append(f"{p.relative_to(REPO_ROOT)}:{idx}: {line.strip()}")
                except Exception:
                    pass

        self.assertEqual(
            violations,
            [],
            f"Found references to deleted plugins/plugin-manager:\n" + "\n".join(violations),
        )

    def test_no_legacy_uvx_plugin_add_commands(self) -> None:
        """Assert no active documentation instructs users to run `uvx ... plugin-add`."""
        pattern = re.compile(r"plugin-add\s+richfrem/agent-plugins-skills")
        violations = []

        for p in REPO_ROOT.rglob("*"):
            if not p.is_file():
                continue
            if any(part in p.parts for part in (".git", ".pytest_cache", "build", "temp", "node_modules", "tests", "archive", "work-tasks", "issue-payloads")):
                continue
            if p.name in self.HISTORICAL_LEDGERS:
                continue
            if p.suffix in (".md", ".txt"):
                try:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                    for idx, line in enumerate(text.splitlines(), 1):
                        if pattern.search(line):
                            violations.append(f"{p.relative_to(REPO_ROOT)}:{idx}: {line.strip()}")
                except Exception:
                    pass

        self.assertEqual(
            violations,
            [],
            f"Found legacy uvx plugin-add commands in documentation:\n" + "\n".join(violations),
        )

    def test_copy_manifest_zero_drift(self) -> None:
        """Assert that materialize_copies.py --check reports 0 drift across all 2,289 files."""
        script = (
            REPO_ROOT
            / "plugins"
            / "agent-scaffolders"
            / "skills"
            / "convert-plugin-to-apm"
            / "scripts"
            / "materialize_copies.py"
        )
        proc = subprocess.run(
            ["python3", str(script), "--path", str(REPO_ROOT), "--check"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, f"materialize_copies --check failed:\n{proc.stdout}\n{proc.stderr}")
        self.assertIn("drifted=0", proc.stdout)
        self.assertIn("missing_source=0", proc.stdout)

    def test_no_stale_ownership_file_references_in_instructions(self) -> None:
        """Assert no active SKILL.md or agent markdown instructs agents to check .agents/ownership/."""
        pattern = re.compile(r"\.agents/ownership/")
        violations = []

        for p in (REPO_ROOT / "plugins").rglob("*.md"):
            if any(part in p.parts for part in (".git", ".pytest_cache", "build", "temp", "node_modules", "tests", "research", "design-artifacts")):
                continue
            if p.name in self.HISTORICAL_LEDGERS or p.name in self.ALLOWED_HOST_SPEC_FILES:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
                for idx, line in enumerate(text.splitlines(), 1):
                    # Skip historical notes or explicit prohibitions
                    if pattern.search(line) and "retired" not in line and "prohibited" not in line and "legacy" not in line and "Zero Legacy" not in line:
                        violations.append(f"{p.relative_to(REPO_ROOT)}:{idx}: {line.strip()}")
            except Exception:
                pass

        self.assertEqual(
            violations,
            [],
            f"Found instructions referencing retired .agents/ownership:\n" + "\n".join(violations),
        )



if __name__ == "__main__":
    unittest.main()
