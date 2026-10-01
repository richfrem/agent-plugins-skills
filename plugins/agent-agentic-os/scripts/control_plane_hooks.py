#!/usr/bin/env python3
"""
control_plane_hooks.py - the one place that knows how the control-plane git guards are
wired, and what the declared control-plane mode is.

Purpose:
    The Agentic OS control plane gates commits and pushes through two git guards
    (`pre-commit-pipeline-guard`, `pre-push-review-guard`). Before this module the wiring
    code lived inline in `init_agentic_os.py` and there was no way to turn the gates off on
    purpose: the guards only ungated themselves when `control_plane.db` was missing, and the
    installer re-wired them on every run.

    This module makes "disabled" a first-class, declared state:

      * Mode lives in `<repo>/context/control-plane-mode` (one word: `enabled` or `disabled`).
        A missing file means `enabled`, so every existing install behaves exactly as before.
      * The guards read the same file and exit 0 immediately when it says `disabled`.
      * `init_agentic_os.py` reads it too, so a re-run never silently re-enables a gate.
      * The `os-control-plane-mode` skill uses `wire_guard` / `unwire_guard` to flip the
        wiring in `.git/hooks` and `read_mode` / `write_mode` to flip the declaration.

Layer:
    Codify / shared helper (stdlib only; imported by init_agentic_os.py and
    skills/os-control-plane-mode/scripts/control_plane_mode.py via registered symlinks).

Key Functions:
    - read_mode(root) / write_mode(root, mode)       declared mode
    - wire_guard / unwire_guard / guard_state        git hook wiring
    - install_guard_script                           copy a guard into .git/hooks
    - common_repo_root                               worktree-safe repo root (matches the guards)

The evolution guard (`pre-commit-evolution-guard`) is deliberately NOT a control-plane guard:
it enforces map-debt / evolution-log discipline and is independent of work-intake.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

MODE_ENABLED = "enabled"
MODE_DISABLED = "disabled"
VALID_MODES = (MODE_ENABLED, MODE_DISABLED)
MODE_RELATIVE_PATH = Path("context") / "control-plane-mode"
MODE_LOG_RELATIVE_PATH = Path("context") / "control-plane-mode.log"


class ModeError(ValueError):
    """The declared mode file exists but does not contain a valid mode."""


@dataclass(frozen=True)
class Guard:
    """A control-plane git guard and the dispatcher hook that calls it."""

    name: str
    dispatcher: str  # e.g. "pre-push"
    comment: str     # comment line written above the stanza when wiring


CONTROL_PLANE_GUARDS: tuple[Guard, ...] = (
    Guard("pre-commit-pipeline-guard", "pre-commit", "# Run pipeline execution guard if it exists"),
    Guard("pre-push-review-guard", "pre-push", "# Run review guard if it exists"),
)


# --------------------------------------------------------------------------- repo + mode


def common_repo_root(start: Path | str) -> Path:
    """Repo root as the guards compute it: parent of the git common dir (worktree-safe)."""
    start = Path(start).resolve()
    try:
        out = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--git-common-dir"],
            capture_output=True, text=True, timeout=10, check=True,
        ).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return start
    common = Path(out)
    if not common.is_absolute():
        common = (start / common).resolve()
    return common.parent


def mode_path(root: Path | str) -> Path:
    return Path(root) / MODE_RELATIVE_PATH


def read_mode(root: Path | str) -> str:
    """The declared mode. A missing file means `enabled` (backward compatible)."""
    path = mode_path(root)
    if not path.is_file():
        return MODE_ENABLED
    value = path.read_text(encoding="utf-8").strip().lower()
    if value not in VALID_MODES:
        raise ModeError(
            f"{path} must contain 'enabled' or 'disabled', found {value!r}. "
            "Fix or delete the file (a missing file means enabled)."
        )
    return value


def _git_commit(root: Path) -> Optional[str]:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return out.stdout.strip() or None if out.returncode == 0 else None
    except (subprocess.SubprocessError, OSError):
        return None


def write_mode(root: Path | str, mode: str, actor: Optional[str] = None) -> Path:
    """Declare the mode and append an audit line to `context/control-plane-mode.log`."""
    if mode not in VALID_MODES:
        raise ModeError(f"mode must be one of {VALID_MODES}, got {mode!r}")
    root = Path(root)
    path = mode_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(mode + "\n", encoding="utf-8")
    entry = {
        "at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "actor": actor,
        "commit": _git_commit(root),
    }
    with (root / MODE_LOG_RELATIVE_PATH).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    return path


# --------------------------------------------------------------------------- hook wiring


def _stanza_regex(guard: Guard) -> re.Pattern[str]:
    """Matches the exact stanza `wire_guard` writes (and the older installer's variants),
    with its optional leading blank line and descriptive comment line."""
    name = re.escape(guard.name)
    return re.compile(
        r"(?:\n)?"
        r"(?:^[ \t]*#[^\n]*guard[^\n]*\n)?"
        rf'^[ \t]*if \[ -x "\$HOOKS_DIR/{name}" \]; then\n'
        rf'[ \t]*"\$HOOKS_DIR/{name}" \|\| exit 1\n'
        r"[ \t]*fi\n",
        re.MULTILINE | re.IGNORECASE,
    )


def _stanza_text(guard: Guard) -> str:
    return (
        f"\n{guard.comment}\n"
        f'if [ -x "$HOOKS_DIR/{guard.name}" ]; then\n'
        f'    "$HOOKS_DIR/{guard.name}" || exit 1\n'
        "fi\n"
    )


def _minimal_dispatcher(guard: Guard) -> str:
    return (
        "#!/usr/bin/env bash\n"
        f"# {guard.dispatcher} hook - installed by init_agentic_os.py\n"
        'HOOKS_DIR="$(dirname "$0")"\n'
        f"{_stanza_text(guard)}"
        "\nexit 0\n"
    )


def wire_guard(hooks_dir: Path, guard: Guard, dry_run: bool = False) -> str:
    """Ensure the dispatcher hook calls `guard`. Returns 'created', 'wired' or 'already-wired'.

    Never rewrites anything other than inserting one stanza before the final `exit 0`
    (or appending it), so custom content in the dispatcher is preserved.
    """
    dispatcher = hooks_dir / guard.dispatcher
    if not dispatcher.exists():
        if not dry_run:
            dispatcher.write_text(_minimal_dispatcher(guard), encoding="utf-8")
            dispatcher.chmod(0o755)
        return "created"

    content = dispatcher.read_text(encoding="utf-8")
    if guard.name in content:
        return "already-wired"

    block = _stanza_text(guard)
    if "HOOKS_DIR=" not in content:
        # The stanza uses $HOOKS_DIR; make sure the dispatcher defines it.
        block = '\nHOOKS_DIR="$(dirname "$0")"' + block
    idx = content.rfind("\nexit 0")
    if idx != -1:
        content = content[:idx] + block + "\nexit 0" + content[idx + len("\nexit 0"):]
    else:
        content += block + "\nexit 0\n"
    if not dry_run:
        dispatcher.write_text(content, encoding="utf-8")
        dispatcher.chmod(0o755)
    return "wired"


def unwire_guard(hooks_dir: Path, guard: Guard, dry_run: bool = False) -> str:
    """Remove the dispatcher's call to `guard`, keeping the guard script itself.

    Returns 'unwired', 'absent' (nothing referenced it) or 'unrecognized' (the dispatcher
    mentions the guard in a shape this code does not recognise; the file is left untouched
    so a hand-edited hook is never guessed at - the guard's own mode check still applies).
    """
    dispatcher = hooks_dir / guard.dispatcher
    if not dispatcher.exists():
        return "absent"
    content = dispatcher.read_text(encoding="utf-8")
    if guard.name not in content:
        return "absent"
    new_content, count = _stanza_regex(guard).subn("", content)
    if count == 0:
        return "unrecognized"
    if not dry_run:
        dispatcher.write_text(new_content, encoding="utf-8")
    return "unwired"


# --------------------------------------------------------------------------- inspection


def file_sha(path: Path) -> Optional[str]:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def guard_state(hooks_dir: Path, guard: Guard, source: Optional[Path] = None) -> dict:
    """Facts about one guard: is its script present/executable, is it wired, is it stale."""
    script = hooks_dir / guard.name
    dispatcher = hooks_dir / guard.dispatcher
    content = dispatcher.read_text(encoding="utf-8") if dispatcher.exists() else ""
    wired = bool(_stanza_regex(guard).search(content))
    mentioned = guard.name in content
    sha = file_sha(script)
    source_sha = file_sha(source) if source and source.exists() else None
    return {
        "guard": guard.name,
        "dispatcher": guard.dispatcher,
        "script_present": script.is_file(),
        "script_executable": script.is_file() and bool(script.stat().st_mode & 0o111),
        "wired": wired,
        "mentioned_but_unrecognized": mentioned and not wired,
        "stale": bool(sha and source_sha and sha != source_sha),
    }


def install_guard_script(source: Path, hooks_dir: Path, guard: Guard, dry_run: bool = False) -> bool:
    """Copy the guard script into `hooks_dir` (always overwrites). Returns True if it changed."""
    target = hooks_dir / guard.name
    data = source.read_bytes()
    changed = not target.exists() or target.read_bytes() != data
    if not dry_run:
        target.write_bytes(data)
        target.chmod(0o755)
    return changed
