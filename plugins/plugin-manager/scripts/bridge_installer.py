"""
Bridge Installer (CLI)
=====================

Purpose:
    Installs Agent Plugins into .agents/ central repository natively 
    and symlinks them across locally installed agent platforms 
    (mimicking the behavior of npx skills add --force).

Layer: Plugin Manager / Installation

Usage Examples:
    python3 plugins/plugin-manager/scripts/bridge_installer.py --plugin plugins/my-pluginF
    
    # install plugin in a different repo e.g. context-bundler specifically
    python <full install path>\agent-plugins-skills\plugins\plugin-manager\scripts\bridge_installer.py --plugin <full install path>\agent-plugins-skills\plugins\context-bundler

Supported Object Types:
    - None (Filesystem operations)

CLI Arguments:
    --plugin: Path to plugin directory (Required)
    --dry-run: Preview actions without writing files

Input Files:
    - .claude-plugin/plugin.json (Manifest reader)

Output:
    - Creates symlinks and updates skills-lock.json

Key Functions:
    _is_pointer_file(): Checks if file is a pointer.
    _copy_resolving_pointers(): Copies resolving pointers.
    _symlink_or_copy(): Symlinks or copies fallback.
    _write_toml_command(): Writes TOML command wrapper.
    deploy_commands(): Deploys commands.
    deploy_agents(): Deploys agents.
    deploy_rules(): Deploys rules.
    write_project_lock(): Writes project lockfile.
    provision_central_and_symlink(): Provisions central and symlinks.

Script Dependencies:
    os, sys, shutil, json, argparse, datetime, pathlib

Consumed by:
    - None (Standalone script)
"""

import os
import sys
import shutil
import json
import argparse
import datetime
from pathlib import Path

# Force UTF-8 output on Windows to avoid UnicodeEncodeError with emoji in print()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# The standard recognized agent configurations in your IDE workspace.
DETECTABLE_AGENTS = {
    ".agent": {
        "name": "antigravity",
        "skills": ".agent/skills",
        "commands": ".agent/workflows",
        "rules": ".agent/rules",
        "hooks": None,
        "rules_mode": "files",
    },
    ".claude": {
        "name": "claude",
        "skills": ".claude/skills",
        "agents": ".claude/agents",
        "commands": ".claude/commands",
        "rules": None,
        "rules_append_target": "CLAUDE.md",
        "hooks": ".claude/hooks",
        "rules_mode": "append",
    },
    ".gemini": {
        "name": "gemini",
        "skills": ".gemini/skills",
        "commands": ".gemini/commands",
        "rules": None,
        "rules_append_target": "GEMINI.md",
        "hooks": None,
        "rules_mode": "append",
        "commands_format": "toml",
    },
    ".github": {
        "name": "github",
        "skills": ".github/skills",
        "commands": ".github/prompts",
        "rules": None,
        "rules_append_target": ".github/copilot-instructions.md",
        "hooks": None,
        "rules_mode": "append",
        "commands_ext": ".prompt.md",
    },
    ".azure": {
        "name": "azure",
        "skills": ".azure/skills",
        "commands": None,
        "rules": None,
        "hooks": None,
    },
}

def _is_pointer_file(path: Path) -> bool:
    """Return True if the file is a single-line relative-path pointer (no real content)."""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore").strip()
        return "\n" not in content and content.startswith("../")
    except Exception:
        return False


def _copy_resolving_pointers(src_dir: Path, dst_dir: Path) -> None:
    """Recursively copy src_dir to dst_dir.
    Pointer files (single-line '../...' paths) are resolved to their real target
    so the installed copy in .agents/ is fully self-contained and works in any
    consuming project that has no plugins/ source tree.
    """
    dst_dir.mkdir(parents=True, exist_ok=True)
    for item in src_dir.iterdir():
        dst_item = dst_dir / item.name
        if item.is_dir():
            _copy_resolving_pointers(item, dst_item)
        elif item.is_file():
            try:
                if _is_pointer_file(item):
                    # Resolve the pointer relative to the file's location
                    rel_target = item.read_text(encoding="utf-8").strip()
                    real_src = (item.parent / rel_target).resolve()
                    if real_src.exists():
                        if real_src.is_dir():
                            shutil.copytree(real_src, dst_item, dirs_exist_ok=True)
                        else:
                            shutil.copy2(real_src, dst_item)
                    else:
                        # Pointer target missing — copy the pointer as-is (best effort)
                        shutil.copy2(item, dst_item)
                else:
                    shutil.copy2(item, dst_item)
            except PermissionError:
                # File is locked by another process (e.g. IDE has it open) — skip,
                # the existing installed copy remains in place.
                print(f"    ! Skipped locked file: {dst_item.name}")


def _symlink_or_copy(src: Path, link_path: Path, dry_run: bool,
                     root: Path, env_name: str) -> bool:
    if dry_run:
        print(f"  [DRY RUN] symlink {link_path.relative_to(root)} -> {src.relative_to(root)}")
        return True

    # Clean existing — use lexists so broken junctions/symlinks (target gone) are also detected.
    # On Windows, a broken junction has .exists()=False and .is_symlink()=False, so we must
    # also check os.path.lexists() and os.path.isjunction() to avoid skipping stale entries.
    _is_broken_or_exists = (
        link_path.exists()
        or link_path.is_symlink()
        or os.path.lexists(str(link_path))
        or (hasattr(os.path, 'isjunction') and os.path.isjunction(link_path))
    )
    if _is_broken_or_exists:
        is_link = (link_path.is_symlink() or os.path.islink(str(link_path))
                   or (hasattr(os.path, 'isjunction') and os.path.isjunction(link_path)))
        if link_path.is_dir() and not is_link:
            shutil.rmtree(link_path)
        else:
            try:
                link_path.unlink()
            except PermissionError:
                try:
                    os.rmdir(link_path)
                except PermissionError:
                    print(f"    ! Skipped locked entry: {link_path.name}")
                    return False

    try:
        rel = os.path.relpath(src, link_path.parent)
        if os.name == 'nt':
            os.symlink(rel, link_path, target_is_directory=src.is_dir())
        else:
            os.symlink(rel, link_path)
        print(f"    -> Symlinked for {env_name}: {link_path.relative_to(root)}")
        return True
    except (OSError, NotImplementedError):
        if os.name == 'nt' and src.is_dir():
            import subprocess
            try:
                subprocess.run(["cmd", "/c", "mklink", "/J", str(link_path), str(src)],
                               check=True, capture_output=True)
                print(f"    -> Symlinked (Junction) for {env_name}: {link_path.relative_to(root)}")
                return True
            except Exception:
                pass

        # Windows fallback: copy instead of symlink
        try:
            if src.is_dir():
                shutil.copytree(src, link_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src, link_path)
            print(f"    -> Copied (symlink failed) for {env_name}: "
                  f"{link_path.relative_to(root)}")
            return False  # False = symlinkFailed, like npx skills
        except Exception as e:
            print(f"    X Failed for {env_name}: {e}")
            return False

def _write_toml_command(md_file: Path, dest_toml: Path, plugin_name: str, flat: str, dry_run: bool, root: Path) -> None:
    if dry_run:
        print(f"  [DRY RUN] write TOML cmd: {dest_toml.relative_to(root)}")
        return
        
    content = md_file.read_text(encoding="utf-8")
    
    # Very basic frontmatter parser
    description = ""
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm = parts[1]
            body = parts[2].strip()
            for line in fm.splitlines():
                if line.startswith("description:"):
                    description = line.replace("description:", "", 1).strip()
                    # Strip basic quotes
                    if description.startswith('"') and description.endswith('"'):
                        description = description[1:-1]
                    elif description.startswith("'") and description.endswith("'"):
                        description = description[1:-1]

    toml_content = f"""command = "{plugin_name}:{flat}"
description = "{description}"
prompt = \"\"\"
{body}
\"\"\"
"""
    dest_toml.write_text(toml_content, encoding="utf-8")
    print(f"    -> Wrapped TOML for gemini: {dest_toml.relative_to(root)}")


def deploy_commands(plugin_path: Path, plugin_name: str, targets: list[str],
                    root: Path, dry_run: bool = False) -> None:
    commands_dir = plugin_path / "commands"
    if not commands_dir.exists():
        return

    central_workflows = root / ".agents" / "workflows"
    if not dry_run:
        central_workflows.mkdir(parents=True, exist_ok=True)

    for cmd_file in sorted(commands_dir.rglob("*.md")):
        content = cmd_file.read_text(encoding="utf-8").strip()
        # Skip pointer files (single-line relative path references)
        if content.startswith("../") and "\n" not in content:
            continue

        # Flatten path to snake_case name
        rel = cmd_file.relative_to(commands_dir)
        flat = "_".join(rel.with_suffix("").parts)
        dest_name = f"{plugin_name}_{flat}"

        # Central canonical copy
        central_dest = central_workflows / f"{dest_name}.md"
        if not dry_run:
            shutil.copy2(cmd_file, central_dest)
        else:
            print(f"  [DRY RUN] copy command: {central_dest.relative_to(root)}")

        for target_dir_name in targets:
            config = DETECTABLE_AGENTS.get(target_dir_name)
            if not config or not config.get("commands"):
                continue

            ide_dir = root / target_dir_name
            if not ide_dir.exists():
                continue

            cmd_dir = root / config["commands"]
            if not dry_run:
                cmd_dir.mkdir(parents=True, exist_ok=True)

            fmt = config.get("commands_format")
            ext = config.get("commands_ext", ".md")

            if fmt == "toml":
                # Parse frontmatter, wrap in TOML
                _write_toml_command(cmd_file, cmd_dir / f"{dest_name}.toml",
                                    plugin_name, flat, dry_run, root)
            else:
                target_link = cmd_dir / f"{dest_name}{ext}"
                _symlink_or_copy(central_dest, target_link, dry_run, root, config["name"])


def deploy_agents(plugin_path: Path, plugin_name: str, targets: list,
                  root: Path, dry_run: bool = False) -> None:
    """Deploy agent .md files to IDE-native agents directories (e.g. .claude/agents/)."""
    agents_dir_src = plugin_path / "agents"
    if not agents_dir_src.exists():
        return

    central_agents = root / ".agents" / "agents"
    if not dry_run:
        central_agents.mkdir(parents=True, exist_ok=True)

    for agent_file in sorted(agents_dir_src.glob("*.md")):
        agent_name = agent_file.stem
        dest_name = f"{plugin_name}-{agent_name}" if not plugin_name.endswith(agent_name) else plugin_name
        central_dest = central_agents / f"{dest_name}.md"

        if not dry_run:
            shutil.copy2(agent_file, central_dest)
        else:
            print(f"  [DRY RUN] central agent copy: .agents/agents/{dest_name}.md")

        for target_dir_name in targets:
            config = DETECTABLE_AGENTS.get(target_dir_name)
            if not config or not config.get("agents"):
                continue

            ide_dir = root / target_dir_name
            if not ide_dir.exists():
                continue

            ide_agents = root / config["agents"]
            if not dry_run:
                ide_agents.mkdir(parents=True, exist_ok=True)

            target_link = ide_agents / f"{dest_name}.md"
            _symlink_or_copy(central_dest, target_link, dry_run, root, config["name"])


def deploy_rules(plugin_path: Path, plugin_name: str, targets: list,
                 root: Path, dry_run: bool = False) -> None:
    rules_dir = plugin_path / "rules"
    if not rules_dir.exists():
        return

    central_rules = root / ".agents" / "rules"
    if not dry_run:
        central_rules.mkdir(parents=True, exist_ok=True)

    for rule_file in sorted(rules_dir.glob("*.md")):
        dest_name = f"{plugin_name}_{rule_file.stem}.md"
        central_dest = central_rules / dest_name
        if not dry_run:
            shutil.copy2(rule_file, central_dest)

        for target_dir_name in targets:
            config = DETECTABLE_AGENTS.get(target_dir_name)
            if not config:
                continue

            ide_dir = root / target_dir_name
            if not ide_dir.exists():
                continue

            if config.get("rules_mode") == "files" and config.get("rules"):
                rules_target_dir = root / config["rules"]
                if not dry_run:
                    rules_target_dir.mkdir(parents=True, exist_ok=True)
                target_link = rules_target_dir / dest_name
                _symlink_or_copy(central_dest, target_link, dry_run, root, config["name"])

            elif config.get("rules_mode") == "append":
                append_target = root / config["rules_append_target"]
                content = rule_file.read_text(encoding="utf-8")
                marker = f"<!-- plugin: {plugin_name} / {rule_file.stem} -->"
                if not dry_run:
                    existing = append_target.read_text(encoding="utf-8") if append_target.exists() else ""
                    if marker not in existing:
                        with open(append_target, "a", encoding="utf-8") as f:
                            f.write(f"\n{marker}\n{content}\n")
                else:
                    try:
                        relative_path = append_target.relative_to(root)
                    except ValueError:
                        relative_path = append_target.name
                    print(f"  [DRY RUN] append rule to {relative_path}")

def write_project_lock(plugin_path: Path, metadata: dict,
                       installed_skills: list[str], root: Path, dry_run: bool = False) -> None:
    if dry_run:
        print(f"  [DRY RUN] skip writing to skills-lock.json ({len(installed_skills)} skills)")
        return
        
    lock_path = root / "skills-lock.json"
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.exists() else {"version": 1, "skills": {}}
    except Exception:
        lock = {"version": 1, "skills": {}}

    source = metadata.get("repository", plugin_path.name)
    now = datetime.datetime.utcnow().isoformat() + "Z"

    for skill_name in installed_skills:
        existing = lock.get("skills", {}).get(skill_name, {})
        if "skills" not in lock:
            lock["skills"] = {}
        lock["skills"][skill_name] = {
            "source": source,
            "sourceType": "local",
            "computedHash": "",   # filled by install_all_plugins if needed
            "installedAt": existing.get("installedAt", now),
            "updatedAt": now,
        }

    # Sort keys for stable diffs
    lock["skills"] = dict(sorted(lock["skills"].items()))
    lock_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(f"  ✓ Updated skills-lock.json ({len(installed_skills)} skills)")


def provision_central_and_symlink(plugin_path: Path, metadata: dict, targets: list[str], dry_run: bool = False) -> list[str]:
    root = Path.cwd()
    plugin_name = metadata.get("name", plugin_path.name)
    
    agents_root = root / ".agents"
    if not dry_run:
        agents_root.mkdir(exist_ok=True)
    
    installed_skills = []
    
    # 2. Central Skills
    skills_dir = plugin_path / "skills"
    central_skills = agents_root / "skills"
    
    if skills_dir.exists():
        if not dry_run:
            central_skills.mkdir(exist_ok=True)
        # Deep copy the real sources
        for item in skills_dir.iterdir():
            if item.is_dir():
                dest = central_skills / item.name
                if not dry_run:
                    _copy_resolving_pointers(item, dest)
                    print(f"  \u2713 Universal central copy: {dest.relative_to(root)}")
                else:
                    print(f"  [DRY RUN] Universal central copy: .agents/skills/{item.name}")
                
                installed_skills.append(item.name)

                # 3. Iterate local agent folders and establish symlinks
                for target_dir_name in targets:
                    config = DETECTABLE_AGENTS.get(target_dir_name)
                    if not config or not config.get("skills"):
                        continue
                        
                    ide_dir = root / target_dir_name
                    if not ide_dir.exists():
                        continue
                    
                    ide_skills = root / config["skills"]
                    if not dry_run:
                        ide_skills.mkdir(parents=True, exist_ok=True)
                    
                    target_symlink = ide_skills / item.name
                    _symlink_or_copy(dest, target_symlink, dry_run, root, config["name"])
                    
    # 4. Standalone Agents:
    #    - For IDEs with native agents/ dirs (e.g. Claude): deploy .md files directly there.
    #    - For IDEs without native agents/ dirs (e.g. Antigravity): wrap in a SKILL.md wrapper.
    agents_dir_src = plugin_path / "agents"
    if agents_dir_src.exists():
        # Targets WITHOUT a native agents dir get the skill-wrapper treatment
        non_native_agent_targets = [
            t for t in targets
            if not DETECTABLE_AGENTS.get(t, {}).get("agents")
        ]

        for agent_file in agents_dir_src.glob("*.md"):
            agent_name = agent_file.stem
            final_name = plugin_name if plugin_name.endswith(agent_name) else f"{plugin_name}-{agent_name}"

            dest = central_skills / final_name
            if not dry_run:
                dest.mkdir(parents=True, exist_ok=True)
                for opt_dir in ["scripts", "references", "assets", "evals"]:
                    (dest / opt_dir).mkdir(exist_ok=True)
                shutil.copy2(agent_file, dest / "SKILL.md")
                print(f"  ✓ Universal central copy (Agent Wrapper): {dest.relative_to(root)}")
            else:
                print(f"  [DRY RUN] Universal central copy (Agent Wrapper): .agents/skills/{final_name}")

            installed_skills.append(final_name)

            for target_dir_name in non_native_agent_targets:
                config = DETECTABLE_AGENTS.get(target_dir_name)
                if not config or not config.get("skills"):
                    continue

                ide_dir = root / target_dir_name
                if not ide_dir.exists():
                    continue

                ide_skills = root / config["skills"]
                if not dry_run:
                    ide_skills.mkdir(parents=True, exist_ok=True)

                target_symlink = ide_skills / final_name
                _symlink_or_copy(dest, target_symlink, dry_run, root, config["name"])

    # 5. Native Hooks (e.g. for PreToolUse, Subagent events)
    hooks_file = plugin_path / "hooks" / "hooks.json"
    if hooks_file.exists():
        central_hooks = agents_root / "hooks"
        if not dry_run:
            central_hooks.mkdir(exist_ok=True)
            
        dest = central_hooks / f"{plugin_name}-hooks.json"
        
        if not dry_run:
            shutil.copy2(hooks_file, dest)
            print(f"  ✓ Hook central copy: {dest.relative_to(root)}")
        else:
            print(f"  [DRY RUN] Hook central copy: .agents/hooks/{dest.name}")
        
        for target_dir_name in targets:
            config = DETECTABLE_AGENTS.get(target_dir_name)
            if not config or not config.get("hooks"):
                continue
                
            ide_dir = root / target_dir_name
            if not ide_dir.exists():
                continue 
            
            ide_hooks = root / config["hooks"]
            if not dry_run:
                ide_hooks.mkdir(parents=True, exist_ok=True)
            
            target_symlink = ide_hooks / dest.name
            _symlink_or_copy(dest, target_symlink, dry_run, root, config["name"])
            
    deploy_commands(plugin_path, plugin_name, targets, root, dry_run)
    deploy_rules(plugin_path, plugin_name, targets, root, dry_run)
    deploy_agents(plugin_path, plugin_name, targets, root, dry_run)
    
    # MCP merge (future -- log intent for now)
    mcp_file = plugin_path / ".mcp.json"
    if mcp_file.exists():
        print(f"  ⚠ .mcp.json found but merge not yet implemented - "
              f"manually merge {mcp_file} into ./.mcp.json")
              
    return installed_skills


def main() -> None:
    parser = argparse.ArgumentParser(description="Plugin Bridge Installer (.agents symlinking)")
    parser.add_argument("--plugin", required=True, help="Path to plugin directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview all actions without writing any files or symlinks")
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
    if args.dry_run:
        print(">>> DRY RUN MODE <<<")

    installed_skills = provision_central_and_symlink(plugin_path, metadata, targets, args.dry_run)
    write_project_lock(plugin_path, metadata, installed_skills, root, args.dry_run)
    
if __name__ == "__main__":
    main()
