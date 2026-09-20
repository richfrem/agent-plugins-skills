#!/usr/bin/env python3
"""
control_plane/isolation_check.py
================================

Purpose:
    Fail-closed isolation preflight for Gate 1 (AWAITING_APPROVAL -> APPROVED) of
    auth-ciba-increment-b (issue #639, task T1). Human decision D4: the security
    boundary is that the trust anchors and signing material are human-owned and
    agent-inaccessible: `allowed_signers`, `allowed_signers_selftest`, the private
    signing keys, and the challenge directory. The SQLite control-plane DB is
    deliberately NOT checked; the agent must keep writing it for ordinary
    transitions (residual risk documented in the spec).

    All evidence comes from `lstat`/`fstat` and uids, never from an environment
    variable or a config string: the agent controls its own environment but cannot
    `chown`. Symlinks are rejected at every path component, every ancestor
    directory is checked for agent write access, and `open_protected_readonly`
    gives callers a file descriptor that is verified once (`O_NOFOLLOW` + `fstat`)
    and can be held across a transaction.

Key Input Dependencies:
    - Python stdlib only (os, stat, pwd, grp, dataclasses)
    - The paths of allowed_signers, allowed_signers_selftest, the challenge
      directory and optional private key files (supplied by the caller)
    - The configured agent identity (default `agentic-os-local-agent`), injectable
      for tests: name, uid and gids

Key Functions:
    - check_isolation() -- run the whole preflight; returns an IsolationResult that
      lists EVERY failure (never stops at the first).
    - open_protected_readonly() -- open a file `O_NOFOLLOW`, verify owner/mode from
      the descriptor, return the fd.
    - _check_chain() -- walk a path from `/`, rejecting symlinks and agent-writable
      ancestor directories.
    - _check_file(), _check_dir() -- final-component checks (type, owner, mode).
    - _resolve_agent_identity() -- uid/gids from injected values or from pwd/grp.
    - _agent_can_write_dir() -- whether the agent identity can modify a directory.

Failure codes:
    IDENTITY_UNRESOLVED, EUID_IS_AGENT, SSH_AUTH_SOCK_SET, PATH_MISSING,
    SYMLINK_COMPONENT, NOT_REGULAR_FILE, NOT_DIRECTORY, NOT_OWNED_BY_HUMAN,
    OWNED_BY_AGENT, BAD_MODE, ANCESTOR_AGENT_WRITABLE, CHALLENGE_DIR_HAS_SYMLINK

Usage:
    result = check_isolation(allowed_signers=..., allowed_signers_selftest=...,
                             challenge_dir=..., key_paths=[...])
    if not result.ok:
        for f in result.failures: print(f.code, f.path, f.message)
"""

import errno
import os
import stat
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Tuple, Union

try:  # pwd/grp are POSIX-only; Windows resolves identity differently (documented)
    import grp
    import pwd
except ImportError:  # pragma: no cover
    grp = None  # type: ignore[assignment]
    pwd = None  # type: ignore[assignment]

DEFAULT_AGENT_NAME = "agentic-os-local-agent"
SSH_AUTH_SOCK = "SSH_AUTH_SOCK"
SIGNERS_MODE = 0o600
CHALLENGE_DIR_MODE = 0o700

PathLike = Union[str, "os.PathLike[str]"]


class IsolationError(Exception):
    """Raised by open_protected_readonly() when a file fails verification."""


@dataclass(frozen=True)
class IsolationFailure:
    """One failed isolation check."""

    code: str
    path: Optional[str]
    message: str


@dataclass(frozen=True)
class IsolationResult:
    """Outcome of the preflight. `ok` is True only when `failures` is empty."""

    ok: bool
    failures: Tuple[IsolationFailure, ...]
    evidence: Dict[str, Any] = field(default_factory=dict)


# External comment: resolve the agent's uid and gids (injected values win; otherwise pwd/grp).
def _resolve_agent_identity(
    agent_name: str, agent_uid: Optional[int], agent_gids: Optional[Set[int]]
) -> Tuple[Optional[int], Set[int]]:
    """Return (uid or None when unresolvable, gids). Never guesses a uid."""
    gids: Set[int] = set(agent_gids) if agent_gids is not None else set()
    uid = agent_uid
    if pwd is not None and uid is None:
        try:
            entry = pwd.getpwnam(agent_name)
            uid = entry.pw_uid
            if agent_gids is None:
                gids.add(entry.pw_gid)
        except KeyError:
            uid = None
    if agent_gids is None and pwd is not None and grp is not None and uid is not None:
        try:
            entry = pwd.getpwuid(uid)
            gids.add(entry.pw_gid)
            gids.update(g.gr_gid for g in grp.getgrall() if entry.pw_name in g.gr_mem)
        except KeyError:
            pass
    return uid, gids


# External comment: can the agent identity modify entries of this directory?
def _agent_can_write_dir(st: os.stat_result, agent_uid: int, agent_gids: Set[int]) -> bool:
    """True if the agent owns the directory or has group/other write access.

    An other-writable directory with the sticky bit is not counted: sticky stops
    non-owners from renaming or deleting entries they do not own."""
    mode = stat.S_IMODE(st.st_mode)
    if st.st_uid == agent_uid:
        return True
    if mode & 0o020 and st.st_gid in agent_gids:
        return True
    if mode & 0o002 and not mode & stat.S_ISVTX:
        return True
    return False


# External comment: walk `/` down to the path; reject symlinks and agent-writable ancestors.
def _check_chain(
    path: Path, agent_uid: Optional[int], agent_gids: Set[int], failures: List[IsolationFailure]
) -> Optional[os.stat_result]:
    """Return lstat of the final component, or None when it cannot be inspected.

    Appends PATH_MISSING / SYMLINK_COMPONENT / ANCESTOR_AGENT_WRITABLE failures."""
    absolute = Path(os.path.abspath(path))
    parts = absolute.parts
    current = Path(parts[0])
    final_stat: Optional[os.stat_result] = None
    for index, part in enumerate(parts[1:], start=1):
        current = current / part
        last = index == len(parts) - 1
        try:
            st = os.lstat(current)
        except FileNotFoundError:
            failures.append(IsolationFailure("PATH_MISSING", str(absolute), f"{current} does not exist"))
            return None
        except OSError as exc:
            failures.append(IsolationFailure("PATH_MISSING", str(absolute), f"cannot lstat {current}: {exc}"))
            return None
        if stat.S_ISLNK(st.st_mode):
            failures.append(
                IsolationFailure("SYMLINK_COMPONENT", str(absolute), f"{current} is a symlink; pass the real path")
            )
            return None
        if last:
            final_stat = st
        elif stat.S_ISDIR(st.st_mode) and agent_uid is not None:
            if _agent_can_write_dir(st, agent_uid, agent_gids):
                failures.append(
                    IsolationFailure(
                        "ANCESTOR_AGENT_WRITABLE", str(absolute), f"ancestor {current} is writable by the agent identity"
                    )
                )
    return final_stat


# External comment: owner checks shared by every protected artifact.
def _check_owner(
    st: os.stat_result, path: Path, euid: int, agent_uid: Optional[int], failures: List[IsolationFailure]
) -> None:
    if st.st_uid != euid:
        failures.append(
            IsolationFailure("NOT_OWNED_BY_HUMAN", str(path), f"owner uid {st.st_uid} is not the human uid {euid}")
        )
    if agent_uid is not None and st.st_uid == agent_uid:
        failures.append(IsolationFailure("OWNED_BY_AGENT", str(path), "owned by the agent uid"))


# External comment: regular file, human-owned, and the required mode (exact or no group/other bits).
def _check_file(
    path: Path,
    euid: int,
    agent_uid: Optional[int],
    agent_gids: Set[int],
    exact_mode: Optional[int],
    failures: List[IsolationFailure],
) -> None:
    st = _check_chain(path, agent_uid, agent_gids, failures)
    if st is None:
        return
    if not stat.S_ISREG(st.st_mode):
        failures.append(IsolationFailure("NOT_REGULAR_FILE", str(path), "not a regular file"))
        return
    _check_owner(st, path, euid, agent_uid, failures)
    mode = stat.S_IMODE(st.st_mode)
    if exact_mode is not None and mode != exact_mode:
        failures.append(IsolationFailure("BAD_MODE", str(path), f"mode {mode:04o}, required {exact_mode:04o}"))
    elif exact_mode is None and mode & 0o077:
        failures.append(IsolationFailure("BAD_MODE", str(path), f"mode {mode:04o} grants group/other access"))


# External comment: challenge directory: human-owned 0700, a real directory, no symlink entries.
def _check_dir(
    path: Path, euid: int, agent_uid: Optional[int], agent_gids: Set[int], failures: List[IsolationFailure]
) -> None:
    st = _check_chain(path, agent_uid, agent_gids, failures)
    if st is None:
        return
    if not stat.S_ISDIR(st.st_mode):
        failures.append(IsolationFailure("NOT_DIRECTORY", str(path), "not a directory"))
        return
    _check_owner(st, path, euid, agent_uid, failures)
    mode = stat.S_IMODE(st.st_mode)
    if mode != CHALLENGE_DIR_MODE:
        failures.append(IsolationFailure("BAD_MODE", str(path), f"mode {mode:04o}, required {CHALLENGE_DIR_MODE:04o}"))
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_symlink():
                    failures.append(
                        IsolationFailure("CHALLENGE_DIR_HAS_SYMLINK", str(path), f"{entry.name} is a symlink")
                    )
    except OSError as exc:
        failures.append(IsolationFailure("PATH_MISSING", str(path), f"cannot list challenge dir: {exc}"))


def check_isolation(
    *,
    allowed_signers: PathLike,
    allowed_signers_selftest: PathLike,
    challenge_dir: PathLike,
    key_paths: Iterable[PathLike] = (),
    agent_name: str = DEFAULT_AGENT_NAME,
    agent_uid: Optional[int] = None,
    agent_gids: Optional[Set[int]] = None,
    euid: Optional[int] = None,
    environ: Optional[Mapping[str, str]] = None,
) -> IsolationResult:
    """Run the fail-closed preflight for the process that verifies/commits Gate 1.

    Fails closed on: an unresolvable agent identity, euid equal to the agent uid,
    `SSH_AUTH_SOCK` present, and any of the protected artifacts failing its
    ownership/mode/symlink/ancestor checks. The DB is intentionally not inspected.
    Every failure is reported. Container/sandbox markers are evidence only."""
    failures: List[IsolationFailure] = []
    human_uid = os.geteuid() if euid is None else euid
    env = os.environ if environ is None else environ

    resolved_uid, gids = _resolve_agent_identity(agent_name, agent_uid, agent_gids)
    if resolved_uid is None:
        failures.append(
            IsolationFailure(
                "IDENTITY_UNRESOLVED",
                None,
                f"cannot resolve agent account '{agent_name}'; create it per references/isolation-setup.md",
            )
        )
    elif human_uid == resolved_uid:
        failures.append(
            IsolationFailure("EUID_IS_AGENT", None, "the verifying process runs as the agent uid")
        )
    if SSH_AUTH_SOCK in env:
        failures.append(
            IsolationFailure("SSH_AUTH_SOCK_SET", None, "SSH_AUTH_SOCK is set in the verifying process")
        )

    for signers in (Path(allowed_signers), Path(allowed_signers_selftest)):
        _check_file(signers, human_uid, resolved_uid, gids, SIGNERS_MODE, failures)
    _check_dir(Path(challenge_dir), human_uid, resolved_uid, gids, failures)
    for key in key_paths:
        _check_file(Path(key), human_uid, resolved_uid, gids, None, failures)

    evidence = {
        "agent_name": agent_name,
        "agent_uid": resolved_uid,
        "euid": human_uid,
        "markers": {"dockerenv": os.path.exists("/.dockerenv"), "container_env": "container" in env},
    }
    return IsolationResult(ok=not failures, failures=tuple(failures), evidence=evidence)


def open_protected_readonly(
    path: PathLike,
    *,
    expected_mode: Optional[int] = None,
    expected_uid: Optional[int] = None,
    forbidden_mode_bits: int = 0,
) -> int:
    """Open `path` read-only with O_NOFOLLOW and verify it from the descriptor.

    Returns the fd (the caller closes it and may hold it across a transaction).
    Raises IsolationError for a symlink, a non-regular file, a wrong owner, a wrong
    mode, or any mode bit in `forbidden_mode_bits` (e.g. 0o022 for group/other write). Verification uses fstat on the opened descriptor, so a swap after
    the check cannot change what was verified."""
    uid = os.geteuid() if expected_uid is None else expected_uid
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        reason = "is a symlink" if exc.errno in (errno.ELOOP, errno.EMLINK) else f"cannot be opened: {exc}"
        raise IsolationError(f"{path} {reason}") from exc
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise IsolationError(f"{path} is not a regular file")
        if st.st_uid != uid:
            raise IsolationError(f"{path} owner uid {st.st_uid} is not the expected uid {uid}")
        mode = stat.S_IMODE(st.st_mode)
        if expected_mode is not None and mode != expected_mode:
            raise IsolationError(f"{path} mode {mode:04o}, required {expected_mode:04o}")
        if mode & forbidden_mode_bits:
            raise IsolationError(f"{path} mode {mode:04o} has forbidden bits {forbidden_mode_bits:04o}")
    except IsolationError:
        os.close(fd)
        raise
    return fd
