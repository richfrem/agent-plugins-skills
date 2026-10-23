#!/usr/bin/env python3
"""
Unit tests for apm_consumer.py (install-apm-package skill).

Purpose:
    Validates consumer tooling logic without network or a real APM install (run_apm is
    replaced by a recorder):
    1. Unpinned installs are refused; pinned specs are built as owner/repo/plugins/<p>#<ref>
    2. dependency_key handles APM's string and dict (--skill) entry forms
    3. set-ref rewrites refs on both entry forms for --source only, after a backup
    4. rollback uninstalls packages added since the backup before restoring state
    5. --checkout installs from a local clone only when its copies are materialized

Key Input Dependencies:
    - ../skills/install-apm-package/scripts/apm_consumer.py (module under test)
"""

import argparse
import os
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "install-apm-package" / "scripts"))
import apm_consumer as consumer  # noqa: E402

SRC = "richfrem/agent-plugins-skills"


class TestApmConsumer(unittest.TestCase):
    """Consumer commands against a temporary HOME."""

    def setUp(self) -> None:
        """Redirect HOME and record APM calls instead of running them."""
        self.tmp = tempfile.TemporaryDirectory()
        self.old_home = os.environ.get("HOME")
        os.environ["HOME"] = self.tmp.name
        self.calls: list[list[str]] = []
        self.real_run = consumer.run_apm
        consumer.run_apm = lambda apm, args, cwd=None: self.calls.append(args) or 0
        (Path(self.tmp.name) / ".apm").mkdir()

    def tearDown(self) -> None:
        """Restore HOME and run_apm."""
        consumer.run_apm = self.real_run
        os.environ["HOME"] = self.old_home or ""
        self.tmp.cleanup()

    def _write_manifest(self, deps: list) -> None:
        manifest = {"name": "global", "dependencies": {"apm": deps}}
        (consumer.apm_home() / "apm.yml").write_text(yaml.safe_dump(manifest))
        (consumer.apm_home() / "apm.lock.yaml").write_text("lockfile_version: 1\n")

    def _args(self, **kw) -> argparse.Namespace:
        base = {"apm": "apm", "source": SRC, "targets": "claude,copilot,agy,codex", "is_global": True,
                "skill": None, "allow_unpinned": False, "ref": None, "backup": None, "plugins": "dev-utils",
                "checkout": None}
        base.update(kw)
        return argparse.Namespace(**base)

    def test_unpinned_install_refused_and_spec_pinned(self) -> None:
        self.assertEqual(consumer.cmd_install(self._args()), 2)
        self.assertEqual(self.calls, [])
        self.assertEqual(consumer.cmd_install(self._args(ref="abc123")), 0)
        self.assertEqual(self.calls[0][:2], ["install", f"{SRC}/plugins/dev-utils#abc123"])
        self.assertIn("--global", self.calls[0])

    def test_checkout_install_requires_materialized_clone(self) -> None:
        clone = Path(self.tmp.name) / "clone"
        (clone / "plugins" / "dev-utils").mkdir(parents=True)
        self.assertEqual(consumer.cmd_install(self._args(checkout=str(clone))), 2)  # no materialize tool
        consumer.checkout_ready = lambda checkout: True
        self.assertEqual(consumer.cmd_install(self._args(checkout=str(clone), skill=["adr-management"])), 0)
        self.assertEqual(self.calls[-1][:2], ["install", str(clone.resolve() / "plugins" / "dev-utils")])

    def test_dependency_key_forms(self) -> None:
        self.assertEqual(consumer.dependency_key(f"{SRC}/plugins/a#r1"), f"{SRC}/plugins/a")
        self.assertEqual(consumer.dependency_key({"git": f"{SRC}/plugins/b", "ref": "r1"}), f"{SRC}/plugins/b")

    def test_set_ref_rewrites_both_forms_for_source_only(self) -> None:
        self._write_manifest([f"{SRC}/plugins/a#old", {"git": f"{SRC}/plugins/b", "ref": "old", "skills": ["x"]},
                              "other/repo/pkg#keep"])
        self.assertEqual(consumer.cmd_set_ref(self._args(ref="new")), 0)
        deps = yaml.safe_load((consumer.apm_home() / "apm.yml").read_text())["dependencies"]["apm"]
        self.assertEqual(deps[0], f"{SRC}/plugins/a#new")
        self.assertEqual(deps[1]["ref"], "new")
        self.assertEqual(deps[2], "other/repo/pkg#keep")
        self.assertEqual(len(consumer.list_backups()), 1)
        self.assertEqual(self.calls[-1], ["install", "--global"])

    def test_rollback_uninstalls_added_then_restores(self) -> None:
        self._write_manifest([f"{SRC}/plugins/a#r1"])
        consumer.backup_global()
        self._write_manifest([f"{SRC}/plugins/a#r1", {"git": f"{SRC}/plugins/b", "ref": "r1", "skills": ["x"]}])
        self.assertEqual(consumer.cmd_rollback(self._args()), 0)
        self.assertEqual(self.calls, [["uninstall", f"{SRC}/plugins/b", "--global"], ["install", "--global"]])
        restored = yaml.safe_load((consumer.apm_home() / "apm.yml").read_text())["dependencies"]["apm"]
        self.assertEqual(restored, [f"{SRC}/plugins/a#r1"])


if __name__ == "__main__":
    unittest.main()
