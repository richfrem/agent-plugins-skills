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
