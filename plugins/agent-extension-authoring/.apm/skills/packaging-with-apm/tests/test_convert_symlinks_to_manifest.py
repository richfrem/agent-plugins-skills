#!/usr/bin/env python3
"""
Unit tests for convert_symlinks_to_manifest.py (convert-plugin-to-apm skill).

Purpose:
    Validates the symlink -> copy-manifest conversion (APM migration plan Section 10.3):
    1. Dry-run changes nothing
    2. Apply removes the links, updates existing manifest entries and adds missing ones
    3. tests/ links and links leaving the plugin are skipped and reported
    4. Stale "symlink" entries whose destination is now a real file are removed
    5. The build pipeline stages the same bytes after conversion as before it

Key Input Dependencies:
    - ../scripts/convert_symlinks_to_manifest.py (module under test)
    - ../scripts/apm_build_pipeline.py (staging comparison)
    - git on PATH
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import apm_build_pipeline as pipeline  # noqa: E402
import convert_symlinks_to_manifest as conv  # noqa: E402


def _git(cwd: Path, *args: str) -> None:
    """Run git quietly with a fixed identity."""
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True, capture_output=True)


class TestConvert(unittest.TestCase):
    """Conversion against a synthetic repository."""

    def setUp(self) -> None:
        """Plugin p: two skills sharing a script, a doc link, a tests/ link, a cross-plugin link."""
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        p = self.root / "plugins" / "p"
        for d in ("scripts", "references", "tests", "skills/a/scripts", "skills/b/scripts", "skills/b/references", "agents"):
            (p / d).mkdir(parents=True)
        (p / "scripts" / "tool.py").write_text("print('tool')\n")
        (p / "references" / "doc.md").write_text("doc\n")
        for skill in ("a", "b"):
            (p / "skills" / skill / "SKILL.md").write_text(f"---\nname: {skill}\ndescription: Test skill.\n---\n")
            os.symlink("../../../scripts/tool.py", p / "skills" / skill / "scripts" / "tool.py")
        os.symlink("../../../references/doc.md", p / "skills" / "b" / "references" / "doc.md")
        os.symlink("../scripts/tool.py", p / "tests" / "tool.py")
        (self.root / "plugins" / "q").mkdir()
        (self.root / "plugins" / "q" / "x.md").write_text("q\n")
        os.symlink("../../../../q/x.md", p / "skills" / "b" / "references" / "x.md")
        (p / "agents" / "a.md").write_text("standalone agent\n")
        (self.root / "symlinks.json").write_text(json.dumps({"version": 1, "links": [
            {"src": "plugins/p/scripts/tool.py", "dst": "plugins/p/skills/a/scripts/tool.py", "strategy": "symlink", "description": "hub"},
            {"src": "plugins/p/skills/a/SKILL.md", "dst": "plugins/p/agents/a.md", "strategy": "symlink", "description": "old mirror"},
            {"src": "plugins/p/x", "dst": "docs/keep.md", "strategy": "symlink", "description": "outside"},
        ]}))
        _git(self.root, "init", "-q")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", "fixture")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _staged_bytes(self) -> dict:
        insp = pipeline.inspect_plugin(self.root, self.root / "plugins" / "p")
        staging = self.root / "build" / "staging" / "p"
        pipeline.normalize_plugin(insp, staging)
        return {str(f.relative_to(staging)): f.read_bytes() for f in staging.rglob("*") if f.is_file()}

    def test_dry_run_changes_nothing(self) -> None:
        before = (self.root / "symlinks.json").read_text()
        result = conv.convert(self.root, ["p"], apply=False)
        self.assertEqual(len(result["converted"]), 3)
        self.assertTrue((self.root / "plugins/p/skills/a/scripts/tool.py").is_symlink())
        self.assertEqual((self.root / "symlinks.json").read_text(), before)

    def test_apply_converts_and_reports(self) -> None:
        result = conv.convert(self.root, ["p"], apply=True)
        self.assertEqual(result["manifest"], {"updated": 1, "added": 2, "stale_removed": 1})
        self.assertFalse((self.root / "plugins/p/skills/a/scripts/tool.py").exists())
        self.assertTrue((self.root / "plugins/p/tests/tool.py").is_symlink())
        reasons = {s["path"]: s["reason"] for s in result["skipped"]}
        self.assertIn("tests/", reasons["plugins/p/tests/tool.py"])
        self.assertIn("outside the plugin", reasons["plugins/p/skills/b/references/x.md"])
        entries = {e["dst"]: e for e in json.loads((self.root / "symlinks.json").read_text())["links"]}
        self.assertEqual(entries["plugins/p/skills/a/scripts/tool.py"]["strategy"], "copy")
        self.assertEqual(entries["plugins/p/skills/b/references/doc.md"]["src"], "plugins/p/references/doc.md")
        self.assertNotIn("plugins/p/agents/a.md", entries)
        self.assertIn("docs/keep.md", entries)

    def test_staged_content_unchanged_by_conversion(self) -> None:
        (self.root / "plugins/p/skills/b/references/x.md").unlink()
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", "drop cross-plugin link")
        before = self._staged_bytes()
        conv.convert(self.root, ["p"], apply=True)
        after = self._staged_bytes()
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
