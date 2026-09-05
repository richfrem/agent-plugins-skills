"""
Bridge Installer (CLI)
=====================

Purpose:
    Installs Agent Plugins into .agents/ central repository natively 
    and symlinks them across locally installed agent platforms.

Layer: Plugin Manager / Installation

Key Input Dependencies:
    - .agents/central_index.json (Central index tracking)
    - plugin-sources.json (Sources database)

Usage Examples:
    python plugins/plugin-manager/scripts/plugin_installer.py --plugin plugins/my-plugin

    # install plugin in a different repo e.g. context-bundler specifically
    python <full install path>/agent-plugins-skills/plugins/plugin-manager/scripts/plugin_installer.py

Platform Command Mapping (commands/ vs workflows/):
    Plugin source always uses commands/ as the canonical folder name.
    The installer maps this to the correct platform-specific directory at install time:

        Source folder:   plugin/commands/*.md
        ─────────────────────────────────────────────────────────
        .agents/         → workflows/<plugin>_<cmd>.md  (canonical)
        .claude/         → commands/<plugin>_<cmd>.md   (Claude Code)

    This means the same source file appears under "workflows/" on .agents/
    but under "commands/" on Claude Code — by design. Never rename the source
    folder to match any single platform.

Supported Object Types:
    - None (Filesystem operations)

CLI Arguments:
    --plugin: Path to plugin directory (Required)
    --dry-run: Preview actions without writing files
    --no-install-rules: Skip installing plugin rules/ into .agent/rules/ (installed by default)
    --no-append-rules-to-ide-files: Skip injecting rules into 'append' mode IDE files (e.g. CLAUDE.md)

Input Files:
    - .claude-plugin/plugin.json (Manifest reader)

Output:
    - Creates symlinks and updates skills-lock.json

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
import difflib
from pathlib import Path
from typing import Tuple, List

# Force UTF-8 output on Windows to avoid UnicodeEncodeError with emoji in print()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Agent environments that require their own directory layout alongside .agents/.
#
# Antigravity, Gemini CLI, and GitHub Copilot have all adopted the standard
# .agents/ install path — they read skills, workflows, and agents directly
# from there. Rules are the one exception: they land in .agent/rules/
# (singular "agent"), the shared Gemini CLI / os-init workspace-rules
# convention — see deploy_rules(). No per-agent symlinks are needed for
# skills/workflows/agents on those platforms anymore; the canonical .agents/
# copy is sufficient. As agents converge on .agents/ as the standard, this
# list shrinks. Only environments that still require a separate directory
# tree (Claude Code, Azure) remain here.
DETECTABLE_AGENTS = {
    ".claude": {
        "name": "claude",
        # Skills, agents, commands, and hooks are intentionally NOT symlinked
        # into .claude/ — Claude Code picks all of these up directly from
        # .agents/ (the canonical multi-IDE store). Symlinking them into
        # .claude/ as well causes every skill to appear twice in /context
        # (once as "Project" from .agents/skills/ and once as "Plugin" from
        # .claude/skills/), doubling the Skills token cost for no benefit.
        "skills": None,
        "agents": None,
        "commands": None,
        "rules": None,
        "rules_append_target": "CLAUDE.md",
        "hooks": None,
        "rules_mode": "append",
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


# Directories that should never be copied into .agents/skills/ — runtime
# artifacts and dependency caches that are large, irrelevant to agents, and
# would cause multi-minute installs (e.g. xml-to-markdown's node_modules).
COPY_EXCLUDE_DIRS = frozenset({
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".env",
    "__pycache__",
    ".git",
    ".hg",
    ".svn",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "coverage",
    ".nyc_output",
})

def _process_symlink_item(item: Path, dst_item: Path) -> None:
    """Helper to process and copy a symlink item resolving its target."""
    try:
        raw_target = os.readlink(str(item))
        real_src = (item.parent / raw_target).resolve()
        if real_src.is_dir():
            if real_src.name not in COPY_EXCLUDE_DIRS:
                _copy_resolving_pointers(real_src, dst_item)
        elif real_src.is_file():
            shutil.copy2(real_src, dst_item)
    except (OSError, PermissionError) as e:
        print(f"    ! Could not resolve symlink {item.name}: {e}")


def _process_file_item(item: Path, dst_item: Path) -> None:
    """Helper to process and copy a pointer file or standard file."""
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
        # File is locked by another process — skip
        print(f"    ! Skipped locked file: {dst_item.name}")


def _copy_resolving_pointers(src_dir: Path, dst_dir: Path) -> None:
    """Recursively copy src_dir to dst_dir, resolving path pointer files."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    for item in src_dir.iterdir():
        dst_item = dst_dir / item.name

        if item.is_symlink():
            _process_symlink_item(item, dst_item)
            continue

        if item.is_dir():
            if item.name in COPY_EXCLUDE_DIRS:
                continue
            _copy_resolving_pointers(item, dst_item)
        elif item.is_file():
            _process_file_item(item, dst_item)


def _inject_plugin_field(skill_md_path: Path, plugin_name: str) -> None:
    """Stamp 'plugin: <plugin-name>' into the SKILL.md frontmatter after the name field.

    This lets AI assistants see which plugin owns a skill and know to invoke it
    by its flat name (e.g. Skill("obsidian-wiki-builder"), not "obsidian-wiki-engine:obsidian-wiki-builder").
    Skips files that already have the field or lack a valid frontmatter block.
    """
    if not skill_md_path.exists():
        return
    try:
        content = skill_md_path.read_text(encoding="utf-8")
    except OSError:
        return
    # Must start with ---
    if not content.startswith("---"):
        return
    # Already stamped
    if f"\nplugin: {plugin_name}" in content or f"\nplugin: " in content:
        return
    # Inject after the name: line inside the frontmatter block
    lines = content.splitlines(keepends=True)
    inserted = False
    for i, line in enumerate(lines):
        if line.startswith("name:") and not inserted:
            lines.insert(i + 1, f"plugin: {plugin_name}\n")
            inserted = True
            break
    if not inserted:
        return
    try:
        skill_md_path.write_text("".join(lines), encoding="utf-8")
    except OSError:
        pass


def _windows_mklink_fallback(src: Path, link_path: Path, env_name: str, root: Path) -> bool:
    """Helper to perform Windows-specific Junction/Hardlink creation fallback."""
    import subprocess
    if src.is_dir():
        # Directories: Junction Point (no Developer Mode required)
        try:
            subprocess.run(["cmd", "/c", "mklink", "/J", str(link_path), str(src)],
                           check=True, capture_output=True)
            print(f"    -> Symlinked (Junction) for {env_name}: {link_path.relative_to(root)}")
            return True
        except Exception:
            pass
    else:
        # Files: Hardlink via mklink /H (no Developer Mode required)
        try:
            subprocess.run(["cmd", "/c", "mklink", "/H", str(link_path), str(src)],
                           check=True, capture_output=True)
            print(f"    -> Hardlinked for {env_name}: {link_path.relative_to(root)}")
            return True
        except Exception:
            pass
    return False


def _cleanup_existing_link(link_path: Path) -> bool:
    """Helper to remove an existing symlink or file at target link path."""
    _is_broken_or_exists = (
        link_path.exists()
        or link_path.is_symlink()
        or os.path.lexists(str(link_path))
        or (hasattr(os.path, 'isjunction') and os.path.isjunction(link_path))
    )
    if not _is_broken_or_exists:
        return True

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
    return True


def _symlink_or_copy(src: Path, link_path: Path, dry_run: bool,
                     root: Path, env_name: str) -> bool:
    """Create a symlink or fallback to junction/hardlink or file copy.

    Args:
        src: Source path.
        link_path: Destination link path.
        dry_run: If True, do not perform writing.
        root: Current working directory path context.
        env_name: Name of target environment config.

    Returns:
        bool: True if symlinked/junctioned/hardlinked successfully, False otherwise.
    """
    if dry_run:
        print(f"  [DRY RUN] symlink {link_path.relative_to(root)} -> {src.relative_to(root)}")
        return True

    if not _cleanup_existing_link(link_path):
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
        if os.name == 'nt' and _windows_mklink_fallback(src, link_path, env_name, root):
            return True

        # Final fallback: plain copy (no sync on update, but functional)
        try:
            if src.is_dir():
                shutil.copytree(src, link_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src, link_path)
            print(f"    -> Copied (symlink failed) for {env_name}: {link_path.relative_to(root)}")
            return False
        except Exception as e:
            print(f"    X Failed for {env_name}: {e}")
            return False

def _deploy_command_to_targets(central_dest: Path, dest_name: str, targets: list,
                               root: Path, dry_run: bool) -> list[Path]:
    """Symlink or copy a central command file into each IDE-specific commands dir.

    Args:
        central_dest: Path to the canonical copy in .agents/workflows/.
        dest_name: Flat filename stem used for the target link.
        targets: List of detected IDE target directory names.
        root: Repository root path context.
        dry_run: If True, do not perform file writes.

    Returns:
        List of deployed target link paths.
    """
    deployed: list[Path] = []
    for target_dir_name in targets:
        config = DETECTABLE_AGENTS.get(target_dir_name)
        if not config or not config.get("commands"):
            continue
        if not (root / target_dir_name).exists():
            continue
        cmd_dir = root / config["commands"]
        if not dry_run:
            cmd_dir.mkdir(parents=True, exist_ok=True)
        target_link = cmd_dir / f"{dest_name}.md"
        _symlink_or_copy(central_dest, target_link, dry_run, root, config["name"])
        deployed.append(target_link)
    return deployed


def deploy_commands(plugin_path: Path, plugin_name: str, targets: list,
                    root: Path, dry_run: bool = False) -> list[Path]:
    """Deprecated: Modern agent platforms discover skills directly from .agents/skills/<name>/SKILL.md.

    This function no longer copies legacy command wrappers into .agents/workflows/,
    eliminating redundant workflow generation. Returns empty list.
    """
    return []


def deploy_agents(plugin_path: Path, plugin_name: str, targets: list,
                  root: Path, dry_run: bool = False) -> list[Path]:
    """Deploy agent .md files to IDE-native agents directories (e.g. .claude/agents/)."""
    deployed = []
    agents_dir_src = plugin_path / "agents"
    if not agents_dir_src.exists():
        return deployed

    central_agents = root / ".agents" / "agents"
    if not dry_run:
        central_agents.mkdir(parents=True, exist_ok=True)

    for agent_file in sorted(agents_dir_src.glob("*.md")):
        agent_name = agent_file.stem
        dest_name = f"{plugin_name}-{agent_name}" if not plugin_name.endswith(agent_name) else plugin_name
        central_dest = central_agents / f"{dest_name}.md"

        if not dry_run:
            shutil.copy2(agent_file, central_dest)
        deployed.append(central_dest)

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
            deployed.append(target_link)
            
    return deployed


def _deploy_rule_to_target(rule_file: Path, dest_name: str, plugin_name: str,
                            target_dir_name: str, root: Path, dry_run: bool,
                            append_to_ide_files: bool = True) -> Path | None:
    """Helper to deploy a rule file to a specific target IDE directory.

    append_to_ide_files gates only "append" mode targets (e.g. .claude's
    CLAUDE.md) — repos that keep AGENTS.md/.agent/rules/ as their sole source
    of truth and don't want rule content injected into CLAUDE.md can disable
    it via --no-append-rules-to-ide-files. "files" mode targets (dedicated
    per-file rule copies, e.g. .azure) are unaffected since they don't mutate
    a shared instructions file.
    """
    config = DETECTABLE_AGENTS.get(target_dir_name)
    if not config:
        return None

    ide_dir = root / target_dir_name
    if not ide_dir.exists():
        return None

    if config.get("rules_mode") == "append" and not append_to_ide_files:
        return None

    if config.get("rules_mode") == "files" and config.get("rules"):
        rules_target_dir = root / config["rules"]
        if not dry_run:
            rules_target_dir.mkdir(parents=True, exist_ok=True)
        target_link = rules_target_dir / dest_name
        if not dry_run:
            if target_link.is_symlink() or target_link.exists() or os.path.lexists(str(target_link)):
                target_link.unlink()
            shutil.copy2(rule_file, target_link)
        print(f"    -> Copied rule for {config['name']}: {target_link.relative_to(root)}")
        return target_link

    elif config.get("rules_mode") == "append":
        append_target = root / config["rules_append_target"]
        content = rule_file.read_text(encoding="utf-8")
        marker = f"<!-- plugin: {plugin_name} / {rule_file.stem} -->"
        if not dry_run:
            existing = append_target.read_text(encoding="utf-8") if append_target.exists() else ""
            if marker not in existing:
                with open(append_target, "a", encoding="utf-8") as f:
                    f.write(f"\n{marker}\n{content}\n")
            return append_target
        else:
            try:
                relative_path = append_target.relative_to(root)
            except ValueError:
                relative_path = append_target.name
            print(f"  [DRY RUN] append rule to {relative_path}")
            return append_target
            
    return None


def _merge_rule_content_preserving_downstream(origin_content: str, existing_content: str) -> Tuple[str, bool]:
    """
    Merge plugin-source rule content into .agent/rules/ while preserving any
    downstream content the origin lacks (both whole sections and intra-section
    additions). Mirrors agent-agentic-os's init_agentic_os.py sync_rules()
    pattern — ported here (not imported) per ADR-001, no cross-plugin imports.
    Returns (merged_text, had_downstream_additions).
    """
    if not existing_content.strip():
        return origin_content, False
    if origin_content.strip() == existing_content.strip():
        return origin_content, False

    orig_lines = origin_content.splitlines(keepends=True)
    existing_lines = existing_content.splitlines(keepends=True)

    matcher = difflib.SequenceMatcher(None, orig_lines, existing_lines)
    merged_lines: List[str] = []
    has_downstream = False

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            merged_lines.extend(orig_lines[i1:i2])
        elif tag == "insert":
            # Content present downstream (.agent/rules/) but absent from plugin source
            merged_lines.extend(existing_lines[j1:j2])
            has_downstream = True
        elif tag == "delete":
            # Plugin source has content absent downstream: adopt it
            merged_lines.extend(orig_lines[i1:i2])
        elif tag == "replace":
            # Both sides modified the same block — the newer/richer side (more
            # lines) wins, since plugin sources can lag a same-day .agent/rules/
            # update (see 2026-09-05 git-operations.md clobber incident).
            if (j2 - j1) > (i2 - i1):
                merged_lines.extend(existing_lines[j1:j2])
                has_downstream = True
            else:
                merged_lines.extend(orig_lines[i1:i2])

    return "".join(merged_lines), has_downstream


def deploy_rules(plugin_path: Path, plugin_name: str, targets: list,
                 root: Path, dry_run: bool = False, append_to_ide_files: bool = True) -> list[Path]:
    """Deploy rule files into .agent/rules/ and target agent environments.

    .agent/rules/ (singular "agent") is the workspace-rules convention shared
    by Gemini CLI and os-init's sync_rules() — see
    ecosystem-authoritative-sources/references/workflows.md. It is distinct
    from .agents/ (plural), the canonical multi-IDE skills/agents/workflows
    store. Writing rules anywhere else means os-init --sync-rules and native
    Gemini workspace rules never see them.

    Args:
        plugin_path: Path to the plugin directory.
        plugin_name: Unique name of the plugin.
        targets: List of active IDE targets (e.g. ['.claude']).
        root: Current repository root path context.
        dry_run: If True, do not perform file writes.
        append_to_ide_files: If False, skip "append" mode targets (e.g.
            CLAUDE.md) — the central .agent/rules/ copy is still written.

    Returns:
        List of Path objects for all successfully deployed rules.
    """
    deployed = []
    rules_dir = plugin_path / "rules"
    if not rules_dir.exists():
        return deployed

    central_rules = root / ".agent" / "rules"
    if not dry_run:
        central_rules.mkdir(parents=True, exist_ok=True)

    for rule_file in sorted(rules_dir.glob("*.md")):
        dest_name = rule_file.name
        central_dest = central_rules / dest_name
        if not dry_run:
            origin_content = rule_file.read_text(encoding="utf-8")
            if central_dest.exists():
                existing_content = central_dest.read_text(encoding="utf-8")
                merged_content, had_downstream = _merge_rule_content_preserving_downstream(
                    origin_content, existing_content
                )
                if had_downstream:
                    print(f"  Reconciled rule {dest_name} (preserved newer/downstream .agent/rules/ content)")
                central_dest.write_text(merged_content, encoding="utf-8")
            else:
                shutil.copy2(rule_file, central_dest)
        deployed.append(central_dest)

        for target_dir_name in targets:
            dest = _deploy_rule_to_target(rule_file, dest_name, plugin_name, target_dir_name,
                                          root, dry_run, append_to_ide_files)
            if dest:
                deployed.append(dest)
                
    return deployed


def write_project_lock(plugin_path: Path, metadata: dict,
                       installed_skills: list, root: Path, dry_run: bool = False) -> None:
    """Record installed skills in skills-lock.json.

    Args:
        plugin_path: Path to the plugin directory.
        metadata: Plugin parsed metadata dictionary.
        installed_skills: List of skill slugs installed.
        root: Repository root path context.
        dry_run: If True, preview lock writing without changes.
    """
    if dry_run:
        print(f"  [DRY RUN] skip writing to skills-lock.json ({len(installed_skills)} skills)")
        return
        
    lock_path = root / "skills-lock.json"
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.exists() else {"version": 1, "skills": {}}
    except Exception:
        lock = {"version": 1, "skills": {}}

    source = metadata.get("repository", plugin_path.name)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

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


def write_ownership_manifest(plugin_name: str, root: Path, deployed_paths: list, dry_run: bool = False) -> None:
    """Writes plugin ownership records mapping deployed artifacts.

    Args:
        plugin_name: Unique name of the plugin.
        root: Workspace root path context.
        deployed_paths: List of Path objects to active rule/cmd files.
        dry_run: If True, do not write manifest files.
    """
    if dry_run:
        return
    ownership_dir = root / ".agents" / "ownership"
    ownership_dir.mkdir(parents=True, exist_ok=True)
    manifest_file = ownership_dir / f"{plugin_name}.json"
    
    paths_str = []
    for p in deployed_paths:
        try:
            paths_str.append(str(p.resolve().relative_to(root.resolve())))
        except ValueError:
            paths_str.append(str(p))
            
    data = {
        "plugin": plugin_name,
        "installed_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "artifacts": sorted(list(set(paths_str)))
    }
    manifest_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"  ✓ Recorded artifact ownership in {manifest_file.relative_to(root)}")


def merge_mcp_config(plugin_path: Path, root: Path, dry_run: bool = False) -> None:
    """Merges plugin-level MCP settings into the workspace MCP manifest.

    Args:
        plugin_path: Path to the plugin directory.
        root: Workspace root path context.
        dry_run: If True, print merging proposal instead of writing.
    """
    plugin_mcp = plugin_path / ".mcp.json"
    if not plugin_mcp.exists():
        plugin_mcp = plugin_path / "mcp.json"
    if not plugin_mcp.exists():
        return
        
    project_mcp = root / ".mcp.json"
    if not project_mcp.exists():
        project_mcp = root / "mcp.json"
        
    print(f"  ✓ Merging MCP configuration for {plugin_path.name}...")
    
    if dry_run:
        print(f"  [DRY RUN] Would merge {plugin_mcp.name} into {project_mcp.name}")
        return
        
    try:
        plugin_data = json.loads(plugin_mcp.read_text(encoding="utf-8"))
        plugin_servers = plugin_data.get("mcpServers", {})
        if not plugin_servers:
            return
            
        project_data = {}
        if project_mcp.exists():
            try:
                project_data = json.loads(project_mcp.read_text(encoding="utf-8"))
            except Exception:
                pass
                
        project_servers = project_data.setdefault("mcpServers", {})
        for name, cfg in plugin_servers.items():
            project_servers[name] = cfg
            
        project_mcp.write_text(json.dumps(project_data, indent=2) + "\n", encoding="utf-8")
        print(f"  ✓ Successfully merged {len(plugin_servers)} MCP server(s) into {project_mcp.name}")
    except Exception as e:
        print(f"  ⚠ Failed to merge MCP configuration: {e}")


def _provision_skills(plugin_path: Path, plugin_name: str, agents_root: Path,
                      targets: list, dry_run: bool, root: Path) -> tuple[list, list]:
    """Copy plugin skills into .agents/skills/ and symlink to IDE targets.

    Args:
        plugin_path: Path to the plugin source directory.
        plugin_name: Unique name stamped into each SKILL.md frontmatter.
        agents_root: Path to the .agents/ canonical store.
        targets: List of detected IDE target directory names.
        dry_run: If True, print actions without writing files.
        root: Repository root path context.

    Returns:
        Tuple of (installed_skill_names, deployed_paths).
    """
    installed_skills: list[str] = []
    deployed_paths: list[Path] = []
    skills_dir = plugin_path / "skills"
    central_skills = agents_root / "skills"
    if not skills_dir.exists():
        return installed_skills, deployed_paths
    if not dry_run:
        central_skills.mkdir(exist_ok=True)
    for item in skills_dir.iterdir():
        if not item.is_dir():
            continue
        dest = central_skills / item.name
        if not dry_run:
            if dest.exists() or dest.is_symlink():
                try:
                    if dest.is_dir() and not dest.is_symlink():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                except Exception as e:
                    print(f"    ! Warning: could not clean existing target {dest.name}: {e}")
            _copy_resolving_pointers(item, dest)
            _inject_plugin_field(dest / "SKILL.md", plugin_name)
            print(f"  ✓ Universal central copy: {dest.relative_to(root)}")
        else:
            print(f"  [DRY RUN] Universal central copy: .agents/skills/{item.name}")
        installed_skills.append(item.name)
        deployed_paths.append(dest)
        for target_dir_name in targets:
            config = DETECTABLE_AGENTS.get(target_dir_name)
            if not config or not config.get("skills"):
                continue
            if not (root / target_dir_name).exists():
                continue
            ide_skills = root / config["skills"]
            if not dry_run:
                ide_skills.mkdir(parents=True, exist_ok=True)
            target_symlink = ide_skills / item.name
            _symlink_or_copy(dest, target_symlink, dry_run, root, config["name"])
            deployed_paths.append(target_symlink)
    return installed_skills, deployed_paths


def _provision_hooks(plugin_path: Path, plugin_name: str, agents_root: Path,
                     targets: list, dry_run: bool, root: Path) -> list[Path]:
    """Copy plugin hooks.json into .agents/hooks/ and symlink to IDE targets.

    Args:
        plugin_path: Path to the plugin source directory.
        plugin_name: Used to name the central hooks file.
        agents_root: Path to the .agents/ canonical store.
        targets: List of detected IDE target directory names.
        dry_run: If True, print actions without writing files.
        root: Repository root path context.

    Returns:
        List of deployed hook file paths.
    """
    deployed_paths: list[Path] = []
    hooks_file = plugin_path / "hooks" / "hooks.json"
    if not hooks_file.exists():
        return deployed_paths
    central_hooks = agents_root / "hooks"
    if not dry_run:
        central_hooks.mkdir(exist_ok=True)
    dest = central_hooks / f"{plugin_name}-hooks.json"
    if not dry_run:
        shutil.copy2(hooks_file, dest)
        print(f"  ✓ Hook central copy: {dest.relative_to(root)}")
    else:
        print(f"  [DRY RUN] Hook central copy: .agents/hooks/{dest.name}")
    deployed_paths.append(dest)
    for target_dir_name in targets:
        config = DETECTABLE_AGENTS.get(target_dir_name)
        if not config or not config.get("hooks"):
            continue
        if not (root / target_dir_name).exists():
            continue
        ide_hooks = root / config["hooks"]
        if not dry_run:
            ide_hooks.mkdir(parents=True, exist_ok=True)
        target_symlink = ide_hooks / dest.name
        _symlink_or_copy(dest, target_symlink, dry_run, root, config["name"])
        deployed_paths.append(target_symlink)
    return deployed_paths


def provision_central_and_symlink(plugin_path: Path, metadata: dict, targets: list,
                                  dry_run: bool = False, install_rules: bool = True,
                                  append_rules_to_ide_files: bool = True) -> list:
    """Orchestrate full plugin installation into .agents/ and linked IDE directories.

    Copies skills, hooks, commands, agents, rules, and MCP config from the
    plugin source tree into .agents/ (the canonical multi-IDE store), then
    establishes symlinks or copies into any detected IDE-specific directories
    (e.g. .claude/). Also stamps the plugin name into each SKILL.md frontmatter
    and writes an ownership manifest.

    Args:
        plugin_path: Path to the plugin source directory.
        metadata: Parsed plugin.json metadata dict (must contain 'name').
        targets: List of detected IDE folder names (e.g. ['.claude']).
        dry_run: If True, print planned actions without writing any files.
        install_rules: If True (default), also deploy plugin rules into
            .agent/rules/ — the same workspace-rules directory os-init's
            sync_rules() reconciles from. Pass False to skip.
        append_rules_to_ide_files: If False, skip "append" mode IDE targets
            (e.g. injecting rule content into CLAUDE.md) while still writing
            the central .agent/rules/ copy. For repos that treat AGENTS.md /
            .agent/rules/ as sole source of truth and don't want CLAUDE.md
            auto-populated.

    Returns:
        List of installed skill slug names.
    """
    root = Path.cwd()
    plugin_name = metadata.get("name", plugin_path.name)
    agents_root = root / ".agents"
    if not dry_run:
        agents_root.mkdir(exist_ok=True)

    installed_skills, deployed_paths = _provision_skills(
        plugin_path, plugin_name, agents_root, targets, dry_run, root
    )
    deployed_paths.extend(_provision_hooks(
        plugin_path, plugin_name, agents_root, targets, dry_run, root
    ))
    deployed_paths.extend(deploy_commands(plugin_path, plugin_name, targets, root, dry_run))
    if install_rules:
        deployed_paths.extend(deploy_rules(plugin_path, plugin_name, targets, root, dry_run,
                                           append_rules_to_ide_files))
    deployed_paths.extend(deploy_agents(plugin_path, plugin_name, targets, root, dry_run))
    merge_mcp_config(plugin_path, root, dry_run)
    write_ownership_manifest(plugin_name, root, deployed_paths, dry_run)
    return installed_skills



def log_failure(tier: int, artifact: str, error: str) -> None:
    """Append a failure row to the plugin-manager evolution log.

    Walks up the directory tree from this script to locate
    plugins/plugin-manager/references/evolution-log.md, then appends
    a Markdown table row recording the date, tier, and error message.
    Silently no-ops if the log file cannot be found or written.

    Args:
        tier: Failure tier level (0-3 per self-evolution policy).
        artifact: Name of the plugin or artifact that failed.
        error: Error message string to record.
    """
    import datetime
    log_path = Path("plugins/plugin-manager/references/evolution-log.md")
    if not log_path.exists():
        candidate = Path(__file__).resolve()
        while candidate != candidate.parent:
            check = candidate.parent / "plugins/plugin-manager/references/evolution-log.md"
            if check.exists():
                log_path = check
                break
            candidate = candidate.parent
    if log_path.parent.exists():
        date_str = datetime.date.today().isoformat()
        row = f"| {date_str} | Tier {tier} | Failure: {error} | None | None | FAILED |\n"
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(row)
        except Exception:
            pass


def _load_plugin_metadata(plugin_path: Path) -> dict:
    """Parse plugin.json manifest and return metadata dict.

    Reads .claude-plugin/plugin.json relative to plugin_path.
    Strips HTML tags from the description field if present.
    Falls back to {'name': plugin_path.name} if the file is missing or malformed.

    Args:
        plugin_path: Resolved path to the plugin directory.

    Returns:
        Metadata dict with at least a 'name' key.
    """
    import re
    manifest = plugin_path / ".claude-plugin" / "plugin.json"
    if not manifest.exists():
        return {"name": plugin_path.name}
    try:
        metadata = json.loads(manifest.read_text(encoding="utf-8"))
        if "description" in metadata and isinstance(metadata["description"], str):
            metadata["description"] = re.sub(r"<[^>]+>", "", metadata["description"]).strip()
        return metadata
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse {manifest}: {e}")
        return {"name": plugin_path.name}


def main() -> None:
    """CLI entry point: load plugin manifest, detect IDE targets, run install.

    Reads --plugin path, loads metadata via _load_plugin_metadata, detects
    which IDE environment folders (.claude, .azure, etc.) exist in the CWD,
    then calls provision_central_and_symlink and write_project_lock.
    Logs and exits with code 1 on any installation crash.
    """
    parser = argparse.ArgumentParser(description="Plugin Bridge Installer (.agents symlinking)")
    parser.add_argument("--plugin", required=True, help="Path to plugin directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview all actions without writing any files or symlinks")
    parser.add_argument("--no-install-rules", dest="install_rules", action="store_false",
                        help="Skip installing plugin rules/ into .agent/rules/ (installed by default)")
    parser.add_argument("--no-append-rules-to-ide-files", dest="append_rules_to_ide_files",
                        action="store_false",
                        help="Skip injecting rule content into 'append' mode IDE files "
                             "(e.g. CLAUDE.md); .agent/rules/ is still written (on by default)")
    parser.set_defaults(install_rules=True, append_rules_to_ide_files=True)
    args = parser.parse_args()

    plugin_path = Path(args.plugin).resolve()
    if not plugin_path.exists():
        print(f"Error: Plugin path not found: {plugin_path}")
        sys.exit(1)

    metadata = _load_plugin_metadata(plugin_path)
    root = Path.cwd()
    targets = [t for t in DETECTABLE_AGENTS.keys() if (root / t).exists()]

    print(f"\nInstalling plugin '{metadata['name']}' using target symlinking (.agents/ Strategy).")
    print(f"Detected IDE environments: {', '.join(targets)}")
    if args.dry_run:
        print(">>> DRY RUN MODE <<<")

    try:
        installed_skills = provision_central_and_symlink(plugin_path, metadata, targets, args.dry_run,
                                                          args.install_rules, args.append_rules_to_ide_files)
        write_project_lock(plugin_path, metadata, installed_skills, root, args.dry_run)
    except Exception as e:
        import traceback
        err_msg = f"Installation crash for {plugin_path.name}: {str(e)}: {traceback.format_exc().splitlines()[-1]}"
        print(f"Error: {err_msg}")
        log_failure(tier=2, artifact=plugin_path.name, error=err_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()

