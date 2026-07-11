"""
Plugin Remove (CLI)
===================

Purpose:
    Interactive plugin uninstaller with a multiselect TUI.
    Reads plugin-sources.json to discover installed plugins, lets the user
    select which to remove, and then safely deletes them from the agent
    environments (.agents/, .claude/, etc) and tracking registries.

Key Input Dependencies:
    plugin-sources.json         — tracks which plugins are installed and from which source
    .agents/ownership/{name}.json — per-plugin artifact manifests listing every deployed file
    skills-lock.json            — plugin install lock file updated on removal

Layer: Plugin Manager / Deletion

Usage Examples:
    python plugins/plugin-manager/scripts/plugin_remove.py
"""

import os
import sys
import json
import shutil
import argparse
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

# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------
_ANSI = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else True

def _col(code: str, text: str) -> str:
    """Wrap text in an ANSI escape sequence if stdout is a TTY."""
    return f"\033[{code}m{text}\033[0m" if _ANSI else text

def cyan(t: str) -> str:
    """Return text formatted in bright cyan."""
    return _col("96", t)

def green(t: str) -> str:
    """Return text formatted in bright green."""
    return _col("92", t)

def yellow(t: str) -> str:
    """Return text formatted in bright yellow."""
    return _col("93", t)

def dim(t: str) -> str:
    """Return text formatted in dim/faint style."""
    return _col("2", t)

def bold(t: str) -> str:
    """Return text formatted in bold."""
    return _col("1", t)

def red(t: str) -> str:
    """Return text formatted in bright red."""
    return _col("91", t)

# ---------------------------------------------------------------------------
# Terminal raw-mode helpers
# ---------------------------------------------------------------------------
def _read_key() -> str:
    """Read one raw keypress from stdin and return a string token.

    Returns 'UP' or 'DOWN' for arrow keys, the character for printable keys,
    or special tokens like ESC. Works on both Windows (msvcrt) and Unix (termios).
    """
    if sys.platform == "win32":
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
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

def _clear_lines(n: int) -> None:
    """Rewind the terminal cursor N lines up and clear to end-of-screen.

    Used by the multiselect TUI to re-render the menu in place.
    No-ops when _ANSI is False (non-TTY output).
    """
    if _ANSI:
        sys.stdout.write(f"\033[{n}A\033[J")
        sys.stdout.flush()

# ---------------------------------------------------------------------------
# Source-grouped item loader
# ---------------------------------------------------------------------------
def _load_installed(data: dict) -> list:
    """Build flat list of {name, source} from plugin-sources.json.

    Supports both new schema (source key) and legacy (local/github/name keys).
    Items are ordered by source so the TUI groups them visually.
    """
    items = []
    for s in data.get("sources", []):
        src = s.get("source") or s.get("github") or s.get("local") or s.get("name", "unknown")
        for p in sorted(s.get("plugins", [])):
            items.append({"name": p, "source": src})
    return items


# ---------------------------------------------------------------------------
# Interactive multi-select (grouped by source, mirrors plugin_add.py)
# ---------------------------------------------------------------------------
def _multiselect_filtered(items: list, search: str) -> list:
    """Filter items by current search query (case-insensitive name/source match)."""
    q = search.lower()
    return [i for i in items if q in i["name"].lower() or q in i.get("source", "").lower()]


def _multiselect_render(title: str, items: list, filtered: list, selected: set,
                         cursor: int, search: str, first_render: bool = False) -> int:
    """Render the TUI removal menu (grouped by source) and return the number of printed lines."""
    PAGE = 18
    lines = []
    lines.append(bold(title))
    lines.append(dim("  \u2191\u2193 move  |  space select  |  / search  |  a all  |  enter confirm  |  q quit"))
    if search:
        lines.append(f"  {dim('Search:')} {cyan(search)}_")
    else:
        lines.append(dim("  Type / to search"))

    visible = filtered[max(0, cursor - PAGE // 2): cursor + PAGE]
    offset = max(0, cursor - PAGE // 2)
    last_src = None

    for idx, item in enumerate(visible):
        abs_idx = offset + idx
        src = item.get("source", "")
        if src != last_src:
            lines.append(f"  {dim('─── ' + src + ' ───')}")
            last_src = src
        is_cursor = abs_idx == cursor
        is_selected = item["name"] in selected
        check = red("[x]") if is_selected else dim("[ ]")
        name  = cyan(item["name"]) if is_cursor else item["name"]
        arrow = ">" if is_cursor else " "
        lines.append(f"  {arrow} {check} {name}")

    count = len(selected)
    lines.append("")
    lines.append(f"  {red(str(count))} of {len(filtered)} selected for removal")

    if not first_render:
        _clear_lines(len(lines))
    print("\n".join(lines), flush=True)
    return len(lines)


def _multiselect_process_key(key: str, cursor: int, selected: set, search: str,
                              items: list, filtered: list) -> tuple[int, set, str, bool]:
    """Handle one keypress in the removal TUI and return updated (cursor, selected, search, should_break)."""
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
        return cursor, selected, search, True
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
    elif key == "\x7f":
        search = search[:-1]
        cursor = 0
    elif key and len(key) == 1 and key.isprintable():
        if not (search == "" and key == "/"):
            search += key
            cursor = 0
    return cursor, selected, search, False


def _multiselect(title: str, items: list) -> list:
    """Interactive arrow-key multi-select TUI for choosing plugins to remove.

    Renders a scrollable, source-grouped list with space-to-toggle selection.
    Supports arrow navigation, '/' search, 'a' to toggle all, 'q' to quit.
    Items are grouped visually by their source (GitHub repo or local path).

    Args:
        title: Header text displayed above the list.
        items: List of dicts with keys 'name' and 'source'.

    Returns:
        Subset of items the user selected for removal.
    """
    if not items:
        return []

    selected = set()
    cursor = 0
    search = ""

    filtered = _multiselect_filtered(items, search)
    _multiselect_render(title, items, filtered, selected, cursor, search, first_render=True)

    while True:
        key = _read_key()
        filtered = _multiselect_filtered(items, search)
        cursor = min(cursor, len(filtered) - 1) if filtered else 0

        cursor, selected, search, done = _multiselect_process_key(key, cursor, selected, search, items, filtered)
        if done:
            break
        _multiselect_render(title, items, filtered, selected, cursor, search)

    print()
    return [i for i in items if i["name"] in selected]


# ---------------------------------------------------------------------------
# Removal Logic
# ---------------------------------------------------------------------------
AGENT_DIRS = {
    "antigravity": [".agents/workflows", ".agents/skills", ".agents/rules", ".agents/agents", ".agents/hooks"],
    "github": [".github/prompts", ".github/skills", ".github/rules"],
    "gemini": [".gemini/commands", ".gemini/skills", ".gemini/rules"],
    "claude": [".claude/commands", ".claude/skills", ".claude/rules", ".claude/agents", ".claude/hooks"]
}

def _remove_via_ownership_manifest(ownership_file: Path, root: Path, dry_run: bool) -> int:
    """Remove all artifacts listed in a plugin's ownership manifest; return count removed."""
    removed_count = 0
    print(f"    - Using ownership manifest: {ownership_file.relative_to(root)}")
    try:
        data = json.loads(ownership_file.read_text(encoding="utf-8"))
        artifacts = data.get("artifacts", [])

        # Sort artifacts by length in descending order so files are unlinked/removed before parent directories
        for art_rel in sorted(artifacts, key=len, reverse=True):
            art_path = root / art_rel
            if art_path.exists():
                print(f"    - Removing owned artifact: {art_rel}")
                if not dry_run:
                    if art_path.is_symlink() or (hasattr(os.path, 'isjunction') and os.path.isjunction(art_path)):
                        art_path.unlink()
                    elif art_path.is_dir():
                        shutil.rmtree(art_path)
                    else:
                        art_path.unlink()
                removed_count += 1
        if not dry_run:
            ownership_file.unlink()
            print(f"    - Removed ownership manifest: {ownership_file.relative_to(root)}")
    except Exception as e:
        print(f"    Warning: Failed to clean via ownership manifest: {e}")
    return removed_count


def _remove_via_legacy_scan(plugin_name: str, root: Path, dry_run: bool) -> int:
    """Fallback cleanup: scan AGENT_DIRS for items matching the plugin name pattern; return count removed."""
    removed_count = 0
    for agent, dirs in AGENT_DIRS.items():
        for dir_path in dirs:
            target_dir = root / dir_path
            if not target_dir.exists():
                continue

            for item in target_dir.iterdir():
                if item.is_dir() and item.name == plugin_name:
                    print(f"    - Removing legacy directory: {item.relative_to(root)}")
                    if not dry_run:
                        if item.is_symlink() or (hasattr(os.path, 'isjunction') and os.path.isjunction(item)):
                            item.unlink()
                        else:
                            shutil.rmtree(item)
                    removed_count += 1
                elif item.is_file():
                    # Files: {plugin_name}_{command}.* or {plugin_name}-{agent}.*
                    if item.name.startswith(f"{plugin_name}_") or item.name.startswith(f"{plugin_name}-"):
                        print(f"    - Removing legacy file: {item.relative_to(root)}")
                        if not dry_run:
                            item.unlink()
                        removed_count += 1
    return removed_count


def remove_plugin_artifacts(plugin_name: str, root: Path, dry_run: bool) -> int:
    """Delete all deployed files for a plugin from the agent environment directories.

    First attempts to use the ownership manifest (.agents/ownership/{name}.json)
    for precise file-level cleanup. Falls back to scanning AGENT_DIRS for items
    whose names match {plugin_name}_* or {plugin_name}-* if no manifest exists.

    Args:
        plugin_name: The plugin slug to remove.
        root: Repository root path context.
        dry_run: If True, print planned deletions without removing files.

    Returns:
        Count of artifact paths removed (or that would be removed in dry-run).
    """
    ownership_file = root / ".agents" / "ownership" / f"{plugin_name}.json"
    removed_count = 0

    if ownership_file.exists():
        removed_count = _remove_via_ownership_manifest(ownership_file, root, dry_run)

    # Legacy fallback if no ownership file exists or it removed nothing
    if not ownership_file.exists() or removed_count == 0:
        removed_count += _remove_via_legacy_scan(plugin_name, root, dry_run)

    return removed_count



def _remove_from_registries(plugin_name: str, root: Path, dry_run: bool) -> None:
    """Remove plugin_name from plugin-sources.json and skills-lock.json.

    Migrates legacy schema entries on read. Prunes empty source entries after
    removal. Silently warns on parse or write errors without crashing.

    Args:
        plugin_name: The plugin slug to deregister.
        root: Repository root where the registry files live.
        dry_run: If True, compute changes but do not write files.
    """
    sources_file = root / "plugin-sources.json"
    if sources_file.exists():
        try:
            data = json.loads(sources_file.read_text(encoding="utf-8"))
            # Migrate legacy schema on read
            migrated = []
            for s in data.get("sources", []):
                src = s.get("source") or s.get("github") or s.get("local") or ""
                if src:
                    migrated.append({"source": src, "plugins": s.get("plugins", [])})
            data["sources"] = migrated

            for s in data["sources"]:
                curr = s.get("plugins", [])
                if isinstance(curr, list) and plugin_name in curr:
                    curr.remove(plugin_name)
                    print(f"    - Removed from plugin-sources.json: {s.get('source')}")

            # prune empty
            data["sources"] = [s for s in data["sources"]
                               if isinstance(s.get("plugins"), list) and s["plugins"]]
            if not dry_run:
                sources_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        except Exception as e:
            print(yellow(f"    Warning: Failed updating plugin-sources.json: {e}"))

    # 2. skills-lock.json
    lock_file = root / "skills-lock.json"
    if lock_file.exists():
        try:
            lock = json.loads(lock_file.read_text(encoding="utf-8"))
            if "skills" in lock and plugin_name in lock["skills"]:
                del lock["skills"][plugin_name]
                print(f"    - Removed from skills-lock.json")
                if not dry_run:
                    lock_file.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
        except Exception as e:
             print(yellow(f"    Warning: Failed updating skills-lock.json: {e}"))


def _print_removal_banner() -> None:
    """Print the ASCII art plugin remover banner."""
    print()
    print(bold("  ██████╗ ███████╗███╗   ███╗ ██████╗ ██╗   ██╗███████╗"))
    print(bold("  ██╔══██╗██╔════╝████╗ ████║██╔═══██╗██║   ██║██╔════╝"))
    print(bold("  ██████╔╝█████╗  ██╔████╔██║██║   ██║██║   ██║█████╗  "))
    print(bold("  ██╔══██╗██╔══╝  ██║╚██╔╝██║██║   ██║╚██╗ ██╔╝██╔══╝  "))
    print(bold("  ██║  ██║███████╗██║ ╚═╝ ██║╚██████╔╝ ╚████╔╝ ███████╗"))
    print(bold("  ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝   ╚═══╝  ╚══════╝"))
    print()


def _load_installed_or_exit(project_root: Path) -> list:
    """Read plugin-sources.json and return the installed plugin list, or exit if unavailable."""
    sources_file = project_root / "plugin-sources.json"

    if not sources_file.exists():
        print(yellow("No plugin-sources.json found. No tracking data available to remove."))
        sys.exit(0)

    try:
        data = json.loads(sources_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(red(f"Error reading plugin-sources.json: {e}"))
        sys.exit(1)

    installed_plugins = _load_installed(data)

    if not installed_plugins:
        print(yellow("No plugins currently recorded in plugin-sources.json."))
        sys.exit(0)

    return installed_plugins


def _select_plugins_to_remove(installed_plugins: list, args) -> list:
    """Return the subset of installed plugins to remove based on CLI flags or TUI."""
    if args.plugins:
        allowed = set(p.strip() for p in args.plugins.split(","))
        return [p for p in installed_plugins if p["name"] in allowed]
    if args.all or args.yes:
        return installed_plugins
    _print_removal_banner()
    return _multiselect("  Select plugins to remove", installed_plugins)


def _remove_selected_plugins(selected: list, project_root: Path, dry_run: bool) -> None:
    """Remove artifacts and registry entries for each selected plugin."""
    print(f"\nProceeding to remove {len(selected)} plugins...")
    for p in selected:
        pname = p["name"]
        print(f"\n{bold(pname)}:")
        artifacts_removed = remove_plugin_artifacts(pname, project_root, dry_run)
        _remove_from_registries(pname, project_root, dry_run)
        if artifacts_removed == 0:
            print(dim("    (no file artifacts found)"))


def main() -> None:
    """CLI entry point: load installed plugins, prompt for selection, remove artifacts.

    Reads plugin-sources.json to build the installed plugin list, presents the
    interactive TUI (or uses --plugins/--all for headless mode), calls
    remove_plugin_artifacts and _remove_from_registries for each selected plugin.
    """
    parser = argparse.ArgumentParser(description="Interactive plugin remover")
    parser.add_argument("--dry-run", action="store_true", help="Preview deletions without removing")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompts (headless)")
    parser.add_argument("--all", "-a", action="store_true", help="Select all plugins without prompting")
    parser.add_argument("--plugins", type=str, help="Comma-separated list of plugins to remove (headless filtering)")
    args = parser.parse_args()

    project_root = Path.cwd()
    installed_plugins = _load_installed_or_exit(project_root)
    selected = _select_plugins_to_remove(installed_plugins, args)

    if not selected:
        print(yellow("  No plugins selected. Exiting."))
        sys.exit(0)

    _remove_selected_plugins(selected, project_root, args.dry_run)

    print()
    if args.dry_run:
        print(bold(green("DRY RUN: No files were actually deleted.")))
    else:
        print(bold(green("Removal complete.")))
    print()

if __name__ == "__main__":
    main()
