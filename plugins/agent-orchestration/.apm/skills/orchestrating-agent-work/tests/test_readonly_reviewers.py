"""S8 test: the three adversarial review agents declare strictly `tools: Read, Grep, Glob` and consistent Constraints."""

from __future__ import annotations

import re
from pathlib import Path


AGENTS_DIR = Path(__file__).resolve().parents[3] / "agents"
TRIO = ("architect-review.md", "security-auditor.md", "tdd-contract-reviewer.md")


def test_trio_agents_declare_readonly_tools_and_consistent_constraints():
    for filename in TRIO:
        path = AGENTS_DIR / filename
        assert path.is_file(), f"Missing agent definition: {path}"
        text = path.read_text(encoding="utf-8")
        fm = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)
        assert fm is not None, f"Missing frontmatter in {filename}"
        tools_match = re.search(r"^tools:\s*(.+)$", fm.group(1), re.MULTILINE)
        assert tools_match is not None, f"Missing tools: in {filename}"
        assert tools_match.group(1).strip() == "Read, Grep, Glob", f"Unexpected tools in {filename}: {tools_match.group(1)}"
        assert "No tools. No filesystem access." not in text, f"Contradictory constraints in {filename}"
        assert "red-team-review/SKILL.md" not in text, f"Stale red-team-review/SKILL.md link in {filename}"
