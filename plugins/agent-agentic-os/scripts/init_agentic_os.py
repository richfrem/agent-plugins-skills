#!/usr/bin/env python3
"""
init_agentic_os.py — Agentic OS Scaffolder & Retrofit Engine
============================================================

Purpose:
    Initialize or retrofit the Agentic OS, 3-Layer Memory architecture, and multi-tool
    instruction mirrors in any project directory.
    Supports fresh setup as well as safe retrofitting of existing projects (auto-upgrades
    legacy skills, seeds 3-layer memory, and mirrors CLAUDE.md to GEMINI/Copilot/AGENTS).

Layer:
    CLI / Initialization & Retrofitting

Usage Examples:
    python3 init_agentic_os.py --target /my/project
    python3 init_agentic_os.py --target /my/project --retrofit
    python3 init_agentic_os.py --target /my/project --sync-instructions
    python3 init_agentic_os.py --target /my/project --dry-run
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Template & Runtime File Loaders
# ---------------------------------------------------------------------------

def _get_plugin_root() -> Path:
    env_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env_root:
        return Path(env_root).resolve()
    return Path(__file__).resolve().parent.parent


def load_template(filename: str) -> str:
    plugin_root = _get_plugin_root()
    search_paths = [
        plugin_root / "assets" / "templates" / filename,
        plugin_root / "skills" / "os-init" / "assets" / "templates" / filename,
        plugin_root / "skills" / "os-init" / "templates" / filename,
    ]
    for p in search_paths:
        if p.exists():
            return p.read_text(encoding="utf-8")

    print(f"Error: Template {filename} not found in search paths: {search_paths}", file=sys.stderr)
    sys.exit(1)


def copy_runtime_file(filename: str) -> str:
    plugin_root = _get_plugin_root()
    canonical_path = plugin_root / "scripts" / filename
    if canonical_path.exists():
        return canonical_path.read_text(encoding="utf-8")
    
    legacy_path = plugin_root / "skills" / "os-init" / "templates" / filename
    if legacy_path.exists():
        return legacy_path.read_text(encoding="utf-8")

    print(f"Error: Runtime file {filename} not found at {canonical_path} or {legacy_path}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Core Helpers
# ---------------------------------------------------------------------------

def announce(msg: str, dry_run: bool) -> None:
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"  {prefix}{msg}")


def make_dir(path: Path, dry_run: bool) -> None:
    if not path.exists():
        announce(f"mkdir  {path}", dry_run)
        if not dry_run:
            path.mkdir(parents=True, exist_ok=True)
    else:
        announce(f"exists {path} (skipped)", dry_run)


def write_file(path: Path, content: str, dry_run: bool, force: bool = False) -> None:
    if path.exists():
        if not force:
            announce(f"exists {path} (skipped - use --force to overwrite)", dry_run)
            return
        backup_path = path.with_suffix(path.suffix + ".bak")
        announce(f"backup {path} -> {backup_path.name}", dry_run)
        if not dry_run:
            path.rename(backup_path)

    announce(f"write  {path}", dry_run)
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# 3-Layer Memory & Evolution Substrate Scaffolder
# ---------------------------------------------------------------------------

def _scaffold_3layer_memory(target: Path, dry_run: bool, force: bool) -> None:
    """Scaffold 3-Layer Memory: Layer 2 wiki + map-debt, Layer 3 traces & evolution state."""
    make_dir(target / "wiki", dry_run)
    make_dir(target / "references", dry_run)
    make_dir(target / ".agent" / "learning" / "traces", dry_run)

    # Layer 2 Index
    wiki_index = target / "wiki" / "index.md"
    if not wiki_index.exists():
        write_file(wiki_index, """# Layer 2 Knowledge Base & Domain Playbooks

This directory stores confirmed architectural insights, domain heuristics, and failure analysis patterns that survive across sessions and agent cycles.

## Confirmed Playbooks
- *(Add links to confirmed domain playbooks created during in-situ evolution cycles e.g. `playbook-<topic>.md`)*

## Rejected Patterns / Negative Constraints
- *(Document proven failure modes and anti-patterns to prevent repeating past mistakes)*

## Playbook Structure Standard
Every playbook in this directory must include:
1. **Status**: `CONFIRMED`, `OBSERVED`, or `HYPOTHESIS`
2. **Discovered Date**: `YYYY-MM-DD`
3. **Hard Invariants**: Non-negotiable code/architecture rules discovered through friction.
4. **Canonical Execution Flow**: Step-by-step CLI commands and scripts.
""", dry_run, force)

    # Layer 2 Map Debt
    map_debt = target / "references" / "map-debt.md"
    if not map_debt.exists():
        write_file(map_debt, """# Map Debt Ledger

Persistent tracking of architectural friction, structural anomalies, and unclosed loops across sessions.
Every Tier 0-3 friction event must be logged here immediately (Status: RESOLVED or Status: OPEN).

| ID | Title | Status | Severity | Repeat | First Seen | Description | Resolution Commit |
|---|---|---|---|---|---|---|---|
""", dry_run, force)

    # Layer 3 Trace Manifest Ledger
    cycle_manifests = target / ".agent" / "learning" / "traces" / "cycle_manifests.jsonl"
    if not cycle_manifests.exists():
        write_file(cycle_manifests, "", dry_run, force)


# ---------------------------------------------------------------------------
# Instruction File Synchronizer (CLAUDE -> GEMINI, Copilot, AGENTS)
# ---------------------------------------------------------------------------

def sync_instructions(target: Path, dry_run: bool) -> None:
    """Mirror CLAUDE.md to GEMINI.md, .github/copilot-instructions.md, and AGENTS.md."""
    claude_md = target / "CLAUDE.md"
    if not claude_md.exists():
        announce("Warning: CLAUDE.md not found — skipping instruction synchronization.", dry_run)
        return

    plugin_root = _get_plugin_root()
    sync_script = plugin_root.parent / "cli-agents" / "scripts" / "sync_instruction_files.py"
    if not sync_script.exists():
        sync_script = target / "plugins" / "cli-agents" / "scripts" / "sync_instruction_files.py"

    if sync_script.exists():
        announce("Synchronizing instruction files via sync_instruction_files.py...", dry_run)
        if not dry_run:
            cmd = [sys.executable, str(sync_script), "--repo-root", str(target), "--execute"]
            subprocess.run(cmd, check=True)
    else:
        # Self-contained fallback mirroring
        announce("Mirroring CLAUDE.md to GEMINI.md, AGENTS.md, and copilot-instructions.md...", dry_run)
        claude_content = claude_md.read_text(encoding="utf-8")
        project_name = target.resolve().name

        # GEMINI.md
        gemini_text = re.sub(r"^#\s+.*", "# GEMINI.md", claude_content, count=1)
        if "## Gemini CLI Tool Mapping" not in gemini_text:
            gemini_text += "\n\n## Gemini CLI Tool Mapping\n| Claude Code Tool | Gemini CLI Equivalent |\n|---|---|\n| View | view_file |\n| Edit | replace_file_content |\n| Write | write_to_file |\n| Bash | run_command |\n| Grep | grep_search |\n| Glob | find_by_name |\n| Agent | invoke_subagent |\n"
        write_file(target / "GEMINI.md", gemini_text, dry_run, force=True)

        # AGENTS.md
        agents_text = re.sub(r"^#\s+.*", "# AGENTS.md", claude_content, count=1)
        write_file(target / "AGENTS.md", agents_text, dry_run, force=True)

        # .github/copilot-instructions.md
        copilot_dir = target / ".github"
        make_dir(copilot_dir, dry_run)
        copilot_header = f"# Copilot Instructions for {project_name}\n\n> Authoritative repository instructions for GitHub Copilot. Mirrors CLAUDE.md.\n\n"
        body = re.sub(r"^#\s+.*", "", claude_content, count=1).lstrip()
        write_file(copilot_dir / "copilot-instructions.md", copilot_header + body, dry_run, force=True)


# ---------------------------------------------------------------------------
# Rule Synchronizer (.agent/rules)
# ---------------------------------------------------------------------------

def sync_rules(target: Path, dry_run: bool) -> None:
    """Sync core ecosystem rules from origin .agent/rules to target .agent/rules."""
    plugin_root = _get_plugin_root()
    repo_root = plugin_root.parent.parent
    origin_rules = repo_root / ".agent" / "rules"
    if not origin_rules.exists() or not origin_rules.is_dir():
        alt_root = plugin_root.resolve()
        while alt_root.parent != alt_root and not (alt_root / ".agent" / "rules").exists():
            alt_root = alt_root.parent
        origin_rules = alt_root / ".agent" / "rules"
        if not origin_rules.exists():
            return

    target_rules = target / ".agent" / "rules"
    make_dir(target_rules, dry_run)

    rule_files = list(origin_rules.glob("*.md"))
    if not rule_files:
        return

    announce(f"Synchronizing {len(rule_files)} core ecosystem rules into {target_rules}...", dry_run)
    for rule_file in rule_files:
        target_file = target_rules / rule_file.name
        content = rule_file.read_text(encoding="utf-8")
        write_file(target_file, content, dry_run, force=True)


# ---------------------------------------------------------------------------
# Skill Auditor & Retrofit Migration Helper
# ---------------------------------------------------------------------------

def retrofit_existing_skills(target: Path, dry_run: bool, fix: bool = True) -> None:
    """Scan target project for custom skills and run audit_skill.py with auto-fix."""
    plugin_root = _get_plugin_root()
    audit_script = plugin_root.parent / "agent-scaffolders" / "scripts" / "audit_skill.py"
    if not audit_script.exists():
        audit_script = target / "plugins" / "agent-scaffolders" / "scripts" / "audit_skill.py"

    skill_mds = list(target.glob("plugins/**/skills/*/SKILL.md")) + list(target.glob("skills/*/SKILL.md"))
    if not skill_mds:
        announce("No custom skill folders detected for retrofitting.", dry_run)
        return

    announce(f"Found {len(skill_mds)} skill(s) to audit/retrofit in {target.name}...", dry_run)
    for smd in skill_mds:
        s_dir = smd.parent
        announce(f"Auditing & upgrading skill: {s_dir.name}", dry_run)
        if not dry_run and audit_script.exists():
            cmd = [sys.executable, str(audit_script), str(s_dir)]
            if fix:
                cmd.append("--fix")
            subprocess.run(cmd, check=False)


# ---------------------------------------------------------------------------
# Standard Scaffolding
# ---------------------------------------------------------------------------

def _scaffold_root_files(target: Path, dry_run: bool, force: bool, project_name: str) -> None:
    write_file(target / "CLAUDE.md",
               load_template("CLAUDE_MD_PROJECT.md").format(project_name=project_name),
               dry_run, force)
    write_file(target / "CLAUDE.local.md", load_template("CLAUDE_LOCAL_MD.md"), dry_run, force)
    write_file(target / "START_HERE.md", load_template("START_HERE_MD.md"), dry_run, force)
    write_file(target / "heartbeat.md", load_template("HEARTBEAT_MD.md"), dry_run, force)


def _scaffold_context_dir(target: Path, dry_run: bool, force: bool, today: str) -> None:
    make_dir(target / "context", dry_run)
    make_dir(target / "context" / "memory", dry_run)
    make_dir(target / "context" / ".locks", dry_run)
    write_file(target / "context" / "soul.md", load_template("SOUL_MD.md"), dry_run, force)
    write_file(target / "context" / "user.md", load_template("USER_MD.md"), dry_run, force)
    write_file(target / "context" / "status.md",
               load_template("STATUS_MD.md").format(today=today), dry_run, force)
    write_file(target / "context" / "memory.md",
               load_template("MEMORY_MD.md").format(today=today), dry_run, force)
    write_file(target / "context" / "os-state.json", load_template("OS_STATE_JSON.json"), dry_run, force)
    write_file(target / "context" / "agents.json", copy_runtime_file("agents.json"), dry_run, force)
    write_file(target / "context" / "events.jsonl",
               load_template("EVENTS_JSONL.jsonl").replace("{today}", today), dry_run, force)
    write_file(target / "context" / "kernel.py", copy_runtime_file("kernel.py"), dry_run, force)


def _scaffold_claude_dir(target: Path, dry_run: bool, force: bool) -> None:
    make_dir(target / ".claude", dry_run)
    make_dir(target / ".claude" / "agents", dry_run)
    make_dir(target / ".claude" / "commands", dry_run)
    make_dir(target / ".claude" / "hooks", dry_run)
    write_file(target / ".claude" / "hooks" / "hooks.json",
               load_template("HOOKS_JSON.json"), dry_run, force)


def _validate_and_finalize(target: Path, dry_run: bool) -> None:
    try:
        subprocess.run(["git", "-C", str(target), "rev-parse", "--is-inside-work-tree"],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        announce("git repository detected (Safe Write Protocol rollback is supported)", dry_run)
    except (subprocess.CalledProcessError, FileNotFoundError):
        announce("⚠️  Warning: target is not inside a git repository or git is not installed.", dry_run)


def create_project_structure(target: Path, dry_run: bool, force: bool) -> None:
    today = date.today().isoformat()
    project_name = target.resolve().name

    print(f"\n--- Project root: {target.resolve()} ---\n")

    _scaffold_root_files(target, dry_run, force, project_name)
    _scaffold_context_dir(target, dry_run, force, today)
    _scaffold_claude_dir(target, dry_run, force)
    _scaffold_3layer_memory(target, dry_run, force)
    _validate_and_finalize(target, dry_run)


def create_global_kernel(dry_run: bool, force: bool) -> None:
    global_claude = Path.home() / ".claude"
    global_md = global_claude / "CLAUDE.md"

    print(f"\n--- Global kernel: {global_claude} ---\n")
    make_dir(global_claude, dry_run)
    write_file(global_md, load_template("CLAUDE_MD_GLOBAL.md"), dry_run, force)


def print_next_steps(target: Path, did_global: bool, did_retrofit: bool) -> None:
    print("\n" + "=" * 60)
    print("Agentic OS Initialization / Retrofit Complete!")
    print("=" * 60)
    print(f"\n1. Project Kernel & Multi-Tool Instructions:")
    print(f"   - {target}/CLAUDE.md (Primary Source of Truth)")
    print(f"   - {target}/GEMINI.md (Mirrored with CLI Tool Mapping)")
    print(f"   - {target}/.github/copilot-instructions.md (Mirrored for Copilot CLI)")
    print(f"   - {target}/AGENTS.md (Mirrored for Codex & Generic Agents)")
    print(f"\n2. 3-Layer Memory & Self-Evolution Substrate:")
    print(f"   - Layer 1: In-prompt context ({target}/context/)")
    print(f"   - Layer 2: Confirmed knowledge & debt ({target}/wiki/, {target}/references/map-debt.md)")
    print(f"   - Layer 3: Append-only trace manifests ({target}/.agent/learning/traces/)")
    print(f"\n3. Install/Update Agent Plugins:")
    print("   Run one of the following based on your preferred package manager / tooling:")
    print("   • uvx (Universal / Recommended):")
    print("     uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills")
    print("   • Claude Code Marketplace:")
    print("     claude plugin add richfrem/agent-plugins-skills")
    print("   • Local Source Reinstall:")
    print("     python3 plugins/plugin-manager/scripts/plugin_add.py --all -y")
    print("\n4. Add to .gitignore:")
    print("   CLAUDE.local.md, context/memory/, context/status.md, context/os-state.json, context/events.jsonl, context/.locks/, .claude/")
    print()


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize or retrofit the Agentic OS and 3-Layer Memory substrate in a project."
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=Path("."),
        help="Project root directory to initialize or retrofit (default: current directory)"
    )
    parser.add_argument(
        "--global",
        dest="global_kernel",
        action="store_true",
        help="Also scaffold ~/.claude/CLAUDE.md as global kernel"
    )
    parser.add_argument(
        "--retrofit",
        action="store_true",
        help="Retrofit existing repository: seed 3-layer memory, sync instruction files, and auto-upgrade skills"
    )
    parser.add_argument(
        "--sync-instructions",
        action="store_true",
        help="Mirror CLAUDE.md to GEMINI.md, .github/copilot-instructions.md, and AGENTS.md"
    )
    parser.add_argument(
        "--sync-rules",
        action="store_true",
        help="Sync core ecosystem rules from origin .agent/rules to target .agent/rules"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be created without writing anything"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files with .bak backups"
    )

    args = parser.parse_args()
    target = Path(args.target).expanduser().resolve()

    if not target.exists():
        print(f"Error: target directory does not exist: {target}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("\n[DRY RUN] Previewing changes - nothing will be written.\n")

    if args.retrofit:
        print(f"\n--- Retrofitting Existing Repository: {target.resolve()} ---\n")
        _scaffold_3layer_memory(target, args.dry_run, args.force)
        sync_instructions(target, args.dry_run)
        sync_rules(target, args.dry_run)
        retrofit_existing_skills(target, args.dry_run, fix=True)
    else:
        create_project_structure(target, args.dry_run, args.force)
        if args.sync_instructions:
            sync_instructions(target, args.dry_run)
        if args.sync_rules:
            sync_rules(target, args.dry_run)

    if args.global_kernel:
        create_global_kernel(args.dry_run, args.force)

    if not args.dry_run:
        print_next_steps(target, args.global_kernel, args.retrofit)
    else:
        print("\n[DRY RUN] Complete. Run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
