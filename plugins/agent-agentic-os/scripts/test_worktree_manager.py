"""RED contract tests for native-first worktree routing."""

from pathlib import Path

import pytest

from capability_probe import probe_runtime
from worktree_manager import (
    build_worktree_plan,
    cleanup_command,
    validate_portable_placement,
)


def test_codex_prefers_native_worktree_when_capability_is_confirmed(monkeypatch, tmp_path):
    monkeypatch.setenv("CODEX_CLI", "1")
    monkeypatch.setenv("CODEX_NATIVE_WORKTREE", "1")
    plan = build_worktree_plan("task-1", "feat/task-1", tmp_path, probe_runtime())
    assert plan.strategy == "native"
    assert plan.activation_guidance


def test_unknown_runtime_uses_portable_repo_worktree_fallback(tmp_path):
    capabilities = probe_runtime(runtime_id="unknown")
    plan = build_worktree_plan("task-2", "feat/task-2", tmp_path, capabilities)
    assert plan.strategy == "portable"
    assert plan.path == tmp_path / ".worktrees" / "task-2"
    assert "issue-worktree-agent" in plan.fallback_command


def test_portable_placement_must_remain_under_worktrees(tmp_path):
    allowed = tmp_path / ".worktrees" / "task-3"
    assert validate_portable_placement(allowed, tmp_path) == allowed
    with pytest.raises(ValueError, match=r"\.worktrees"):
        validate_portable_placement(tmp_path / "outside", tmp_path)


def test_cleanup_routes_native_and_portable_modes():
    assert cleanup_command(Path("/tmp/native"), "native") == ["native-worktree-cleanup", "/tmp/native"]
    assert cleanup_command(Path("/tmp/portable"), "portable")[-1] == "/tmp/portable"
