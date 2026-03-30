# Changelog

All notable changes to `agent-agentic-os` are documented here.

## [1.3.1] - 2026-03-19

### Bug Fixes (claude-4.6 review of v1.3.0)
- **os-learning-loop.md Phase 1**: Lock acquisition (`acquire_lock kernel`) is now conditional — skipped entirely in Fast Path mode. Previously Fast Path held the kernel write lock while doing a read-only analysis, defeating the lightweight intent.
- **AUTO-APPLY ZONE**: Replaced vague "low-risk" with four concrete, enumerable conditions that must ALL be true for auto-apply (user-confirmed this session, pure addition, factual not policy, non-strict mode). Conditions are now present in both the CLAUDE.md template comment and the SANDBOX PROTECTION RULE in `os-learning-loop.md` so the agent has them at decision time.

## [1.3.0] - 2026-03-19

### Execution Tiers (Issue: process overhead for lightweight use cases)
- **os-state.json template**: Added `execution_mode` (`lightweight` | `standard` | `strict`, default `standard`), `hook_sample_rate` (default 1 = every call), and `lock_timeout_seconds` (default 1800) fields.
- **update_memory.py**: Added `_check_execution_gate()` — skips hook entirely when `execution_mode=lightweight`; skips `N-1` of every `N` calls when `hook_sample_rate > 1` (counter stored in `os-state.json["hook_call_count"]`).
- **CLAUDE_MD_PROJECT.md template**: Added `## [AUTO-APPLY ZONE]` append-only section; the learning loop may write low-risk facts here without manual approval when `execution_mode != strict`.
- **os-learning-loop.md**: Added "Fast Path (Passive Analyzer)" mode — default for routine sessions. Completes Phases 0-2 and emits a `FINDINGS:` block without acquiring write locks or modifying files. Full loop only on explicit user request or 3+ same-type friction events.

### Hook Visibility (Issue: silent failures unnoticed)
- **post_run_metrics.py**: Added `count_hook_errors()` that reads `context/memory/hook-errors.log`; hook error count included in Stop-hook summary line and in the emitted metric event (`results.hook_errors`). Failures are now visible at session end.

### Memory Schema (Issue: freeform drift)
- **os-memory-manager/SKILL.md**: Added Option B — structured JSONL format (`context/memory.jsonl`) as an alternative to freeform markdown. Benefits: unambiguous deduplication by `id`, machine-queryable, easier `<SUPERSEDE>` enforcement.

### Backlog (architectural, deferred to v2.0)
- `temp/backlog/agentic-os-backlog-kernel-split.md` — split `kernel.py` into `lock_manager`, `event_bus`, `state_manager`
- `temp/backlog/agentic-os-backlog-sqlite-backend.md` — SQLite backend for `events.jsonl` and `context/memory.md`
- `temp/backlog/agentic-os-backlog-embedding-routing.md` — TF-IDF / embedding-based skill routing replacing keyword heuristic

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
- **os-init/templates/HOOKS_JSON.json**: Was empty `{"hooks": []}`. Now ships with `SessionStart`, `PostToolUse`, and `Stop` hooks so fresh installs get auto-memory wiring.
- **agents/os-health-check.md**: Removed `Write` from tool list; health check is read-only.
- **agent-agentic-os-architecture.mmd**: Removed stale `mcp.json` node.

### Improvements
- **os-memory-manager/SKILL.md**: Added `<SUPERSEDE old_id=NNN>` audit marker requirement when a promoted fact supersedes an existing memory entry.
- **os-memory-manager/SKILL.md**: Archive policy changed from `wc -l > 500` (unreliable on Windows CRLF) to `wc -c > 50000` bytes.
- **os-clean-locks/SKILL.md**: Added Phase 0 (intent emit) and Phase 4 (result emit) Event Bus hooks.
- **eval_runner.py**: Added `llm_routing_score` column to `results.tsv` (value `N/A`; reserved for future LLM judge integration).
- **references/diagrams/**: Removed 5 binary PNG files; `.mmd` source files retained.
- **todo-check/scripts/check_todos.py**: Expanded debt pattern to include `FIXME`, `HACK`, `XXX`, `NOTE` in addition to `TODO`.

### Evals
- **os-clean-locks/evals/evals.json**: Created (was the only skill without evals). 6 positive triggers, 3 negatives.
- **os-memory-manager/evals/evals.json**: Normalized to standard `{prompt, should_trigger: bool}` schema.
- **os-eval-runner/evals/evals.json**: Normalized schema and added 3 additional entries matching SKILL.md triggers.

### Routing / Trigger Quality
- **os-eval-runner/SKILL.md**: Added scope caveat documenting that `eval_runner.py` uses keyword-heuristic routing, not real LLM routing.
- **os-guide/SKILL.md**: Added 2 `<example>` blocks (including 1 implicit/audit trigger).
- **os-init/SKILL.md**: Added 3 `<example>` blocks (including 1 implicit/audit trigger).
- **todo-check/SKILL.md**: Added 1 implicit/audit `<example>` block.
- **os-eval-runner/SKILL.md**: Added 1 implicit/audit `<example>` block.
- **os-clean-locks/SKILL.md**: Added 1 implicit/audit `<example>` block.
- **agents/os-learning-loop.md**: Added 1 implicit/audit `<example>` block (proactive friction detection from event stream).

## [1.1.0] - 2026-03-18

### Fixes (from claude-review-v2 and claude-review-v6)
- **hooks/hooks.json**: Migrated to Anthropic-spec format.
- **agents/os-health-check.md**: Removed unnecessary `Write` tool.
- **agent-agentic-os-architecture.mmd**: Removed stale `mcp.json` reference node.
- **os-clean-locks/evals/evals.json**: Created initial eval suite.
- **os-memory-manager/evals/evals.json**: Schema normalized.
- **os-eval-runner/evals/evals.json**: Schema normalized.

## [1.0.0] - Initial release
