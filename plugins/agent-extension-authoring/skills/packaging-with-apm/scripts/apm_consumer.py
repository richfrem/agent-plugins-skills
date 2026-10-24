#!/usr/bin/env python3
"""
apm_consumer.py (CLI)
=====================================

Purpose:
    Consumer tooling for installing this repository's plugins with APM (APM migration plan,
    Phase 3): pinned installs (from a materialized local clone, or a pinned git ref), a backup of the global APM state before every change, moving
    all installs to a new ref, and rollback to a backup.

    Rollback was verified against APM 0.33.0: restoring ~/.apm/apm.yml and apm.lock.yaml
    alone leaves orphaned skills from packages added after the backup (the restored lockfile
    no longer records their files, and `apm prune` has no --global). So rollback first
    uninstalls every package added since the backup, then restores both files, then runs
    `apm install --global`.

Usage:
    python3 apm_consumer.py install --plugins dev-utils --checkout <clone> --global [--skill NAME ...]   # recommended
    python3 apm_consumer.py install --plugins dev-utils,agent-memory --ref <tag-or-sha> [--global] [--skill NAME ...]
    python3 apm_consumer.py backup
    python3 apm_consumer.py list-backups
    python3 apm_consumer.py set-ref --ref <tag-or-sha>
    python3 apm_consumer.py rollback [--backup <id>]

Exit codes: 0 success, 1 APM command failed, 2 usage error (e.g. unpinned install).

Key Input Dependencies:
    - APM CLI on PATH or via --apm (pinned in plugins/agent-extension-authoring/skills/packaging-with-apm/requirements-dev.in)
    - ~/.apm/apm.yml and ~/.apm/apm.lock.yaml (global APM state; created by APM)
    - ~/.apm/backups/<id>/ (created by this script)
    - PyYAML

Function Index:
    - apm_home() -> Path
    - run_apm(apm_bin, args, cwd) -> int
    - dependency_entries(manifest_path) -> list
    - dependency_key(entry) -> str
    - plugin_spec(source, plugin, ref) -> str
    - backup_global() -> Path | None
    - list_backups() -> list[Path]
    - checkout_ready(checkout) -> bool
    - cmd_install(args) -> int
    - cmd_set_ref(args) -> int
    - cmd_rollback(args) -> int
    - main() -> None
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

DEFAULT_SOURCE = "richfrem/agent-plugins-skills"
DEFAULT_TARGETS = "claude,copilot,agy,codex"
STATE_FILES = ("apm.yml", "apm.lock.yaml")


# Global APM state lives in ~/.apm/ (honours HOME so tests can redirect it).
def apm_home() -> Path:
    """Return the global APM directory."""
    return Path(os.path.expanduser("~")) / ".apm"


# Run one APM command, streaming its output; return the exit code.
def run_apm(apm_bin: str, args: list[str], cwd: Path | None = None) -> int:
    """Run apm with args and return its exit code."""
    print(f"$ apm {' '.join(args)}")
    return subprocess.run([apm_bin, *args], cwd=cwd).returncode


# Dependency entries of an apm.yml, or [] if the file is missing. APM writes a plain
# string (`owner/repo/path#ref`) or, when --skill is used, a dict (`git:`, `ref:`, `skills:`).
def dependency_entries(manifest_path: Path) -> list:
    """Return the raw dependencies.apm entries from an apm.yml."""
    if not manifest_path.is_file():
        return []
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    return list((data.get("dependencies") or {}).get("apm") or [])


# The package identity of one entry, without its ref.
def dependency_key(entry: object) -> str:
    """Return owner/repo/path (or a local path) for a string or dict dependency entry."""
    if isinstance(entry, dict):
        return str(entry.get("git") or entry.get("path") or entry.get("local") or "")
    return str(entry).split("#", 1)[0]


# One plugin of the source repository, pinned to a ref.
def plugin_spec(source: str, plugin: str, ref: str) -> str:
    """Return owner/repo/plugins/<plugin>#<ref>."""
    return f"{source}/plugins/{plugin}#{ref}"


# Copy the global manifest and lockfile into a timestamped backup folder.
def backup_global() -> Path | None:
    """Back up ~/.apm/apm.yml and apm.lock.yaml; return the backup folder, or None if no state."""
    home = apm_home()
    if not (home / "apm.yml").is_file():
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    dest = home / "backups" / stamp
    dest.mkdir(parents=True)
    for name in STATE_FILES:
        if (home / name).is_file():
            shutil.copy2(home / name, dest / name)
    print(f"Backed up global APM state to {dest}")
    return dest


# Existing backups, oldest first.
def list_backups() -> list[Path]:
    """Return backup folders sorted by id (timestamp)."""
    root = apm_home() / "backups"
    return sorted(p for p in root.iterdir() if p.is_dir()) if root.is_dir() else []


# A local clone is usable only when every copy-manifest file is materialized and current.
def checkout_ready(checkout: Path) -> bool:
    """Run materialize_copies.py --check in the clone; True when copies are in sync."""
    tool = checkout / "plugins/agent-extension-authoring/skills/packaging-with-apm/scripts/materialize_copies.py"
    if not tool.is_file():
        print(f"{checkout} has no materialize_copies.py; is it a clone of {DEFAULT_SOURCE}?")
        return False
    result = subprocess.run([sys.executable, str(tool), "--path", str(checkout), "--check"])
    if result.returncode != 0:
        print(f"Copies are missing or stale; run: python3 {tool} --path {checkout}")
    return result.returncode == 0


# install: pinned install of one or more plugins, global or into the current project.
# Plugins share files through the copy manifest, so the git path alone lacks those copies;
# --checkout installs from a materialized local clone (pinned by the clone's commit).
def cmd_install(args: argparse.Namespace) -> int:
    """Install plugins pinned to --ref, or from a materialized --checkout; back up first when --global."""
    if args.checkout:
        checkout = Path(args.checkout).resolve()
        if not checkout_ready(checkout):
            return 2
    elif not args.ref and not args.allow_unpinned:
        print("Refusing an unpinned install: pass --ref <tag-or-sha> (or --allow-unpinned).")
        return 2
    plugins = [p.strip() for p in args.plugins.split(",") if p.strip()]
    if args.skill and len(plugins) != 1:
        print("--skill selects skills from one plugin; pass exactly one plugin with it.")
        return 2
    if args.is_global:
        backup_global()
    for plugin in plugins:
        if args.checkout:
            spec = str(Path(args.checkout).resolve() / "plugins" / plugin)
        else:
            spec = plugin_spec(args.source, plugin, args.ref) if args.ref else f"{args.source}/plugins/{plugin}"
        cmd = ["install", spec, "--target", args.targets]
        cmd += ["--global"] if args.is_global else []
        for skill in args.skill or []:
            cmd += ["--skill", skill]
        if run_apm(args.apm, cmd) != 0:
            return 1
    return 0


# set-ref: move every global dependency from --source to a new ref, then reinstall.
def cmd_set_ref(args: argparse.Namespace) -> int:
    """Rewrite #<ref> on global dependencies from --source and run apm install --global."""
    manifest = apm_home() / "apm.yml"
    if not manifest.is_file():
        print(f"No global manifest at {manifest}; install something first.")
        return 2
    backup_global()
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    deps = data["dependencies"]["apm"]
    prefix = re.escape(args.source) + "/"
    changed = 0
    for i, dep in enumerate(deps):
        if not re.match(prefix, dependency_key(dep)):
            continue
        if isinstance(dep, dict):
            dep["ref"] = args.ref
        else:
            deps[i] = dependency_key(dep) + f"#{args.ref}"
        changed += 1
    manifest.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    print(f"Set {changed} dependencies to #{args.ref}")
    return 0 if run_apm(args.apm, ["install", "--global"]) == 0 else 1


# rollback: uninstall what was added since the backup, restore state, reinstall.
def cmd_rollback(args: argparse.Namespace) -> int:
    """Return the global APM state to a backup (default: the latest)."""
    backups = list_backups()
    if not backups:
        print("No backups found.")
        return 2
    chosen = next((b for b in backups if b.name == args.backup), None) if args.backup else backups[-1]
    if chosen is None:
        print(f"Backup {args.backup} not found. Available: {[b.name for b in backups]}")
        return 2
    home = apm_home()
    previous = {dependency_key(d) for d in dependency_entries(chosen / "apm.yml")}
    added = [dependency_key(d) for d in dependency_entries(home / "apm.yml") if dependency_key(d) not in previous]
    for key in added:
        if run_apm(args.apm, ["uninstall", key, "--global"]) != 0:
            print(f"Could not uninstall {key}; rollback stopped before restoring state.")
            return 1
    for name in STATE_FILES:
        if (chosen / name).is_file():
            shutil.copy2(chosen / name, home / name)
    print(f"Restored global APM state from {chosen.name}")
    return 0 if run_apm(args.apm, ["install", "--global"]) == 0 else 1


# CLI entry point.
def main() -> None:
    """Parse arguments and dispatch the subcommand."""
    parser = argparse.ArgumentParser(description="Install this repository's plugins with APM (pinned, with rollback)")
    parser.add_argument("--apm", default="apm", help="APM CLI executable (default: apm on PATH)")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help=f"Source repository (default: {DEFAULT_SOURCE})")
    sub = parser.add_subparsers(dest="command", required=True)
    p_install = sub.add_parser("install", help="Pinned install of one or more plugins")
    p_install.add_argument("--plugins", required=True, help="Comma-separated plugin names, e.g. dev-utils,agent-memory")
    p_install.add_argument("--ref", help="Release tag or commit SHA to pin")
    p_install.add_argument("--targets", default=DEFAULT_TARGETS, help=f"Harness targets (default: {DEFAULT_TARGETS})")
    p_install.add_argument("--global", dest="is_global", action="store_true", help="Install at user level (~/.apm/)")
    p_install.add_argument("--skill", action="append", help="Install only this skill (repeatable; one plugin only)")
    p_install.add_argument("--allow-unpinned", action="store_true", help="Allow an install without --ref")
    p_install.add_argument("--checkout", help="Install from this materialized local clone instead of the git path")
    sub.add_parser("backup", help="Back up the global APM manifest and lockfile")
    sub.add_parser("list-backups", help="List global APM backups")
    p_ref = sub.add_parser("set-ref", help="Move every global install from --source to a new ref")
    p_ref.add_argument("--ref", required=True, help="Release tag or commit SHA")
    p_rb = sub.add_parser("rollback", help="Return global APM state to a backup")
    p_rb.add_argument("--backup", help="Backup id from list-backups (default: latest)")
    args = parser.parse_args()

    if args.command == "backup":
        sys.exit(0 if backup_global() else 2)
    if args.command == "list-backups":
        for backup in list_backups():
            print(f"{backup.name}  {len(dependency_entries(backup / 'apm.yml'))} dependencies")
        sys.exit(0)
    handlers = {"install": cmd_install, "set-ref": cmd_set_ref, "rollback": cmd_rollback}
    sys.exit(handlers[args.command](args))


if __name__ == "__main__":
    main()
