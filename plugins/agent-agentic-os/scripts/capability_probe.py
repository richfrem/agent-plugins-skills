"""Session-aware runtime capability probing for native-first orchestration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping, Optional


@dataclass(frozen=True)
class RuntimeCapabilities:
    """Explicitly observed runtime facilities and portable fallback guidance."""

    runtime_id: str
    available: bool
    native_planning: bool
    native_worktree: bool
    native_subagents: bool
    tool_support: tuple[str, ...]
    worktree_activation: str
    portable_fallback: str


_RUNTIME_MARKERS = (
    ("claude-code", ("CLAUDE_CODE_ENTRY", "CLAUDE_PROJECT_DIR")),
    ("agy", ("ANTIGRAVITY_IDE", "ANTIGRAVITY_AGENT")),
    ("copilot", ("GITHUB_COPILOT_CLI", "COPILOT_CLI")),
    ("codex", ("CODEX_CLI", "CODEX_SESSION")),
)


def detect_runtime(env: Optional[Mapping[str, str]] = None) -> str:
    """Return the active runtime from session markers, never from model names."""
    values = os.environ if env is None else env
    for runtime_id, markers in _RUNTIME_MARKERS:
        if any(values.get(marker) for marker in markers):
            return runtime_id
    return "unknown"


def probe_runtime(
    runtime_id: Optional[str] = None,
    env: Optional[Mapping[str, str]] = None,
) -> RuntimeCapabilities:
    """Build a capability result from explicit session evidence.

    Codex native worktree support is reported only when the runtime explicitly
    advertises it with ``CODEX_NATIVE_WORKTREE``. A model identifier alone never
    grants native capability.
    """
    values = os.environ if env is None else env
    runtime = (runtime_id or detect_runtime(values)).lower()
    fallback = "Invoke the issue-worktree-agent skill for the portable .worktrees lifecycle."
    base = {
        "runtime_id": runtime,
        "available": runtime != "unknown",
        "native_planning": False,
        "native_worktree": False,
        "native_subagents": False,
        "tool_support": (),
        "worktree_activation": "Use the portable worktree fallback.",
        "portable_fallback": fallback,
    }
    if runtime == "claude-code":
        base.update(native_planning=True, native_subagents=True, tool_support=("plan_mode", "tools"),
                    worktree_activation="Use Claude Code native plan mode; retain the portable worktree fallback.")
    elif runtime == "agy":
        base.update(native_planning=True, tool_support=("planning", "tools"),
                    worktree_activation="Use Antigravity native planning when available; retain the portable worktree fallback.")
    elif runtime == "copilot":
        base.update(tool_support=("prompt",),
                    worktree_activation="Copilot CLI has no confirmed native worktree facility; use the portable fallback.")
    elif runtime == "codex":
        native_worktree = values.get("CODEX_NATIVE_WORKTREE", "").lower() in {"1", "true", "yes"}
        base.update(native_worktree=native_worktree, tool_support=("plan_mode", "tools"),
                    worktree_activation=(
                        "Activate Codex native worktree mode before creating files; do not create a portable worktree."
                        if native_worktree else
                        "Codex native worktree capability is not confirmed; use the portable fallback."
                    ))
    return RuntimeCapabilities(**base)
