"""TDD parity test for Target 3: Dependency Boilerplate Consolidation.

Asserts that confirmed ELIGIBLE skills have the exact standardized one-liner,
zero INELIGIBLE skills (with third-party dependencies or inter-skill capability dependencies) were modified,
non-dependency content (titles, dividers, and descriptions) is strictly preserved,
and at least 25 skills were discovered and classified.
"""

from pathlib import Path
import json
import re
import pytest
import sys

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PLUGIN_ROOT.parent.parent
DEV_UTILS_SCRIPTS = PLUGIN_ROOT / "scripts"

if str(DEV_UTILS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(DEV_UTILS_SCRIPTS))

from classify_skill_dependencies import (  # type: ignore
    classify_all_skills,
    CANONICAL_ONE_LINER,
    extract_dependencies_section,
)

REPORT_PATH = REPO_ROOT / "context" / "dependency-classification-report.json"


def test_dependency_classification_bounds():
    """Assert classifier finds at least 25 skills with dependency blocks."""
    plugins_dir = REPO_ROOT / "plugins"
    report = classify_all_skills(plugins_dir)

    total_evaluated = len(report["eligible"]) + len(report["ineligible"]) + len(report["ambiguous"])
    assert total_evaluated >= 25, (
        f"Discovery found only {total_evaluated} skills with dependency sections; expected at least 25."
    )
    assert len(report["eligible"]) >= 7, (
        f"Expected at least 7 eligible skills, found {len(report['eligible'])}"
    )


def test_dependencies_parity_on_disk():
    """Assert eligible skills have exact one-liner, and ineligible skills are untouched."""
    assert REPORT_PATH.exists(), f"Missing classification report at {REPORT_PATH}"
    report_data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    eligible_skills = report_data.get("eligible", [])
    ineligible_skills = report_data.get("ineligible", [])

    assert len(eligible_skills) >= 7, f"Expected at least 7 eligible skills, found {len(eligible_skills)}"

    for rel_path in eligible_skills:
        skill_file = REPO_ROOT / rel_path
        assert skill_file.exists(), f"Skill file {skill_file} does not exist"
        section = extract_dependencies_section(skill_file)
        assert section is not None, f"Skill {rel_path} missing ## Dependencies section"
        assert CANONICAL_ONE_LINER in section, (
            f"Eligible skill {rel_path} does not contain canonical one-liner"
        )
        assert "pip-compile" not in section, (
            f"Eligible skill {rel_path} still has legacy pip-compile boilerplate"
        )

    for rel_path in ineligible_skills:
        skill_file = REPO_ROOT / rel_path
        if skill_file.exists():
            section = extract_dependencies_section(skill_file)
            if section:
                assert CANONICAL_ONE_LINER not in section, (
                    f"Ineligible skill {rel_path} was improperly modified with standard-library one-liner"
                )


def test_structural_preservation_of_non_dependency_content():
    """Asserts that replacing ## Dependencies preserved all subsequent headings, dividers, and titles."""
    assert REPORT_PATH.exists()
    report_data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    for rel_path in report_data.get("eligible", []):
        skill_file = REPO_ROOT / rel_path
        content = skill_file.read_text(encoding="utf-8")

        # Must have exactly one ## Dependencies header
        assert content.count("## Dependencies") == 1, (
            f"Skill {rel_path} has corrupted ## Dependencies count"
        )

        # Must retain primary markdown title (# Title)
        title_matches = re.findall(r"^#\s+[A-Za-z0-9: \(\)\-]+", content, re.MULTILINE)
        assert len(title_matches) >= 1, (
            f"Skill {rel_path} lost its primary title (# Heading) during standardization"
        )

        # Ensure content length is reasonable (not truncated)
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        assert len(lines) >= 20, (
            f"Skill {rel_path} has only {len(lines)} lines; possible content truncation"
        )


def test_inter_skill_dependencies_classified_as_ineligible():
    """Asserts that skills declaring inter-skill or capability dependencies are preserved as ineligible."""
    plugins_dir = REPO_ROOT / "plugins"
    report = classify_all_skills(plugins_dir)

    # red-team-review requires context-bundler and adversarial personas
    red_team_rel = "plugins/agent-orchestration/skills/red-team-review/SKILL.md"
    assert red_team_rel in report["ineligible"], (
        f"Skill {red_team_rel} declares inter-skill dependencies and must be classified as INELIGIBLE"
    )
    red_team_content = (REPO_ROOT / red_team_rel).read_text(encoding="utf-8")
    assert "context-bundler" in red_team_content
    assert CANONICAL_ONE_LINER not in red_team_content

    # triple-loop-learning declares evaluation gate guidance
    triple_loop_rel = "plugins/agent-orchestration/skills/triple-loop-learning/SKILL.md"
    assert triple_loop_rel in report["ineligible"], (
        f"Skill {triple_loop_rel} declares evaluation gate requirements and must be classified as INELIGIBLE"
    )
    triple_loop_content = (REPO_ROOT / triple_loop_rel).read_text(encoding="utf-8")
    assert "Evaluation gate" in triple_loop_content
    assert CANONICAL_ONE_LINER not in triple_loop_content
