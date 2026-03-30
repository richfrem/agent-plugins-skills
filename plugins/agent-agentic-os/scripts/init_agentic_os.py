#!/usr/bin/env python3
"""
Purpose: Initialize the Agentic OS / Agent Harness structure in a target project directory.
Creates CLAUDE.md, context/, .claude/, START_HERE.md, heartbeat.md, and optional
global ~/.claude/CLAUDE.md. Safe for existing projects via --dry-run preview.
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import date


# ---------------------------------------------------------------------------
# Template Loader
# ---------------------------------------------------------------------------

def load_template(filename: str) -> str:
    """Load a given template from the skills/os-init/templates directory.
    Tries CLAUDE_PLUGIN_ROOT env var first (set by Claude Code and npx skills),
    then falls back to path-relative resolution for direct script invocation."""
    env_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env_root:
        plugin_root = Path(env_root).resolve()
    else:
        plugin_root = Path(__file__).resolve().parent.parent.parent.parent
    template_path = plugin_root / "skills" / "os-init" / "templates" / filename
    
    if not template_path.exists():
        # Fail loudly if template is missing (crucial for kernel setup)
        print(f"Error: Template {filename} not found at {template_path}", file=sys.stderr)
        print("This typically happens if the script is run outside the plugin directory structure.", file=sys.stderr)
        sys.exit(1)
        
    return template_path.read_text(encoding="utf-8")


def copy_runtime_file(filename: str) -> str:
    """Load a runtime file from scripts/ (canonical location) or skills/os-init/runtime/ (legacy fallback).
    Tries CLAUDE_PLUGIN_ROOT env var first (set by Claude Code and npx skills),
    then falls back to path-relative resolution for direct script invocation."""
    env_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env_root:
        plugin_root = Path(env_root).resolve()
    else:
        plugin_root = Path(__file__).resolve().parent.parent.parent.parent

    # Canonical location: scripts/ at plugin root
    canonical_path = plugin_root / "scripts" / filename
    if canonical_path.exists():
        return canonical_path.read_text(encoding="utf-8")

    # Legacy fallback: skills/os-init/runtime/ (symlink to scripts/)
    legacy_path = plugin_root / "skills" / "os-init" / "runtime" / filename
    if legacy_path.exists():
        return legacy_path.read_text(encoding="utf-8")

    print(f"Error: Runtime file {filename} not found at {canonical_path} or {legacy_path}", file=sys.stderr)
    print("This typically happens if the script is run outside the plugin directory structure.", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def announce(msg: str, dry_run: bool) -> None:
    """Print a status line with DRY RUN prefix when applicable."""
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"  {prefix}{msg}")


def make_dir(path: Path, dry_run: bool) -> None:
    """Create a directory if it does not exist."""
    if not path.exists():
        announce(f"mkdir  {path}", dry_run)
        if not dry_run:
            path.mkdir(parents=True, exist_ok=True)
    else:
        announce(f"exists {path} (skipped)", dry_run)


def write_file(path: Path, content: str, dry_run: bool, force: bool = False) -> None:
    """Write a file, skipping if it already exists unless force is set. Creates .bak backups."""
    if path.exists():
        if not force:
            announce(f"exists {path} (skipped - use --force to overwrite)", dry_run)
            return
        
        # P0 Red Team Fix: Never silently overwrite, especially CLAUDE.md
        backup_path = path.with_suffix(path.suffix + ".bak")
        announce(f"backup {path} -> {backup_path.name}", dry_run)
        if not dry_run:
            path.rename(backup_path)

    announce(f"write  {path}", dry_run)
    if not dry_run:
        path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Build functions
# ---------------------------------------------------------------------------

def create_project_structure(target: Path, dry_run: bool, force: bool) -> None:
    """Create the full Agentic OS directory tree in target."""
    today = date.today().isoformat()
    project_name = target.resolve().name

    print(f"\n--- Project root: {target.resolve()} ---\n")

    # Root files
    write_file(target / "CLAUDE.md",
               load_template("CLAUDE_MD_PROJECT.md").format(project_name=project_name),
               dry_run, force)
    write_file(target / "CLAUDE.local.md", load_template("CLAUDE_LOCAL_MD.md"), dry_run, force)
    write_file(target / "START_HERE.md", load_template("START_HERE_MD.md"), dry_run, force)
    write_file(target / "heartbeat.md", load_template("HEARTBEAT_MD.md"), dry_run, force)

    # context/
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

    # .claude/
    make_dir(target / ".claude", dry_run)
    make_dir(target / ".claude" / "agents", dry_run)
    make_dir(target / ".claude" / "commands", dry_run)
    make_dir(target / ".claude" / "hooks", dry_run)
    write_file(target / ".claude" / "hooks" / "hooks.json",
               load_template("HOOKS_JSON.json"), dry_run, force)

    # Validation and Permissions Step
    import subprocess
    try:
        subprocess.run(["git", "-C", str(target), "rev-parse", "--is-inside-work-tree"], 
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        announce("git repository detected (Safe Write Protocol rollback is supported)", dry_run)
    except (subprocess.CalledProcessError, FileNotFoundError):
        announce("⚠️  Warning: target is not inside a git repository or git is not installed. Safe Write Protocols relying on git stash/pop for rollbacks will fail.", dry_run)

    hooks_json_path = target / ".claude" / "hooks" / "hooks.json"
    if not dry_run and hooks_json_path.exists():
        import json
        try:
            with open(hooks_json_path, 'r', encoding='utf-8') as f:
                json.load(f)
            announce("hooks.json syntax validated", dry_run)
        except json.JSONDecodeError as e:
            announce(f"❌ Error: Generated hooks.json is invalid - {e}", dry_run)

    plugin_root = Path(__file__).resolve().parent.parent.parent.parent
    hook_script = plugin_root / "hooks" / "update_memory.py"
    if not dry_run and hook_script.exists():
        hook_script.chmod(0o755)
        announce(f"chmod 755 {hook_script.name}", dry_run)


def create_global_kernel(dry_run: bool, force: bool) -> None:
    """Create ~/.claude/CLAUDE.md for the global kernel."""
    global_claude = Path.home() / ".claude"
    global_md = global_claude / "CLAUDE.md"

    print(f"\n--- Global kernel: {global_claude} ---\n")
    make_dir(global_claude, dry_run)
    write_file(global_md, load_template("CLAUDE_MD_GLOBAL.md"), dry_run, force)


def print_next_steps(target: Path, did_global: bool) -> None:
    """Print post-init guidance."""
    print("\n" + "=" * 60)
    print("Agentic OS initialized. Next steps:")
    print("=" * 60)
    print(f"\n1. Fill in {target}/CLAUDE.md")
    print("   Add your build commands, architecture summary, conventions.")
    print(f"\n2. Fill in {target}/context/soul.md")
    print("   Define agent identity and tone (if using a persona).")
    print(f"\n3. Fill in {target}/context/user.md")
    print("   Add your working style and preferences.")
    print("\n4. Install skills (optional):")
    print("   npx skills add richfrem/agent-plugins-skills/plugins/agent-agentic-os")
    print("\n5. Add to .gitignore:")
    print("   CLAUDE.local.md")
    print("   context/memory/")
    print("   context/status.md")
    print("   context/os-state.json")
    print("   context/events.jsonl")
    print("   context/.locks/")
    print("   .claude/")
    print("\n6. Keep in git (shared with team):")
    print("   CLAUDE.md, context/soul.md, context/user.md, heartbeat.md, START_HERE.md")
    print("   context/kernel.py, context/agents.json, context/memory.md")
    if did_global:
        print("\n7. Global kernel created at ~/.claude/CLAUDE.md")
        print("   Add your identity, universal rules, and tool defaults there.")
        print("   Note: manually @import context/kernel.py or add kernel rules to this file")
    print("\n8. Start the OS (optional):")
    print("   /loop \"Read heartbeat.md and execute the items listed under Every Hour\" --interval 1h")
    print("\n9. Wire Hooks (optional, requires restart):")
    print("   Add to .claude/hooks/hooks.json under SessionStart and PostToolUse:")
    print("   { \"type\": \"command\", \"command\": \"python3 ${CLAUDE_PLUGIN_ROOT}/hooks/update_memory.py && cat .claude/hooks/hooks.json\", \"timeout\": 5 }")
    print()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Parse arguments and run the Agentic OS initialization."""
    parser = argparse.ArgumentParser(
        description="Initialize the Agentic OS / Agent Harness structure in a project."
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=Path("."),
        help="Project root directory to initialize (default: current directory)"
    )
    parser.add_argument(
        "--global",
        dest="global_kernel",
        action="store_true",
        help="Also scaffold ~/.claude/CLAUDE.md as global kernel"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be created without writing anything"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files (use with caution on existing projects)"
    )

    args = parser.parse_args()
    target = Path(args.target).expanduser().resolve()

    if not target.exists():
        print(f"Error: target directory does not exist: {target}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("\n[DRY RUN] Previewing changes - nothing will be written.\n")

    create_project_structure(target, args.dry_run, args.force)

    if args.global_kernel:
        create_global_kernel(args.dry_run, args.force)

    if not args.dry_run:
        print_next_steps(target, args.global_kernel)
    else:
        print("\n[DRY RUN] Complete. Run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
