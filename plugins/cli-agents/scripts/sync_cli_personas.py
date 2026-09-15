#!/usr/bin/env python3
"""Sync CLI Persona Registry across CLI Agent skills.

Stamps canonical Persona Registry template inline into discovered CLI skills,
ensuring standalone skill runtime self-containment without authoring duplication (D1).

Enforces H1 (target confinement, symlink rejection, atomic write) and
H2 (hard exit sys.exit(1) outside .worktrees/ on --apply).
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent
DEFAULT_TEMPLATE_PATH = PLUGIN_ROOT / "assets" / "templates" / "cli-persona-registry.template.md"
SKILLS_DIR = PLUGIN_ROOT / "skills"

# Import shared discovery library
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from cli_persona_lib import (  # type: ignore
    discover_cli_persona_skills,
    extract_persona_section,
    PERSONA_SECTION_PATTERN,
)


def enforce_worktree_confinement() -> None:
    """Enforce H2: Process isolation check for mutating operations."""
    cwd = Path.cwd().resolve()
    if ".worktrees" not in cwd.parts:
        print(
            "ERROR (H2): --apply must be executed inside a registered .worktrees directory. Aborting.",
            file=sys.stderr,
        )
        sys.exit(1)


def sync_personas(
    template_path: Path, skills_dir: Path, apply: bool = False
) -> int:
    """Checks or applies canonical persona template to discovered CLI skills."""
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}", file=sys.stderr)
        return 1

    canonical_text = template_path.read_text(encoding="utf-8").strip()
    discovered = discover_cli_persona_skills(skills_dir)

    if len(discovered) < 6:
        print(
            f"Error: Minimum discovery bound not met (expected >= 6, got {len(discovered)})",
            file=sys.stderr,
        )
        return 1

    drifted: List[Path] = []

    for skill_file in discovered:
        # H1 Target Confinement
        if skill_file.name != "SKILL.md":
            print(f"Skipping {skill_file}: Not SKILL.md", file=sys.stderr)
            continue
        if skill_file.is_symlink():
            print(f"Skipping {skill_file}: Symlink write rejected", file=sys.stderr)
            continue
        if not skill_file.resolve().is_relative_to(skills_dir.resolve()):
            print(f"Skipping {skill_file}: Outside {skills_dir}", file=sys.stderr)
            continue

        existing_section = extract_persona_section(skill_file)
        if existing_section is None or existing_section.strip() != canonical_text:
            drifted.append(skill_file)

    if not apply:
        if drifted:
            print(f"Drift detected in {len(drifted)} skills:")
            for p in drifted:
                print(f"  - {p.parent.name}")
            return 1
        print("Check passed: All CLI agent skills match canonical Persona Registry.")
        return 0

    # Apply updates
    enforce_worktree_confinement()
    updated_count = 0

    for skill_file in drifted:
        content = skill_file.read_text(encoding="utf-8")
        match = PERSONA_SECTION_PATTERN.search(content)

        if match:
            # Replace matched section
            new_content = (
                content[:match.start()]
                + canonical_text
                + "\n\n"
                + content[match.end():]
            )
        else:
            # If skill had no existing section (e.g. local-llm-setup), insert before Smoke Test or EOF
            smoke_match = re.search(r"(?ms)(^##\s+.*?Smoke Test|\Z)", content)
            if smoke_match and smoke_match.start() > 0:
                pos = smoke_match.start()
                new_content = content[:pos] + canonical_text + "\n\n---\n\n" + content[pos:]
            else:
                new_content = content.rstrip() + "\n\n---\n\n" + canonical_text + "\n"

        # Atomic write
        tmp_path = skill_file.with_suffix(".tmp")
        original_mode = skill_file.stat().st_mode
        tmp_path.write_text(new_content, encoding="utf-8")
        os.chmod(tmp_path, original_mode)
        os.replace(tmp_path, skill_file)
        updated_count += 1
        print(f"Updated {skill_file.parent.name}/SKILL.md")

    print(f"Successfully synced {updated_count} CLI agent skills.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync CLI Persona Registry across CLI agent skills.")
    parser.add_argument("--check", action="store_true", help="Read-only check for drift against canonical template.")
    parser.add_argument("--apply", action="store_true", help="Apply canonical template inline to CLI skills.")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE_PATH, help="Path to template file.")
    parser.add_argument("--skills-dir", type=Path, default=SKILLS_DIR, help="Skills directory.")

    args = parser.parse_args()

    if args.apply:
        enforce_worktree_confinement()

    return sync_personas(
        template_path=args.template.resolve(),
        skills_dir=args.skills_dir.resolve(),
        apply=args.apply,
    )


if __name__ == "__main__":
    sys.exit(main())
