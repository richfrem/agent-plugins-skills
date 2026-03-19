# Changelog

All notable changes to `agent-agentic-os` are documented here.

## [1.2.0] - 2026-03-19

### Security / Correctness
- **kernel.py**: Configurable lock timeout via `os-state.json["lock_timeout_seconds"]` (default 1800s). Replaces hardcoded value.
- **kernel.py**: PID stamp written inside `events_rotate.lock` directory on acquisition; startup self-heal clears orphaned rotation lock if age > 60s (prevents SIGKILL deadlock).
- **kernel.py**: `validate_event_schema()` rejects events missing required fields (`time`, `agent`, `type`, `action`) before writing to bus.
- **post_run_metrics.py**: Removed stale metric->result fallback. Kernel natively accepts `"metric"` event type.
- **post_run_metrics.py**: Added 2048-char payload truncation guard on `--summary` argument.

### Bug Fixes
- **init_agentic_os.py**: `context/memory.md` removed from `.gitignore` guidance; moved to "Keep in git" section (it is curated long-term memory and must be committed).
- **init_agentic_os.py**: `--global` flag now prints a note reminding users to manually `@import` or wire `context/kernel.py` into `~/.claude/CLAUDE.md`.
- **init_agentic_os.py**: Both `load_template()` and `copy_runtime_file()` now prefer `CLAUDE_PLUGIN_ROOT` env var (set by Claude Code and `npx skills add`) before falling back to `Path(__file__)` resolution. Fixes path breakage on Windows and symlinked npx installs.
- **hooks/hooks.json**: Fixed from flat format to Anthropic-spec nested format (`hooks -> EventName -> [{matcher, hooks: [{type, command}]}]`).
- **agentic-os-init/templates/HOOKS_JSON.json**: Was empty `{"hooks": []}`. Now ships with `SessionStart`, `PostToolUse`, and `Stop` hooks so fresh installs get auto-memory wiring.
- **agents/os-health-check.md**: Removed `Write` from tool list; health check is read-only.
- **agent-agentic-os-architecture.mmd**: Removed stale `mcp.json` node.

### Improvements
- **session-memory-manager/SKILL.md**: Added `<SUPERSEDE old_id=NNN>` audit marker requirement when a promoted fact supersedes an existing memory entry.
- **session-memory-manager/SKILL.md**: Archive policy changed from `wc -l > 500` (unreliable on Windows CRLF) to `wc -c > 50000` bytes.
- **os-clean-locks/SKILL.md**: Added Phase 0 (intent emit) and Phase 4 (result emit) Event Bus hooks.
- **eval_runner.py**: Added `llm_routing_score` column to `results.tsv` (value `N/A`; reserved for future LLM judge integration).
- **references/diagrams/**: Removed 5 binary PNG files; `.mmd` source files retained.
- **todo-check/scripts/check_todos.py**: Expanded debt pattern to include `FIXME`, `HACK`, `XXX`, `NOTE` in addition to `TODO`.

### Evals
- **os-clean-locks/evals/evals.json**: Created (was the only skill without evals). 6 positive triggers, 3 negatives.
- **session-memory-manager/evals/evals.json**: Normalized to standard `{prompt, should_trigger: bool}` schema.
- **skill-improvement-eval/evals/evals.json**: Normalized schema and added 3 additional entries matching SKILL.md triggers.

### Routing / Trigger Quality
- **skill-improvement-eval/SKILL.md**: Added scope caveat documenting that `eval_runner.py` uses keyword-heuristic routing, not real LLM routing.
- **agentic-os-guide/SKILL.md**: Added 2 `<example>` blocks (including 1 implicit/audit trigger).
- **agentic-os-init/SKILL.md**: Added 3 `<example>` blocks (including 1 implicit/audit trigger).
- **todo-check/SKILL.md**: Added 1 implicit/audit `<example>` block.
- **skill-improvement-eval/SKILL.md**: Added 1 implicit/audit `<example>` block.
- **os-clean-locks/SKILL.md**: Added 1 implicit/audit `<example>` block.
- **agents/os-learning-loop.md**: Added 1 implicit/audit `<example>` block (proactive friction detection from event stream).

## [1.1.0] - 2026-03-18

### Fixes (from claude-review-v2 and claude-review-v6)
- **hooks/hooks.json**: Migrated to Anthropic-spec format.
- **agents/os-health-check.md**: Removed unnecessary `Write` tool.
- **agent-agentic-os-architecture.mmd**: Removed stale `mcp.json` reference node.
- **os-clean-locks/evals/evals.json**: Created initial eval suite.
- **session-memory-manager/evals/evals.json**: Schema normalized.
- **skill-improvement-eval/evals/evals.json**: Schema normalized.

## [1.0.0] - Initial release
