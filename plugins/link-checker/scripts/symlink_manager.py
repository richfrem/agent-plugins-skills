#!/usr/bin/env python
"""
symlink_manager.py — Cross-platform symlink creation and management.

Works on Windows (with Developer Mode or admin), macOS, and Linux.
Stores a symlinks.json manifest so links can be restored after git reset --hard
or on a fresh checkout on a different OS.

Usage:
  python symlink_manager.py diagnose
  python symlink_manager.py create --src <source> --dst <link>
  python symlink_manager.py restore [--manifest symlinks.json]
  python symlink_manager.py audit   [--manifest symlinks.json]
  python symlink_manager.py list    [--manifest symlinks.json]
  python symlink_manager.py remove  --dst <link>
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

# Ensure Unicode output works on Windows terminals that default to cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

LinkStrategy = Literal["symlink", "junction", "hardlink"]

MANIFEST_FILE = Path("symlinks.json")


@dataclass
class LinkEntry:
    src: str          # target the link points TO  (relative to repo root or absolute)
    dst: str          # path of the link itself    (relative to repo root or absolute)
    strategy: LinkStrategy = "symlink"
    description: str = ""

    def src_path(self, root: Path) -> Path:
        p = Path(self.src)
        return p if p.is_absolute() else root / p

    def dst_path(self, root: Path) -> Path:
        p = Path(self.dst)
        return p if p.is_absolute() else root / p


@dataclass
class Manifest:
    version: int = 1
    links: list[LinkEntry] = field(default_factory=list)

    # --- persistence --------------------------------------------------------

    @classmethod
    def load(cls, path: Path) -> "Manifest":
        if not path.exists():
            return cls()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        links = [LinkEntry(**e) for e in data.get("links", [])]
        return cls(version=data.get("version", 1), links=links)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {"version": self.version, "links": [asdict(e) for e in self.links]},
                f,
                indent=2,
            )

    # --- helpers ------------------------------------------------------------

    def find(self, dst: str) -> LinkEntry | None:
        return next((e for e in self.links if e.dst == dst), None)

    def upsert(self, entry: LinkEntry) -> None:
        for i, e in enumerate(self.links):
            if e.dst == entry.dst:
                self.links[i] = entry
                return
        self.links.append(entry)

    def remove(self, dst: str) -> bool:
        before = len(self.links)
        self.links = [e for e in self.links if e.dst != dst]
        return len(self.links) < before


# ---------------------------------------------------------------------------
# OS detection helpers
# ---------------------------------------------------------------------------

IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"


def is_admin() -> bool:
    """Return True if running with elevated privileges."""
    if IS_WINDOWS:
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    return os.geteuid() == 0


def windows_developer_mode_enabled() -> bool:
    """Check if Windows Developer Mode is active (allows unprivileged symlinks)."""
    if not IS_WINDOWS:
        return False
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock",
        )
        value, _ = winreg.QueryValueEx(key, "AllowDevelopmentWithoutDevLicense")
        return bool(value)
    except Exception:
        return False


def can_create_symlinks() -> bool:
    """Return True if the current process can create filesystem symlinks."""
    if not IS_WINDOWS:
        return True
    return is_admin() or windows_developer_mode_enabled()


def git_core_symlinks(scope: Literal["local", "global", "system"] = "local") -> str | None:
    """Return the git core.symlinks value for the given scope, or None."""
    try:
        result = subprocess.run(
            ["git", "config", f"--{scope}", "core.symlinks"],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except FileNotFoundError:
        return None  # git not on PATH


def find_repo_root() -> Path:
    """Walk up from cwd to find the git repo root."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except FileNotFoundError:
        pass
    return Path.cwd()


# ---------------------------------------------------------------------------
# Core link creation / removal
# ---------------------------------------------------------------------------

def _create_windows_symlink(src: Path, dst: Path) -> tuple[bool, str, LinkStrategy]:
    """
    Try to create a Windows symlink; fall back to junction (dirs) or hardlink (files).
    Always uses relative paths for portability.
    Returns (success, message, strategy_used).
    """
    # Calculate relative path from dst's parent directory to src
    try:
        rel_path = os.path.relpath(src, dst.parent).replace("\\", "/")
    except ValueError:
        # On Windows, relpath can fail if src and dst are on different drives
        rel_path = str(src).replace("\\", "/")

    if can_create_symlinks():
        try:
            dst.symlink_to(rel_path)
            return True, "symlink created", "symlink"
        except OSError as e:
            pass  # fall through to fallback

    # Fallback: junction for directories, hardlink for files
    if src.is_dir():
        try:
            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(dst), str(src)],
                check=True,
                capture_output=True,
            )
            return True, "junction point created (symlink fallback)", "junction"
        except subprocess.CalledProcessError as e:
            return False, f"junction creation failed: {e.stderr.decode().strip()}", "junction"
    else:
        try:
            os.link(src, dst)
            return True, "hardlink created (symlink fallback)", "hardlink"
        except OSError as e:
            return False, f"hardlink creation failed: {e}", "hardlink"


def create_link(src: Path, dst: Path) -> tuple[bool, str, LinkStrategy]:
    """
    Create a symlink at `dst` pointing to `src`.
    Returns (success, message, strategy_used).
    """
    # Validate source exists
    if not src.exists():
        return False, f"source does not exist: {src}", "symlink"

    # Remove existing link/file at dst if it's already a link
    if dst.is_symlink() or dst.exists():
        try:
            if dst.is_dir() and not dst.is_symlink():
                # Check if it's a junction on Windows
                if IS_WINDOWS:
                    subprocess.run(
                        ["cmd", "/c", "rmdir", str(dst)],
                        capture_output=True,
                    )
                else:
                    return False, f"destination is a real directory, refusing to overwrite: {dst}", "symlink"
            else:
                dst.unlink()
        except OSError as e:
            return False, f"could not remove existing destination: {e}", "symlink"

    dst.parent.mkdir(parents=True, exist_ok=True)

    if IS_WINDOWS:
        return _create_windows_symlink(src, dst)
    else:
        # macOS/Linux: use relative path for portability
        try:
            rel_path = os.path.relpath(src, dst.parent)
            dst.symlink_to(rel_path)
            return True, "symlink created", "symlink"
        except OSError as e:
            return False, f"symlink creation failed: {e}", "symlink"


def remove_link(dst: Path) -> tuple[bool, str]:
    """Remove a symlink or junction at `dst`."""
    if not dst.exists() and not dst.is_symlink():
        return False, "destination does not exist"
    try:
        if dst.is_symlink():
            dst.unlink()
        elif IS_WINDOWS and dst.is_dir():
            subprocess.run(["cmd", "/c", "rmdir", str(dst)], check=True, capture_output=True)
        else:
            return False, "destination is not a symlink or junction"
        return True, "removed"
    except Exception as e:
        return False, str(e)


def link_status(src: Path, dst: Path) -> str:
    """Return a human-readable status for a link entry."""
    if not dst.exists() and not dst.is_symlink():
        return "✗ missing"
    if dst.is_symlink():
        target = dst.resolve()
        if not target.exists():
            return "✗ broken symlink"
        return "✓ symlink"
    if IS_WINDOWS:
        # Could be a junction
        try:
            result = subprocess.run(
                ["fsutil", "reparsepoint", "query", str(dst)],
                capture_output=True,
                text=True,
            )
            if "Junction" in result.stdout or "Mount Point" in result.stdout:
                return "✓ junction"
        except Exception:
            pass
        # Could be a hardlink — check inode match
        if dst.is_file() and src.is_file():
            try:
                if os.stat(src).st_ino == os.stat(dst).st_ino:
                    return "✓ hardlink"
            except Exception:
                pass
    return "? regular file (not a link)"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_diagnose(args: argparse.Namespace) -> None:
    root = find_repo_root()

    print("=" * 60)
    print("  Symlink Environment Diagnosis")
    print("=" * 60)
    print(f"  OS           : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"  Python       : {sys.version.split()[0]}")
    print(f"  Repo root    : {root}")
    print(f"  Running as   : {'administrator/root' if is_admin() else 'normal user'}")

    if IS_WINDOWS:
        dev_mode = windows_developer_mode_enabled()
        print(f"  Developer Mode: {'✓ enabled' if dev_mode else '✗ disabled'}")
        print(f"  Can create symlinks: {'yes' if can_create_symlinks() else 'NO — enable Developer Mode or run as admin'}")
    else:
        print(f"  Can create symlinks: yes")

    print()
    print("  Git core.symlinks:")
    for scope in ("local", "global", "system"):
        val = git_core_symlinks(scope)  # type: ignore[arg-type]
        display = val if val is not None else "(not set)"
        flag = "✓" if val == "true" else ("✗" if val == "false" else " ")
        print(f"    {flag} {scope:8s}: {display}")

    if IS_WINDOWS and git_core_symlinks("local") != "true":
        print()
        print("  ⚠  Git core.symlinks is not 'true' locally.")
        print("     Fix: git config core.symlinks true")
        print("     Then: git rm --cached -r . && git reset --hard")

    # Scan for text-file symlink stand-ins
    print()
    print("  Scanning repo for symlink stand-ins (text files containing a path)...")
    standins = []
    try:
        for path in root.rglob("*"):
            if path.is_file() and not path.is_symlink() and path.stat().st_size < 512:
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore").strip()
                    # Heuristic: short content that looks like a relative path
                    if "/" in content and "\n" not in content and not content.startswith("#"):
                        candidate = root / content
                        if candidate.exists():
                            standins.append((path, content))
                except Exception:
                    pass
    except Exception:
        pass

    if standins:
        print(f"  Found {len(standins)} possible stand-in(s):")
        for p, target in standins:
            print(f"    {p.relative_to(root)}  →  {target}")
        print("  These may be symlinks that Git checked out as plain text.")
    else:
        print("  None found.")

    print()
    manifest_path = root / MANIFEST_FILE
    if manifest_path.exists():
        manifest = Manifest.load(manifest_path)
        print(f"  Manifest: {manifest_path} ({len(manifest.links)} link(s))")
        cmd_audit(args, quiet_header=True)
    else:
        print(f"  Manifest: not found ({manifest_path})")
        print("  Run 'create' or 'restore' to build one.")
    print()


def cmd_create(args: argparse.Namespace) -> None:
    root = find_repo_root()
    manifest_path = root / (args.manifest or MANIFEST_FILE)
    manifest = Manifest.load(manifest_path)

    src = Path(args.src)
    dst = Path(args.dst)

    # Resolve relative to repo root
    src_abs = src if src.is_absolute() else root / src
    dst_abs = dst if dst.is_absolute() else root / dst

    ok, msg, strategy = create_link(src_abs, dst_abs)
    status = "✓" if ok else "✗"
    print(f"  {status} {dst}  →  {src}  [{strategy}]  {msg}")

    if ok:
        entry = LinkEntry(
            src=str(src).replace("\\", "/"),
            dst=str(dst).replace("\\", "/"),
            strategy=strategy,
            description=args.description or "",
        )
        manifest.upsert(entry)
        manifest.save(manifest_path)
        print(f"  Manifest updated: {manifest_path}")


def cmd_restore(args: argparse.Namespace) -> None:
    root = find_repo_root()
    manifest_path = root / (args.manifest or MANIFEST_FILE)
    manifest = Manifest.load(manifest_path)

    if not manifest.links:
        print("  No links in manifest. Nothing to restore.")
        return

    created = skipped = failed = 0
    print(f"  Restoring {len(manifest.links)} link(s) from {manifest_path}...\n")
    print(f"  {'DST':<40}  {'SRC':<30}  {'TYPE':<10}  STATUS")
    print(f"  {'-'*40}  {'-'*30}  {'-'*10}  ------")

    for entry in manifest.links:
        src_abs = entry.src_path(root)
        dst_abs = entry.dst_path(root)

        # Skip if already correctly linked
        current_status = link_status(src_abs, dst_abs)
        if current_status.startswith("✓"):
            print(f"  {entry.dst:<40}  {entry.src:<30}  {entry.strategy:<10}  {current_status} (skipped)")
            skipped += 1
            continue

        ok, msg, strategy = create_link(src_abs, dst_abs)
        if ok:
            created += 1
            entry.strategy = strategy
            print(f"  {entry.dst:<40}  {entry.src:<30}  {strategy:<10}  ✓ {msg}")
        else:
            failed += 1
            print(f"  {entry.dst:<40}  {entry.src:<30}  {'?':<10}  ✗ {msg}")

    manifest.save(manifest_path)
    print()
    print(f"  Done — created: {created}, skipped: {skipped}, failed: {failed}")
    if failed:
        print("  Run 'diagnose' for help fixing failures.")


def cmd_audit(args: argparse.Namespace, quiet_header: bool = False) -> None:
    root = find_repo_root()
    manifest_path = root / (args.manifest if hasattr(args, "manifest") and args.manifest else MANIFEST_FILE)
    manifest = Manifest.load(manifest_path)

    if not quiet_header:
        print(f"  Auditing {len(manifest.links)} link(s) from {manifest_path}...\n")

    if not manifest.links:
        print("  No links in manifest.")
        return

    print(f"  {'DST':<40}  {'SRC':<30}  STATUS")
    print(f"  {'-'*40}  {'-'*30}  ------")

    broken = 0
    for entry in manifest.links:
        src_abs = entry.src_path(root)
        dst_abs = entry.dst_path(root)
        status = link_status(src_abs, dst_abs)
        print(f"  {entry.dst:<40}  {entry.src:<30}  {status}")
        if status.startswith("✗"):
            broken += 1

    print()
    if broken:
        print(f"  ⚠  {broken} broken link(s). Run 'restore' to fix.")
    else:
        print("  All links OK.")


def cmd_list(args: argparse.Namespace) -> None:
    root = find_repo_root()
    manifest_path = root / (args.manifest or MANIFEST_FILE)
    manifest = Manifest.load(manifest_path)
    print(json.dumps({"links": [asdict(e) for e in manifest.links]}, indent=2))


def cmd_remove(args: argparse.Namespace) -> None:
    root = find_repo_root()
    manifest_path = root / (args.manifest or MANIFEST_FILE)
    manifest = Manifest.load(manifest_path)

    dst = Path(args.dst)
    dst_abs = dst if dst.is_absolute() else root / dst

    ok, msg = remove_link(dst_abs)
    print(f"  {'✓' if ok else '✗'}  {dst}  {msg}")

    if ok:
        removed = manifest.remove(str(dst))
        if removed:
            manifest.save(manifest_path)
            print(f"  Removed from manifest: {manifest_path}")
        else:
            print("  (not in manifest)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cross-platform symlink manager for Git repos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # diagnose
    sub.add_parser("diagnose", help="Show environment info and scan for issues")

    # create
    p_create = sub.add_parser("create", help="Create a new symlink and add to manifest")
    p_create.add_argument("--src", required=True, help="Link target (what the link points TO)")
    p_create.add_argument("--dst", required=True, help="Link path (where the link lives)")
    p_create.add_argument("--description", default="", help="Optional description for the manifest")
    p_create.add_argument("--manifest", default=None, help="Path to manifest file (default: symlinks.json)")

    # restore
    p_restore = sub.add_parser("restore", help="Re-create all links from the manifest")
    p_restore.add_argument("--manifest", default=None)

    # audit
    p_audit = sub.add_parser("audit", help="Check all links in the manifest")
    p_audit.add_argument("--manifest", default=None)

    # list
    p_list = sub.add_parser("list", help="Print manifest as JSON")
    p_list.add_argument("--manifest", default=None)

    # remove
    p_remove = sub.add_parser("remove", help="Remove a link and delete it from manifest")
    p_remove.add_argument("--dst", required=True, help="Link path to remove")
    p_remove.add_argument("--manifest", default=None)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "diagnose": cmd_diagnose,
        "create":   cmd_create,
        "restore":  cmd_restore,
        "audit":    cmd_audit,
        "list":     cmd_list,
        "remove":   cmd_remove,
    }
    print()
    dispatch[args.command](args)
    print()


if __name__ == "__main__":
    main()
