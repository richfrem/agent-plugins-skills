---
concept: changelog
source: plugin-code
source_file: agent-agentic-os/CHANGELOG.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.121293+00:00
cluster: added
content_hash: 59822d41cbefff54
---

# Changelog

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Changelog

All notable changes to `agent-agentic-os` are documented here.

## [1.4.0] - 2026-04-04

### Deep Architecture & Triple-Loop Paradigm
- **Full Pattern 5 Deprecation**: Formally sunset the legacy "Flywheel" and "Pattern 5" orchestration methodologies in favor of the unified **Triple-Loop Orchestrator** framework.
- **Dynamic Sibling-Repo Evaluations**: Migrated automated code evaluations entirely to isolated, headless sibling-labs via `evaluate.py`. Removed obsolete subjective testing instructions from `test-scenarios-seed.md` and deprecated `init_flywheel_files.py`.
- **Reference & Taxonomy Healing**: Restructured the 24 flat file `references/` directory into highly organized semantic subfolders (`architecture/`, `operations/`, `memory/`, `testing/`, `meta/`), executing a cross-plugin automated parser to safely heal every markdown text link and symlink within the `.agents/skills` isolation boundaries.
- **Hook Portability**: Re-engineered shell-script hooks (`session-start.sh`) into clean, inherently cross-platform Python binaries (`session_start.py`) ensuring full Windows and MacOS resilience.
- **Metric Normalzation**: Transformed logging metrics within `post_run_metrics.py` to correctly surface Triple Loop progression rather than "Fast Cycle" phases.

## [1.3.1] - 2026-03-19

### Bug Fixes (claude-4.6 review of v1.3.0)
- **Triple-Loop Retrospective.md Phase 1**: Lock acquisition (`acquire_lock kernel`) is now conditional — skipped entirely in Fast Path mode. Previously Fast Path held the kernel write lock while doing a read-only analysis, defeating the lightweight intent.
- **AUTO-APPLY ZONE**: Replaced vague "low-risk" with four concrete, enumerable conditions that must ALL be true for auto-apply (user-confirmed this session, pure addition, factual not policy, non-strict mode). Conditions are now present in both the CLAUDE.md template comment and the SANDBOX PROTECTION RULE in `Triple-Loop Retrospective.md` so the agent has them at decision time.

## [1.3.0] - 2026-03-19

### Execution Tiers (Issue: process overhead for lightweight use cases)
- **os-state.json template**: Added `execution_mode` (`lightweight` | `standard` | `strict`, default `standard`), `hook_sample_rate` (default 1 = every call), and `lock_timeout_seconds` (default 1800) fields.
- **update_memory.py**: Added `_check_execution_gate()` — skips hook entirely when `execution_mode=lightweight`; skips `N-1` of every `N` calls when `hook_sample_rate > 1` (counter stored in `os-state.json["hook_call_count"]`).
- **CLAUDE_MD_PROJECT.md template**: Added `## [AUTO-APPLY ZONE]` append-only section; the learning loop may write low-risk facts here without manual approval when `execution_mode != strict`.
- **Triple-Loop Retrospective.md**: Added "Fast Path (Passive Analyzer)" mode — default for routine sessions. Completes Phases 0-2 and emits a `FINDINGS:` block without acquiring write locks or modifying files. Full loop only on explicit user request or 3+ same-type friction events.

### Hook Visibility (Issue: silent failures unnoticed)
- **post_run_metrics.py**: Added `count_hook_errors()` that reads `context/memory/hook-errors.log`; hook error count included in Stop-hook summary line and in the emitted metric event (`results.hook_errors`). Failures are now visible at session end.

### Memory Schema (Issue: freeform drift)
- **os-memory-manager/SKILL.md**: Added Option B — structured JSONL format (`context/memory.jsonl`) as an alternative to freeform markdown. Benefits: unambiguous deduplication by `id`, machine-queryable, easier `<SUPERSEDE>` enforcement.

### Backlog (architectural, deferred to v2.0)
- `temp/backlog/agentic-os-backlog-kernel-split.md` — split `kernel.py` into `lock_manager`, `event_bus`, `state_manager`
- `temp/backlog/agentic-os-backlog-sqlite-backend.md` — SQLite backend for `events.jsonl` and `context/memory.md`
- `temp/backlog/agentic-os-backlog-embedding-routing.md` — TF-IDF / embedding-based skill routing replacing keyword heuri

*(content truncated)*

## See Also

*(No related concepts found yet)*

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/CHANGELOG.md`
- **Indexed:** 2026-04-17T06:42:09.121293+00:00
