#!/usr/bin/env python3
"""
control_plane_mode.py - status / enable / disable the Agentic OS control plane.

Purpose:
    The control plane gates commits and pushes through two git guards in `.git/hooks`. This
    script switches that gating on or off for the clone it runs in, by changing the declared
    mode (`context/control-plane-mode`) and wiring or unwiring the guards. The skill itself
    stays installed: APM owns installation, this script owns only the per-clone switch.

Usage:
    control_plane_mode.py status  [--json] [--target DIR]
    control_plane_mode.py disable --dry-run | --yes [--actor NAME] [--target DIR]
    control_plane_mode.py enable  --dry-run | --yes [--actor NAME] [--target DIR]

Safety properties:
    * Nothing changes without --yes (the skill requires the user's explicit confirmation).
    * Gates are only ever ON while the machinery behind them exists:
        enable  = install + wire guards -> declare `enabled`   (mode last)
        disable = declare `disabled` -> unwire guards          (mode first)
    * `context/control_plane.db` and its task history are never touched or deleted.
    * The Claude Code plugin hooks and the evolution guard are never touched.
    * The mode file and the hook dispatchers are backed up under
      `context/control-plane-backup/<timestamp>/` before any change.
    * If the target is already in the requested mode AND consistent, it does nothing; if
      the mode matches but the repo has drifted, it reconciles.
    * The guard scripts are installed from this script's own folder, so it works from any
      APM install location (project `.claude/skills`, `.agents/skills`, or a global folder).

Exit codes:  0 consistent / success   1 inconsistent after the operation   2 refused or usage

Layer:
    Codify (stdlib only). Shares control_plane_hooks.py with init_agentic_os.py.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import control_plane_hooks as cph

SCRIPT_DIR = Path(__file__).resolve().parent
GUARDS = cph.CONTROL_PLANE_GUARDS


class ModeToggleError(RuntimeError):
    """A precondition failed; nothing has been changed."""


# --------------------------------------------------------------------------- files


def guard_source(guard: cph.Guard) -> Optional[Path]:
    """The guard script shipped beside this script (the installed skill's copy)."""
    path = SCRIPT_DIR / guard.name
    return path if path.is_file() else None


def hooks_dir(root: Path) -> Optional[Path]:
    path = root / ".git" / "hooks"
    return path if path.is_dir() else None


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


# --------------------------------------------------------------------------- status


def collect_status(root: Path) -> dict:
    problems: list[str] = []
    warnings: list[str] = []

    mode_error = None
    try:
        mode = cph.read_mode(root)
    except cph.ModeError as exc:
        mode, mode_error = cph.MODE_ENABLED, str(exc)
        problems.append(str(exc))

    hdir = hooks_dir(root)
    guards = []
    for g in GUARDS:
        state = (
            cph.guard_state(hdir, g, guard_source(g))
            if hdir
            else {"guard": g.name, "dispatcher": g.dispatcher, "script_present": False,
                  "script_executable": False, "wired": False, "mentioned_but_unrecognized": False,
                  "stale": False}
        )
        guards.append(state)

    want_on = mode == cph.MODE_ENABLED
    if hdir is None:
        warnings.append("no .git/hooks directory: guards cannot be checked")
    for g in guards:
        if want_on:
            if not (g["script_present"] and g["script_executable"]):
                problems.append(f"{g['guard']} script is missing or not executable in .git/hooks")
            if not g["wired"]:
                problems.append(f"{g['guard']} is not wired into .git/hooks/{g['dispatcher']}")
        elif g["wired"]:
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
            warnings.append(
                f"{g['guard']} in .git/hooks differs from the installed skill's copy (stale, or the skill "
                "moved). Run enable --yes to refresh it."
            )

    db = root / "context" / "control_plane.db"
    if want_on and not db.is_file():
        warnings.append("context/control_plane.db is missing; run the init mode (init_agentic_os.py --retrofit) to create it")

    phase0 = _agents_md_phase0(root)
    if not want_on and phase0 == "mandatory":
        warnings.append("AGENTS.md still says Phase 0 intake is mandatory; make it conditional on the control plane")

    return {
        "repo": str(root),
        "mode": mode,
        "mode_file_present": cph.mode_path(root).is_file(),
        "mode_error": mode_error,
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
           f"Repo: {st['repo']}", "", "Git guards:"]
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


def _backup(root: Path, hdir: Optional[Path]) -> Path:
    dest = root / "context" / "control-plane-backup" / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    dest.mkdir(parents=True, exist_ok=True)
    sources = [cph.mode_path(root)]
    if hdir:
        sources += [hdir / g.dispatcher for g in GUARDS]
    for src in sources:
        if src.is_file():
            shutil.copy2(src, dest / src.name)
    return dest


def plan_text(root: Path, want: str, hdir: Optional[Path]) -> list[str]:
    names = ", ".join(g.name for g in GUARDS)
    mode_file = str(cph.MODE_RELATIVE_PATH)
    if want == cph.MODE_ENABLED:
        lines = [f"Plan: ENABLE the control plane in {root}",
                 f"  1. install + wire the guards: {names}",
                 f"  2. declare mode `enabled` in {mode_file}"]
    else:
        lines = [f"Plan: DISABLE the control plane in {root}",
                 f"  1. declare mode `disabled` in {mode_file} (guards now exit 0)",
                 f"  2. unwire the guards from .git/hooks: {names} (scripts kept for re-enable)"]
    lines.append("  The skill stays installed; only this clone's gating changes.")
    lines.append("  Never touched: context/control_plane.db (task history), plugin hooks, the evolution guard.")
    lines.append("  Backups of the mode file and hook dispatchers go to context/control-plane-backup/.")
    if hdir is None:
        lines.append("  NOTE: no .git/hooks directory here: the guard steps are skipped.")
    return lines


def apply_mode(root: Path, want: str, *, actor: Optional[str]) -> list[str]:
    desired = want == cph.MODE_ENABLED
    hdir = hooks_dir(root)
    sources = {g.name: guard_source(g) for g in GUARDS}
    if desired and hdir:
        missing = [n for n, s in sources.items() if s is None]
        if missing:
            raise ModeToggleError(f"cannot enable: guard script source not found beside this script for {', '.join(missing)}")
    log: list[str] = [f"backup: {_backup(root, hdir)}"]

    def guards_step() -> None:
        if hdir is None:
            log.append("guards: skipped (no .git/hooks)")
            return
        for g in GUARDS:
            if desired:
                changed = cph.install_guard_script(sources[g.name], hdir, g)
                result = cph.wire_guard(hdir, g)
                log.append(f"guard {g.name}: script {'updated' if changed else 'current'}, dispatcher {result}")
            else:
                log.append(f"guard {g.name}: dispatcher {cph.unwire_guard(hdir, g)}")

    if desired:
        guards_step()
        cph.write_mode(root, cph.MODE_ENABLED, actor)
        log.append("mode: enabled")
    else:
        cph.write_mode(root, cph.MODE_DISABLED, actor)
        log.append("mode: disabled")
        guards_step()
    return log


# --------------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("status", "enable", "disable"):
        sp = sub.add_parser(name)
        sp.add_argument("--target", default=".", help="repository (default: current directory)")
        if name == "status":
            sp.add_argument("--json", action="store_true")
        else:
            sp.add_argument("--dry-run", action="store_true", help="print the plan, change nothing")
            sp.add_argument("--yes", action="store_true", help="apply (requires the user's explicit confirmation)")
            sp.add_argument("--actor", default=None, help="recorded in context/control-plane-mode.log")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = cph.common_repo_root(args.target)

        if args.command == "status":
            st = collect_status(root)
            print(json.dumps(st, indent=2) if args.json else format_status(st))
            return 0 if st["consistent"] else 1

        want = cph.MODE_ENABLED if args.command == "enable" else cph.MODE_DISABLED
        before = collect_status(root)

        if args.dry_run or not args.yes:
            print("\n".join(plan_text(root, want, hooks_dir(root))))
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

        print("\n".join(apply_mode(root, want, actor=args.actor)))
        after = collect_status(root)
        print()
        print(format_status(after))
        return 0 if after["consistent"] else 1
    except (ModeToggleError, cph.ModeError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
