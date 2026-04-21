"""
Plugin Remove (CLI)
===================

Purpose:
    Interactive plugin uninstaller with a multiselect TUI.
    Reads plugin-sources.json to discover installed plugins, lets the user
    select which to remove, and then safely deletes them from the agent
    environments (.agents/, .claude/, etc) and tracking registries.

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
    return f"\033[{code}m{text}\033[0m" if _ANSI else text

def cyan(t: str) -> str:    return _col("96", t)
def green(t: str) -> str:   return _col("92", t)
def yellow(t: str) -> str:  return _col("93", t)
def dim(t: str) -> str:     return _col("2", t)
def bold(t: str) -> str:    return _col("1", t)
def red(t: str) -> str:     return _col("91", t)

# ---------------------------------------------------------------------------
# Terminal raw-mode helpers
# ---------------------------------------------------------------------------
def _read_key():
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

def _clear_lines(n: int):
    if _ANSI:
        sys.stdout.write(f"\033[{n}A\033[J")
        sys.stdout.flush()

# ---------------------------------------------------------------------------
# Interactive multi-select
# ---------------------------------------------------------------------------
def _multiselect(title: str, items: list[dict]) -> list[dict]:
    if not items:
        return []

    selected = set()
    cursor = 0
    search = ""
    PAGE = 18

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
            is_cursor = (offset + idx) == cursor
            is_selected = item["name"] in selected
            check = red("[x]") if is_selected else dim("[ ]")
            name  = cyan(item["name"]) if is_cursor else item["name"]
            desc  = dim(item.get("description", "")[:55])
            arrow = ">" if is_cursor else " "
            lines.append(f"  {arrow} {check} {name}  {desc}")

        count = len(selected)
        total = len(filtered)
        lines.append("")
        lines.append(f"  {red(str(count))} of {total} selected for removal")

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
# Removal Logic
# ---------------------------------------------------------------------------
AGENT_DIRS = {
    "antigravity": [".agents/workflows", ".agents/skills", ".agents/rules", ".agents/agents", ".agents/hooks"],
    "github": [".github/prompts", ".github/skills", ".github/rules"],
    "gemini": [".gemini/commands", ".gemini/skills", ".gemini/rules"],
    "claude": [".claude/commands", ".claude/skills", ".claude/rules", ".claude/agents", ".claude/hooks"]
}

def remove_plugin_artifacts(plugin_name: str, root: Path, dry_run: bool) -> int:
    removed_count = 0
    for agent, dirs in AGENT_DIRS.items():
        for dir_path in dirs:
            target_dir = root / dir_path
            if not target_dir.exists():
                continue

            for item in target_dir.iterdir():
                if item.is_dir() and item.name == plugin_name:
                    print(f"    - Removing directory: {item.relative_to(root)}")
                    if not dry_run:
                        if item.is_symlink() or (hasattr(os.path, 'isjunction') and os.path.isjunction(item)):
                            item.unlink()
                        else:
                            shutil.rmtree(item)
                    removed_count += 1
                elif item.is_file():
                    # Files: {plugin_name}_{command}.* or {plugin_name}-{agent}.*
                    if item.name.startswith(f"{plugin_name}_") or item.name.startswith(f"{plugin_name}-"):
                        print(f"    - Removing file: {item.relative_to(root)}")
                        if not dry_run:
                            item.unlink()
                        removed_count += 1
    return removed_count


def _remove_from_registries(plugin_name: str, root: Path, dry_run: bool) -> None:
    # 1. plugin-sources.json
    sources_file = root / "plugin-sources.json"
    if sources_file.exists():
        try:
            data = json.loads(sources_file.read_text(encoding="utf-8"))
            for s in data.get("sources", []):
                curr = s.get("plugins", [])
                if isinstance(curr, list) and plugin_name in curr:
                    curr.remove(plugin_name)
                    print(f"    - Removed from plugin-sources.json mapping: {s.get('name')}")
            
            # prune empty
            data["sources"] = [s for s in data.get("sources", []) if isinstance(s.get("plugins"), list) and len(s.get("plugins")) > 0]
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


def main():
    parser = argparse.ArgumentParser(description="Interactive plugin remover")
    parser.add_argument("--dry-run", action="store_true", help="Preview deletions without removing")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompts (headless)")
    parser.add_argument("--all", "-a", action="store_true", help="Select all plugins without prompting")
    parser.add_argument("--plugins", type=str, help="Comma-separated list of plugins to remove (headless filtering)")
    args = parser.parse_args()

    project_root = Path.cwd()
    sources_file = project_root / "plugin-sources.json"

    if not sources_file.exists():
        print(yellow("No plugin-sources.json found. No tracking data available to remove."))
        sys.exit(0)

    try:
        data = json.loads(sources_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(red(f"Error reading plugin-sources.json: {e}"))
        sys.exit(1)

    installed_plugins = []
    for s in data.get("sources", []):
        plugs = s.get("plugins", [])
        if isinstance(plugs, list):
            src_name = s.get("name", "unknown source")
            for p in plugs:
                installed_plugins.append({
                    "name": p,
                    "description": f"Installed from {src_name}"
                })

    if not installed_plugins:
        print(yellow("No plugins currently recorded in plugin-sources.json."))
        sys.exit(0)

    if args.plugins:
        allowed = set(p.strip() for p in args.plugins.split(","))
        selected = [p for p in installed_plugins if p["name"] in allowed]
    elif args.all or args.yes:
        selected = installed_plugins
    else:
        print()
        print(bold("  ██████╗ ███████╗███╗   ███╗ ██████╗ ██╗   ██╗███████╗"))
        print(bold("  ██╔══██╗██╔════╝████╗ ████║██╔═══██╗██║   ██║██╔════╝"))
        print(bold("  ██████╔╝█████╗  ██╔████╔██║██║   ██║██║   ██║█████╗  "))
        print(bold("  ██╔══██╗██╔══╝  ██║╚██╔╝██║██║   ██║╚██╗ ██╔╝██╔══╝  "))
        print(bold("  ██║  ██║███████╗██║ ╚═╝ ██║╚██████╔╝ ╚████╔╝ ███████╗"))
        print(bold("  ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝   ╚═══╝  ╚══════╝"))
        print()

        selected = _multiselect("  Select plugins to remove", installed_plugins)

    if not selected:
        print(yellow("  No plugins selected. Exiting."))
        sys.exit(0)

    print(f"\nProceeding to remove {len(selected)} plugins...")
    
    for p in selected:
        pname = p["name"]
        print(f"\n{bold(pname)}:")
        artifacts_removed = remove_plugin_artifacts(pname, project_root, args.dry_run)
        _remove_from_registries(pname, project_root, args.dry_run)
        if artifacts_removed == 0:
             print(dim("    (no file artifacts found)"))

    print()
    if args.dry_run:
        print(bold(green("DRY RUN: No files were actually deleted.")))
    else:
        print(bold(green("Removal complete.")))
    print()

if __name__ == "__main__":
    main()
