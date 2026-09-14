"""
test_worktree_manager.py -- Contract Tests for Native-First Worktree Routing
==================================================================================

Purpose:
    RED contract tests for native-first worktree routing: verifies build_worktree_plan()
    prefers a runtime's native worktree capability when confirmed, falls back to the
    portable `.worktrees/<task-id>` layout for unknown runtimes, bounds portable
    placement under `.worktrees`, and routes cleanup_command() per strategy.

Key Input Dependencies:
    - capability_probe.py's probe_runtime() (runtime capability detection).
    - worktree_manager.py (module under test) -- build_worktree_plan(),
      cleanup_command(), validate_portable_placement().

Key Functions:
    - test_codex_prefers_native_worktree_when_capability_is_confirmed()
    - test_unknown_runtime_uses_portable_repo_worktree_fallback()
    - test_portable_placement_must_remain_under_worktrees()
    - test_cleanup_routes_native_and_portable_modes()
"""

from pathlib import Path

import pytest

from capability_probe import probe_runtime
from worktree_manager import (
    build_worktree_plan,
    cleanup_command,
    validate_portable_placement,
    STRATEGY_NATIVE,
    STRATEGY_PORTABLE,
)


def test_codex_prefers_native_worktree_when_capability_is_confirmed(monkeypatch, tmp_path):
    monkeypatch.setenv("CODEX_CLI", "1")
    monkeypatch.setenv("CODEX_NATIVE_WORKTREE", "1")
    plan = build_worktree_plan("task-1", "feat/task-1", tmp_path, probe_runtime())
    assert plan.strategy == STRATEGY_NATIVE
    assert plan.activation_guidance


def test_unknown_runtime_uses_portable_repo_worktree_fallback(tmp_path):
    capabilities = probe_runtime(runtime_id="unknown")
    plan = build_worktree_plan("task-2", "feat/task-2", tmp_path, capabilities)
    assert plan.strategy == STRATEGY_PORTABLE
    assert plan.path == tmp_path / ".worktrees" / "task-2"
    assert "issue-worktree-agent" in plan.fallback_command


def test_portable_placement_must_remain_under_worktrees(tmp_path):
    allowed = tmp_path / ".worktrees" / "task-3"
    assert validate_portable_placement(allowed, tmp_path) == allowed
    with pytest.raises(ValueError, match=r"\.worktrees"):
        validate_portable_placement(tmp_path / "outside", tmp_path)


def test_cleanup_routes_native_and_portable_modes():
    assert cleanup_command(Path("/tmp/native"), STRATEGY_NATIVE) == ["native-worktree-cleanup", "/tmp/native"]
    assert cleanup_command(Path("/tmp/portable"), STRATEGY_PORTABLE)[-1] == "/tmp/portable"
