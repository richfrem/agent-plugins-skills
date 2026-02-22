#!/usr/bin/env python3
"""
Sync Skills Bridge
------------------
Synchronizes skill directories from .agent/skills/ to the native skill
locations expected by each AI agent:

  - Claude Code:  .claude/skills/<skill-name>/SKILL.md
  - Copilot:      .github/skills/<skill-name>/SKILL.md
  - Gemini:       .agent/skills/ (native, no copy needed)

Role in Architecture:
This script acts as the "Final Mile" distributor.
1. Plugin Manager installs skills to `.agent/skills`.
2. This script propagates them to `.claude` and `.github`.

Usage:
    python3 plugins/spec-kitty/sync_skills.py --all
    python3 plugins/spec-kitty/sync_skills.py --clean  (remove old injected blocks only)

References:
    - https://docs.anthropic.com/en/docs/claude-code/skills#where-skills-live
    - https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
    - https://agentskills.io/specification
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
SOURCE_SKILLS_DIR = PROJECT_ROOT / ".agent" / "skills"

# Native skill directories for each agent
SKILL_TARGETS = {
    "CLAUDE": PROJECT_ROOT / ".claude" / "skills",
    "COPILOT": PROJECT_ROOT / ".github" / "skills",
    # Gemini reads .agent/skills/ natively - no copy needed
}

# Monolithic config files that may have old injected blocks to clean up
CONFIG_FILES = {
    "CLAUDE": PROJECT_ROOT / ".claude" / "CLAUDE.md",
    "COPILOT": PROJECT_ROOT / ".github" / "copilot-instructions.md",
    "GEMINI": PROJECT_ROOT / "GEMINI.md",
}

MARKER_START = "<!-- SKILLS_SYNC_START -->"
MARKER_END = "<!-- SKILLS_SYNC_END -->"


def clean_injected_blocks():
    """Remove any previously injected SKILLS_SYNC blocks from config files."""
    cleaned = False
    for name, config_path in CONFIG_FILES.items():
        if not config_path.exists():
            continue

        content = config_path.read_text(encoding="utf-8")

        if MARKER_START in content and MARKER_END in content:
            pre = content.split(MARKER_START)[0]
            post = content.split(MARKER_END)[1]
            # Remove trailing whitespace from the join point
            updated = pre.rstrip("\n") + post
            config_path.write_text(updated, encoding="utf-8")
            print(f"[{name}] Removed old SKILLS_SYNC block from {config_path.name}")
            cleaned = True
        else:
            print(f"[{name}] No SKILLS_SYNC block found in {config_path.name} (clean)")

    return cleaned


def copy_skills():
    """Copy skill directories from .agent/skills/ to native agent locations."""
    if not SOURCE_SKILLS_DIR.exists():
        print(f"Error: Source skills directory not found: {SOURCE_SKILLS_DIR}")
        sys.exit(1)

    # Discover all skill directories (must contain SKILL.md)
    skills = []
    for skill_dir in sorted(SOURCE_SKILLS_DIR.iterdir()):
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            skills.append(skill_dir)

    if not skills:
        print("No skills found in .agent/skills/")
        return

    print(f"Found {len(skills)} skill(s): {[s.name for s in skills]}")

    for target_name, target_dir in SKILL_TARGETS.items():
        # Create target skills directory if it doesn't exist
        target_dir.mkdir(parents=True, exist_ok=True)

        for skill_source in skills:
            skill_name = skill_source.name
            skill_dest = target_dir / skill_name

            # Remove existing copy to ensure clean sync
            if skill_dest.exists():
                shutil.rmtree(skill_dest)

            # Copy the entire skill directory
            shutil.copytree(skill_source, skill_dest)
            print(f"  [{target_name}] Copied {skill_name}/ -> {skill_dest.relative_to(PROJECT_ROOT)}")

        print(f"[{target_name}] Synced {len(skills)} skill(s) to {target_dir.relative_to(PROJECT_ROOT)}/")

    print(f"\n[GEMINI] .agent/skills/ is the native location - no copy needed.")


def main():
    parser = argparse.ArgumentParser(
        description="Sync agent skills to native directories per Agent Skills spec."
    )
    parser.add_argument("--all", action="store_true",
                        help="Copy ALL skills from .agent/skills/ to native agent directories")
    parser.add_argument("--clean", action="store_true",
                        help="Only remove old injected SKILLS_SYNC blocks from config files")
    args = parser.parse_args()

    if not args.all and not args.clean:
        print("Usage: provide --all (copy skills + clean) or --clean (clean only)")
        sys.exit(1)

    # Always clean up old injected blocks first
    print("=== Step 1: Cleaning old SKILLS_SYNC blocks from config files ===")
    clean_injected_blocks()

    if args.all:
        print("\n=== Step 2: Copying skills to native agent directories ===")
        copy_skills()

    print("\nDone.")


if __name__ == "__main__":
    main()
