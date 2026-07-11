#!/usr/bin/env python
"""
Purpose:
    Bootstrap script for Universal Agent Plugins Installer.
    Acts as the entry point for both `uvx` and `curl -sL ... | python -`.
    Securely downloads required installer scripts into an ephemeral directory
    and executes them, enabling zero-clone installation that mirrors `npx skills add`.

Key Input Dependencies:
    - GitHub repository (richfrem/agent-plugins-skills on main branch)
    - Internet connectivity to download scripts
    - Python 3.7+
    - uv package manager (optional, but recommended)

Key Functions:
    - _col(): ANSI color wrapper for terminal output
    - cyan/green/yellow/dim/bold/red(): Color helper functions
    - suggest_uv(): Recommend uv package manager installation
    - fetch_file(): Download scripts from GitHub
    - run_script(): Execute installer script with proper arguments

Usage:
    curl -sL https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main/bootstrap.py | python -
    uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add
"""

import os
import sys
import shutil
import tempfile
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

# ANSI colour helpers
def _col(code: str, text: str) -> str:
    """Wrap text in ANSI escape sequence if stdout is a TTY."""
    # Disable color if piped or windows without support
    if not sys.stdout.isatty(): return text
    return f"\033[{code}m{text}\033[0m"

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
    """Return text formatted in dim gray."""
    return _col("2", t)

def bold(t: str) -> str:
    """Return text formatted in bold."""
    return _col("1", t)

def red(t: str) -> str:
    """Return text formatted in bright red."""
    return _col("91", t)

def suggest_uv():
    """If uv isn't installed, gently suggest it as the better path."""
    if shutil.which("uv") is None:
        print(f"\n{yellow('💡 Tip: The `uv` package manager is highly recommended.')}")
        print(f"   Install it via:  {cyan('curl -LsSf https://astral.sh/uv/install.sh | sh')}")
        print(f"   Then run:        {cyan('uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills')}")
        print(f"   {dim('(uv handles isolated execution perfectly without curl pipes)')}\n")

def fetch_file(url: str, dest: Path):
    """Download a file directly from GitHub user content."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "agent-plugins-bootstrap/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            dest.write_bytes(response.read())
    except urllib.error.URLError as e:
        print(red(f"  Error: Failed to fetch {url}"))
        print(red(f"  {e}"))
        sys.exit(1)

def _resolve_args(primary_script_name: str, raw_args: list) -> list:
    """Resolve CLI args to pass through, defaulting plugin_add's source when piped from curl."""
    args = raw_args

    # If no args were passed and we are piped from curl, sys.argv is just ['-']
    # Default to richfrem/agent-plugins-skills if no source provided for plugin_add
    if primary_script_name == "plugin_add.py":
        if not args or args == ["-"]:
            args = ["richfrem/agent-plugins-skills"]
        if args and args[0] == "-":
            args = args[1:]
            if not args:
                args = ["richfrem/agent-plugins-skills"]
    elif args and args[0] == "-":
        args = args[1:]
    return args


def _run_local(local_script: Path, args: list, title: str) -> None:
    """Execute the locally cloned script (uvx / git-clone case)."""
    print(f"  {green('✓ Using cloned scripts')}", flush=True)
    print(f"  {dim(f'Launching {title}...')}\n")
    cmd = [sys.executable, str(local_script)] + args
    try:
        sys.exit(subprocess.call(cmd))
    except KeyboardInterrupt:
        print(red("\n  Cancelled."))
        sys.exit(0)


def _run_downloaded(required_scripts: list, primary_script_name: str, args: list, title: str) -> None:
    """Download required scripts to a temp dir and execute the primary script (curl-pipe / pypi case)."""
    with tempfile.TemporaryDirectory(prefix="plugin_manager_env_") as tmpdir:
        tmp_path = Path(tmpdir)

        print(f"  {dim('Downloading core scripts... (standalone)')}", flush=True)
        base_raw_url = "https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main"

        # Download the required files side-by-side
        for file_path in required_scripts:
            filename = Path(file_path).name
            fetch_file(f"{base_raw_url}/{file_path}", tmp_path / filename)

        print(f"  {green('✓ Bootstrapped.')} Launching {title}...\n")

        cmd = [sys.executable, str(tmp_path / primary_script_name)] + args

        try:
            sys.exit(subprocess.call(cmd))
        except KeyboardInterrupt:
            print(red("\n  Cancelled."))
            sys.exit(0)


def run_script(primary_script_name: str, required_scripts: list, title: str):
    """Download scripts and execute the primary installer script."""
    print(bold(f"\n  Initializing {title}..."))

    # Enable ANSI escape sequences on Windows
    if sys.platform == "win32":
        try:
            os.system("")
        except Exception:
            pass

    suggest_uv()

    # Check if we're running from a cloned git repo (uvx case)
    bootstrap_dir = Path(__file__).parent
    local_script = bootstrap_dir / "plugins" / "plugin-manager" / "scripts" / primary_script_name
    args = _resolve_args(primary_script_name, sys.argv[1:])

    # If running from cloned repo (uvx case), use local scripts directly
    if local_script.exists():
        _run_local(local_script, args, title)
    else:
        # Running from curl pipe or pypi install — download from main
        _run_downloaded(required_scripts, primary_script_name, args, title)

def add_main():
    """Entry point for plugin installation (default when run as `python bootstrap.py`)."""
    run_script(
        primary_script_name="plugin_add.py",
        required_scripts=[
            "plugins/plugin-manager/scripts/plugin_add.py",
            "plugins/plugin-manager/scripts/plugin_installer.py"
        ],
        title="Plugin Installer"
    )

def remove_main():
    """Entry point for plugin uninstallation."""
    run_script(
        primary_script_name="plugin_remove.py",
        required_scripts=[
            "plugins/plugin-manager/scripts/plugin_remove.py"
        ],
        title="Plugin Uninstaller"
    )

def sync_main():
    """Entry point for plugin sync and cleanup."""
    run_script(
        primary_script_name="sync_with_inventory.py",
        required_scripts=[
            "plugins/plugin-manager/scripts/sync_with_inventory.py",
            "plugins/plugin-manager/scripts/plugin_add.py",
            "plugins/plugin-manager/scripts/plugin_installer.py"
        ],
        title="Plugin Sync & Cleanup"
    )

if __name__ == "__main__":
    # If run generically via python bootstrap.py, default to install
    add_main()
