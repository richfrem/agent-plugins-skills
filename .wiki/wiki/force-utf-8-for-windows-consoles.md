---
concept: force-utf-8-for-windows-consoles
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/maintain-plugins/scripts/audit_structure.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.249314+00:00
cluster: plugin_path
content_hash: 58d8dfbae60507f5
---

# Force UTF-8 for Windows Consoles

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

"""
Audit Plugin Structure
======================

Purpose:
    Fast filesystem sanity-check that all plugins follow the standard structure:
    - plugins/<plugin>/skills/<skill>/SKILL.md present
    - plugins/<plugin>/skills/<skill>/scripts/ (preferred over top-level scripts/)
    - No non-exempt top-level scripts/ directory

Layer: Plugin Manager / Structure Validation

Usage Examples:
    python3 plugins/plugin-manager/scripts/audit_structure.py

Supported Object Types:
    - None (Filesystem scan)

CLI Arguments:
    None.

Input Files:
    - None (Scans plugins/ directory)

Output:
    - Status messages and error reports.

Key Functions:
    audit_plugin(): Audits structure of a single plugin.

Script Dependencies:
    sys, pathlib

Consumed by:
    - None (Standalone script)
Related:
    - plugins/agent-skill-open-specifications/skills/ecosystem-standards/SKILL.md
      → For a deeper LLM-driven content audit (YAML frontmatter, anti-patterns,
        line limits, SKILL.md quality). Use this after the structure check passes.
"""


# 
import sys
# Force UTF-8 for Windows Consoles
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
PLUGINS_DIR = PROJECT_ROOT / "plugins"

# Exemptions (Legacy or Bridge plugins that might have top-level scripts)
# Ideally, we want 0 exemptions eventually.
TOP_LEVEL_SCRIPTS_EXEMPT = {
    'plugin-manager', 
}

from typing import List, Tuple

def audit_plugin(plugin_path: Path) -> Tuple[List[str], List[str]]:
    errors = []
    warnings = []
    
    plugin_name = plugin_path.name
    
    # 1. Check for 'skills' directory
    skills_dir = plugin_path / "skills"
    has_skills = False
    
    if skills_dir.exists():
        has_skills = True
        # Check individual skills
        for skill_path in skills_dir.iterdir():
            if skill_path.is_dir():
                # Check SKILL.md
                skill_md = skill_path / "SKILL.md"
                if not skill_md.exists():
                    errors.append(f"Skill '{skill_path.name}' missing SKILL.md")
                
                # Check for loose scripts
                for f in skill_path.glob("*.py"):
                     warnings.append(f"Skill '{skill_path.name}' has loose python script '{f.name}'. Move to scripts/?")
    else:
        # Skills are optional if other components exist (commands, agents, mcp)
        has_other = (plugin_path / "commands").exists() or \
                    (plugin_path / "agents").exists() or \
                    (plugin_path / ".mcp.json").exists() or \
                    (plugin_path / ".claude-plugin" / "plugin.json").exists() # Bare minimum
        
        if not has_other:
             errors.append(f"Empty plugin? Missing skills/, commands/, or agents/.")
        else:
             warnings.append(f"No 'skills/' directory (Optional).")

    # 3. Check for deprecated top-level directories
    if (plugin_path / "scripts").exists() and plugin_name not in TOP_LEVEL_SCRIPTS_EXEMPT:
        # Check if it's empty
        if any((plugin_path / "scripts").iterdir()):
             errors.append(f"Has top-level 'scripts/' directory (NON-STANDARD). Move to skills/<skill>/scripts/.")
    
    if (plugin_path / "docs").exists():
         warnings.append(f"Has top-level 'docs/' directory. Consider moving to skills/<skill>/references/.")

    return errors, warnings

def main() -> None:
    print(f"🏗️  Auditing Plugin Structure in {PLUGINS_DIR}...\n")
    
    results = {}
    
    for plugin_path in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_path.is_dir(): continue
        if plugin_path.name.startswith("."): continue
        if plugin_path.name == "__pycache__": continue
        
        errors, warnings = audit_plugin(plugin_path)
        if errors or warnings:
            results[plugin_path.name] = {"errors": errors, "warnings"

*(content truncated)*

## See Also

- [[force-utf-8-output-on-windows-if-possible]]
- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]
- [[attempt-to-handle-langchain-version-differences-for-storage]]
- [[check-all-text-files-in-skill-for-regex-py-mentions]]
- [[check-for-broken-symlinks]]
- [[check-if-we-already-emitted-for-this-completion-avoid-duplicate-events]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/maintain-plugins/scripts/audit_structure.py`
- **Indexed:** 2026-04-27T05:21:04.249314+00:00
