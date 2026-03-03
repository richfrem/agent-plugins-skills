#!/usr/bin/env python3
"""
Spec Kitty Configuration Sync
=============================

Synchronizes fresh artifacts from the local workspace back into the plugin's
source of truth directories for distribution via the Bridge.

Artifacts:
1. Workflows (.windsurf/workflows -> plugins/spec-kitty/commands)
2. Rules (.kittify/memory -> plugins/spec-kitty/rules)

Assumptions:
1. User has installed the 'spec-kitty' CLI: `pip install --upgrade spec-kitty-cli`
2. User has initialized the repository: `spec-kitty init . --ai windsurf`
3. Run this script to propagate updates into the plugin system.

Usage:
    python3 plugins/spec-kitty/skills/spec-kitty-agent/scripts/sync_configuration.py
"""

import shutil
import os
import re
from pathlib import Path
from typing import NoReturn

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
ROOT = PROJECT_ROOT

# Sources
WORKFLOWS_SOURCE_DIR = ROOT / ".windsurf/workflows"
RULES_SOURCE_DIR = ROOT / ".kittify/memory"
AGENTS_RULES_SRC = ROOT / ".kittify/AGENTS.md"
TEMPLATES_SOURCE_DIR = ROOT / ".kittify/missions/research/command-templates"

# Destinations
WORKFLOWS_DEST_DIR = ROOT / "plugins/spec-kitty-plugin/commands"
RULES_DEST_DIR = ROOT / "plugins/spec-kitty-plugin/rules"
TEMPLATES_DEST_DIR = ROOT / "plugins/spec-kitty-plugin/templates"

# Legacy Cleanup
LEGACY_WORKFLOWS_DIR = ROOT / "plugins/spec-kitty-plugin/workflows"

def sync_workflows() -> None:
    """Syncs workflow files from Windsurf source to plugin commands."""
    if not WORKFLOWS_SOURCE_DIR.exists():
        print(f"⚠️  Workflows source not found: {WORKFLOWS_SOURCE_DIR}")
        return

    print(f"🔄 Syncing workflows from {WORKFLOWS_SOURCE_DIR} to {WORKFLOWS_DEST_DIR}...")
    WORKFLOWS_DEST_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for src_file in WORKFLOWS_SOURCE_DIR.glob("*.md"):
        # Format skill name from filename (e.g., spec-kitty.plan.md -> spec-kitty-plan)
        skill_name = src_file.stem
        if skill_name.endswith(".md"):
            skill_name = skill_name.rsplit(".md", maxsplit=1)[0]
        
        # Determine the user-facing name for the YAML
        display_name = skill_name.replace("spec-kitty.", "Spec Kitty ").replace(".", " ").title()
        
        # Create skill directory
        skill_dir = WORKFLOWS_DEST_DIR / skill_name.replace(".", "-")
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # Read source content
        content = src_file.read_text(encoding="utf-8")
        
        # Parse existing frontmatter if present
        description = "A standard Spec-Kitty workflow routine."
        body_content = content
        
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                body_content = parts[2].lstrip()
                
                # Try to extract existing description
                desc_match = re.search(r'^description:\s*(.*?)$', frontmatter, re.MULTILINE)
                if desc_match:
                    description = desc_match.group(1).strip()
        
        # Generate formal SKILL.md
        skill_md_path = skill_dir / "SKILL.md"
        
        new_content = f"""---
name: {skill_name.replace(".", "-")}
description: {description}
---

{body_content}"""

        skill_md_path.write_text(new_content, encoding="utf-8")
        count += 1

    print(f"   ✅ Generated {count} skills.")

    if LEGACY_WORKFLOWS_DIR.exists():
        print(f"🗑️  Removing legacy workflows dir: {LEGACY_WORKFLOWS_DIR}")
        shutil.rmtree(LEGACY_WORKFLOWS_DIR)

def sync_rules() -> None:
    """Syncs rule files and templates from Kittify source to plugin rules."""
    print(f"🔄 Syncing rules from Kittify to {RULES_DEST_DIR}...")
    RULES_DEST_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATES_DEST_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    # 1. Sync memory rules
    if RULES_SOURCE_DIR.exists():
        for src_file in RULES_SOURCE_DIR.glob("*.md"):
            dest_file = RULES_DEST_DIR / src_file.name
            shutil.copy2(src_file, dest_file)
            count += 1
            
    # 2. Sync AGENTS.md rule
    if AGENTS_RULES_SRC.exists():
        dest_file = RULES_DEST_DIR / AGENTS_RULES_SRC.name
        shutil.copy2(AGENTS_RULES_SRC, dest_file)
        count += 1

    print(f"   ✅ Synced {count} rules.")
    
    # 3. Sync Templates
    template_count = 0
    if TEMPLATES_SOURCE_DIR.exists():
        for src_file in TEMPLATES_SOURCE_DIR.glob("*.md"):
            dest_file = TEMPLATES_DEST_DIR / src_file.name
            shutil.copy2(src_file, dest_file)
            template_count += 1
            
    print(f"   ✅ Synced {template_count} templates.")

def main() -> None:
    print("🚀 Synchronizing Spec-Kitty configurations...")
    sync_workflows()
    sync_rules()
    
    print("\n⚠️  NEXT STEP: Propagate to Agents")
    print("   Run: python plugins/plugin-mapper/skills/agent-bridge/scripts/bridge_installer.py --plugin plugins/spec-kitty-plugin --target <your_ide>")

if __name__ == "__main__":
    main()
