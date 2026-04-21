"""
Plugin Add (CLI)
================

Purpose:
    Interactive plugin installer with a multiselect TUI.
    Accepts a local path OR a GitHub owner/repo shorthand, clones into a
    temp directory if remote, discovers all plugins, lets the user select
    which to install, then runs plugin_installer.py for each.

    The interactive TUI design pattern (multiselect, arrow navigation, search,
    owner/repo GitHub shorthand, temp-clone-then-install flow) follows modern
    command-line interface best practices:
      https://github.com/vercel-labs/skills
      https://skills.sh
    This script re-implements those UX patterns in pure Python (stdlib only)
    for cross-platform compatibility and to operate at the plugin level
    (skills + agents + commands + hooks) rather than individual SKILL.md files.

Layer: Plugin Manager / Installation

Usage Examples:
    # Install from the local repo (select plugins interactively)
    python plugins/plugin-manager/scripts/plugin_add.py

    # Install from explicit local path (relative or absolute, Mac/Linux/Windows)
    python plugins/plugin-manager/scripts/plugin_add.py plugins/
    python plugins/plugin-manager/scripts/plugin_add.py plugins/agent-scaffolders
    python plugins/plugin-manager/scripts/plugin_add.py /Users/path/to/plugins
    python plugins/plugin-manager/scripts/plugin_add.py C:\\Users\\path\\to\\plugins

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
INSTALLER_SCRIPT = SCRIPT_DIR / "plugin_installer.py"

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
def _multiselect(title: str, items: list) -> list:
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
def _is_github_source(source: str) -> bool:
    """Return True if source looks like a GitHub reference (owner/repo or URL)."""
    if os.path.exists(source):
        return False
    if source.startswith("http://") or source.startswith("https://") or source.startswith("git@"):
        return True
    # owner/repo[/optional/subpath]
    parts = source.strip("/").split("/")
    return len(parts) >= 2 and not source.startswith(".")


def _parse_github_source(source: str):
    """
    Parse a GitHub source string into (owner/repo, optional_subpath).

    Supports:
      anthropics/claude-plugins-official                  → ("anthropics/claude-plugins-official", None)
      anthropics/claude-plugins-official/plugins          → ("anthropics/claude-plugins-official", "plugins")
      anthropics/knowledge-work-plugins/engineering       → ("anthropics/knowledge-work-plugins", "engineering")
      https://github.com/anthropics/claude-plugins-official/tree/main/plugins
                                                          → ("anthropics/claude-plugins-official", "plugins")
    """
    s = source.strip("/")

    # Strip full GitHub URLs
    for prefix in ("https://github.com/", "http://github.com/", "github.com/"):
        if s.startswith(prefix):
            s = s[len(prefix):]
            break

    # Strip git@ URLs: git@github.com:owner/repo.git
    if s.startswith("git@github.com:"):
        s = s[len("git@github.com:"):].removesuffix(".git")

    # Strip GitHub web tree noise: owner/repo/tree/BRANCH/subpath → owner/repo/subpath
    parts = s.rstrip(".git").split("/")
    if len(parts) >= 4 and parts[2] == "tree":
        # parts: [owner, repo, "tree", branch, ...subpath]
        owner_repo = f"{parts[0]}/{parts[1]}"
        subpath = "/".join(parts[4:]) or None
        return owner_repo, subpath

    # Plain owner/repo[/subpath]
    owner_repo = f"{parts[0]}/{parts[1]}"
    subpath = "/".join(parts[2:]) or None
    return owner_repo, subpath


def _clone_repo(owner_repo: str, dest: Path) -> Path:
    url = f"https://github.com/{owner_repo}.git"
    print(f"\n  {cyan('Source:')} https://github.com/{owner_repo}")
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
def _has_plugin_manifest(path: Path) -> bool:
    """Return True if a directory looks like a valid plugin."""
    return (
        (path / ".claude-plugin" / "plugin.json").exists()
        or (path / "plugin.json").exists()
        or (path / "skills").is_dir()
    )


def _read_plugin_meta(p: Path) -> dict:
    """Build a plugin metadata dict from a directory."""
    meta = {"name": p.name, "description": "", "path": p, "version": ""}
    for manifest_rel in [".claude-plugin/plugin.json", "plugin.json"]:
        manifest = p / manifest_rel
        if manifest.exists():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                description = data.get("description", "")
                # Strip any residual HTML tags from the description (e.g., <example> tags)
                import re
                description = re.sub(r'<[^>]+>', '', description).strip()
                meta["description"] = description
                meta["version"] = data.get("version", "")
                meta["name"] = data.get("name", p.name)
            except Exception:
                pass
            break
    if not meta["description"]:
        skills_dir = p / "skills"
        n = len(list(skills_dir.iterdir())) if skills_dir.is_dir() else 0
        meta["description"] = f"{n} skill{'s' if n != 1 else ''}" if n else ""
    return meta


def _discover_plugins(search_root: Path) -> list:
    """
    Discover plugins under search_root using a three-tier waterfall:

    1. If search_root has a plugins/ subdirectory → scan that (classic monorepo layout).
    2. Otherwise scan search_root itself for subdirs that look like plugins
       (root-level flat layout, e.g. anthropics/knowledge-work-plugins).
    3. If search_root itself has a .claude-plugin/plugin.json → treat it as a
       single plugin (e.g. pointing directly at a plugin subdir).
    """
    SKIP = frozenset({"node_modules", "venv", "env", ".venv", "__pycache__", ".git"})

    def _scan_dir(root: Path) -> list[dict]:
        plugins = []
        for p in sorted(root.iterdir()):
            if not p.is_dir() or p.name.startswith(".") or p.name.startswith("__"):
                continue
            if p.name in SKIP:
                continue
            plugins.append(_read_plugin_meta(p))
        return plugins

    if not search_root.is_dir():
        return []

    # Tier 1: classic plugins/ subdir
    plugins_subdir = search_root / "plugins"
    if plugins_subdir.is_dir():
        return _scan_dir(plugins_subdir)

    # Tier 2: root-level dirs that look like plugins (flat layout)
    root_plugins = [_read_plugin_meta(p)
                    for p in sorted(search_root.iterdir())
                    if p.is_dir() and not p.name.startswith(".")
                    and p.name not in SKIP
                    and _has_plugin_manifest(p)]
    if root_plugins:
        return root_plugins

    # Tier 3: the directory itself is a single plugin
    if _has_plugin_manifest(search_root):
        return [_read_plugin_meta(search_root)]

    return []


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
        description="Interactive plugin installer (for full plugins)"
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
    parser.add_argument("--plugins", type=str, help="Comma-separated list of plugins to install (headless filtering)")
    args = parser.parse_args()

    if not INSTALLER_SCRIPT.exists():
        print(red(f"  Error: plugin_installer.py not found at {INSTALLER_SCRIPT}"))
        sys.exit(1)

    # ------------------------------------------------------------------
    # Resolve source
    # ------------------------------------------------------------------
    temp_dir = None
    plugins_root: Path

    if args.source and _is_github_source(args.source):
        owner_repo, subpath = _parse_github_source(args.source)
        _print_banner(f"{owner_repo}" + (f"/{subpath}" if subpath else ""))
        temp_dir = Path(tempfile.mkdtemp(prefix="plugin_add_"))
        repo_root = _clone_repo(owner_repo, temp_dir / owner_repo.replace("/", "_"))
        # If a subpath was specified, descend into it; otherwise use repo root
        plugins_root = repo_root / subpath if subpath else repo_root
    elif args.source:
        source_path = Path(args.source).resolve()
        _print_banner(str(source_path))
        plugins_root = source_path
    else:
        # Default: find this repo's root relative to cwd
        cwd = Path.cwd()
        candidate = cwd
        for _ in range(4):
            if (candidate / "plugins").is_dir() or (candidate / ".claude-plugin").is_dir():
                break
            candidate = candidate.parent
        plugins_root = candidate
        _print_banner(str(candidate))

    # .claude/ auto-init for fresh projects
    project_root = Path.cwd()
    if not (project_root / ".claude").exists() and not args.dry_run:
        print()
        print(yellow("  No .claude/ directory found in this project."))
        if args.yes:
            answer = "yes"
        else:
            try:
                answer = input(f"  Initialize .claude/ for IDE integration? [{green('Y')}/n] ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                answer = ""
        if answer in ("", "y", "yes"):
            (project_root / ".claude").mkdir(exist_ok=True)
            print(f"  {green('✓')} Created .claude/ — Claude Code symlinks will be activated")

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
    if args.plugins:
        allowed = set(p.strip() for p in args.plugins.split(","))
        selected_plugins = [p for p in all_plugins if p["name"] in allowed]
        print(f"  {green('✓')} Installing {len(selected_plugins)} requested plugins")
    elif args.all or args.yes:
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
    # Record Subscription in plugin-sources.json
    # ------------------------------------------------------------------
    if not args.dry_run and success_count:
        sources_file = project_root / "plugin-sources.json"
        try:
            data = {"sources": []}
            if sources_file.exists():
                try:
                    raw = json.loads(sources_file.read_text(encoding="utf-8"))
                    # Migrate legacy schema (local/github/name keys → source key)
                    migrated = []
                    for s in raw.get("sources", []):
                        src = s.get("source") or s.get("github") or s.get("local") or ""
                        if src:
                            migrated.append({"source": src, "plugins": s.get("plugins", [])})
                    data = {"sources": migrated}
                except ValueError:
                    pass

            sources = data.setdefault("sources", [])

            # Determine canonical source key
            if args.source and _is_github_source(args.source):
                # GitHub: normalize to owner/repo (strip subpaths)
                source_key, _ = _parse_github_source(args.source)
            elif args.source:
                # Local: resolve to the nearest ancestor that looks like a repo/plugins root
                resolved = Path(args.source).resolve()
                # Walk up to find the plugins/ root or project root
                candidate = resolved
                while candidate != candidate.parent:
                    if (candidate.parent / "plugin-sources.json").exists() or \
                       (candidate.parent / ".claude-plugin").exists() or \
                       candidate.name == "plugins":
                        candidate = candidate.parent
                        break
                    candidate = candidate.parent
                source_key = str(resolved)  # default: keep full resolved path
                # If the resolved path is INSIDE a plugins/ folder, normalize to that folder
                parts = resolved.parts
                if "plugins" in parts:
                    plugins_idx = len(parts) - 1 - parts[::-1].index("plugins")
                    source_key = str(Path(*parts[:plugins_idx + 1]))
            else:
                source_key = str(plugins_root)

            installed_names = [p["name"] for p in selected_plugins]

            # Step 1: Remove these plugins from ALL other sources (move = one source of truth)
            for s in sources:
                if s.get("source") != source_key:
                    curr = s.get("plugins", [])
                    s["plugins"] = [p for p in curr if p not in installed_names]

            # Clean up empty source entries
            data["sources"] = [s for s in sources
                               if isinstance(s.get("plugins"), list) and s["plugins"]]
            sources = data["sources"]

            # Step 2: Upsert into the matching source entry
            existing = next((s for s in sources if s.get("source") == source_key), None)
            if not existing:
                existing = {"source": source_key, "plugins": []}
                sources.append(existing)

            curr_plugins = existing.get("plugins", [])
            existing["plugins"] = sorted(list(set(curr_plugins + installed_names)))

            sources_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        except Exception as e:
            print(f"  {yellow('Warning:')} Failed to update plugin-sources.json: {e}")

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
        print(f"  {dim('Tip:')} Run {cyan('git add .agents/ .claude/')} to track installed plugins.")
        print(f"  {dim('Tip:')} Restart your agent to pick up new commands and hooks.")
        print()

    sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
