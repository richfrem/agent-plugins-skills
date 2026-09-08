"""RED contract tests for active-runtime capability detection."""

from capability_probe import detect_runtime, probe_runtime


def test_detects_codex_from_active_session_marker(monkeypatch):
    monkeypatch.setenv("CODEX_CLI", "1")
    assert detect_runtime() == "codex"


def test_detects_agy_from_active_session_marker(monkeypatch):
    monkeypatch.setenv("ANTIGRAVITY_IDE", "1")
    assert detect_runtime() == "agy"


def test_detects_copilot_from_active_session_marker(monkeypatch):
    monkeypatch.setenv("GITHUB_COPILOT_CLI", "1")
    assert detect_runtime() == "copilot"


def test_detects_claude_code_from_active_session_marker(monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_ENTRY", "1")
    assert detect_runtime() == "claude-code"


def test_unknown_runtime_is_explicitly_unavailable(monkeypatch):
    for name in ("CODEX_CLI", "ANTIGRAVITY_IDE", "GITHUB_COPILOT_CLI", "CLAUDE_CODE_ENTRY"):
        monkeypatch.delenv(name, raising=False)
    result = probe_runtime()
    assert result.runtime_id == "unknown"
    assert result.available is False
    assert result.native_worktree is False


def test_codex_native_worktree_requires_explicit_capability_marker(monkeypatch):
    monkeypatch.setenv("CODEX_CLI", "1")
    monkeypatch.delenv("CODEX_NATIVE_WORKTREE", raising=False)
    assert probe_runtime().native_worktree is False

    monkeypatch.setenv("CODEX_NATIVE_WORKTREE", "1")
    result = probe_runtime()
    assert result.native_worktree is True
    assert "native" in result.worktree_activation.lower()

