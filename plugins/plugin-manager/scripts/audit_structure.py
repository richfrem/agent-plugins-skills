#!/usr/bin/env python3
"""
Audit Plugin Structure
======================

Purpose:
    Fast filesystem sanity-check that all plugins follow the standard structure:
    - plugins/<plugin>/skills/<skill>/SKILL.md present
    - plugins/<plugin>/skills/<skill>/scripts/ (preferred over top-level scripts/)
    - No non-exempt top-level scripts/ directory

Layer: Plugin Manager / Structure Validation

Usage:
    python3 plugins/plugin-manager/scripts/audit_structure.py

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

def audit_plugin(plugin_path: Path):
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

def main():
    print(f"🏗️  Auditing Plugin Structure in {PLUGINS_DIR}...\n")
    
    results = {}
    
    for plugin_path in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_path.is_dir(): continue
        if plugin_path.name.startswith("."): continue
        if plugin_path.name == "__pycache__": continue
        
        errors, warnings = audit_plugin(plugin_path)
        if errors or warnings:
            results[plugin_path.name] = {"errors": errors, "warnings": warnings}

    # Report
    if not results:
        print("✨ All plugins follow standard structure!")
        sys.exit(0)
        
    print(f"⚠️  Found issues in {len(results)} plugins:\n")
    
    error_count = 0
    
    for plugin, inconsistencies in results.items():
        if inconsistencies["errors"]:
            print(f"❌ {plugin}:")
            for e in inconsistencies["errors"]:
                print(f"   - {e}")
                error_count += 1
        
        if inconsistencies["warnings"]:
            if not inconsistencies["errors"]:
                print(f"⚠️  {plugin}:")
            for w in inconsistencies["warnings"]:
                print(f"   - {w}")
        print("")

    if error_count > 0:
        print(f"❌ Total Errors: {error_count}")
        sys.exit(1)
    else:
        print("✅ No critical errors found (only warnings).")
        sys.exit(0)

if __name__ == "__main__":
    main()
