"""
Plugin Add (CLI)
================

Purpose:
    Interactive plugin installer with an npx-skills-add-like TUI.
    Accepts a local path OR a GitHub owner/repo shorthand, clones into a
    temp directory if remote, discovers all plugins, lets the user select
    which to install, then runs bridge_installer.py for each.

Inspiration & Attribution:
    The interactive TUI design pattern (multiselect, arrow navigation, search,
    owner/repo GitHub shorthand, temp-clone-then-install flow) is inspired by
    the `npx skills add` command from the Vercel Labs `skills` CLI:
      https://github.com/vercel-labs/skills
      https://skills.sh
    This script re-implements those UX patterns in pure Python (stdlib only)
    for cross-platform compatibility and to operate at the plugin level
    (skills + agents + commands + hooks) rather than individual SKILL.md files.

Layer: Plugin Manager / Installation

Usage Examples:
    # Install from the local repo (select plugins interactively)
    python plugins/plugin-manager/scripts/plugin_add.py

    # Install from a remote GitHub repo
    python plugins/plugin-manager/scripts/plugin_add.py richfrem/agent-plugins-skills

    # Install all plugins non-interactively
    python plugins/plugin-manager/scripts/plugin_add.py richfrem/agent-plugins-skills --all -y

    # Dry-run preview
    python plugins/plugin-manager/scripts/plugin_add.py --dry-run

CLI Arguments:
    source          GitHub owner/repo OR local path (optional; defaults to cwd)
    --all           Select all discovered plugins without prompting
    -y / --yes      Skip confirmation prompts
    --dry-run       Preview actions without writing files
    --install-rules Also install rules into CLAUDE.md

Script Dependencies:
    os, sys, argparse, subprocess, shutil, tempfile, json, pathlib
"""

import os
import sys
import argparse
import subprocess
import shutil
import tempfile
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# UTF-8 safety on Windows
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
INSTALLER_SCRIPT = SCRIPT_DIR / "bridge_installer.py"

# ---------------------------------------------------------------------------
# ANSI colour helpers (no external deps)
# ---------------------------------------------------------------------------
_ANSI = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else True


def _col(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _ANSI else text


def cyan(t: str) -> str:    return _col("96", t)
def green(t: str) -> str:   return _col("92", t)
def yellow(t: str) -> str:  return _col("93", t)
def dim(t: str) -> str:     return _col("2", t)
def bold(t: str) -> str:    return _col("1", t)
def red(t: str) -> str:     return _col("91", t)


# ---------------------------------------------------------------------------
# Terminal raw-mode helpers for arrow-key / space navigation
# ---------------------------------------------------------------------------
def _read_key():
    """Read one keypress.  Returns a string token."""
    if sys.platform == "win32":
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):          # special / arrow prefix
            ch2 = msvcrt.getwch()
            return {"\x48": "UP", "\x50": "DOWN"}.get(ch2, "")
        return ch
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                ch += sys.stdin.read(2)
                return {"[A": "UP", "[B": "DOWN"}.get(ch[1:], "ESC")
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _clear_lines(n: int):
    if _ANSI:
        sys.stdout.write(f"\033[{n}A\033[J")
        sys.stdout.flush()


# ---------------------------------------------------------------------------
# Interactive multi-select (space = toggle, enter = confirm, / = search)
# ---------------------------------------------------------------------------
def _multiselect(title: str, items: list[dict]) -> list[dict]:
    """
    items: list of {"name": str, "description": str, "path": Path}
    Returns selected subset.
    """
    if not items:
        return []

    selected = set()
    cursor = 0
    search = ""
    PAGE = 18                   # visible rows

    def _filtered():
        q = search.lower()
        return [i for i in items if q in i["name"].lower() or q in i.get("description", "").lower()]

    def _render(filtered, first_render=False):
        lines = []
        lines.append(bold(title))
        lines.append(dim("  ↑↓ move  |  space select  |  / search  |  a all  |  enter confirm  |  q quit"))
        if search:
            lines.append(f"  {dim('Search:')} {cyan(search)}_")
        else:
            lines.append(dim("  Type / to search"))

        visible = filtered[max(0, cursor - PAGE // 2): cursor + PAGE]
        offset = max(0, cursor - PAGE // 2)

        for idx, item in enumerate(visible):
            real_idx = items.index(item)
            is_cursor = (offset + idx) == cursor
            is_selected = item["name"] in selected
            check = green("[x]") if is_selected else dim("[ ]")
            name  = cyan(item["name"]) if is_cursor else item["name"]
            desc  = dim(item.get("description", "")[:55])
            arrow = ">" if is_cursor else " "
            lines.append(f"  {arrow} {check} {name}  {desc}")

        count = len(selected)
        total = len(filtered)
        lines.append("")
        lines.append(f"  {green(str(count))} of {total} selected")

        if not first_render:
            _clear_lines(len(lines))
        print("\n".join(lines), flush=True)
        return len(lines)

    filtered = _filtered()
    line_count = _render(filtered, first_render=True)

    while True:
        key = _read_key()
        filtered = _filtered()
        if not filtered:
            cursor = 0
        else:
            cursor = min(cursor, len(filtered) - 1)

        if key == "UP":
            cursor = max(0, cursor - 1)
        elif key == "DOWN":
            cursor = min(len(filtered) - 1, cursor + 1)
        elif key == " ":
            if filtered and 0 <= cursor < len(filtered):
                name = filtered[cursor]["name"]
                if name in selected:
                    selected.discard(name)
                else:
                    selected.add(name)
        elif key in ("\r", "\n", ""):
            break
        elif key in ("q", "Q", "\x03"):
            print(red("\nCancelled."))
            sys.exit(0)
        elif key == "a":
            if len(selected) == len(items):
                selected.clear()
            else:
                selected = {i["name"] for i in items}
        elif key == "/":
            search = ""
            cursor = 0
        elif key == "\x7f":          # backspace
            search = search[:-1]
            cursor = 0
        elif key and len(key) == 1 and key.isprintable():
            if search == "" and key == "/":
                pass
            else:
                search += key
                cursor = 0

        line_count = _render(filtered)

    print()
    return [i for i in items if i["name"] in selected]


# ---------------------------------------------------------------------------
# GitHub clone helpers
# ---------------------------------------------------------------------------
def _is_github_shorthand(source: str) -> bool:
    """owner/repo style with no path separators other than one /."""
    parts = source.strip("/").split("/")
    return (
        len(parts) == 2
        and not source.startswith("http")
        and not source.startswith("git@")
        and not os.path.exists(source)
    )


def _clone_repo(owner_repo: str, dest: Path) -> Path:
    url = f"https://github.com/{owner_repo}.git"
    print(f"\n  {cyan('Source:')} https://github.com/{owner_repo}.git")
    print(f"  {dim('Cloning repository...')}", flush=True)
    result = subprocess.run(
        ["git", "clone", "--depth=1", url, str(dest)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(red(f"\n  Clone failed:\n{result.stderr}"))
        sys.exit(1)
    print(f"  {green('Cloned')} → {dim(str(dest))}")
    return dest


# ---------------------------------------------------------------------------
# Plugin discovery
# ---------------------------------------------------------------------------
def _discover_plugins(plugins_root: Path) -> list[dict]:
    """Walk plugins_root and return metadata for each plugin directory."""
    plugins = []
    if not plugins_root.is_dir():
        return plugins

    for p in sorted(plugins_root.iterdir()):
        if not p.is_dir() or p.name.startswith(".") or p.name.startswith("__"):
            continue
        if p.name in ("node_modules", "venv", "env"):
            continue

        meta = {"name": p.name, "description": "", "path": p, "version": ""}
        # Try .claude-plugin/plugin.json first, then plugin.json
        for manifest_rel in [".claude-plugin/plugin.json", "plugin.json"]:
            manifest = p / manifest_rel
            if manifest.exists():
                try:
                    data = json.loads(manifest.read_text(encoding="utf-8"))
                    meta["description"] = data.get("description", "")
                    meta["version"] = data.get("version", "")
                    meta["name"] = data.get("name", p.name)
                except Exception:
                    pass
                break

        # Fallback description: count skills
        if not meta["description"]:
            skills_dir = p / "skills"
            n = len(list(skills_dir.iterdir())) if skills_dir.is_dir() else 0
            meta["description"] = f"{n} skill{'s' if n != 1 else ''}" if n else ""

        plugins.append(meta)

    return plugins


# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
def _print_banner(source_label: str):
    print()
    print(bold("  ██████╗ ██╗     ██╗   ██╗ ██████╗ ██╗███╗  ██╗███████╗"))
    print(bold("  ██╔══██╗██║     ██║   ██║██╔════╝ ██║████╗ ██║██╔════╝"))
    print(bold("  ██████╔╝██║     ██║   ██║██║  ███╗██║██╔██╗██║███████╗"))
    print(bold("  ██╔═══╝ ██║     ██║   ██║██║   ██║██║██║╚████║╚════██║"))
    print(bold("  ██║     ███████╗╚██████╔╝╚██████╔╝██║██║ ╚███║███████║"))
    print(bold("  ╚═╝     ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝╚═╝  ╚══╝╚══════╝"))
    print()
    print(f"  {dim('Source:')} {cyan(source_label)}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Interactive plugin installer  (npx-skills-add style, for full plugins)"
    )
    parser.add_argument(
        "source",
        nargs="?",
        default=None,
        help="owner/repo (GitHub) or local path to a repo root (default: current directory)",
    )
    parser.add_argument("--all", "-a", action="store_true", help="Select all plugins without prompting")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompts")
    parser.add_argument("--dry-run", action="store_true", help="Preview — no files written")
    parser.add_argument("--install-rules", action="store_true", help="Also install plugin rules into CLAUDE.md")
    args = parser.parse_args()

    if not INSTALLER_SCRIPT.exists():
        print(red(f"  Error: bridge_installer.py not found at {INSTALLER_SCRIPT}"))
        sys.exit(1)

    # ------------------------------------------------------------------
    # Resolve source
    # ------------------------------------------------------------------
    temp_dir = None
    plugins_root: Path

    if args.source and _is_github_shorthand(args.source):
        _print_banner(args.source)
        temp_dir = Path(tempfile.mkdtemp(prefix="plugin_add_"))
        repo_root = _clone_repo(args.source, temp_dir / args.source.replace("/", "_"))
        plugins_root = repo_root / "plugins"
    elif args.source:
        source_path = Path(args.source).resolve()
        _print_banner(str(source_path))
        plugins_root = source_path / "plugins" if (source_path / "plugins").is_dir() else source_path
    else:
        # Default: find this repo's plugins/ relative to the project root
        # Walk up from cwd until we find a plugins/ directory
        cwd = Path.cwd()
        candidate = cwd
        for _ in range(4):
            if (candidate / "plugins").is_dir():
                break
            candidate = candidate.parent
        plugins_root = candidate / "plugins"
        _print_banner(str(candidate))

    if not plugins_root.is_dir():
        print(red(f"  Error: plugins directory not found at {plugins_root}"))
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Discover plugins
    # ------------------------------------------------------------------
    print(f"  {dim('Discovering plugins...')}", end="", flush=True)
    all_plugins = _discover_plugins(plugins_root)
    print(f"\r  {green(str(len(all_plugins)))} plugins found" + " " * 20)

    if not all_plugins:
        print(red("  No plugins found. Is this a valid agent-plugins-skills repo?"))
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Plugin selection
    # ------------------------------------------------------------------
    if args.all or args.yes:
        selected_plugins = all_plugins
        print(f"  {green('✓')} Installing all {len(selected_plugins)} plugins")
    else:
        selected_plugins = _multiselect(
            "  Select plugins to install",
            all_plugins
        )

    if not selected_plugins:
        print(yellow("  No plugins selected. Exiting."))
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(0)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    tag = " [DRY RUN]" if args.dry_run else ""
    print()
    print(bold(f"  Installation Plan{tag}"))
    print(f"  {dim('─' * 48)}")
    for p in selected_plugins:
        ver = f"  {dim('v' + p['version'])}" if p["version"] else ""
        desc = f"  {dim(p['description'][:50])}" if p["description"] else ""
        print(f"   {green('•')} {cyan(p['name'])}{ver}{desc}")
    print(f"  {dim('─' * 48)}")
    print(f"  {green(str(len(selected_plugins)))} plugin(s) → {dim('.agents/')} (skills + agents + commands + hooks)")
    print()

    if not args.yes and not args.dry_run:
        try:
            answer = input(f"  Proceed? [{green('y')}/n] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(red("\n  Cancelled."))
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
            sys.exit(0)
        if answer and answer not in ("y", "yes"):
            print(yellow("  Cancelled."))
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
            sys.exit(0)

    # ------------------------------------------------------------------
    # Install
    # ------------------------------------------------------------------
    success_count = 0
    fail_count = 0

    for plugin in selected_plugins:
        print(f"\n  {bold('→')} {cyan(plugin['name'])}")
        cmd = [sys.executable, str(INSTALLER_SCRIPT), "--plugin", str(plugin["path"])]
        if args.dry_run:
            cmd.append("--dry-run")
        if args.install_rules:
            cmd.append("--install-rules")

        result = subprocess.run(cmd, text=True)
        if result.returncode == 0:
            print(f"    {green('✓')} Done")
            success_count += 1
        else:
            print(f"    {red('✗')} Failed (exit {result.returncode})")
            fail_count += 1

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    if temp_dir and temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)

    # ------------------------------------------------------------------
    # Result
    # ------------------------------------------------------------------
    print()
    print(f"  {dim('═' * 48)}")
    status = "DRY RUN complete" if args.dry_run else "Installation complete"
    print(f"  {bold(status)}")
    print(f"  {green('✓ Success:')} {success_count}")
    if fail_count:
        print(f"  {red('✗ Failed: ')} {fail_count}")
    print(f"  {dim('═' * 48)}")
    print()

    if not args.dry_run and success_count:
        print(f"  {dim('Tip:')} Run {cyan('npx skills update')} to sync the skills lock file.")
        print(f"  {dim('Tip:')} Restart your agent to pick up new commands and hooks.")
        print()

    sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
