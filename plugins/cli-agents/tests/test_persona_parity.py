"""TDD parity test for Target 2: CLI Persona Registry Alignment.

Asserts that dynamically discovered CLI agent skills (>= 6) contain byte-identical
inline copies of the canonical Persona Registry template, ensuring runtime self-containment
without authoring duplication.
"""

from pathlib import Path
import pytest
import sys

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PLUGIN_ROOT.parent.parent
CLI_SCRIPTS = PLUGIN_ROOT / "scripts"

if str(CLI_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(CLI_SCRIPTS))

from cli_persona_lib import discover_cli_persona_skills, extract_persona_section  # type: ignore

TEMPLATE_PATH = PLUGIN_ROOT / "assets" / "templates" / "cli-persona-registry.template.md"


def test_canonical_template_exists():
    """Assert canonical template exists and contains required sections."""
    assert TEMPLATE_PATH.exists(), f"Missing template at {TEMPLATE_PATH}"
    content = TEMPLATE_PATH.read_text(encoding="utf-8").strip()
    assert "## 🎭 Persona Registry" in content
    assert "security-auditor.md" in content
    assert "refactor-expert.md" in content
    assert "architect-review.md" in content
    assert "Force Agent Behavior" in content


def test_cli_persona_parity():
    """Assert all discovered CLI skills (>= 6) match canonical template inline content."""
    assert TEMPLATE_PATH.exists(), "Cannot verify parity without canonical template"
    canonical_content = TEMPLATE_PATH.read_text(encoding="utf-8").strip()

    skills_dir = PLUGIN_ROOT / "skills"
    discovered = discover_cli_persona_skills(skills_dir)

    # Anti-vacuity bound: must discover >= 6 skills
    assert len(discovered) >= 6, (
        f"Discovery found only {len(discovered)} skills; expected at least 6. Discovered: {discovered}"
    )

    for skill_path in discovered:
        section = extract_persona_section(skill_path)
        assert section is not None, f"Skill {skill_path.name} missing Persona Registry section"
        assert section.strip() == canonical_content, (
            f"Persona section in {skill_path} does not match canonical template"
        )
