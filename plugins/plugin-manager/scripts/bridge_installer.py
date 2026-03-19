#!/usr/bin/env python3
"""
bridge_installer.py (CLI)
=====================================

Purpose:
    Installs Agent Plugins into .agents/ central repository natively 
    and symlinks them across locally installed agent platforms 
    (mimicking the behavior of npx skills add --force).

Usage Examples:
    python3 bridge_installer.py --plugin <path>
"""

import os
import sys
import shutil
import json
import argparse
from pathlib import Path

# The standard recognized agent configurations in your IDE workspace.
DETECTABLE_AGENTS = {
    ".agent": "antigravity",
    ".claude": "claude",
    ".github": "github",
    ".gemini": "gemini",
    ".azure": "azure"
}

def provision_central_and_symlink(plugin_path: Path, metadata: dict, targets: list[str]):
    root = Path.cwd()
    plugin_name = metadata.get("name", plugin_path.name)
    
    # 1. Ensure central `c:/Users/RICHFREM/source/repos/agent-plugins-skills/.agents` exists
    agents_root = root / ".agents"
    agents_root.mkdir(exist_ok=True)
    
    # 2. Central Skills
    skills_dir = plugin_path / "skills"
    central_skills = agents_root / "skills"
    
    if skills_dir.exists():
        central_skills.mkdir(exist_ok=True)
        # Deep copy the real sources
        for item in skills_dir.iterdir():
            if item.is_dir():
                dest = central_skills / item.name
                shutil.copytree(item, dest, dirs_exist_ok=True)
                print(f"  ✓ Universal central copy: {dest.relative_to(root)}")

                # 3. Iterate local agent folders and establish symlinks
                for target_dir_name in targets:
                    ide_dir = root / target_dir_name
                    if not ide_dir.exists():
                        continue
                    
                    ide_skills = ide_dir / "skills"
                    ide_skills.mkdir(exist_ok=True)
                    
                    target_symlink = ide_skills / item.name
                    
                    # Clean out previous symlinks strictly
                    if target_symlink.exists() or target_symlink.is_symlink():
                        if target_symlink.is_dir() and not target_symlink.is_symlink():
                            shutil.rmtree(target_symlink)
                        else:
                            target_symlink.unlink()
                            
                    try:
                        rel = os.path.relpath(dest, target_symlink.parent)
                        os.symlink(rel, target_symlink)
                    except Exception:
                        os.symlink(dest.absolute(), target_symlink)
                        
                    env_name = DETECTABLE_AGENTS.get(target_dir_name, target_dir_name)
                    print(f"    -> Symlinked for {env_name}: {target_symlink.relative_to(root)}")
                    
    # 4. Standalone Agents (Convert native agent artifacts to AgentSkills wrappers)
    agents_dir_src = plugin_path / "agents"
    if agents_dir_src.exists():
        for agent_file in agents_dir_src.glob("*.md"):
            agent_name = agent_file.stem
            final_name = plugin_name if plugin_name.endswith(agent_name) else f"{plugin_name}-{agent_name}"
            
            dest = central_skills / final_name
            dest.mkdir(parents=True, exist_ok=True)
            for opt_dir in ["scripts", "references", "assets", "evals"]:
                (dest / opt_dir).mkdir(exist_ok=True)
            
            shutil.copy2(agent_file, dest / "SKILL.md")
            print(f"  ✓ Universal central copy (Agent Wrapper): {dest.relative_to(root)}")
            
            for target_dir_name in targets:
                ide_dir = root / target_dir_name
                if not ide_dir.exists():
                    continue
                ide_skills = ide_dir / "skills"
                ide_skills.mkdir(exist_ok=True)
                
                target_symlink = ide_skills / final_name
                if target_symlink.exists() or target_symlink.is_symlink():
                    if target_symlink.is_dir() and not target_symlink.is_symlink():
                        shutil.rmtree(target_symlink)
                    else:
                        target_symlink.unlink()
                        
                try:
                    rel = os.path.relpath(dest, target_symlink.parent)
                    os.symlink(rel, target_symlink)
                except Exception:
                    os.symlink(dest.absolute(), target_symlink)

    # 5. Native Hooks (e.g. for PreToolUse, Subagent events)
    hooks_file = plugin_path / "hooks" / "hooks.json"
    if hooks_file.exists():
        central_hooks = agents_root / "hooks"
        central_hooks.mkdir(exist_ok=True)
        dest = central_hooks / f"{plugin_name}-hooks.json"
        shutil.copy2(hooks_file, dest)
        
        for target_dir_name in targets:
            ide_dir = root / target_dir_name
            # Hooks generally only deployed to Claude environment
            if not ide_dir.exists() or target_dir_name not in [".claude"]:
                continue 
            
            ide_hooks = ide_dir / "hooks"
            ide_hooks.mkdir(exist_ok=True)
            
            target_symlink = ide_hooks / dest.name
            if target_symlink.exists() or target_symlink.is_symlink():
                target_symlink.unlink()
            try:
                os.symlink(os.path.relpath(dest, target_symlink.parent), target_symlink)
            except Exception:
                os.symlink(dest.absolute(), target_symlink)
            print(f"    -> Hook Symlinked for claude: {target_symlink.relative_to(root)}")


def main():
    parser = argparse.ArgumentParser(description="Plugin Bridge Installer (.agents symlinking)")
    parser.add_argument("--plugin", required=True, help="Path to plugin directory")
    args = parser.parse_args()

    plugin_path = Path(args.plugin).resolve()
    if not plugin_path.exists():
        print(f"Error: Plugin path not found: {plugin_path}")
        sys.exit(1)

    manifest = plugin_path / ".claude-plugin" / "plugin.json"
    metadata = {}
    if manifest.exists():
        metadata = json.loads(manifest.read_text(encoding='utf-8'))
    else:
        metadata = {"name": plugin_path.name}

    root = Path.cwd()
    targets = [t for t in DETECTABLE_AGENTS.keys() if (root / t).exists()]
    
    print(f"\nInstalling plugin '{metadata['name']}' using target symlinking (.agents/ Strategy).")
    print(f"Detected IDE environments: {', '.join(targets)}")

    provision_central_and_symlink(plugin_path, metadata, targets)
    
if __name__ == "__main__":
    main()
