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
    --no-install-rules  Skip installing plugin rules into .agent/rules/ (installed by default)
    --no-append-rules-to-ide-files  Skip injecting rules into IDE files like CLAUDE.md (installed by default)

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


def _clear_lines(n: int) -> None:
    """Rewind the terminal cursor N lines up and clear to end-of-screen.

    Used by the multiselect TUI to re-render the menu in place.
    No-ops when _ANSI is False (non-TTY output).
    """
    if _ANSI:
        sys.stdout.write(f"\033[{n}A\033[J")
        sys.stdout.flush()


# ---------------------------------------------------------------------------
# Interactive multi-select (space = toggle, enter = confirm, / = search)
# ---------------------------------------------------------------------------
def _multiselect_filtered(items: list, search: str) -> list:
    """Filter items by current search query (case-insensitive name/description match)."""
    q = search.lower()
    return [i for i in items if q in i["name"].lower() or q in i.get("description", "").lower()]


def _multiselect_render(title: str, items: list, filtered: list, selected: set,
                         cursor: int, search: str, first_render: bool = False) -> int:
    """Render the TUI menu and return the number of printed lines."""
    PAGE = 18                   # visible rows
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


def _multiselect_process_key(key: str, cursor: int, selected: set, search: str,
                              items: list) -> tuple[int, set, str, bool]:
    """Handle one keypress and return updated (cursor, selected, search, should_break).

    Args:
        key: Keypress token from _read_key().
        cursor: Current cursor row index in the filtered list.
        selected: Set of currently selected item names.
        search: Current search query string.
        items: Full unfiltered item list (used for filtering and 'a' toggle-all).

    Returns:
        Updated (cursor, selected, search, should_break).
    """
    f = _multiselect_filtered(items, search)
    n = len(f)
    if key == "UP":
        cursor = max(0, cursor - 1)
    elif key == "DOWN":
        cursor = min(n - 1, cursor + 1)
    elif key == " ":
        if f and 0 <= cursor < n:
            name = f[cursor]["name"]
            selected.discard(name) if name in selected else selected.add(name)
    elif key in ("\r", "\n", ""):
        return cursor, selected, search, True
    elif key in ("q", "Q", "\x03"):
        print(red("\nCancelled."))
        sys.exit(0)
    elif key == "a":
        selected = set() if len(selected) == len(items) else {i["name"] for i in items}
    elif key == "/":
        search, cursor = "", 0
    elif key == "\x7f":
        search, cursor = search[:-1], 0
    elif key and len(key) == 1 and key.isprintable():
        search += key
        cursor = 0
    return cursor, selected, search, False


def _multiselect(title: str, items: list) -> list:
    """Interactive arrow-key multi-select TUI for choosing plugins.

    Renders a scrollable, filterable list with space-to-toggle selection.
    Supports arrow navigation, '/' search, 'a' to toggle all, 'q' to quit.

    Args:
        title: Header text displayed above the list.
        items: List of dicts with keys 'name', 'description', 'path'.

    Returns:
        Subset of items the user selected, preserving original order.
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
        cursor, selected, search, done = _multiselect_process_key(key, cursor, selected, search, items)
        filtered = _multiselect_filtered(items, search)
        cursor = min(cursor, len(filtered) - 1) if filtered else 0
        if done:
            break
        _multiselect_render(title, items, filtered, selected, cursor, search)

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
    """Shallow-clone a GitHub repo into dest and return the cloned path.

    Exits the process with code 1 if git clone fails.

    Args:
        owner_repo: GitHub 'owner/repo' string.
        dest: Destination directory path for the clone.

    Returns:
        dest after successful clone.
    """
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
    print(f"  {green('Cloned')} -> {dim(str(dest))}")
    return dest


def log_failure(tier: int, artifact: str, error: str) -> None:
    """Append a failure row to the plugin-manager evolution log.

    Walks up the directory tree to locate evolution-log.md and appends a
    Markdown table row recording the date, tier, and error. Silently no-ops
    if the log cannot be found or written.

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


def validate_plugin(plugin_path: Path) -> None:
    """Assert that a plugin directory meets minimum structural requirements.

    Checks for a plugin.json manifest (validating author object schema and no duplicate
    keys), a skills/ directory, and a SKILL.md inside each skill subfolder. Missing
    evals.json produces a warning rather than a hard failure, to accommodate third-party plugins.

    Args:
        plugin_path: Path to the plugin directory to validate.

    Raises:
        AssertionError: If the manifest or skills/ directory is missing, author format is invalid,
            duplicate manifest keys exist, or any skill subfolder lacks a SKILL.md file.
    """
    manifest_path = None
    if (plugin_path / ".claude-plugin" / "plugin.json").exists():
        manifest_path = plugin_path / ".claude-plugin" / "plugin.json"
    elif (plugin_path / "plugin.json").exists():
        manifest_path = plugin_path / "plugin.json"

    assert manifest_path is not None, f"Missing manifest (.claude-plugin/plugin.json or plugin.json) in {plugin_path.name}"

    try:
        raw_text = manifest_path.read_text(encoding="utf-8")

        def _check_dup_pairs(pairs):
            """Raise on any duplicate JSON key instead of silently keeping the last one."""
            d = {}
            for k, v in pairs:
                if k in d:
                    raise AssertionError(f"Duplicate top-level key '{k}' in {manifest_path.name} of {plugin_path.name}")
                d[k] = v
            return d

        data = json.loads(raw_text, object_pairs_hook=_check_dup_pairs)
        if "author" in data:
            author = data["author"]
            assert isinstance(author, dict), f"`author` in {plugin_path.name}/{manifest_path.name} must be an object ({{\"name\": \"...\", \"email\": \"...\"}}), not {type(author).__name__}"
            assert author.get("name") and isinstance(author.get("name"), str), f"`author` object in {plugin_path.name}/{manifest_path.name} must contain a non-empty string for `name`"
    except json.JSONDecodeError as je:
        raise AssertionError(f"Invalid JSON in {manifest_path.name} of {plugin_path.name}: {je}")

    # 2. Enforce skills dir
    skills_dir = plugin_path / "skills"
    assert skills_dir.is_dir(), f"Missing skills/ directory in {plugin_path.name}"
    
    # 3. Enforce SKILL.md and evals.json per skill folder
    for skill_folder in skills_dir.iterdir():
        if skill_folder.is_dir():
            skill_md = skill_folder / "SKILL.md"
            assert skill_md.is_file(), f"Skill directory '{skill_folder.name}' in plugin '{plugin_path.name}' is missing SKILL.md"
            
            # Log warning instead of hard assert for evals.json to allow 3rd party plugins
            evals_json = skill_folder / "evals" / "evals.json"
            if not evals_json.is_file():
                print(f"  ⚠ Warning: Skill '{skill_folder.name}' in plugin '{plugin_path.name}' is missing evals/evals.json")


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
        """Scan root for immediate subdirectories that look like valid plugins."""
        plugins = []
        for p in sorted(root.iterdir()):
            if not p.is_dir() or p.name.startswith(".") or p.name.startswith("__"):
                continue
            if p.name in SKIP:
                continue
            if not _has_plugin_manifest(p):
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
def _print_banner(source_label: str) -> None:
    """Print the ASCII art plugin manager banner with the resolved source label."""
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
def _resolve_source(args) -> tuple[Path, Path | None]:
    """Resolve the plugin source to a local directory, cloning if GitHub.

    Args:
        args: Parsed argparse namespace with 'source' attribute.

    Returns:
        Tuple of (plugins_root, temp_dir). temp_dir is set if a clone was
        performed and must be removed by the caller after installation.
    """
    if args.source and _is_github_source(args.source):
        owner_repo, subpath = _parse_github_source(args.source)
        _print_banner(f"{owner_repo}" + (f"/{subpath}" if subpath else ""))
        temp_dir = Path(tempfile.mkdtemp(prefix="plugin_add_"))
        repo_root = _clone_repo(owner_repo, temp_dir / owner_repo.replace("/", "_"))
        return (repo_root / subpath if subpath else repo_root), temp_dir
    if args.source:
        source_path = Path(args.source).resolve()
        _print_banner(str(source_path))
        return source_path, None
    cwd = Path.cwd()
    candidate = cwd
    for _ in range(4):
        if (candidate / "plugins").is_dir() or (candidate / ".claude-plugin").is_dir():
            break
        candidate = candidate.parent
    _print_banner(str(candidate))
    return candidate, None


def _select_plugins(all_plugins: list, args) -> list:
    """Return the subset of plugins to install based on CLI flags or TUI.

    Args:
        all_plugins: Full list of discovered plugin metadata dicts.
        args: Parsed argparse namespace (--plugins, --all, --yes).

    Returns:
        List of selected plugin dicts.
    """
    if args.plugins:
        allowed = set(p.strip() for p in args.plugins.split(","))
        chosen = [p for p in all_plugins if p["name"] in allowed]
        print(f"  {green('✓')} Installing {len(chosen)} requested plugins")
        return chosen
    if args.all or args.yes:
        print(f"  {green('✓')} Installing all {len(all_plugins)} plugins")
        return all_plugins
    return _multiselect("  Select plugins to install", all_plugins)


def _confirm_install(selected_plugins: list, args, temp_dir: Path | None) -> None:
    """Print installation summary and prompt for confirmation unless --yes.

    Exits the process with code 0 if the user declines.

    Args:
        selected_plugins: List of plugin dicts about to be installed.
        args: Parsed argparse namespace (--dry_run, --yes).
        temp_dir: Temp directory to clean up on cancellation, or None.
    """
    tag = " [DRY RUN]" if args.dry_run else ""
    print()
    print(bold(f"  Installation Plan{tag}"))
    print(f"  {dim('─' * 48)}")
    for p in selected_plugins:
        ver = f"  {dim('v' + p['version'])}" if p["version"] else ""
        desc = f"  {dim(p['description'][:50])}" if p["description"] else ""
        print(f"   {green('•')} {cyan(p['name'])}{ver}{desc}")
    print(f"  {dim('─' * 48)}")
    print(f"  {green(str(len(selected_plugins)))} plugin(s) -> {dim('.agents/')} (skills + agents + commands + hooks)")
    print()
    if args.yes or args.dry_run:
        return
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


def _install_plugins(selected_plugins: list, args) -> tuple[int, int]:
    """Run plugin_installer.py for each selected plugin and return counts.

    Args:
        selected_plugins: List of plugin metadata dicts with 'path' and 'name'.
        args: Parsed argparse namespace (--dry_run, --install_rules).

    Returns:
        Tuple of (success_count, fail_count).
    """
    success_count = 0
    fail_count = 0
    for plugin in selected_plugins:
        print(f"\n  {bold('->')} {cyan(plugin['name'])}")
        try:
            validate_plugin(Path(plugin["path"]))
        except AssertionError as ae:
            print(f"    {red('✗')} Validation Failed: {ae}")
            log_failure(tier=1, artifact=plugin["name"], error=str(ae))
            fail_count += 1
            continue
        cmd = [sys.executable, str(INSTALLER_SCRIPT), "--plugin", str(plugin["path"])]
        if args.dry_run:
            cmd.append("--dry-run")
        if not args.install_rules:
            cmd.append("--no-install-rules")
        if not args.append_rules_to_ide_files:
            cmd.append("--no-append-rules-to-ide-files")
        result = subprocess.run(cmd, text=True)
        if result.returncode == 0:
            print(f"    {green('✓')} Done")
            success_count += 1
        else:
            print(f"    {red('✗')} Failed (exit {result.returncode})")
            fail_count += 1
    return success_count, fail_count


def _read_and_migrate_sources(sources_file: Path) -> dict:
    """Load plugin-sources.json, migrating legacy schema entries to the flat 'source' key."""
    data: dict = {"sources": []}
    if sources_file.exists():
        try:
            raw = json.loads(sources_file.read_text(encoding="utf-8"))
            migrated = []
            for s in raw.get("sources", []):
                src = s.get("source") or s.get("github") or s.get("local") or ""
                if src:
                    migrated.append({"source": src, "plugins": s.get("plugins", [])})
            data = {"sources": migrated}
        except ValueError:
            pass
    return data


def _determine_source_key(args, plugins_root: Path) -> str:
    """Resolve the canonical source key (GitHub owner/repo or local path) for registry storage."""
    if args.source and _is_github_source(args.source):
        source_key, _ = _parse_github_source(args.source)
        return source_key
    if args.source:
        resolved = Path(args.source).resolve()
        parts = resolved.parts
        if "plugins" in parts:
            plugins_idx = len(parts) - 1 - parts[::-1].index("plugins")
            return str(Path(*parts[:plugins_idx + 1]))
        return str(resolved)
    return str(plugins_root)


def _update_sources_registry(selected_plugins: list, args, plugins_root: Path, project_root: Path) -> None:
    """Record installed plugin names in plugin-sources.json.

    Normalises the source key (GitHub owner/repo or local path), migrates
    any legacy schema entries, moves plugins to their new source, and upserts
    the current selection. No-ops in dry-run mode.

    Args:
        selected_plugins: List of successfully installed plugin metadata dicts.
        args: Parsed argparse namespace (source, dry_run).
        plugins_root: Resolved local plugins directory used for installation.
        project_root: Repository root where plugin-sources.json lives.
    """
    sources_file = project_root / "plugin-sources.json"
    try:
        data = _read_and_migrate_sources(sources_file)
        sources = data.setdefault("sources", [])
        source_key = _determine_source_key(args, plugins_root)
        installed_names = [p["name"] for p in selected_plugins]
        for s in sources:
            if s.get("source") != source_key:
                s["plugins"] = [p for p in s.get("plugins", []) if p not in installed_names]
        data["sources"] = [s for s in sources if isinstance(s.get("plugins"), list) and s["plugins"]]
        sources = data["sources"]
        existing = next((s for s in sources if s.get("source") == source_key), None)
        if not existing:
            existing = {"source": source_key, "plugins": []}
            sources.append(existing)
        existing["plugins"] = sorted(list(set(existing.get("plugins", []) + installed_names)))
        sources_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    except Exception as e:
        print(f"  {yellow('Warning:')} Failed to update plugin-sources.json: {e}")


def _print_results(success_count: int, fail_count: int, dry_run: bool) -> None:
    """Print the final installation summary banner.

    Args:
        success_count: Number of plugins successfully installed.
        fail_count: Number of plugins that failed to install.
        dry_run: If True, label the output as a dry-run completion.
    """
    print()
    print(f"  {dim('═' * 48)}")
    status = "DRY RUN complete" if dry_run else "Installation complete"
    print(f"  {bold(status)}")
    print(f"  {green('✓ Success:')} {success_count}")
    if fail_count:
        print(f"  {red('✗ Failed: ')} {fail_count}")
    print(f"  {dim('═' * 48)}")
    print()
    if not dry_run and success_count:
        print(f"  {dim('Tip:')} Run {cyan('git add .agents/ .claude/')} to track installed plugins.")
        print(f"  {dim('Tip:')} Restart your agent to pick up new commands and hooks.")
        print()


def _maybe_init_claude_dir(project_root: Path, args) -> None:
    """Prompt to create .claude/ if missing, so Claude Code symlinks activate.

    Args:
        project_root: Repository root to check/create .claude/ within.
        args: Parsed argparse namespace (yes, dry_run).
    """
    if (project_root / ".claude").exists() or args.dry_run:
        return
    print()
    print(yellow("  No .claude/ directory found in this project."))
    try:
        answer = input(f"  Initialize .claude/ for IDE integration? [{green('Y')}/n] ").strip().lower() if not args.yes else "yes"
    except (EOFError, KeyboardInterrupt):
        answer = ""
    if answer in ("", "y", "yes"):
        (project_root / ".claude").mkdir(exist_ok=True)
        print(f"  {green('✓')} Created .claude/ — Claude Code symlinks will be activated")


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser for plugin_add.py."""
    parser = argparse.ArgumentParser(
        description="Interactive plugin installer (for full plugins)"
    )
    parser.add_argument(
        "source", nargs="?", default=None,
        help="owner/repo (GitHub) or local path to a repo root (default: current directory)",
    )
    parser.add_argument("--all", "-a", action="store_true", help="Select all plugins without prompting")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompts")
    parser.add_argument("--dry-run", action="store_true", help="Preview — no files written")
    parser.add_argument("--no-install-rules", dest="install_rules", action="store_false",
                        help="Skip installing plugin rules into .agent/rules/ (installed by default)")
    parser.add_argument("--no-append-rules-to-ide-files", dest="append_rules_to_ide_files",
                        action="store_false",
                        help="Skip injecting rule content into 'append' mode IDE files "
                             "(e.g. CLAUDE.md); .agent/rules/ is still written (on by default)")
    parser.set_defaults(install_rules=True, append_rules_to_ide_files=True)
    parser.add_argument("--plugins", type=str, help="Comma-separated list of plugins to install (headless filtering)")
    return parser


def _abort(message: str, temp_dir: Path | None, code: int) -> None:
    """Print message, clean up temp_dir if present, and exit with code."""
    print(message)
    if temp_dir:
        shutil.rmtree(temp_dir, ignore_errors=True)
    sys.exit(code)


def main() -> None:
    """CLI entry point: resolve source, discover plugins, select, install, record.

    Parses CLI arguments, resolves the plugin source (local path or GitHub
    shorthand with auto-clone), optionally initialises .claude/ for new
    projects, presents an interactive TUI for plugin selection (or headless
    --all / --plugins mode), runs plugin_installer.py for each chosen plugin,
    updates plugin-sources.json, and prints a final summary.
    """
    args = _build_arg_parser().parse_args()

    if not INSTALLER_SCRIPT.exists():
        print(red(f"  Error: plugin_installer.py not found at {INSTALLER_SCRIPT}"))
        sys.exit(1)

    plugins_root, temp_dir = _resolve_source(args)

    project_root = Path.cwd()
    _maybe_init_claude_dir(project_root, args)

    print(f"  {dim('Discovering plugins...')}", end="", flush=True)
    all_plugins = _discover_plugins(plugins_root)
    print(f"\r  {green(str(len(all_plugins)))} plugins found" + " " * 20)

    if not all_plugins:
        _abort(red("  No plugins found. Is this a valid agent-plugins-skills repo?"), temp_dir, 1)

    selected_plugins = _select_plugins(all_plugins, args)
    if not selected_plugins:
        _abort(yellow("  No plugins selected. Exiting."), temp_dir, 0)

    _confirm_install(selected_plugins, args, temp_dir)
    success_count, fail_count = _install_plugins(selected_plugins, args)

    if not args.dry_run and success_count:
        _update_sources_registry(selected_plugins, args, plugins_root, project_root)

    if temp_dir and temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)

    _print_results(success_count, fail_count, args.dry_run)
    sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
