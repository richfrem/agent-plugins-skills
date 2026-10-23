from pathlib import Path
import sys

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from audit_skill import audit_skill


def test_audit_flags_bloated_skill_router(tmp_path: Path):
    skill_dir = tmp_path / "bloated-skill"
    skill_dir.mkdir()
    # Write a SKILL.md with 94 lines (> 80 lines)
    lines = ["---", "name: bloated-skill", "description: Tests bloat", "---"] + ["Line"] * 90
    (skill_dir / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")
    report = audit_skill(skill_dir)
    assert any("exceeds progressive disclosure budget" in w for w in report.warnings)


def test_sibling_reference_reached_through_parent_link_is_not_nested(tmp_path: Path):
    """A mode reference linking `../gate.md` must not make `gate.md` look nested when SKILL.md links it."""
    skill_dir = tmp_path / "linked-skill"
    (skill_dir / "references" / "modes").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: linked-skill\ndescription: Tests link normalisation. Use when testing.\n---\n\n# Linked\n\n"
        "- [mode](references/modes/a.md)\n- [gate](references/gate.md)\n", encoding="utf-8")
    (skill_dir / "references" / "modes" / "a.md").write_text("# Mode A\n\nSee [gate](../gate.md).\n", encoding="utf-8")
    (skill_dir / "references" / "gate.md").write_text("# Gate\n\nChecks.\n", encoding="utf-8")
    result = audit_skill(skill_dir)
    assert not [f for f in result.findings if f["rule_id"] == "navigation.direct-reference"]


def test_link_syntax_inside_inline_code_is_not_a_link(tmp_path: Path):
    """`[x](missing.md)` inside an inline code span is an example, not a link."""
    skill_dir = tmp_path / "code-span-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: code-span-skill\ndescription: Tests code spans. Use when testing.\n---\n\n# Code spans\n\n"
        "Write `Read [AGENTS.md](AGENTS.md).` in the bridge file.\n", encoding="utf-8")
    result = audit_skill(skill_dir)
    assert not [f for f in result.findings if f["rule_id"] == "links.resolve"]
