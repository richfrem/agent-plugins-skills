#!/usr/bin/env python3
"""
Spec Kitty Configuration Sync
=============================

Synchronizes fresh artifacts from the local workspace back into the plugin's
source of truth directories for distribution via the Bridge.

Artifacts:
1. Workflows (.windsurf/workflows -> ../../skills)
2. Rules (.kittify/memory -> ../../rules)

Assumptions:
1. User has installed the 'spec-kitty' CLI: `pip install --upgrade spec-kitty-cli`
2. User has initialized the repository: `spec-kitty init . --ai windsurf`
3. Run this script to propagate updates into the plugin system.

Usage:
    python3 ./scripts/sync_configuration.py
"""

import shutil
import os
import re
from pathlib import Path
from typing import NoReturn

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
PLUGIN_ROOT = Path(__file__).parent.parent

# Sources
WORKFLOWS_SOURCE_DIR = PROJECT_ROOT / ".windsurf/workflows"
RULES_SOURCE_DIR = PROJECT_ROOT / ".kittify/memory"
AGENTS_RULES_SRC = PROJECT_ROOT / ".kittify/AGENTS.md"
TEMPLATES_SOURCE_DIR = PROJECT_ROOT / ".kittify/missions"

# Destinations
WORKFLOWS_DEST_DIR = PLUGIN_ROOT / "skills"
RULES_DEST_DIR = PLUGIN_ROOT / "rules"
TEMPLATES_DEST_DIR = PLUGIN_ROOT / "assets" / "templates"
WORKFLOWS_PLUGIN_DIR = PLUGIN_ROOT / "workflows"

# Legacy Cleanup
LEGACY_COMMANDS_DIR = PLUGIN_ROOT / "commands"

def sync_workflows() -> None:
    """Syncs workflow files from Windsurf source to plugin commands."""
    if not WORKFLOWS_SOURCE_DIR.exists():
        print(f"⚠️  Workflows source not found: {WORKFLOWS_SOURCE_DIR}")
        return

    print(f"🔄 Syncing workflows from {WORKFLOWS_SOURCE_DIR} to {WORKFLOWS_DEST_DIR}...")
    WORKFLOWS_DEST_DIR.mkdir(parents=True, exist_ok=True)
    WORKFLOWS_PLUGIN_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Sync Base Workflows to Plugin Root as Master Symlinks
    for src_file in WORKFLOWS_SOURCE_DIR.glob("*.md"):
        dest_file = WORKFLOWS_PLUGIN_DIR / src_file.name
        rel_target = os.path.relpath(src_file, dest_file.parent)
        
        if dest_file.is_symlink() or dest_file.exists():
            dest_file.unlink()
        dest_file.symlink_to(rel_target)

    count = 0
    for src_file in WORKFLOWS_SOURCE_DIR.glob("*.md"):
        # Format skill name from filename (e.g., spec-kitty.plan.md -> spec-kitty-plan)
        skill_name = src_file.stem
        if skill_name.endswith(".md"):
            skill_name = skill_name.rsplit(".md", maxsplit=1)[0]
        
        # Determine the user-facing name for the YAML
        display_name = skill_name.replace("spec-kitty.", "Spec Kitty ").replace(".", " ").title()
        
        # Create skill directory (AgentSkills 2.0 Native Wrapper)
        skill_dir = WORKFLOWS_DEST_DIR / skill_name.replace(".", "-")
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # Enforce AgentSkills Optional Directories
        for opt_dir in ["scripts", "references", "assets", "evals"]:
            (skill_dir / opt_dir).mkdir(exist_ok=True)
        
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
        
        # Create local skill symlink inside the specific skill workflows directory
        skill_workflows_dir = skill_dir / "workflows"
        skill_workflows_dir.mkdir(parents=True, exist_ok=True)
        skill_symlink = skill_workflows_dir / src_file.name
        rel_asset_target = os.path.relpath(WORKFLOWS_PLUGIN_DIR / src_file.name, skill_symlink.parent)
        
        # Cleanup old direct symlink if it exists
        legacy_root_symlink = skill_dir / src_file.name
        if legacy_root_symlink.is_symlink() or legacy_root_symlink.exists():
            legacy_root_symlink.unlink()
        
        if skill_symlink.is_symlink() or skill_symlink.exists():
            skill_symlink.unlink()
        skill_symlink.symlink_to(rel_asset_target)
        
        new_content = f"""---
name: {skill_name.replace(".", "-")}
description: {description}
---

## 🔗 Workflow Provenance

> **Source**: This skill augments the baseline workflow located at [`./workflows/{src_file.name}`](./workflows/{src_file.name}).
> It acts as an intelligent wrapper that is continuously improved with each execution.

{body_content}"""

        skill_md_path.write_text(new_content, encoding="utf-8")
        count += 1

    print(f"   ✅ Generated {count} skills.")

    # Note: Legacy workflows directory is now actively used as the master symlink folder
        
    if LEGACY_COMMANDS_DIR.exists():
        print(f"🗑️  Removing legacy commands dir: {LEGACY_COMMANDS_DIR}")
        shutil.rmtree(LEGACY_COMMANDS_DIR)

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
        for src_file in TEMPLATES_SOURCE_DIR.rglob("*.md"):
            rel_path = src_file.relative_to(PROJECT_ROOT)
            dest_file = TEMPLATES_DEST_DIR / rel_path
            
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            rel_target = os.path.relpath(src_file, dest_file.parent)
            
            if dest_file.is_symlink():
                if os.readlink(dest_file) != rel_target:
                    dest_file.unlink()
                    dest_file.symlink_to(rel_target)
            elif dest_file.exists():
                dest_file.unlink()
                dest_file.symlink_to(rel_target)
            else:
                dest_file.symlink_to(rel_target)
                
            template_count += 1
            
    print(f"   ✅ Synced {template_count} template symlinks.")

def main() -> None:
    print("🚀 Synchronizing Spec-Kitty configurations...")
    sync_workflows()
    sync_rules()
    
    print("\n⚠️  AGENT INSTRUCTION:")
    print("   The local repository is now synced. Ask the user if they want to use their ecosystem's plugin bridge to install or update `plugins/spec-kitty-plugin` for their active AI environment.")

if __name__ == "__main__":
    main()
