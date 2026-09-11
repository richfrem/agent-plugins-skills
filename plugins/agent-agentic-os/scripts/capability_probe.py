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


def _explicit_capability(values: Mapping[str, str], prefix: str, capability: str, default: bool = False) -> bool:
    """Return a native capability only when the active runtime advertises it."""
    raw = values.get(f"{prefix}_NATIVE_{capability}")
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes"}


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
    """Build a capability result from documented runtime facilities.

    An explicit ``<RUNTIME>_NATIVE_*`` marker can disable a documented facility
    or opt into a host-provided extension. Model names never grant capability.
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
        native_planning = _explicit_capability(values, "CLAUDE", "PLANNING", default=True)
        native_worktree = _explicit_capability(values, "CLAUDE", "WORKTREE", default=True)
        native_subagents = _explicit_capability(values, "CLAUDE", "SUBAGENTS", default=True)
        base.update(native_planning=native_planning, native_worktree=native_worktree,
                    native_subagents=native_subagents, tool_support=("plan_mode", "worktree", "subagents", "tools"),
                    worktree_activation=("Use Claude Code native worktree capability."
                                         if native_worktree else "Use Claude Code native plan mode; retain the portable worktree fallback."))
    elif runtime == "agy":
        native_planning = _explicit_capability(values, "AGY", "PLANNING", default=True)
        native_worktree = _explicit_capability(values, "AGY", "WORKTREE")
        native_subagents = _explicit_capability(values, "AGY", "SUBAGENTS", default=True)
        base.update(native_planning=native_planning, native_worktree=native_worktree,
                    native_subagents=native_subagents, tool_support=("plan_mode", "subagents", "tools"),
                    worktree_activation=("Use Antigravity native worktree capability."
                                         if native_worktree else "Use Antigravity native planning when available; retain the portable worktree fallback."))
    elif runtime == "copilot":
        native_planning = _explicit_capability(values, "COPILOT", "PLANNING", default=True)
        native_worktree = _explicit_capability(values, "COPILOT", "WORKTREE")
        native_subagents = _explicit_capability(values, "COPILOT", "SUBAGENTS", default=True)
        base.update(native_planning=native_planning, native_worktree=native_worktree,
                    native_subagents=native_subagents, tool_support=("plan_mode", "subagents", "tools"),
                    worktree_activation=("Use Copilot native worktree capability."
                                         if native_worktree else "Copilot native worktree capability is not confirmed; use the portable fallback."))
    elif runtime == "codex":
        native_planning = _explicit_capability(values, "CODEX", "PLANNING")
        native_worktree = _explicit_capability(values, "CODEX", "WORKTREE")
        native_subagents = _explicit_capability(values, "CODEX", "SUBAGENTS")
        base.update(native_planning=native_planning, native_worktree=native_worktree,
                    native_subagents=native_subagents, tool_support=("plan_mode", "tools"),
                    worktree_activation=(
                        "Activate Codex native worktree mode before creating files; do not create a portable worktree."
                        if native_worktree else
                        "Codex native worktree capability is not confirmed; use the portable fallback."
                    ))
    return RuntimeCapabilities(**base)
