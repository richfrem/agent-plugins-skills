#!/usr/bin/env python3
"""Interactively choose which plugins to install and build the `apm install` command.

Lists every folder under plugins/ that has an apm.yml, lets you tick plugins with a
checkbox menu, prints the `apm install` command for the selection, then asks before
running it. Standard library only.

Usage:
    python scripts/install_plugins.py                 # global install, all four targets
    python scripts/install_plugins.py --targets claude,copilot
    python scripts/install_plugins.py --project       # install into the current project instead
"""

import argparse
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

DEFAULT_TARGETS = "claude,copilot,agy,codex"
PLUGINS_DIR = Path(__file__).resolve().parent.parent / "plugins"
IS_WINDOWS = os.name == "nt"


def find_plugins():
    """Return [(name, version, path)] for each plugin folder that has an apm.yml."""
    found = []
    for manifest in sorted(PLUGINS_DIR.glob("*/apm.yml")):
        text = manifest.read_text(encoding="utf-8")
        match = re.search(r"^version:\s*['\"]?([^'\"\s]+)", text, re.MULTILINE)
        found.append((manifest.parent.name, match.group(1) if match else "?", manifest.parent))
    return found


def read_key():
    """Read one keypress and normalise it to up, down, space, enter, all, none or quit."""
    if IS_WINDOWS:
        import msvcrt

        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            return {"H": "up", "P": "down"}.get(msvcrt.getwch(), "")
    else:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                ch += sys.stdin.read(2)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        if ch in ("\x1b[A", "\x1b[B"):
            return "up" if ch.endswith("A") else "down"
    if ch == " ":
        return "space"
    if ch in ("\r", "\n"):
        return "enter"
    if ch in ("\x03", "q", "Q"):
        return "quit"
    return {"a": "all", "A": "all", "n": "none", "N": "none"}.get(ch, "")


def checkbox_menu(plugins):
    """Show a checkbox list and return the chosen indexes, or None if cancelled."""
    checked = [False] * len(plugins)
    cursor = 0
    help_text = "Up/Down move, Space tick, A all, N none, Enter confirm, Q quit"
    first = True
    while True:
        if not first:
            sys.stdout.write(f"\x1b[{len(plugins) + 2}A")
        first = False
        print(f"\x1b[2K{help_text}")
        for i, (name, version, _) in enumerate(plugins):
            pointer = ">" if i == cursor else " "
            box = "[x]" if checked[i] else "[ ]"
            print(f"\x1b[2K {pointer} {box} {name} ({version})")
        print(f"\x1b[2K{sum(checked)} of {len(plugins)} selected")
        key = read_key()
        if key == "up":
            cursor = (cursor - 1) % len(plugins)
        elif key == "down":
            cursor = (cursor + 1) % len(plugins)
        elif key == "space":
            checked[cursor] = not checked[cursor]
        elif key == "all":
            checked = [True] * len(plugins)
        elif key == "none":
            checked = [False] * len(plugins)
        elif key == "enter":
            return [i for i, on in enumerate(checked) if on]
        elif key == "quit":
            return None


def numbered_menu(plugins):
    """Fallback when stdin is not a terminal: type numbers, 'all', or nothing to cancel."""
    for i, (name, version, _) in enumerate(plugins, 1):
        print(f"  {i}. {name} ({version})")
    answer = input("Plugins to install (numbers separated by commas, or 'all'): ").strip().lower()
    if not answer:
        return None
    if answer == "all":
        return list(range(len(plugins)))
    try:
        picks = sorted({int(n) - 1 for n in answer.split(",")})
    except ValueError:
        return None
    return [i for i in picks if 0 <= i < len(plugins)]


def build_command(paths, targets, project):
    command = ["apm", "install", *[str(p) for p in paths]]
    if not project:
        command.append("--global")
    command += ["--target", targets]
    if IS_WINDOWS:
        command += ["--parallel-downloads", "0"]
    return command


def display(command):
    if IS_WINDOWS:
        return subprocess.list2cmdline(command)
    return " ".join(shlex.quote(part) for part in command)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--targets", default=DEFAULT_TARGETS, help=f"Harness targets (default: {DEFAULT_TARGETS})")
    parser.add_argument("--project", action="store_true", help="Install into the current project instead of globally")
    args = parser.parse_args()

    plugins = find_plugins()
    if not plugins:
        sys.exit(f"No plugins with an apm.yml found under {PLUGINS_DIR}")

    interactive = sys.stdin.isatty() and sys.stdout.isatty()
    if interactive and IS_WINDOWS:
        os.system("")  # enable ANSI escapes in the Windows console
    chosen = checkbox_menu(plugins) if interactive else numbered_menu(plugins)
    if not chosen:
        sys.exit("Nothing selected. Nothing installed.")

    command = build_command([plugins[i][2] for i in chosen], args.targets, args.project)
    print("\nCommand:\n")
    print(display(command))
    if input("\nRun it now? [y/N] ").strip().lower() != "y":
        print("Not run. Copy the command above to run it yourself.")
        return
    sys.exit(subprocess.run(command).returncode)


if __name__ == "__main__":
    main()
