"""Shared discovery and extraction library for CLI Persona Registry.

Used by both sync_cli_personas.py generator and test_persona_parity.py test fixture
to ensure single-source discovery logic without discrepancies (M4, M6).
"""

from pathlib import Path
import re
from typing import List, Optional, Set

TARGET_SKILL_NAMES = (
    "claude-cli-agent",
    "agy-cli-agent",
    "codex-cli-agent",
    "copilot-cli-agent",
    "local-llm-bridge",
    "local-llm-setup",
)

PERSONA_SECTION_PATTERN = re.compile(
    r"(?ms)(^##\s+(?:🎭\s+)?Persona Registry.*?\n)(.*?)(?=^##\s+(?!#)|^\-\-\-|\Z)"
)


def discover_cli_persona_skills(skills_dir: Path) -> List[Path]:
    """Discovers CLI skills defining or dispatching personas under skills_dir.

    Deduplicates paths and ensures boundary confinement to skills_dir and SKILL.md basename only.
    Preserves symlink paths for callers to enforce symlink write rejection.
    """
    resolved_skills_dir = skills_dir.resolve()
    discovered: Set[Path] = set()

    # 1. Target known persona skills
    for name in TARGET_SKILL_NAMES:
        skill_file = skills_dir / name / "SKILL.md"
        if skill_file.exists() and skill_file.resolve().is_relative_to(resolved_skills_dir):
            discovered.add(skill_file)

    # 2. Dynamic discovery: any other skill in skills_dir with Persona Registry
    for candidate in sorted(skills_dir.glob("*/SKILL.md")):
        if not candidate.exists() or candidate.name != "SKILL.md":
            continue
        if not candidate.resolve().is_relative_to(resolved_skills_dir):
            continue
        try:
            content = candidate.read_text(encoding="utf-8")
            if "Persona Registry" in content or "run_agent.py" in content:
                discovered.add(candidate)
        except (OSError, UnicodeDecodeError):
            continue

    return sorted(list(discovered))


def extract_persona_section(skill_file: Path) -> Optional[str]:
    """Extracts the Persona Registry section from SKILL.md.

    Captures from '## [🎭 ]Persona Registry' through any ### subsections
    until the next '## ' section, '---' separator, or end of file.
    """
    content = skill_file.read_text(encoding="utf-8")
    match = PERSONA_SECTION_PATTERN.search(content)
    if match:
        return match.group(0).strip()
    return None
