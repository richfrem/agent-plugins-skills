#!/usr/bin/env python3
"""
init_agentic_os.py — Agentic OS Scaffolder & Retrofit Engine
============================================================

Purpose:
    Initialize or retrofit the Agentic OS and 3-Layer Memory architecture in any project
    directory, keeping AGENTS.md as the single canonical instruction file.
    Supports fresh setup as well as safe retrofitting of existing projects (auto-upgrades
    legacy skills, and seeds 3-layer memory).

Layer:
    CLI / Initialization & Retrofitting

Key Input Dependencies:
    - Template directory: assets/templates/ or skills/os-init/assets/templates/
    - Agent control plane schema: context/control_plane.db (auto-initialized)
    - Instruction files: AGENTS.md (canonical); CLAUDE.md may be a pointer
    - Ecosystem rules: .agent/rules/ (synced across workspaces)

Key Functions:
    - _get_plugin_root() — Resolves plugin root path
    - load_template() — Loads markdown/json template from assets
    - copy_runtime_file() — Loads canonical script/json runtime file
    - announce() — Prints status message with dry-run indicator
    - make_dir() — Creates directory safely
    - write_file() — Writes file with backup and dry-run support
    - _init_control_plane_db() — Bootstraps SQLite control plane DB with WAL mode
    - _scaffold_3layer_memory() — Creates 3-layer memory directory structure
    - _merge_instructions_with_judgment() — Merges OS sections into AGENTS.md
    - sync_instructions() — Preserves AGENTS.md and the optional CLAUDE.md pointer
    - _merge_rule_content_preserving_downstream() — Diff-merges upstream rules preserving local edits
    - sync_rules() — Synchronizes ecosystem rules into .agent/rules/
    - retrofit_existing_skills() — Audits and auto-upgrades custom skills
    - _scaffold_root_files() — Scaffolds root instruction files
    - _scaffold_context_dir() — Scaffolds context/ runtime state and SQLite DB
    - _scaffold_claude_dir() — Scaffolds .claude/ directory and hooks
    - _validate_and_finalize() — Validates git repository and installs hooks
    - create_project_structure() — Orchestrates project directory scaffolding
    - create_global_kernel() — Scaffolds user-level ~/.claude/CLAUDE.md kernel
    - print_next_steps() — Displays completion guidance and next steps
    - dual_identity_notice() — Reports human approval, simulation and isolation readiness separately
    - ensure_simulation_identity_step() — Creates or reuses the agent's simulation identity (--with-simulation-identity)
    - _parse_args() — Parses CLI arguments
    - _execute_action() — Dispatches retrofit or standard project scaffolding
    - main() — CLI dispatcher entry point

Usage Examples:
    python3 init_agentic_os.py --target /my/project
    python3 init_agentic_os.py --target /my/project --retrofit
    python3 init_agentic_os.py --target /my/project --sync-instructions
    python3 init_agentic_os.py --target /my/project --dry-run
"""

import argparse
import difflib
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

# External comment: Resolve plugin root directory
try:  # shared control-plane hook wiring + declared mode
    import control_plane_hooks
except ImportError:  # imported from another working directory, or an incomplete install
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import control_plane_hooks
    except ImportError:
        sys.exit(
            "ERROR: control_plane_hooks.py was not found next to init_agentic_os.py "
            f"({Path(__file__).resolve().parent}).\n"
            "It is part of the os-init skill's scripts/ folder. Re-run the plugin sync "
            "(plugin-syncer) to restore it, then retry."
        )


def _get_plugin_root() -> Path:
    """Resolves and returns the canonical plugin root path."""
    env_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env_root:
        return Path(env_root).resolve()
    return Path(__file__).resolve().parent.parent


# External comment: Load a template file from plugin assets
def load_template(filename: str) -> str:
    """Loads markdown or JSON template string from asset search paths."""
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


# External comment: Load a canonical runtime file
def copy_runtime_file(filename: str) -> str:
    """Loads content of a canonical script or JSON configuration file."""
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

# External comment: Print an announcement message with dry-run support
def announce(msg: str, dry_run: bool) -> None:
    """Prints status message with optional dry-run indicator prefix."""
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"  {prefix}{msg}")


# External comment: Create directory safely
def make_dir(path: Path, dry_run: bool) -> None:
    """Creates a directory if it does not already exist."""
    if not path.exists():
        announce(f"mkdir  {path}", dry_run)
        if not dry_run:
            path.mkdir(parents=True, exist_ok=True)
    else:
        announce(f"exists {path} (skipped)", dry_run)


# Global tracker for backup files created during the run
_CREATED_BACKUPS: List[Path] = []

CLAUDE_POINTER = "# CLAUDE.md\n\nRead [AGENTS.md](AGENTS.md).\n"


# External comment: Write content to file with backup handling
def write_file(path: Path, content: str, dry_run: bool, force: bool = False) -> None:
    """Writes content to file with optional backup creation if existing."""
    if path.exists():
        try:
            if path.read_text(encoding="utf-8") == content:
                announce(f"unchanged {path} (skipped)", dry_run)
                return
        except (OSError, UnicodeError):
            pass
        if not force:
            announce(f"exists {path} (skipped - use --force to overwrite)", dry_run)
            return
        backup_path = path.with_suffix(path.suffix + ".bak")
        suffix = 1
        while backup_path.exists():
            backup_path = path.with_name(f"{path.name}.{suffix}.bak")
            suffix += 1
        announce(f"backup {path} -> {backup_path.name}", dry_run)
        if not dry_run:
            path.rename(backup_path)
            _CREATED_BACKUPS.append(backup_path)

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
# Canonical Instruction File Synchronizer (AGENTS.md)
# ---------------------------------------------------------------------------

def _merge_instructions_with_judgment(existing_text: str, project_name: str) -> str:
    """Merge Agentic OS guidance into AGENTS.md without clobbering project context."""
    text = existing_text
    
    # Check for Phase 0 Intake & Socratic Gate
    if "Phase 0 Intake & Socratic Gate" not in text and "work-intake" not in text:
        intake_block = (
            "\n\n## Phase 0 Intake & Socratic Gate (Mandatory)\n"
            "> Every engineering task, feature proposal, bugfix, or improvement MUST trigger `work-intake` first.\n"
            "- Register the task in `context/control_plane.db` via `python3 scripts/agent_control.py init`.\n"
            "- Enforce host-native Plan Mode (strictly read-only discovery).\n"
            "- Socratic Pacing: Interrogate ONE question per turn with structured options and explicit `[Recommended]` default.\n"
            "- Compile draft 4-Pillar Spec (`TASK_SPEC.md`) and implementation plan in state `DRAFT_PLAN`.\n"
            "- User Stage Gate: Ask user whether to run Multi-Agent Review (generate bundle in `temp/` via `context-bundler`) or proceed directly.\n"
            "- Obtain explicit human authorization (\"Proceed\", \"Go\", or \"Execute\") before creating a worktree or modifying code.\n"
        )
        text += intake_block
    
    # Check for 3-layer memory section
    if "### The 3 Filesystem Memory Layers" not in text and "## 3-Layer Memory" not in text:
        memory_block = (
            "\n\n## 3-Layer Memory Architecture\n"
            "- **Layer 1 (Runtime Context)**: Lean prompt instructions loaded on-demand.\n"
            "- **Layer 2 (Permanent Knowledge)**: Confirmed domain playbooks in `wiki/` and `references/map-debt.md`.\n"
            "- **Layer 3 (Audit Ledger)**: Append-only trace manifests in `.agent/learning/traces/cycle_manifests.jsonl`.\n"
        )
        text += memory_block

    # Check for Pre-Completion Gate section
    if "PRE-COMPLETION GATE:" not in text:
        gate_block = (
            "\n\n## Pre-Completion Self-Evolution Gate\n"
            "> On EVERY turn where code is modified or verifications are run, emit this receipt verbatim:\n"
            "```\n"
            "PRE-COMPLETION GATE:\n"
            "  Capability check: Did I verify whether an existing repo capability was intended for this task? [YES/NO]\n"
            "  1. Did any existing capability fail, get bypassed, or get manually replaced?  [YES/NO]\n"
            "  2. Did I guess, assume, or get corrected on a repeatable process?              [YES/NO]\n"
            "  3. Did I notice something the next agent will hit again if not fixed?          [YES/NO]\n"
            "\n"
            "If any YES: action taken -> FIX / MAP_DEBT / ESCALATE\n"
            "  [Physical Disk Write Verified: wiki/<playbook>.md or references/map-debt.md]\n"
            "```\n"
        )
        text += gate_block

    # Check for Plugin Maintenance & Contribution Strategy
    if "## Plugin & Skill Maintenance Policy" not in text:
        strategy_block = (
            "\n\n## Plugin & Skill Maintenance Policy\n"
            "- Check `context/plugin-config.json` for this repository's configured contribution mode:\n"
            "  1. `fork-and-pr`: Test fix locally, commit to feature branch in cloned upstream repo, and submit PR to `richfrem/agent-plugins-skills`.\n"
            "  2. `local-patch-and-issue`: Apply immediate fix directly in `.agents/skills/` and log an issue in `richfrem/agent-plugins-skills` with reproduction details.\n"
            "  3. `domain-override`: Keep upstream shared skills unmodified; put project customizations in `.agent/rules/local-*` or local `plugins/`.\n"
            "- Never make silent undocumented edits to shared skills without either opening an upstream PR or logging an issue.\n"
        )
        text += strategy_block

    return text


def _is_claude_pointer(text: str) -> bool:
    return text == CLAUDE_POINTER


def _agents_template(project_name: str) -> str:
    template = load_template("CLAUDE_MD_PROJECT.md").format(project_name=project_name)
    return re.sub(r"^#\s+.*", "# AGENTS.md", template, count=1)


def _write_if_changed(path: Path, content: str, dry_run: bool) -> None:
    """Write an instruction update only when its content actually changes."""
    if path.exists():
        try:
            if path.read_text(encoding="utf-8") == content:
                announce(f"unchanged {path} (skipped)", dry_run)
                return
        except (OSError, UnicodeError):
            pass
    announce(f"write  {path}", dry_run)
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _report_existing_instruction_copies(target: Path) -> None:
    """Report legacy copies without creating, changing, or deleting them."""
    for relative in ("GEMINI.md", ".github/copilot-instructions.md", "CLAUDE.local.md"):
        if (target / relative).exists():
            print(f"Advisory: existing {relative} left untouched; AGENTS.md is the canonical instruction file.")


def sync_instructions(target: Path, dry_run: bool) -> None:
    """Update AGENTS.md only; preserve a pointer CLAUDE.md and all legacy copies."""
    claude_md = target / "CLAUDE.md"
    agents_md = target / "AGENTS.md"
    project_name = target.resolve().name

    claude_content = claude_md.read_text(encoding="utf-8") if claude_md.exists() else None
    if agents_md.exists() and claude_content is not None and not _is_claude_pointer(claude_content):
        print("Advisory: both AGENTS.md and non-pointer CLAUDE.md exist; leaving both unchanged. Keep AGENTS.md canonical and reconcile CLAUDE.md manually if desired.")
        _report_existing_instruction_copies(target)
        return

    if not agents_md.exists():
        if claude_content is not None and not _is_claude_pointer(claude_content):
            agents_content = re.sub(r"^#\s+.*", "# AGENTS.md", claude_content, count=1)
            announce("Migrating CLAUDE.md content into AGENTS.md", dry_run)
        else:
            agents_content = _agents_template(project_name)
        agents_content = _merge_instructions_with_judgment(agents_content, project_name)
        write_file(agents_md, agents_content, dry_run, force=False)
    else:
        existing_agents = agents_md.read_text(encoding="utf-8")
        merged_agents = _merge_instructions_with_judgment(existing_agents, project_name)
        _write_if_changed(agents_md, merged_agents, dry_run)

    if claude_content is not None and not _is_claude_pointer(claude_content):
        # Preserve the source as CLAUDE.md.bak before replacing it with the pointer.
        write_file(claude_md, CLAUDE_POINTER, dry_run, force=True)
    elif claude_content is None:
        announce("CLAUDE.md is absent; AGENTS.md remains the sole instruction file.", dry_run)

    _report_existing_instruction_copies(target)


# ---------------------------------------------------------------------------
# Rule Synchronizer (.agent/rules)
# ---------------------------------------------------------------------------

def _merge_rule_content_preserving_downstream(origin_content: str, existing_content: str) -> Tuple[str, bool]:
    """
    Merge upstream rule content into target while preserving any downstream custom additions
    (both whole sections and intra-section blockquotes/paragraphs like DEBT-20260902-01).
    Returns (merged_text, had_custom_additions).
    """
    if not existing_content.strip():
        return origin_content, False
    if origin_content.strip() == existing_content.strip():
        return origin_content, False

    orig_lines = origin_content.splitlines(keepends=True)
    existing_lines = existing_content.splitlines(keepends=True)

    matcher = difflib.SequenceMatcher(None, orig_lines, existing_lines)
    merged_lines: List[str] = []
    has_custom = False

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            merged_lines.extend(orig_lines[i1:i2])
        elif tag == "insert":
            # Content added downstream in target that doesn't exist in origin
            inserted = existing_lines[j1:j2]
            merged_lines.extend(inserted)
            has_custom = True
        elif tag == "delete":
            # Upstream has content absent downstream: adopt upstream changes
            merged_lines.extend(orig_lines[i1:i2])
        elif tag == "replace":
            # Both upstream and downstream modified the same logical line/block:
            # Upstream evolution takes precedence for modified lines to prevent duplicating
            # contradictory schema definitions or conflicting rules.
            merged_lines.extend(orig_lines[i1:i2])

    return "".join(merged_lines), has_custom


def sync_rules(target: Path, dry_run: bool) -> None:
    """Sync core ecosystem rules from origin .agent/rules to target .agent/rules, preserving custom downstream sections."""
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

    announce(f"Reconciling {len(rule_files)} core ecosystem rules into {target_rules}...", dry_run)
    for rule_file in rule_files:
        target_file = target_rules / rule_file.name
        origin_content = rule_file.read_text(encoding="utf-8")
        
        final_content = origin_content
        had_custom = False
        if target_file.exists():
            existing_content = target_file.read_text(encoding="utf-8")
            if existing_content.strip() == origin_content.strip():
                continue
            final_content, had_custom = _merge_rule_content_preserving_downstream(origin_content, existing_content)
            if had_custom:
                announce(f"Reconciled rule {rule_file.name} (preserved custom downstream sections)", dry_run)
            else:
                announce(f"Updated rule {rule_file.name} (upstream sync)", dry_run)
        
        write_file(target_file, final_content, dry_run, force=True)


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


# External comment: Scaffold plugin-level evolution substrates for local plugins
def _scaffold_plugin_evolution_substrates(target: Path, dry_run: bool, force: bool) -> None:
    """Scaffolds references/evolution-log.md in each local plugin under target/plugins/ if missing."""
    plugins_dir = target / "plugins"
    if not plugins_dir.exists() or not plugins_dir.is_dir():
        return

    # Find directories under plugins/ that have skills, agents, or plugin manifests
    plugin_dirs = [
        d for d in plugins_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".") and (
            (d / "skills").exists() or (d / "agents").exists() or
            (d / "plugin.json").exists() or (d / "plugin.yaml").exists()
        )
    ]
    if not plugin_dirs:
        return

    announce(f"Inspecting {len(plugin_dirs)} local plugin(s) for evolution substrates...", dry_run)
    for p in sorted(plugin_dirs):
        refs_dir = p / "references"
        make_dir(refs_dir, dry_run)
        evo_log = refs_dir / "evolution-log.md"
        if not evo_log.exists():
            content = (
                f"# Evolution Log — {p.name}\n\n"
                "Append-only record of every self-evolution event. Written by the `self-evolution` skill.\n"
                "Do not edit manually except to correct a factual error.\n\n"
                "| Date | Tier | Friction / Failure | Patch | Edit Type | Outcome |\n"
                "|------|------|-------------------|-------|-----------|---------|\n"
            )
            write_file(evo_log, content, dry_run, force)
        else:
            announce(f"exists {evo_log} (skipped)", dry_run)



# External comment: Initialize SQLite control plane database
def _init_control_plane_db(target: Path, dry_run: bool) -> None:
    """Initializes SQLite control plane database via agent_control.py's own ControlPlane
    class — reuses the canonical schema directly instead of a hand-copied duplicate, so
    consumer repos always get the current, self-healing schema (task_type column,
    schema_version table) rather than drifting out of sync with agent_control.py."""
    db_path = target / "context" / "control_plane.db"
    if db_path.exists():
        announce(f"exists {db_path} (skipped)", dry_run)
        return

    announce(f"init   {db_path}", dry_run)
    if not dry_run:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        scripts_dir = str(Path(__file__).resolve().parent)
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from agent_control import ControlPlane
        ControlPlane(db_path=db_path).init_db()


# ---------------------------------------------------------------------------
# Standard Scaffolding
# ---------------------------------------------------------------------------

# External comment: Scaffold repository root instruction files
def _scaffold_root_instruction_files(target: Path, dry_run: bool, project_name: str) -> None:
    """Create AGENTS.md and the optional CLAUDE.md pointer without overwriting instructions."""
    agents_md = target / "AGENTS.md"
    claude_md = target / "CLAUDE.md"

    if claude_md.exists() and not agents_md.exists():
        claude_content = claude_md.read_text(encoding="utf-8")
        if not _is_claude_pointer(claude_content):
            sync_instructions(target, dry_run)
            return

    if not agents_md.exists():
        write_file(agents_md, _agents_template(project_name), dry_run, force=False)

    if not claude_md.exists():
        write_file(claude_md, CLAUDE_POINTER, dry_run, force=False)
    elif not _is_claude_pointer(claude_md.read_text(encoding="utf-8")):
        print("Advisory: existing non-pointer CLAUDE.md left untouched; AGENTS.md is canonical.")

    _report_existing_instruction_copies(target)


def _scaffold_root_files(target: Path, dry_run: bool, force: bool, project_name: str) -> None:
    """Scaffolds top-level kernel instructions, architecture, and project status files."""
    _scaffold_root_instruction_files(target, dry_run, project_name)
    write_file(target / "START_HERE.md", load_template("START_HERE_MD.md"), dry_run, force)
    write_file(target / "heartbeat.md", load_template("HEARTBEAT_MD.md"), dry_run, force)
    write_file(target / "architecture.md",
               load_template("ARCHITECTURE_MD.md").format(project_name=project_name),
               dry_run, force)


# External comment: Configure or prompt for plugin maintenance policy
def _configure_plugin_contribution_policy(target: Path, mode: Optional[str], dry_run: bool, force: bool) -> str:
    """Configures context/plugin-config.json interactively or via CLI mode."""
    config_file = target / "context" / "plugin-config.json"
    valid_modes = {"fork-and-pr", "local-patch-and-issue", "domain-override"}
    selected_mode = mode

    if not selected_mode and not config_file.exists():
        if sys.stdin.isatty():
            print("\n--- Plugin Maintenance & Contribution Strategy ---")
            print("When you or AI agents encounter bugs or gaps in shared plugins/skills:")
            print("  1) [Recommended] Fork & Upstream PR (fork-and-pr)")
            print("     -> Fix locally, test with pytest in cloned upstream repo, submit PR to richfrem/agent-plugins-skills.")
            print("  2) Local Patch & Issue Reporting (local-patch-and-issue)")
            print("     -> Hotfix .agents/skills/ directly for immediate use, and log an issue with reproduction details.")
            print("  3) Domain Override Only (domain-override)")
            print("     -> Keep shared upstream plugins pristine; place customizations in .agent/rules/local-* or custom plugins/.")
            try:
                choice = input("Select preference [1-3, default: 1]: ").strip()
                if choice == "2":
                    selected_mode = "local-patch-and-issue"
                elif choice == "3":
                    selected_mode = "domain-override"
                else:
                    selected_mode = "fork-and-pr"
            except (EOFError, KeyboardInterrupt):
                selected_mode = "fork-and-pr"
        else:
            selected_mode = "fork-and-pr"

    if not selected_mode and config_file.exists():
        try:
            data = json.loads(config_file.read_text(encoding="utf-8"))
            selected_mode = data.get("contribution_mode", "fork-and-pr")
        except Exception:
            selected_mode = "fork-and-pr"

    if not selected_mode or selected_mode not in valid_modes:
        selected_mode = "fork-and-pr"

    config_payload = {
        "contribution_mode": selected_mode,
        "upstream_repo": "https://github.com/richfrem/agent-plugins-skills",
        "issue_reporting_url": "https://github.com/richfrem/agent-plugins-skills/issues",
        "allow_local_patching": True if selected_mode in {"fork-and-pr", "local-patch-and-issue"} else False,
        "description": {
            "fork-and-pr": "Fix locally, port to upstream clone, and submit Pull Request.",
            "local-patch-and-issue": "Hotfix local installed copy and report issue upstream.",
            "domain-override": "Keep shared skills pristine; isolate customizations in local rules."
        }.get(selected_mode, "")
    }

    if not config_file.exists() or force:
        write_file(config_file, json.dumps(config_payload, indent=2) + "\n", dry_run, force)
        announce(f"Configured plugin contribution mode: {selected_mode} -> context/plugin-config.json", dry_run)

    return selected_mode


# External comment: Scaffold context directory, runtime state, and control plane DB
def _scaffold_context_dir(target: Path, dry_run: bool, force: bool, today: str) -> None:
    """Scaffolds context directory, locks, runtime manifests, and control_plane.db."""
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
               load_template("EVENTS_JSONL.jsonl"), dry_run, force)
    _configure_plugin_contribution_policy(target, None, dry_run, force)
    _init_control_plane_db(target, dry_run)


# External comment: Scaffold Claude Code configuration directory
def _scaffold_claude_dir(target: Path, dry_run: bool, force: bool) -> None:
    """Scaffolds .claude configuration directory, commands, and hooks."""
    make_dir(target / ".claude", dry_run)
    make_dir(target / ".claude" / "agents", dry_run)
    make_dir(target / ".claude" / "commands", dry_run)
    make_dir(target / ".claude" / "hooks", dry_run)
    write_file(target / ".claude" / "hooks" / "hooks.json",
               load_template("HOOKS_JSON.json"), dry_run, force)


# External comment: Install the control-plane git guards unless the control plane is disabled
def _install_control_plane_guards(target: Path, git_hooks_dir: Path, plugin_root: Path, dry_run: bool) -> None:
    """Install and wire pre-commit-pipeline-guard and pre-push-review-guard.

    Honours the declared mode in `context/control-plane-mode`: when it says `disabled`,
    nothing is installed or wired, so a re-run of os-init never silently re-enables a gate.
    A missing file means `enabled` (every pre-existing install is unchanged). An unreadable
    mode file fails closed: the guards are installed and the problem is announced.
    """
    root = control_plane_hooks.common_repo_root(target)
    try:
        mode = control_plane_hooks.read_mode(root)
    except control_plane_hooks.ModeError as exc:
        announce(f"WARNING: {exc} Treating the control plane as enabled.", dry_run)
        mode = control_plane_hooks.MODE_ENABLED

    if mode == control_plane_hooks.MODE_DISABLED:
        announce(
            "Control plane is DISABLED (context/control-plane-mode): not installing or wiring "
            "pre-commit-pipeline-guard / pre-push-review-guard. "
            "Re-enable with the os-control-plane-mode skill.",
            dry_run,
        )
        return

    for guard in control_plane_hooks.CONTROL_PLANE_GUARDS:
        source = plugin_root / "scripts" / guard.name
        if not source.exists():
            continue
        control_plane_hooks.install_guard_script(source, git_hooks_dir, guard, dry_run)
        control_plane_hooks.wire_guard(git_hooks_dir, guard, dry_run)
        announce(f"Installed {guard.name} into .git/hooks/", dry_run)


# External comment: Validate git repo and install pre-commit evolution guard
def _validate_and_finalize(target: Path, dry_run: bool, install_workflow: bool = True) -> None:
    """Validates git repository context and installs pre-commit evolution guard."""
    try:
        subprocess.run(["git", "-C", str(target), "rev-parse", "--is-inside-work-tree"],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        announce("git repository detected (Safe Write Protocol rollback is supported)", dry_run)
        
        # Install pre-commit evolution guard
        git_hooks_dir = target / ".git" / "hooks"
        if git_hooks_dir.exists() and git_hooks_dir.is_dir():
            plugin_root = _get_plugin_root()
            guard_source = plugin_root / "scripts" / "pre-commit-evolution-guard"
            if guard_source.exists():
                guard_target = git_hooks_dir / "pre-commit-evolution-guard"
                guard_content = guard_source.read_text(encoding="utf-8")
                write_file(guard_target, guard_content, dry_run, force=True)
                if not dry_run:
                    guard_target.chmod(0o755)
                
                # Wire the guard into the pre-commit hook
                pre_commit = git_hooks_dir / "pre-commit"
                if pre_commit.exists():
                    pc_content = pre_commit.read_text(encoding="utf-8")
                    if "pre-commit-evolution-guard" not in pc_content:
                        guard_block = "\n# Run evolution guard if it exists\nif [ -x \"$HOOKS_DIR/pre-commit-evolution-guard\" ]; then\n    \"$HOOKS_DIR/pre-commit-evolution-guard\" || exit 1\nfi\n"
                        # Anchor replacement strictly to the final exit 0 line
                        if "\nexit 0" in pc_content:
                            idx = pc_content.rfind("\nexit 0")
                            pc_content = pc_content[:idx] + guard_block + "\nexit 0" + pc_content[idx+7:]
                        else:
                            pc_content += guard_block + "\nexit 0\n"
                        write_file(pre_commit, pc_content, dry_run, force=True)
                else:
                    # No pre-commit hook exists — create a minimal one that runs the guard
                    minimal_hook = (
                        "#!/usr/bin/env bash\n"
                        "# pre-commit hook — installed by init_agentic_os.py\n"
                        "HOOKS_DIR=\"$(dirname \"$0\")\"\n"
                        "\n"
                        "# Run evolution guard\n"
                        "if [ -x \"$HOOKS_DIR/pre-commit-evolution-guard\" ]; then\n"
                        "    \"$HOOKS_DIR/pre-commit-evolution-guard\" || exit 1\n"
                        "fi\n"
                        "\n"
                        "exit 0\n"
                    )
                    write_file(pre_commit, minimal_hook, dry_run, force=False)
                    if not dry_run:
                        pre_commit.chmod(0o755)
                announce("Installed pre-commit-evolution-guard into .git/hooks/", dry_run)

            # Install the control-plane guards (pipeline + push). One shared implementation in
            # control_plane_hooks.py; skipped when the declared mode is 'disabled'.
            _install_control_plane_guards(target, git_hooks_dir, plugin_root, dry_run)

        if not install_workflow:
            return

        # Install GitHub Actions evolution integrity workflow
        github_workflows_dir = target / ".github" / "workflows"
        make_dir(github_workflows_dir, dry_run)
        ci_workflow_target = github_workflows_dir / "verify-evolution-integrity.yml"
        if not ci_workflow_target.exists():
            workflow_content = (
                "name: Evolution Integrity & Compliance Gate\n\n"
                "on:\n"
                "  pull_request:\n"
                "    paths:\n"
                "      - 'plugins/**'\n"
                "      - 'py_services/**'\n"
                "      - 'src/**'\n\n"
                "jobs:\n"
                "  verify-evolution:\n"
                "    name: Verify Evolution & Map Debt Compliance\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - name: Checkout Repository\n"
                "        uses: actions/checkout@v4\n"
                "        with:\n"
                "          fetch-depth: 0\n\n"
                "      - name: Set up Python\n"
                "        uses: actions/setup-python@v5\n"
                "        with:\n"
                "          python-version: '3.11'\n\n"
                "      - name: Check Map Debt & Evolution Compliance in PR Diff\n"
                "        env:\n"
                "          BASE_REF: ${{ github.base_ref }}\n"
                "        run: |\n"
                "          # Check if PR touches core logic\n"
                "          CHANGED_SRC=$(git diff --name-only origin/\"$BASE_REF\"...HEAD | grep -E '^(plugins/|py_services/|src/)' || true)\n"
                "          \n"
                "          if [ -n \"$CHANGED_SRC\" ]; then\n"
                "            echo \"Checking Evolution & Map Debt compliance for modified code...\"\n"
                "            \n"
                "            # Check for escape valve in commit messages\n"
                "            if git log origin/\"$BASE_REF\"...HEAD --grep='Evolution-Check:[[:space:]]*none' -n 1 | grep -q 'Evolution-Check'; then\n"
                "              echo \"✓ Escape valve found: Evolution-Check: none trailer verified.\"\n"
                "              exit 0\n"
                "            fi\n"
                "            \n"
                "            # Check for map-debt, wiki, or evolution-log changes\n"
                "            DOC_CHANGED=$(git diff --name-only origin/\"$BASE_REF\"...HEAD | grep -E '^(references/map-debt.md|wiki/|plugins/.*/references/evolution-log.md)' || true)\n"
                "            \n"
                "            if [ -z \"$DOC_CHANGED\" ]; then\n"
                "              echo \"❌ CI FAILURE: PR modifies core logic but contains no staged Map Debt or Evolution Log updates!\"\n"
                "              echo \"Modified logic files:\"\n"
                "              echo \"$CHANGED_SRC\"\n"
                "              echo \"\"\n"
                "              echo \"Please record the evolution/friction in references/map-debt.md or include 'Evolution-Check: none' in your commit message.\"\n"
                "              exit 1\n"
                "            fi\n"
                "            echo \"✓ Evolution & Map Debt documentation verified in PR diff.\"\n"
                "          else\n"
                "            echo \"✓ No core logic files changed in this PR.\"\n"
                "          fi\n"
            )
            write_file(ci_workflow_target, workflow_content, dry_run, force=False)
            announce("Installed verify-evolution-integrity.yml into .github/workflows/", dry_run)
        else:
            announce(f"exists {ci_workflow_target} (skipped)", dry_run)

    except (subprocess.CalledProcessError, FileNotFoundError):
        announce("⚠️  Warning: target is not inside a git repository or git is not installed.", dry_run)



# External comment: Orchestrate end-to-end project directory scaffolding
def create_project_structure(target: Path, dry_run: bool, force: bool) -> None:
    """Orchestrates creation of full Agentic OS project directory structure."""
    today = date.today().isoformat()
    project_name = target.resolve().name

    print(f"\n--- Project root: {target.resolve()} ---\n")

    _scaffold_root_files(target, dry_run, force, project_name)
    _scaffold_context_dir(target, dry_run, force, today)
    _scaffold_claude_dir(target, dry_run, force)
    _scaffold_3layer_memory(target, dry_run, force)
    _validate_and_finalize(target, dry_run)


# External comment: Scaffold global ~/.claude/CLAUDE.md kernel
def create_global_kernel(dry_run: bool, force: bool) -> None:
    """Creates ~/.claude/CLAUDE.md global agentic kernel if requested."""
    global_claude = Path.home() / ".claude"
    global_md = global_claude / "CLAUDE.md"

    print(f"\n--- Global kernel: {global_claude} ---\n")
    make_dir(global_claude, dry_run)
    write_file(global_md, load_template("CLAUDE_MD_GLOBAL.md"), dry_run, force)


# External comment: Print initialization completion summary and next steps
def signing_identity_notice(target: Path) -> List[str]:
    """READ-ONLY report of cryptographic-verification readiness for `target` (auth-ciba-increment-b T13, Item C).

    Reports whether ssh-keygen can verify SSHSIG, whether `allowed_signers` holds a key scoped to the gate
    namespace, and prints the exact command a HUMAN runs to set the identity up. It never creates a key, never writes `context/identity/` and never runs the
    setup: os-init is an agent-run surface, so enrolling a key from here would be an enrollment path
    for an agent."""
    lines = ["\n6. Signing identity (cryptographic gates: APPROVED, VERIFY_EXIT, DONE):"]
    try:
        from control_plane.identity_layout import default_layout
        from control_plane.identity_setup import identity_status

        status = identity_status(default_layout(target))
    except Exception as exc:  # older installed copies may not ship the signing modules
        return lines + [f"   (signing status unavailable: {exc}; see the os-signing-setup skill)"]
    cap = status["ssh_keygen"]
    lines.append(
        "   ssh-keygen: " + (f"OpenSSH {cap['version']}, SSHSIG {'supported' if cap['supports_sshsig'] else 'NOT supported (needs >= 8.1)'}"
                             if cap["available"] else f"unavailable ({cap['reason']}); install OpenSSH >= 8.1")
    )
    if status["enrolled_keys"]:
        lines.append(f"   {status['enrolled_keys']} enrolled key(s):")
        for key in status["keys"]:
            lines.append(f"   - {key['principal']}  {key['key_type']}  {key['fingerprint']}")
    if status["ready"]:
        lines.append("   Signing identity is set up and safely isolated.")
    else:
        lines.append("   Signing identity is not set up yet (needed to approve Gate 1). A HUMAN runs, in their own terminal:")
        lines.append("     python3 plugins/agent-agentic-os/scripts/setup_ciba_identity.py")
        lines.append("   os-init never runs this and never creates or enrolls a key; agents must not either (see the os-signing-setup skill).")
        for failure in status["failures"][:3]:
            lines.append(f"   - {failure}")
    return lines + dual_identity_notice(target)


# External comment: Report the real-work / simulation / isolation split separately
def dual_identity_notice(target: Path) -> List[str]:
    """READ-ONLY report of the two approval identities and of isolation, each with its own readiness.

    Real work (context/control_plane.db) is approved only by the human's key; simulations
    (context/simulation/simulation_control_plane.db) only by the agent's simulation key. Isolation
    (the agent running as its own OS account) is what stops a hostile agent from editing the human's
    trust files; its account commands are printed for the HUMAN, per operating system."""
    try:
        from control_plane.simulation_identity import dual_identity_status
    except Exception as exc:  # older installed copies may not ship the module
        return [f"   (dual-identity status unavailable: {exc})"]
    status = dual_identity_status(target)
    lines = ["\n   Approval identities (one approver per pipeline):"]
    human = status["human"]
    lines.append(f"   - Human approval: {'ready' if human['ready'] else 'not ready'} ({human['detail']})")
    sim = status["simulation"]
    lines.append(f"   - Simulation: {'ready' if sim['ready'] else 'not set up'} ({sim['detail']})")
    if not sim["ready"]:
        lines.append("       The agent may create it (it is the agent's own key, kept apart from yours):")
        lines.append("         python3 plugins/agent-agentic-os/scripts/init_agentic_os.py --target . --retrofit --with-simulation-identity")
    iso = status["isolation"]
    lines.append(f"   - Isolation: {'ready' if iso['ready'] else 'not ready'} ({iso['detail']})")
    if iso.get("commands"):
        lines.append("       A HUMAN administrator runs (for this operating system; see references/isolation-setup.md for others):")
        lines.extend(f"         {command}" for command in iso["commands"])
    return lines


# External comment: Create or reuse the agent's simulation identity on request
def ensure_simulation_identity_step(target: Path, dry_run: bool) -> None:
    """Creates or reuses context/simulation/identity/ (agent-owned); never writes context/identity/."""
    if dry_run:
        print("  [DRY RUN] would create or reuse the simulation identity in context/simulation/identity/")
        return
    from control_plane.simulation_identity import ensure_simulation_identity

    info = ensure_simulation_identity(target)
    verb = "Created" if info["created"] else "Reused"
    print(f"  {verb} the simulation identity {info['fingerprint']} in {info['layout'].root}")


def print_next_steps(target: Path, did_global: bool, did_retrofit: bool) -> None:
    """Displays user guidance, next steps, and plugin installation commands."""
    print("\n" + "=" * 60)
    print("Agentic OS Initialization / Retrofit Complete!")
    print("=" * 60)
    print(f"\n1. Canonical Project Instructions:")
    print(f"   - {target}/AGENTS.md (single source of truth)")
    print(f"   - {target}/CLAUDE.md (optional pointer to AGENTS.md)")
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
    print("   context/memory/, context/status.md, context/os-state.json, context/events.jsonl, context/.locks/, .claude/")
    print("\n5. Recommended Verification Check:")
    print("   Immediately run the health check skill/engine to verify substrate liveness:")
    print("   • Slash command / Skill: /os-health-check")
    print("   • Deterministic substrate check:")
    print("     test -f context/control_plane.db && test -f .claude/hooks/hooks.json && test -f .git/hooks/pre-commit-evolution-guard && test -f .github/workflows/verify-evolution-integrity.yml && echo 'OK: All OS substrates active'")
    for line in signing_identity_notice(target):
        print(line)

    if _CREATED_BACKUPS:
        print("\n" + "!" * 60)
        print("ATTENTION: Temporary Backup Files Created (.bak)")
        print("!" * 60)
        for b in _CREATED_BACKUPS:
            print(f"   • {b.resolve()}")
        print("\n👉 Consuming Agent Directive for Backup Cleanup:")
        print("   DO NOT blindly delete these .bak files with automated scripts.")
        print("   First, review the diff between each .bak file and the newly updated file.")
        print("   Reconcile any custom project-specific rules, configs, or domain contexts.")
        print("   Once all edits are verified and preserved, manually remove the .bak files.")
    print()



# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

# External comment: Parse command line arguments
def _parse_args() -> argparse.Namespace:
    """Parses and validates command line arguments."""
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
        help="Also write ~/.claude/CLAUDE.md global agentic kernel"
    )
    parser.add_argument(
        "--retrofit",
        action="store_true",
        help="Retrofit existing repository: seed 3-layer memory, sync instruction files, and auto-upgrade skills"
    )
    parser.add_argument(
        "--sync-instructions",
        action="store_true",
        help="Merge missing Agentic OS sections into AGENTS.md; preserve optional CLAUDE.md pointer"
    )
    parser.add_argument(
        "--install-hooks",
        action="store_true",
        help="Install or update only the Agentic OS git hooks in the target repository"
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
        "--contribution-mode",
        choices=["fork-and-pr", "local-patch-and-issue", "domain-override"],
        default=None,
        help="Strategy for managing and contributing plugin/skill bug fixes (default: interactive prompt or fork-and-pr)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files with .bak backups"
    )
    parser.add_argument(
        "--with-simulation-identity",
        action="store_true",
        help="Create or reuse the agent's simulation signing identity in context/simulation/identity/ "
             "(never touches the human's production trust file)"
    )
    return parser.parse_args()


# External comment: Execute scaffold or retrofit action workflow
def _execute_action(target: Path, args: argparse.Namespace) -> None:
    """Executes either retrofit migration or fresh project scaffolding."""
    if args.install_hooks:
        print(f"\n--- Installing Git Hooks Only: {target.resolve()} ---\n")
        _validate_and_finalize(target, args.dry_run, install_workflow=False)
    elif args.retrofit:
        print(f"\n--- Retrofitting Existing Repository: {target.resolve()} ---\n")
        _scaffold_3layer_memory(target, args.dry_run, args.force)
        _configure_plugin_contribution_policy(target, args.contribution_mode, args.dry_run, args.force)
        _init_control_plane_db(target, args.dry_run)
        _scaffold_claude_dir(target, args.dry_run, args.force)
        _validate_and_finalize(target, args.dry_run)
        sync_instructions(target, args.dry_run)
        sync_rules(target, args.dry_run)
        retrofit_existing_skills(target, args.dry_run, fix=True)
        _scaffold_plugin_evolution_substrates(target, args.dry_run, args.force)
    else:
        create_project_structure(target, args.dry_run, args.force)
        _scaffold_plugin_evolution_substrates(target, args.dry_run, args.force)
        if args.sync_instructions:
            sync_instructions(target, args.dry_run)
        if args.sync_rules:
            sync_rules(target, args.dry_run)


# External comment: CLI entry point
def main() -> None:
    """Entry point for os-init / init_agentic_os CLI engine."""
    args = _parse_args()
    target = Path(args.target).expanduser().resolve()

    if not target.exists():
        print(f"Error: target directory does not exist: {target}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("\n[DRY RUN] Previewing changes - nothing will be written.\n")

    _execute_action(target, args)

    if args.install_hooks:
        if not args.dry_run:
            print("Git hooks installation complete; no other project files were changed.")
        return

    if args.with_simulation_identity:
        ensure_simulation_identity_step(target, args.dry_run)

    if args.global_kernel:
        create_global_kernel(args.dry_run, args.force)

    if not args.dry_run:
        print_next_steps(target, args.global_kernel, args.retrofit)
    else:
        print("\n[DRY RUN] Complete. Run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
