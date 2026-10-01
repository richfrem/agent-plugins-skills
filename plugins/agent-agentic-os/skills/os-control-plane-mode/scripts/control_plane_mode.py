#!/usr/bin/env python3
"""
control_plane_mode.py - status / enable / disable the Agentic OS control plane as one unit.

Purpose:
    The control plane is more than one switch: the `work-intake` family of skills, a rule,
    two git guards in `.git/hooks`, and a declared mode. This script reads the list of what
    belongs to it from `control-plane.manifest.json` and makes the repository match the
    declared mode, then proves it with `status`.

Usage:
    control_plane_mode.py status  [--json] [--target DIR]
    control_plane_mode.py disable --dry-run | --yes [--no-sync] [--target DIR]
    control_plane_mode.py enable  --dry-run | --yes [--no-sync] [--target DIR]

Safety properties:
    * Nothing changes without --yes (the skill requires the user's explicit confirmation).
    * Gates are only ever ON while the machinery behind them exists:
        enable  = ownership -> sync -> install/wire guards -> declare `enabled`   (mode last)
        disable = declare `disabled` -> unwire guards -> ownership -> sync        (mode first)
    * `context/control_plane.db` and its task history are never touched or deleted.
    * The Claude Code plugin hooks and the evolution guard are never touched.
    * Hook files, the ownership file and the mode file are backed up under
      `context/control-plane-backup/<timestamp>/` before any change.
    * If the target is already in the requested mode AND consistent, it does nothing; if
      the mode matches but the repo has drifted, it reconciles.

Exit codes:  0 consistent / success   1 inconsistent after the operation   2 refused or usage
             3 the plugin sync failed (earlier steps are listed in the output)

Layer:
    Codify (stdlib only). Shares control_plane_hooks.py (registered symlink) with os-init.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import control_plane_hooks as cph

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = SKILL_DIR / "control-plane.manifest.json"
COMPONENT_KINDS = ("skills", "rules", "agents")


class ModeToggleError(RuntimeError):
    """A precondition failed; nothing has been changed."""


# --------------------------------------------------------------------------- manifest + files


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("ownership_file", "mode_file", "members", "git_guards"):
        if key not in data:
            raise ModeToggleError(f"manifest {path} is missing '{key}'")
    for kind in COMPONENT_KINDS:
        data["members"].setdefault(kind, [])
    return data


def manifest_guards(manifest: dict) -> list[cph.Guard]:
    by_name = {g.name: g for g in cph.CONTROL_PLANE_GUARDS}
    guards = []
    for entry in manifest["git_guards"]:
        if entry["name"] not in by_name:
            raise ModeToggleError(
                f"manifest lists guard {entry['name']!r} that control_plane_hooks.py does not know"
            )
        guards.append(by_name[entry["name"]])
    return guards


def guard_source(root: Path, guard: cph.Guard) -> Optional[Path]:
    """Where the current copy of a guard script lives (installed skill, or this plugin)."""
    candidates = [
        root / ".agents" / "skills" / "os-init" / "scripts" / guard.name,
        SKILL_DIR.parent / "os-init" / "scripts" / guard.name,
        SKILL_DIR.parent.parent / "scripts" / guard.name,
    ]
    return next((c for c in candidates if c.exists()), None)


def hooks_dir(root: Path) -> Optional[Path]:
    path = root / ".git" / "hooks"
    return path if path.is_dir() else None


def _detect_indent(text: str, data: object) -> int:
    for indent in (2, 4):
        if json.dumps(data, indent=indent, ensure_ascii=False) + ("\n" if text.endswith("\n") else "") == text:
            return indent
    return 2


def load_ownership(path: Path) -> tuple[dict, int]:
    if not path.is_file():
        raise ModeToggleError(
            f"ownership file not found: {path}. Run the plugin installer first (plugin-syncer)."
        )
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    return data, _detect_indent(text, data)


def save_ownership(path: Path, data: dict, indent: int) -> None:
    path.write_text(json.dumps(data, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8")


def find_syncer(root: Path, override: Optional[str]) -> Optional[Path]:
    if override:
        return Path(override)
    path = root / ".agents" / "skills" / "plugin-syncer" / "scripts" / "sync_with_inventory.py"
    return path if path.exists() else None


# --------------------------------------------------------------------------- status


def _component(own: dict, kind: str, name: str, root: Path) -> dict:
    entry = own.get("components", {}).get(kind, {}).get(name)
    if entry is None:
        return {"kind": kind, "name": name, "listed": False, "should_install": None, "on_disk": False}
    artifacts = entry.get("artifacts", [])
    on_disk = bool(artifacts) and all((root / a).exists() for a in artifacts)
    return {
        "kind": kind, "name": name, "listed": True,
        "should_install": bool(entry.get("should_install")), "on_disk": on_disk,
    }


def _agents_md_phase0(root: Path) -> str:
    path = root / "AGENTS.md"
    if not path.is_file():
        return "no AGENTS.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    heading = next((ln for ln in lines if "Phase 0 Intake & Socratic Gate" in ln), None)
    if heading is None:
        return "absent"
    body = "\n".join(lines)
    if "(Mandatory)" in heading and "opt-in" not in body.lower() and "control plane is enabled" not in heading.lower():
        return "mandatory"
    return "conditional"


def collect_status(root: Path, manifest: dict) -> dict:
    problems: list[str] = []
    warnings: list[str] = []

    mode_error = None
    try:
        mode = cph.read_mode(root)
    except cph.ModeError as exc:
        mode, mode_error = cph.MODE_ENABLED, str(exc)
        problems.append(str(exc))

    own_path = root / manifest["ownership_file"]
    own, _indent = load_ownership(own_path)
    components = [
        _component(own, kind, name, root)
        for kind in COMPONENT_KINDS
        for name in manifest["members"][kind]
    ]

    hdir = hooks_dir(root)
    guards = []
    for g in manifest_guards(manifest):
        state = (
            cph.guard_state(hdir, g, guard_source(root, g))
            if hdir
            else {"guard": g.name, "dispatcher": g.dispatcher, "script_present": False,
                  "script_executable": False, "wired": False, "mentioned_but_unrecognized": False,
                  "stale": False}
        )
        guards.append(state)

    want_on = mode == cph.MODE_ENABLED
    for c in components:
        label = f"{c['kind']}/{c['name']}"
        if not c["listed"]:
            problems.append(f"{label} is in the manifest but not in the ownership file")
        elif want_on and not (c["should_install"] and c["on_disk"]):
            problems.append(f"{label} is not installed while the control plane is enabled")
        elif not want_on and (c["should_install"] or c["on_disk"]):
            problems.append(f"{label} is still installed while the control plane is disabled")

    if hdir is None:
        warnings.append("no .git/hooks directory: guards cannot be checked")
    for g in guards:
        if want_on:
            if not (g["script_present"] and g["script_executable"]):
                problems.append(f"{g['guard']} script is missing or not executable in .git/hooks")
            if not g["wired"]:
                problems.append(f"{g['guard']} is not wired into .git/hooks/{g['dispatcher']}")
        else:
            if g["wired"]:
                warnings.append(
                    f"{g['guard']} is still wired into {g['dispatcher']} (inert: the guard exits 0 "
                    "while the mode is disabled). Run disable to unwire it."
                )
        if g["mentioned_but_unrecognized"]:
            warnings.append(
                f"{g['dispatcher']} mentions {g['guard']} in a shape this tool does not recognise; "
                "it was left untouched"
            )
        if g["stale"]:
            warnings.append(f"{g['guard']} in .git/hooks differs from the plugin's copy (stale)")

    db = root / "context" / "control_plane.db"
    if want_on and not db.is_file():
        warnings.append("context/control_plane.db is missing; run os-init --retrofit to create it")

    phase0 = _agents_md_phase0(root)
    if not want_on and phase0 == "mandatory":
        warnings.append("AGENTS.md still says Phase 0 intake is mandatory; make it conditional on the control plane")

    return {
        "repo": str(root),
        "mode": mode,
        "mode_file_present": cph.mode_path(root).is_file(),
        "mode_error": mode_error,
        "components": components,
        "guards": guards,
        "control_plane_db_present": db.is_file(),
        "agents_md_phase0": phase0,
        "problems": problems,
        "warnings": warnings,
        "consistent": not problems,
    }


def format_status(st: dict) -> str:
    out = [f"Control plane: {st['mode'].upper()}"
           + ("" if st["mode_file_present"] else "  (no mode file: default)"),
           f"Repo: {st['repo']}", "", "Members (skills/rules/agents):"]
    for c in st["components"]:
        out.append(f"  {c['kind']}/{c['name']:<36} should_install={c['should_install']!s:<5} on_disk={c['on_disk']}")
    out += ["", "Git guards:"]
    for g in st["guards"]:
        flags = [k for k in ("script_present", "script_executable", "wired", "stale") if g[k]]
        out.append(f"  {g['guard']:<28} -> {g['dispatcher']:<10} {', '.join(flags) or 'not installed'}")
    out += ["", f"control_plane.db present: {st['control_plane_db_present']} (never touched by this tool)",
            f"AGENTS.md Phase 0 section: {st['agents_md_phase0']}", ""]
    if st["problems"]:
        out.append("PROBLEMS (state does not match the declared mode):")
        out += [f"  - {p}" for p in st["problems"]]
    if st["warnings"]:
        out.append("Warnings:")
        out += [f"  - {w}" for w in st["warnings"]]
    out.append("RESULT: " + ("consistent" if st["consistent"] else "INCONSISTENT"))
    return "\n".join(out)


# --------------------------------------------------------------------------- operations


def _backup(root: Path, manifest: dict, hdir: Optional[Path]) -> Path:
    dest = root / "context" / "control-plane-backup" / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    dest.mkdir(parents=True, exist_ok=True)
    sources = [root / manifest["ownership_file"], cph.mode_path(root)]
    if hdir:
        sources += [hdir / g.dispatcher for g in manifest_guards(manifest)]
    for src in sources:
        if src.is_file():
            shutil.copy2(src, dest / src.name)
    return dest


def _flag_changes(own: dict, manifest: dict, desired: bool) -> list[tuple[str, str, Optional[bool]]]:
    changes = []
    for kind in COMPONENT_KINDS:
        for name in manifest["members"][kind]:
            entry = own.get("components", {}).get(kind, {}).get(name)
            if entry is None:
                raise ModeToggleError(
                    f"{kind}/{name} is in the manifest but not in the ownership file; "
                    "run the plugin-syncer to refresh the ownership file first"
                )
            if bool(entry.get("should_install")) != desired:
                changes.append((kind, name, entry.get("should_install")))
    return changes


def _run_sync(syncer: Optional[Path], root: Path, skip: bool) -> str:
    if skip:
        return "skipped (--no-sync): run the plugin-syncer to apply the ownership change"
    if syncer is None:
        return "skipped (plugin-syncer not found): run the plugin-syncer to apply the ownership change"
    proc = subprocess.run([sys.executable, str(syncer)], cwd=root, capture_output=True, text=True)
    tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-6:])
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, str(syncer), output=tail)
    return "ok\n" + tail


def plan_text(root: Path, manifest: dict, want: str, own: dict, hdir: Optional[Path]) -> list[str]:
    desired = want == cph.MODE_ENABLED
    verb = "ENABLE" if desired else "DISABLE"
    lines = [f"Plan: {verb} the control plane in {root}"]
    changes = _flag_changes(own, manifest, desired)
    if want == cph.MODE_ENABLED:
        lines.append("  1. ownership: set should_install=true for: "
                     + (", ".join(f"{k}/{n}" for k, n, _ in changes) or "(already set)"))
        lines.append("  2. run the plugin-syncer so those components are installed")
        lines.append("  3. install + wire the guards: " + ", ".join(g.name for g in manifest_guards(manifest)))
        lines.append("  4. declare mode `enabled` in " + manifest["mode_file"])
    else:
        lines.append("  1. declare mode `disabled` in " + manifest["mode_file"] + " (guards now exit 0)")
        lines.append("  2. unwire the guards from .git/hooks: " + ", ".join(g.name for g in manifest_guards(manifest))
                     + " (scripts kept for re-enable)")
        lines.append("  3. ownership: set should_install=false for: "
                     + (", ".join(f"{k}/{n}" for k, n, _ in changes) or "(already set)"))
        lines.append("  4. run the plugin-syncer so those components are removed")
    lines.append("  Never touched: context/control_plane.db (task history), os-init, os-health-check, "
                 "plugin hooks, the evolution guard.")
    lines.append("  Backups of the ownership file, mode file and hook files go to context/control-plane-backup/.")
    if hdir is None:
        lines.append("  NOTE: no .git/hooks directory here: the guard steps are skipped.")
    return lines


def apply_mode(root: Path, manifest: dict, want: str, *, syncer_override: Optional[str],
               no_sync: bool, actor: Optional[str]) -> list[str]:
    desired = want == cph.MODE_ENABLED
    own_path = root / manifest["ownership_file"]
    own, indent = load_ownership(own_path)
    hdir = hooks_dir(root)
    guards = manifest_guards(manifest)
    log: list[str] = []

    sources = {g.name: guard_source(root, g) for g in guards}
    if desired and hdir:
        missing = [n for n, s in sources.items() if s is None]
        if missing:
            raise ModeToggleError(f"cannot enable: guard script source not found for {', '.join(missing)}")
    _flag_changes(own, manifest, desired)  # raises early if the manifest and ownership disagree

    log.append(f"backup: {_backup(root, manifest, hdir)}")
    syncer = find_syncer(root, syncer_override)

    def set_flags() -> None:
        data, ind = load_ownership(own_path)
        for kind in COMPONENT_KINDS:
            for name in manifest["members"][kind]:
                data["components"][kind][name]["should_install"] = desired
        save_ownership(own_path, data, ind)
        log.append(f"ownership: members set should_install={str(desired).lower()}")

    def guards_step() -> None:
        if hdir is None:
            log.append("guards: skipped (no .git/hooks)")
            return
        for g in guards:
            if desired:
                changed = cph.install_guard_script(sources[g.name], hdir, g)
                result = cph.wire_guard(hdir, g)
                log.append(f"guard {g.name}: script {'updated' if changed else 'current'}, dispatcher {result}")
            else:
                result = cph.unwire_guard(hdir, g)
                log.append(f"guard {g.name}: dispatcher {result}")

    if desired:
        set_flags()
        log.append("sync: " + _run_sync(syncer, root, no_sync))
        guards_step()
        cph.write_mode(root, cph.MODE_ENABLED, actor)
        log.append("mode: enabled")
    else:
        cph.write_mode(root, cph.MODE_DISABLED, actor)
        log.append("mode: disabled")
        guards_step()
        set_flags()
        log.append("sync: " + _run_sync(syncer, root, no_sync))
    return log


# --------------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("status", "enable", "disable"):
        sp = sub.add_parser(name)
        sp.add_argument("--target", default=".", help="repository (default: current directory)")
        sp.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help=argparse.SUPPRESS)
        if name == "status":
            sp.add_argument("--json", action="store_true")
        else:
            sp.add_argument("--dry-run", action="store_true", help="print the plan, change nothing")
            sp.add_argument("--yes", action="store_true", help="apply (requires the user's explicit confirmation)")
            sp.add_argument("--no-sync", action="store_true", help="do not run the plugin-syncer")
            sp.add_argument("--syncer", default=None, help=argparse.SUPPRESS)
            sp.add_argument("--actor", default=None, help="recorded in context/control-plane-mode.log")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = load_manifest(Path(args.manifest))
        root = cph.common_repo_root(args.target)

        if args.command == "status":
            st = collect_status(root, manifest)
            print(json.dumps(st, indent=2) if args.json else format_status(st))
            return 0 if st["consistent"] else 1

        want = cph.MODE_ENABLED if args.command == "enable" else cph.MODE_DISABLED
        before = collect_status(root, manifest)
        own, _ = load_ownership(root / manifest["ownership_file"])
        hdir = hooks_dir(root)

        if args.dry_run or not args.yes:
            print("\n".join(plan_text(root, manifest, want, own, hdir)))
            if before["mode"] == want and before["consistent"]:
                print("\nAlready in this mode and consistent: nothing to do.")
            if not args.dry_run:
                print("\nRefusing to change anything without --yes (confirm with the user first).",
                      file=sys.stderr)
                return 2
            return 0

        if before["mode"] == want and before["consistent"] and before["mode_file_present"]:
            print(f"Already {want} and consistent: nothing to do.")
            print(format_status(before))
            return 0

        try:
            log = apply_mode(root, manifest, want, syncer_override=args.syncer,
                             no_sync=args.no_sync, actor=args.actor)
        except subprocess.CalledProcessError as exc:
            print(f"ERROR: the plugin sync failed (exit {exc.returncode}):\n{exc.output}", file=sys.stderr)
            print("Earlier steps were applied; fix the sync problem and re-run this command to finish.",
                  file=sys.stderr)
            return 3
        print("\n".join(log))
        after = collect_status(root, manifest)
        print()
        print(format_status(after))
        return 0 if after["consistent"] else 1
    except (ModeToggleError, cph.ModeError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
