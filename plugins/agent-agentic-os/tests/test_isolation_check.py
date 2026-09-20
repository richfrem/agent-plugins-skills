"""
tests/test_isolation_check.py
=============================

Purpose:
    Failing-first acceptance tests for T1 (auth-ciba-increment-b, issue #639):
    control_plane/isolation_check.py's fail-closed isolation preflight for
    Gate 1 (AWAITING_APPROVAL -> APPROVED). The boundary (human decision D4):
    `allowed_signers`, `allowed_signers_selftest`, the private signing keys and
    the challenge directory are human-owned and agent-inaccessible. The SQLite DB
    is deliberately NOT part of the check (the agent must keep writing it).
    Spec section 4 case 6a. All tests use real files and real modes in tmp_path;
    the agent identity (name, uid, gids) and the process environment are injected
    through the function's parameters, so no os.stat/pwd/subprocess mocking is used.
    Case 6b (an ordinary transition as the real agent account) is environment-gated
    and reported UNTESTED on this platform; see test_case6b_* at the bottom.

Key Input Dependencies:
    - control_plane/isolation_check.py (check_isolation, open_protected_readonly,
      DEFAULT_AGENT_NAME, IsolationResult, IsolationError)
    - Real temporary files and directories only (pytest tmp_path)

Key Functions (test cases):
    - test_default_agent_name_constant
    - test_pass_with_correct_layout
    - test_signature_has_no_db_parameter
    - test_passes_while_db_is_world_writable
    - test_denies_when_euid_is_agent
    - test_denies_unresolvable_identity
    - test_denies_ssh_auth_sock_set
    - test_denies_bad_allowed_signers_mode / test_denies_bad_selftest_mode
    - test_denies_missing_files
    - test_denies_symlinked_file / test_denies_symlink_in_ancestor
    - test_denies_file_owned_by_agent_uid
    - test_denies_bad_challenge_dir_mode / _with_symlink_entry / _not_a_directory
    - test_denies_key_with_group_or_other_bits
    - test_denies_world_writable_non_sticky_ancestor / _sticky_ancestor_ok
    - test_denies_group_writable_ancestor_when_agent_in_group
    - test_all_failures_are_reported
    - test_open_protected_readonly_* (incl. forbidden_mode_bits, added for T3)
    - test_case6b_ordinary_transition_as_real_agent_account (environment-gated)
"""

import inspect
import os
import pwd
import sqlite3
import stat
import sys
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from control_plane.isolation_check import (
    DEFAULT_AGENT_NAME,
    IsolationError,
    check_isolation,
    open_protected_readonly,
)


def _other_uid() -> int:
    """A uid that is not the current user's (real account if available)."""
    for name in ("nobody", "daemon"):
        try:
            uid = pwd.getpwnam(name).pw_uid
            if uid != os.geteuid():
                return uid
        except KeyError:
            continue
    return os.geteuid() + 4242


@pytest.fixture
def layout(tmp_path):
    """A correct human-owned layout: 0600 files, 0700 challenge dir."""
    root = tmp_path / "identity"
    root.mkdir()
    os.chmod(root, 0o700)
    files = {}
    for name in ("allowed_signers", "allowed_signers_selftest", "id_ed25519"):
        p = root / name
        p.write_text("placeholder\n")
        os.chmod(p, 0o600)
        files[name] = p
    chal = root / "challenges"
    chal.mkdir()
    os.chmod(chal, 0o700)
    return {
        "root": root,
        "allowed_signers": files["allowed_signers"],
        "allowed_signers_selftest": files["allowed_signers_selftest"],
        "key": files["id_ed25519"],
        "challenge_dir": chal,
    }


def _run(layout, **over):
    kwargs = dict(
        allowed_signers=layout["allowed_signers"],
        allowed_signers_selftest=layout["allowed_signers_selftest"],
        challenge_dir=layout["challenge_dir"],
        key_paths=[layout["key"]],
        agent_name=DEFAULT_AGENT_NAME,
        agent_uid=_other_uid(),
        agent_gids=set(),
        environ={},
    )
    kwargs.update(over)
    return check_isolation(**kwargs)


def _codes(result):
    return {f.code for f in result.failures}


def test_default_agent_name_constant():
    assert DEFAULT_AGENT_NAME == "agentic-os-local-agent"


def test_pass_with_correct_layout(layout):
    result = _run(layout)
    assert result.ok, result.failures
    assert result.failures == ()


def test_signature_has_no_db_parameter():
    params = set(inspect.signature(check_isolation).parameters)
    assert not {p for p in params if "db" in p.lower() or "sqlite" in p.lower()}


def test_passes_while_db_is_world_writable(layout, tmp_path):
    """D4: the agent keeps DB write access; the preflight must not care."""
    db = tmp_path / "control_plane.db"
    sqlite3.connect(db).close()
    os.chmod(db, 0o666)
    assert stat.S_IMODE(os.stat(db).st_mode) == 0o666
    assert _run(layout).ok


def test_denies_when_euid_is_agent(layout):
    result = _run(layout, agent_uid=os.geteuid())
    assert not result.ok
    assert "EUID_IS_AGENT" in _codes(result)


def test_denies_unresolvable_identity(layout):
    result = _run(layout, agent_name="no-such-account-xyz-123", agent_uid=None)
    assert not result.ok
    assert "IDENTITY_UNRESOLVED" in _codes(result)


def test_denies_ssh_auth_sock_set(layout):
    result = _run(layout, environ={"SSH_AUTH_SOCK": "/tmp/agent.sock"})
    assert not result.ok
    assert "SSH_AUTH_SOCK_SET" in _codes(result)


@pytest.mark.parametrize("mode", [0o644, 0o660, 0o640, 0o400, 0o666, 0o700])
def test_denies_bad_allowed_signers_mode(layout, mode):
    os.chmod(layout["allowed_signers"], mode)
    result = _run(layout)
    assert not result.ok
    assert "BAD_MODE" in _codes(result)


@pytest.mark.parametrize("mode", [0o644, 0o660, 0o400])
def test_denies_bad_selftest_mode(layout, mode):
    os.chmod(layout["allowed_signers_selftest"], mode)
    result = _run(layout)
    assert not result.ok
    assert "BAD_MODE" in _codes(result)


@pytest.mark.parametrize("which", ["allowed_signers", "allowed_signers_selftest", "challenge_dir"])
def test_denies_missing_files(layout, which):
    target = layout[which]
    if target.is_dir():
        target.rmdir()
    else:
        target.unlink()
    result = _run(layout)
    assert not result.ok
    assert "PATH_MISSING" in _codes(result)


def test_denies_symlinked_file(layout, tmp_path):
    real = tmp_path / "elsewhere"
    real.write_text("x")
    os.chmod(real, 0o600)
    layout["allowed_signers"].unlink()
    layout["allowed_signers"].symlink_to(real)
    result = _run(layout)
    assert not result.ok
    assert "SYMLINK_COMPONENT" in _codes(result)


def test_denies_symlink_in_ancestor(layout, tmp_path):
    link = tmp_path / "link_to_identity"
    link.symlink_to(layout["root"])
    result = _run(
        layout,
        allowed_signers=link / "allowed_signers",
        allowed_signers_selftest=link / "allowed_signers_selftest",
        challenge_dir=link / "challenges",
        key_paths=[link / "id_ed25519"],
    )
    assert not result.ok
    assert "SYMLINK_COMPONENT" in _codes(result)


def test_denies_file_owned_by_agent_uid(layout):
    """Files here are owned by the current user; declare that uid to be the agent."""
    result = _run(layout, agent_uid=os.geteuid(), euid=os.geteuid() + 1)
    assert not result.ok
    assert "OWNED_BY_AGENT" in _codes(result)


@pytest.mark.parametrize("mode", [0o755, 0o770, 0o750, 0o777, 0o500])
def test_denies_bad_challenge_dir_mode(layout, mode):
    os.chmod(layout["challenge_dir"], mode)
    try:
        result = _run(layout)
    finally:
        os.chmod(layout["challenge_dir"], 0o700)
    assert not result.ok
    assert "BAD_MODE" in _codes(result)


def test_denies_challenge_dir_with_symlink_entry(layout, tmp_path):
    (layout["challenge_dir"] / "7.sig").symlink_to(tmp_path / "anything")
    result = _run(layout)
    assert not result.ok
    assert "CHALLENGE_DIR_HAS_SYMLINK" in _codes(result)


def test_denies_challenge_dir_not_a_directory(layout):
    layout["challenge_dir"].rmdir()
    layout["challenge_dir"].write_text("not a dir")
    os.chmod(layout["challenge_dir"], 0o700)
    result = _run(layout)
    assert not result.ok
    assert "NOT_DIRECTORY" in _codes(result)


@pytest.mark.parametrize("mode", [0o640, 0o604, 0o660, 0o666])
def test_denies_key_with_group_or_other_bits(layout, mode):
    os.chmod(layout["key"], mode)
    result = _run(layout)
    assert not result.ok
    assert "BAD_MODE" in _codes(result)


@pytest.mark.parametrize("mode", [0o600, 0o400])
def test_accepts_private_key_modes(layout, mode):
    os.chmod(layout["key"], mode)
    assert _run(layout).ok


def test_denies_world_writable_non_sticky_ancestor(layout):
    os.chmod(layout["root"], 0o777)
    try:
        result = _run(layout)
    finally:
        os.chmod(layout["root"], 0o700)
    assert not result.ok
    assert "ANCESTOR_AGENT_WRITABLE" in _codes(result)


def test_sticky_world_writable_ancestor_is_ok(layout):
    os.chmod(layout["root"], 0o1777)
    try:
        result = _run(layout)
    finally:
        os.chmod(layout["root"], 0o700)
    assert result.ok, result.failures


def test_denies_group_writable_ancestor_when_agent_in_group(layout):
    gid = os.stat(layout["root"]).st_gid
    os.chmod(layout["root"], 0o770)
    try:
        result = _run(layout, agent_gids={gid})
        not_in_group = _run(layout, agent_gids=set())
    finally:
        os.chmod(layout["root"], 0o700)
    assert not result.ok
    assert "ANCESTOR_AGENT_WRITABLE" in _codes(result)
    assert "ANCESTOR_AGENT_WRITABLE" not in _codes(not_in_group)


def test_all_failures_are_reported(layout):
    os.chmod(layout["allowed_signers"], 0o644)
    os.chmod(layout["challenge_dir"], 0o755)
    try:
        result = _run(layout, environ={"SSH_AUTH_SOCK": "/x"}, agent_uid=os.geteuid())
    finally:
        os.chmod(layout["challenge_dir"], 0o700)
    assert not result.ok
    assert {"BAD_MODE", "SSH_AUTH_SOCK_SET", "EUID_IS_AGENT"} <= _codes(result)


def test_open_protected_readonly_returns_readable_fd(layout):
    fd = open_protected_readonly(layout["allowed_signers"], expected_mode=0o600)
    try:
        assert os.read(fd, 64) == b"placeholder\n"
    finally:
        os.close(fd)


def test_open_protected_readonly_rejects_symlink(layout, tmp_path):
    real = tmp_path / "real"
    real.write_text("x")
    os.chmod(real, 0o600)
    link = tmp_path / "link"
    link.symlink_to(real)
    with pytest.raises(IsolationError):
        open_protected_readonly(link, expected_mode=0o600)


def test_open_protected_readonly_rejects_wrong_mode(layout):
    os.chmod(layout["allowed_signers"], 0o644)
    with pytest.raises(IsolationError):
        open_protected_readonly(layout["allowed_signers"], expected_mode=0o600)


def test_open_protected_readonly_rejects_wrong_owner(layout):
    with pytest.raises(IsolationError):
        open_protected_readonly(
            layout["allowed_signers"], expected_mode=0o600, expected_uid=os.geteuid() + 1
        )


def test_open_protected_readonly_rejects_forbidden_mode_bits(layout):
    """T3 uses this for signature files: group/other write bits are refused."""
    os.chmod(layout["allowed_signers"], 0o666)
    with pytest.raises(IsolationError):
        open_protected_readonly(layout["allowed_signers"], forbidden_mode_bits=0o022)


def test_open_protected_readonly_accepts_when_forbidden_bits_absent(layout):
    os.chmod(layout["allowed_signers"], 0o644)
    fd = open_protected_readonly(layout["allowed_signers"], forbidden_mode_bits=0o022)
    os.close(fd)


@pytest.mark.skipif(
    os.geteuid() != 0 or not os.environ.get("AGENTIC_OS_REAL_AGENT_ACCOUNT"),
    reason="UNTESTED here: case 6b needs root (or equivalent) to run as the real "
    "agentic-os-local-agent account; non-root identity switching is unavailable on macOS",
)
def test_case6b_ordinary_transition_as_real_agent_account():
    """Environment-gated (spec 6b): an ordinary agent_or_human transition succeeds
    as the real agent account while the preflight passes. Not part of the automated
    acceptance claim; recorded as UNTESTED where this cannot run."""
    raise NotImplementedError("Run manually in a provisioned isolation setup; see isolation-setup.md")
