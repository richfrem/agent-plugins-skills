---
concept: paths
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/spec-kitty-implement/scripts/sync_configuration.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.412315+00:00
cluster: spec
content_hash: 5041d2a977179bf5
---

# Paths

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/spec-kitty-implement/scripts/sync_configuration.py -->
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
        shutil.copy2(src_file, dest_file)

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
        skill_workflows_dir.mkdir(parents=True, exist_ok=True

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/spec-kitty-merge/scripts/sync_configuration.py -->
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
PROJECT_ROOT = Path(__file__).pare

*(combined content truncated)*

## See Also

- [[1-handle-absolute-paths-from-repo-root]]
- [[match-pythonexecution-paths-that-are-hardcoded-to-the-repo-root-plugins-folder]]
- [[plugin-paths-whitelist]]
- [[project-paths]]
- [[resolve-paths]]
- [[setup-paths]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/spec-kitty-implement/scripts/sync_configuration.py`
- **Indexed:** 2026-04-27T05:21:04.412315+00:00
