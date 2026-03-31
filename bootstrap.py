#!/usr/bin/env python3
"""
Bootstrap script for Universal Agent Plugins Installer.

This script acts as the entry point for both `uvx` and `curl -sL ... | python3 -`.
Its sole purpose is to securely download the required installer scripts into an
ephemeral directory and execute them, enabling a zero-clone installation experience
that mirrors `npx skills add`.

Usage:
    curl -sL https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main/bootstrap.py | python3 -
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
    # Disable color if piped or windows without support
    if not sys.stdout.isatty(): return text
    return f"\033[{code}m{text}\033[0m"

def cyan(t: str) -> str: return _col("96", t)
def green(t: str) -> str: return _col("92", t)
def yellow(t: str) -> str: return _col("93", t)
def dim(t: str) -> str: return _col("2", t)
def bold(t: str) -> str: return _col("1", t)
def red(t: str) -> str: return _col("91", t)

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

def main():
    print(bold("\n  Initializing Plugin Installer Bootstrap..."))
    
    # Enable ANSI escape sequences on Windows
    if sys.platform == "win32":
        try:
            os.system("")
        except Exception:
            pass

    suggest_uv()
    
    # We always pull from main to ensure the bootstrap user gets the latest stable installer
    base_raw_url = "https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main"
    scripts = [
        "plugins/plugin-manager/scripts/plugin_add.py",
        "plugins/plugin-manager/scripts/bridge_installer.py"
    ]
    
    with tempfile.TemporaryDirectory(prefix="plugin_installer_env_") as tmpdir:
        tmp_path = Path(tmpdir)
        
        print(f"  {dim('Downloading installer core... (standalone)')}", flush=True)
        # Download the required files side-by-side
        for file_path in scripts:
            filename = Path(file_path).name
            fetch_file(f"{base_raw_url}/{file_path}", tmp_path / filename)
            
        print(f"  {green('✓ Bootstrapped.')} Launching interactive UI...\n")
        
        # Determine args to pass along
        args = sys.argv[1:]
        # If no args were passed and we are piped from curl, sys.argv is just ['-']
        # We want to default to `richfrem/agent-plugins-skills` if no source was provided
        if not args or args == ["-"]:
            args = ["richfrem/agent-plugins-skills"]
            
        # Ensure we pass the clean args to the downloaded python script
        if args and args[0] == "-":
            args = args[1:]
            if not args:
                 args = ["richfrem/agent-plugins-skills"]
                 
        cmd = [sys.executable, str(tmp_path / "plugin_add.py")] + args
        
        try:
            # We use replace to handle any windows encoding quirks from subprocess
            sys.exit(subprocess.call(cmd))
        except KeyboardInterrupt:
            print(red("\n  Cancelled."))
            sys.exit(0)

if __name__ == "__main__":
    main()
