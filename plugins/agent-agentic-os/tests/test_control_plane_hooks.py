"""
test_control_plane_hooks.py - unit tests for scripts/control_plane_hooks.py.

Purpose:
    The helper is the single implementation of guard wiring and of the declared control-plane
    mode. These tests pin its exact behaviour so the installer and the toggle cannot drift.
"""

import subprocess
from pathlib import Path

import pytest

import control_plane_hooks as cph

PUSH = next(g for g in cph.CONTROL_PLANE_GUARDS if g.name == "pre-push-review-guard")
COMMIT = next(g for g in cph.CONTROL_PLANE_GUARDS if g.name == "pre-commit-pipeline-guard")


def _hooks(tmp_path):
    d = tmp_path / "hooks"
    d.mkdir()
    return d


# ---- mode ----------------------------------------------------------------------------


def test_missing_mode_file_means_enabled(tmp_path):
    assert cph.read_mode(tmp_path) == "enabled"


def test_mode_round_trip_and_audit_log(tmp_path):
    cph.write_mode(tmp_path, "disabled", actor="me")
    assert cph.read_mode(tmp_path) == "disabled"
    assert cph.mode_path(tmp_path).read_text() == "disabled\n"
    cph.write_mode(tmp_path, "enabled")
    lines = (tmp_path / cph.MODE_LOG_RELATIVE_PATH).read_text().splitlines()
    assert len(lines) == 2 and '"mode": "disabled"' in lines[0] and '"actor": "me"' in lines[0]


@pytest.mark.parametrize("text", ["maybe", "", "ENABLE", "on"])
def test_invalid_mode_is_an_error_not_a_default(tmp_path, text):
    cph.mode_path(tmp_path).parent.mkdir(parents=True)
    cph.mode_path(tmp_path).write_text(text)
    with pytest.raises(cph.ModeError):
        cph.read_mode(tmp_path)


def test_mode_is_case_and_whitespace_tolerant(tmp_path):
    cph.mode_path(tmp_path).parent.mkdir(parents=True)
    cph.mode_path(tmp_path).write_text("  Disabled \n")
    assert cph.read_mode(tmp_path) == "disabled"


def test_write_mode_rejects_unknown_values(tmp_path):
    with pytest.raises(cph.ModeError):
        cph.write_mode(tmp_path, "paused")


def test_common_repo_root_is_the_main_checkout_for_a_worktree(tmp_path):
    main = tmp_path / "main"
    main.mkdir()
    for cmd in (["git", "init", "-q"], ["git", "config", "user.email", "a@b.c"], ["git", "config", "user.name", "T"],
                ["git", "commit", "--allow-empty", "-q", "-m", "x"]):
        subprocess.run(cmd, cwd=main, check=True, capture_output=True)
    wt = tmp_path / "wt"
    subprocess.run(["git", "worktree", "add", "-q", str(wt), "-b", "b"], cwd=main, check=True, capture_output=True)
    assert cph.common_repo_root(wt) == main.resolve()
    assert cph.common_repo_root(main) == main.resolve()


# ---- wiring --------------------------------------------------------------------------


def test_wire_creates_a_minimal_dispatcher_when_none_exists(tmp_path):
    d = _hooks(tmp_path)
    assert cph.wire_guard(d, PUSH) == "created"
    text = (d / "pre-push").read_text()
    assert text.startswith("#!/usr/bin/env bash") and 'HOOKS_DIR="$(dirname "$0")"' in text
    assert '"$HOOKS_DIR/pre-push-review-guard" || exit 1' in text and text.rstrip().endswith("exit 0")
    assert (d / "pre-push").stat().st_mode & 0o111


def test_wire_inserts_before_the_final_exit_and_keeps_custom_content(tmp_path):
    d = _hooks(tmp_path)
    (d / "pre-push").write_text('#!/bin/sh\nHOOKS_DIR="$(dirname "$0")"\necho custom\nexit 0\n')
    assert cph.wire_guard(d, PUSH) == "wired"
    text = (d / "pre-push").read_text()
    assert "echo custom" in text and text.index("pre-push-review-guard") < text.rindex("exit 0")


def test_wire_adds_the_hooks_dir_variable_when_the_dispatcher_lacks_it(tmp_path):
    d = _hooks(tmp_path)
    (d / "pre-push").write_text("#!/bin/sh\necho custom\nexit 0\n")
    cph.wire_guard(d, PUSH)
    assert 'HOOKS_DIR="$(dirname "$0")"' in (d / "pre-push").read_text()


def test_wire_is_idempotent(tmp_path):
    d = _hooks(tmp_path)
    cph.wire_guard(d, PUSH)
    first = (d / "pre-push").read_text()
    assert cph.wire_guard(d, PUSH) == "already-wired"
    assert (d / "pre-push").read_text() == first


def test_wire_then_unwire_restores_the_original_dispatcher_exactly(tmp_path):
    d = _hooks(tmp_path)
    original = '#!/bin/sh\nHOOKS_DIR="$(dirname "$0")"\necho custom\n\nexit 0\n'
    (d / "pre-push").write_text(original)
    cph.wire_guard(d, PUSH)
    assert cph.unwire_guard(d, PUSH) == "unwired"
    assert (d / "pre-push").read_text() == original


def test_unwire_handles_the_older_installer_style(tmp_path):
    d = _hooks(tmp_path)
    (d / "pre-push").write_text(
        '#!/usr/bin/env bash\n# pre-push hook - installed by init_agentic_os.py\nHOOKS_DIR="$(dirname "$0")"\n'
        '\n# Run review guard\nif [ -x "$HOOKS_DIR/pre-push-review-guard" ]; then\n'
        '    "$HOOKS_DIR/pre-push-review-guard" || exit 1\nfi\n\nexit 0\n'
    )
    assert cph.unwire_guard(d, PUSH) == "unwired"
    text = (d / "pre-push").read_text()
    assert "pre-push-review-guard" not in text and "Run review guard" not in text and "exit 0" in text


def test_unwire_only_removes_the_named_guard(tmp_path):
    d = _hooks(tmp_path)
    (d / "pre-commit").write_text('#!/bin/sh\nHOOKS_DIR="$(dirname "$0")"\n')
    cph.wire_guard(d, COMMIT)
    evolution = (
        '\n# Run evolution guard if it exists\nif [ -x "$HOOKS_DIR/pre-commit-evolution-guard" ]; then\n'
        '    "$HOOKS_DIR/pre-commit-evolution-guard" || exit 1\nfi\n'
    )
    text = (d / "pre-commit").read_text().replace("\nexit 0\n", "") + evolution + "\nexit 0\n"
    (d / "pre-commit").write_text(text)
    cph.unwire_guard(d, COMMIT)
    after = (d / "pre-commit").read_text()
    assert "pre-commit-pipeline-guard" not in after and "pre-commit-evolution-guard" in after


def test_unwire_reports_absent_and_unrecognized_without_modifying(tmp_path):
    d = _hooks(tmp_path)
    assert cph.unwire_guard(d, PUSH) == "absent"  # no dispatcher at all
    (d / "pre-push").write_text("#!/bin/sh\nexit 0\n")
    assert cph.unwire_guard(d, PUSH) == "absent"  # dispatcher never mentioned the guard
    odd = '#!/bin/sh\n[ -x "$H/pre-push-review-guard" ] && "$H/pre-push-review-guard"\nexit 0\n'
    (d / "pre-push").write_text(odd)
    assert cph.unwire_guard(d, PUSH) == "unrecognized"
    assert (d / "pre-push").read_text() == odd


def test_dry_run_writes_nothing(tmp_path):
    d = _hooks(tmp_path)
    assert cph.wire_guard(d, PUSH, dry_run=True) == "created"
    assert not (d / "pre-push").exists()
    cph.wire_guard(d, PUSH)
    before = (d / "pre-push").read_text()
    assert cph.unwire_guard(d, PUSH, dry_run=True) == "unwired"
    assert (d / "pre-push").read_text() == before


# ---- inspection + install ------------------------------------------------------------


def test_guard_state_and_install_script(tmp_path):
    d = _hooks(tmp_path)
    source = tmp_path / "guard-src"
    source.write_text("#!/bin/sh\nexit 0\n")
    assert cph.guard_state(d, PUSH, source)["script_present"] is False
    assert cph.install_guard_script(source, d, PUSH) is True
    assert cph.install_guard_script(source, d, PUSH) is False  # unchanged the second time
    cph.wire_guard(d, PUSH)
    state = cph.guard_state(d, PUSH, source)
    assert state["script_present"] and state["script_executable"] and state["wired"] and not state["stale"]
    source.write_text("#!/bin/sh\nexit 1\n")
    assert cph.guard_state(d, PUSH, source)["stale"] is True


def test_control_plane_guards_exclude_the_evolution_guard():
    assert {g.name for g in cph.CONTROL_PLANE_GUARDS} == {"pre-commit-pipeline-guard", "pre-push-review-guard"}
