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

Key Input Dependencies:
    - Template directory: assets/templates/ or skills/os-init/assets/templates/
    - Agent control plane schema: context/control_plane.db (auto-initialized)
    - Instruction files: CLAUDE.md (source of truth for mirroring)
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
    - _merge_instructions_with_judgment() — Merges OS sections into instruction files
    - sync_instructions() — Reconciles CLAUDE.md to GEMINI, Copilot, AGENTS
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
import sqlite3
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Template & Runtime File Loaders
# ---------------------------------------------------------------------------

# External comment: Resolve plugin root directory
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


# External comment: Write content to file with backup handling
def write_file(path: Path, content: str, dry_run: bool, force: bool = False) -> None:
    """Writes content to file with optional backup creation if existing."""
    if path.exists():
        if not force:
            announce(f"exists {path} (skipped - use --force to overwrite)", dry_run)
            return
        backup_path = path.with_suffix(path.suffix + ".bak")
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
# Instruction File Synchronizer (CLAUDE -> GEMINI, Copilot, AGENTS)
# ---------------------------------------------------------------------------

def _merge_instructions_with_judgment(existing_text: str, project_name: str) -> str:
    """Smartly merge Agentic OS evolution & memory sections into existing instruction files without clobbering project domain context."""
    # Ensure standard title
    text = existing_text
    
    # Check for Phase 0 Intake & Socratic Gate
    if "Phase 0 Intake & Socratic Gate" not in text and "interview-spec" not in text:
        intake_block = (
            "\n\n## Phase 0 Intake & Socratic Gate (Mandatory)\n"
            "> Every engineering task, feature proposal, bugfix, or improvement MUST trigger `interview-spec` first.\n"
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


def sync_instructions(target: Path, dry_run: bool) -> None:
    """Reconcile CLAUDE.md to GEMINI.md, .github/copilot-instructions.md, and AGENTS.md using section preservation rather than blind overwrite."""
    claude_md = target / "CLAUDE.md"
    if not claude_md.exists():
        announce("Warning: CLAUDE.md not found — skipping instruction synchronization.", dry_run)
        return

    # Enrich CLAUDE.md with Phase 0 intake, 3-layer memory, and pre-completion gate if missing
    project_name = target.resolve().name
    claude_content = claude_md.read_text(encoding="utf-8")
    enriched_claude = _merge_instructions_with_judgment(claude_content, project_name)
    if enriched_claude != claude_content:
        write_file(claude_md, enriched_claude, dry_run, force=True)
        announce("Enriched CLAUDE.md with core control-plane intake and memory gates", dry_run)

    plugin_root = _get_plugin_root()
    sync_script = plugin_root.parent / "cli-agents" / "scripts" / "sync_instruction_files.py"
    if not sync_script.exists():
        sync_script = target / "plugins" / "cli-agents" / "scripts" / "sync_instruction_files.py"

    if sync_script.exists():
        announce("Synchronizing instruction files via sync_instruction_files.py...", dry_run)
        if not dry_run:
            cmd = [sys.executable, str(sync_script), "--project-root", str(target), "--execute"]
            subprocess.run(cmd, check=True)
    else:
        # Smart Section-Aware Fallback Mirroring
        announce("Reconciling instructions to GEMINI.md, AGENTS.md, and copilot-instructions.md with section preservation...", dry_run)
        claude_content = claude_md.read_text(encoding="utf-8")
        project_name = target.resolve().name

        # GEMINI.md
        gemini_target = target / "GEMINI.md"
        existing_gemini = gemini_target.read_text(encoding="utf-8") if gemini_target.exists() else ""
        gemini_text = re.sub(r"^#\s+.*", "# GEMINI.md", claude_content, count=1)
        
        # Preserve existing Gemini Tool Mapping or add standard table
        if "## Gemini CLI Tool Mapping" in existing_gemini:
            tool_mapping_part = existing_gemini[existing_gemini.find("## Gemini CLI Tool Mapping"):]
            gemini_text = gemini_text.split("## Gemini CLI Tool Mapping")[0].rstrip() + "\n\n" + tool_mapping_part
        elif "## Gemini CLI Tool Mapping" not in gemini_text:
            gemini_text += "\n\n## Gemini CLI Tool Mapping\n| Claude Code Tool | Gemini CLI Equivalent |\n|---|---|\n| View | view_file |\n| Edit | replace_file_content |\n| Write | write_to_file |\n| Bash | run_command |\n| Grep | grep_search |\n| Glob | find_by_name |\n| Agent | invoke_subagent |\n"
        write_file(gemini_target, gemini_text, dry_run, force=True)

        # AGENTS.md
        agents_target = target / "AGENTS.md"
        agents_text = re.sub(r"^#\s+.*", "# AGENTS.md", claude_content, count=1)
        write_file(agents_target, agents_text, dry_run, force=True)

        # .github/copilot-instructions.md
        copilot_dir = target / ".github"
        make_dir(copilot_dir, dry_run)
        copilot_header = f"# Copilot Instructions for {project_name}\n\n> Authoritative repository instructions for GitHub Copilot. Mirrors CLAUDE.md.\n\n"
        body = re.sub(r"^#\s+.*", "", claude_content, count=1).lstrip()
        write_file(copilot_dir / "copilot-instructions.md", copilot_header + body, dry_run, force=True)


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



CONTROL_PLANE_SCHEMA_SQL = """PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    state TEXT NOT NULL CHECK (
        state IN (
            'INTAKE', 'INTERVIEW', 'DRAFT_PLAN', 'MULTI_AGENT_REVIEW', 'PLAN_REVIEW', 'AWAITING_APPROVAL',
            'APPROVED', 'IN_WORKTREE', 'WORKTREE_REVIEW', 'MULTI_AGENT_CODE_REVIEW', 'VERIFY_EXIT', 'DONE',
            'ROLLED_BACK', 'ESCALATED'
        )
    ),
    runtime_tool TEXT NOT NULL,
    worktree_path TEXT,
    worktree_branch TEXT,
    worktree_state TEXT CHECK (
        worktree_state IS NULL OR worktree_state IN (
            'written_in_worktree', 'committed_in_worktree', 'pushed_to_origin',
            'merged_into_origin_main', 'local_branch_ref_updated', 'checked_out_on_disk'
        )
    ),
    spec_path TEXT,
    model_tier TEXT CHECK (model_tier IS NULL OR model_tier IN ('low', 'medium', 'high')),
    model_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_transitions (
    transition_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    actor TEXT NOT NULL,
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS locked_verifier_baselines (
    baseline_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    expected_sha256 TEXT NOT NULL,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS critic_reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    iteration INTEGER NOT NULL CHECK(iteration BETWEEN 1 AND 3),
    model_used TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK (verdict IN ('PASS', 'REVISE', 'REJECT')),
    critique_findings TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS verification_receipts (
    receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    gate_name TEXT NOT NULL,
    command_executed TEXT NOT NULL,
    exit_code INTEGER NOT NULL,
    receipt_token TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS asymmetric_persistence_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    destination TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('OBSERVED', 'HYPOTHESIS', 'CONFIRMED', 'RESOLVED')),
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state);
CREATE INDEX IF NOT EXISTS idx_transitions_task ON task_transitions(task_id);
"""


# External comment: Initialize SQLite control plane database
def _init_control_plane_db(target: Path, dry_run: bool) -> None:
    """Initializes SQLite control plane database with WAL mode and schema."""
    db_path = target / "context" / "control_plane.db"
    if db_path.exists():
        announce(f"exists {db_path} (skipped)", dry_run)
        return

    announce(f"init   {db_path}", dry_run)
    if not dry_run:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path), timeout=10.0)
        try:
            conn.executescript(CONTROL_PLANE_SCHEMA_SQL)
            conn.commit()
        finally:
            conn.close()


# ---------------------------------------------------------------------------
# Standard Scaffolding
# ---------------------------------------------------------------------------

# External comment: Scaffold repository root instruction files
def _scaffold_root_files(target: Path, dry_run: bool, force: bool, project_name: str) -> None:
    """Scaffolds top-level kernel instructions, architecture, and project status files."""
    write_file(target / "CLAUDE.md",
               load_template("CLAUDE_MD_PROJECT.md").format(project_name=project_name),
               dry_run, force)
    write_file(target / "CLAUDE.local.md", load_template("CLAUDE_LOCAL_MD.md"), dry_run, force)
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


# External comment: Validate git repo and install pre-commit evolution guard
def _validate_and_finalize(target: Path, dry_run: bool) -> None:
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

            # Install pre-push review guard
            push_guard_source = plugin_root / "scripts" / "pre-push-review-guard"
            if push_guard_source.exists():
                push_guard_target = git_hooks_dir / "pre-push-review-guard"
                push_guard_content = push_guard_source.read_text(encoding="utf-8")
                write_file(push_guard_target, push_guard_content, dry_run, force=True)
                if not dry_run:
                    push_guard_target.chmod(0o755)

                # Wire the guard into the pre-push hook
                pre_push = git_hooks_dir / "pre-push"
                if pre_push.exists():
                    pp_content = pre_push.read_text(encoding="utf-8")
                    if "pre-push-review-guard" not in pp_content:
                        pp_block = "\n# Run review guard if it exists\nif [ -x \"$HOOKS_DIR/pre-push-review-guard\" ]; then\n    \"$HOOKS_DIR/pre-push-review-guard\" || exit 1\nfi\n"
                        if "\nexit 0" in pp_content:
                            idx = pp_content.rfind("\nexit 0")
                            pp_content = pp_content[:idx] + pp_block + "\nexit 0" + pp_content[idx+7:]
                        else:
                            pp_content += pp_block + "\nexit 0\n"
                        write_file(pre_push, pp_content, dry_run, force=True)
                else:
                    minimal_push_hook = (
                        "#!/usr/bin/env bash\n"
                        "# pre-push hook — installed by init_agentic_os.py\n"
                        "HOOKS_DIR=\"$(dirname \"$0\")\"\n"
                        "\n"
                        "# Run review guard\n"
                        "if [ -x \"$HOOKS_DIR/pre-push-review-guard\" ]; then\n"
                        "    \"$HOOKS_DIR/pre-push-review-guard\" || exit 1\n"
                        "fi\n"
                        "\n"
                        "exit 0\n"
                    )
                    write_file(pre_push, minimal_push_hook, dry_run, force=False)
                    if not dry_run:
                        pre_push.chmod(0o755)
                announce("Installed pre-push-review-guard into .git/hooks/", dry_run)

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
                "      - 'investment_screener/backend/py_services/**'\n"
                "      - 'src/**'\n"
                "      - 'investment_screener/backend/src/**'\n\n"
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
                "        run: |\n"
                "          # Check if PR touches core logic\n"
                "          CHANGED_SRC=$(git diff --name-only origin/${{ github.base_ref }}...HEAD | grep -E '^(plugins/|investment_screener/backend/py_services/|py_services/|src/|investment_screener/backend/src/)' || true)\n"
                "          \n"
                "          if [ -n \"$CHANGED_SRC\" ]; then\n"
                "            echo \"Checking Evolution & Map Debt compliance for modified code...\"\n"
                "            \n"
                "            # Check for escape valve in commit messages\n"
                "            if git log origin/${{ github.base_ref }}...HEAD --grep='Evolution-Check:[[:space:]]*none' -n 1 | grep -q 'Evolution-Check'; then\n"
                "              echo \"✓ Escape valve found: Evolution-Check: none trailer verified.\"\n"
                "              exit 0\n"
                "            fi\n"
                "            \n"
                "            # Check for map-debt, wiki, or evolution-log changes\n"
                "            DOC_CHANGED=$(git diff --name-only origin/${{ github.base_ref }}...HEAD | grep -E '^(references/map-debt.md|wiki/|plugins/.*/references/evolution-log.md)' || true)\n"
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
def print_next_steps(target: Path, did_global: bool, did_retrofit: bool) -> None:
    """Displays user guidance, next steps, and plugin installation commands."""
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
    print("\n5. Recommended Verification Check:")
    print("   Immediately run the health check skill/engine to verify substrate liveness:")
    print("   • Slash command / Skill: /os-health-check")
    print("   • Deterministic substrate check:")
    print("     test -f context/control_plane.db && test -f .claude/hooks/hooks.json && test -f .git/hooks/pre-commit-evolution-guard && test -f .github/workflows/verify-evolution-integrity.yml && echo 'OK: All OS substrates active'")

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
    return parser.parse_args()


# External comment: Execute scaffold or retrofit action workflow
def _execute_action(target: Path, args: argparse.Namespace) -> None:
    """Executes either retrofit migration or fresh project scaffolding."""
    if args.retrofit:
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

    if args.global_kernel:
        create_global_kernel(args.dry_run, args.force)

    if not args.dry_run:
        print_next_steps(target, args.global_kernel, args.retrofit)
    else:
        print("\n[DRY RUN] Complete. Run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
