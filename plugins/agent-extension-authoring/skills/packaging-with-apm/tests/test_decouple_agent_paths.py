#!/usr/bin/env python3
"""
Unit tests for decouple_agent_paths.py (convert-plugin-to-apm skill).

Purpose:
    Validates the install-folder reference rewriter (APM migration plan Section 6.2):
    1. R1/R2 rewrite a skill's own `.agents/skills/<self>/...` paths to skill-relative paths
    2. R3 rewrites links and bare paths to another skill's SKILL.md into a name reference
    3. Fenced code, commands inside inline code, and JSON values are left untouched
    4. Excluded files (legacy installer, ledgers, ignore files) are never scanned
    5. Dry-run writes nothing; --apply writes only the rewrites

Key Input Dependencies:
    - ../scripts/decouple_agent_paths.py (module under test)
    - git on PATH
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import decouple_agent_paths as decouple  # noqa: E402


class TestRewriteText(unittest.TestCase):
    """rewrite_text on in-memory markdown."""

    def test_own_skill_script_and_file(self) -> None:
        text = "Run `python3 .agents/skills/me/scripts/run.py` and read .agents/skills/me/references/a.md."
        new, changes = decouple.rewrite_text(text, "me")
        self.assertIn("`python3 .agents/skills/me/scripts/run.py`", new)  # command span untouched
        self.assertIn("read references/a.md.", new)
        self.assertEqual([c["rule"] for c in changes], ["R2"])

    def test_own_skill_whole_span_path(self) -> None:
        new, changes = decouple.rewrite_text("See `.agents/skills/me/scripts/run.py`.", "me")
        self.assertEqual(new, "See `scripts/run.py`.")
        self.assertEqual(changes[0]["rule"], "R1")

    def test_other_skill_link_and_bare_path(self) -> None:
        text = "Use [ADR tool](.agents/skills/adr-management/SKILL.md). Details: `.agents/skills/dep/SKILL.md`"
        new, changes = decouple.rewrite_text(text, None)
        self.assertEqual(new, "Use ADR tool (the `adr-management` skill). Details: the `dep` skill")
        self.assertEqual(len(changes), 2)

    def test_code_and_data_left_alone(self) -> None:
        text = ("```bash\npython3 .agents/skills/x/scripts/y.py\n```\n"
                '"source_file": ".agents/skills/x/SKILL.md"\n'
                "`python scripts/e.py --skill .agents/skills/x/SKILL.md`\n"
                "`./Other/.agents/skills/x/SKILL.md`\n")
        new, changes = decouple.rewrite_text(text, "x")
        self.assertEqual(new.count(".agents/skills/x/"), 4 - sum(1 for c in changes))
        self.assertIn("python3 .agents/skills/x/scripts/y.py", new)
        self.assertIn("--skill .agents/skills/x/SKILL.md", new)
        self.assertIn("./Other/.agents/skills/x/SKILL.md", new)


class TestScan(unittest.TestCase):
    """scan() over a temporary git repository."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        files = {
            "plugins/p/skills/me/SKILL.md": "Read .agents/skills/me/references/a.md and .agents/skills/other/SKILL.md\n",
            "plugins/p/rules/r.md": "Full workflow details -> `.agents/skills/me/SKILL.md`\n",
            "plugins/plugin-manager/README.md": "Installs into .agents/skills/me/SKILL.md\n",
            "references/map-debt.md": "Old: .agents/skills/me/SKILL.md\n",
            ".claudeignore": ".agents/\n",
        }
        for rel, body in files.items():
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_text(body)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_dry_run_reports_without_writing(self) -> None:
        before = (self.root / "plugins/p/skills/me/SKILL.md").read_text()
        result = decouple.scan(self.root, apply=False)
        self.assertEqual(sorted(c["file"] for c in result["changed_files"]),
                         ["plugins/p/rules/r.md", "plugins/p/skills/me/SKILL.md"])
        self.assertEqual((self.root / "plugins/p/skills/me/SKILL.md").read_text(), before)

    def test_apply_writes_and_skips_excluded(self) -> None:
        decouple.scan(self.root, apply=True)
        self.assertEqual((self.root / "plugins/p/skills/me/SKILL.md").read_text(),
                         "Read references/a.md and the `other` skill\n")
        self.assertEqual((self.root / "plugins/p/rules/r.md").read_text(), "Full workflow details -> the `me` skill\n")
        self.assertIn(".agents/", (self.root / "plugins/plugin-manager/README.md").read_text())
        self.assertIn(".agents/", (self.root / "references/map-debt.md").read_text())
        self.assertEqual((self.root / ".claudeignore").read_text(), ".agents/\n")


if __name__ == "__main__":
    unittest.main()
