# Changelog

All notable changes to `agent-agentic-os` are documented here.

## [1.5.0] - 2026-04-25

### os-architect — Front-Door Evolution Intake
- **New agent**: `agents/os-architect-agent.md` — interactive conductor that classifies user intent into 5 categories (Pattern Abstraction, Research Application, Lab Setup, Gap Fill, Multi-Loop Orchestration), audits the ecosystem, proposes Path A/B/C, and dispatches via `run_agent.py`. Replaces the "where do I start" problem in agent-agentic-os.
- **New skill**: `skills/os-architect/SKILL.md` — slash command entry point (`/os-architect`)
- **New evals**: `skills/os-architect/evals/evals.json` — 19 routing cases with `expected_category` field (1–5) on all TP cases and 4 misrouting-risk boundary cases
- **Confidence-aware classification**: Phase 1 classification block includes `Confidence: High | Medium | Low`; Low confidence triggers a clarifying question before proceeding to audit
- **Path A+ (no-op path)**: When audit shows Full match + current + all self-healing patterns present, agent tells user "no action needed" rather than forcing a path
- **Category 5 dispatch spec**: Multi-Loop Orchestration now has a concrete per-target sequential dispatch protocol in Phase 3

### os-evolution-verifier — Evolution Artifact Verification Skill
- **New skill**: `skills/os-evolution-verifier/SKILL.md` — dispatches os-architect in single-shot simulation mode for a given test scenario, checks artifact presence via grep/file-exists (not transcript review), and reports PASS/FAIL with evidence. Uses structured EVOLUTION_VERIFICATION output block with VERDICT: PASS | PARTIAL | FAIL. Accumulates results into `temp/os-evolution-verifier/test-report.md`.
- **New evals**: `skills/os-evolution-verifier/evals/evals.json` — 10 routing cases covering explicit verifier invocations vs. general architect queries
- **PARTIAL verdict**: More precise than binary pass/fail — pinpoints which specific workstream failed

### os-experiment-log — Persistent Experiment Log Skill
- **New skill**: `skills/os-experiment-log/SKILL.md` — append-only log of evolution verification runs at `context/experiment-log.md`. Three modes: `append` (post-run), `query <term>` (search by scenario ID/verdict), `summary` (aggregate stats). Closes the loop on learnings — every test run leaves a durable record with actions taken.
- **New evals**: `skills/os-experiment-log/evals/evals.json` — 8 routing cases
- **Initialized**: `context/experiment-log.md` — empty log ready to receive first run

### os-evolution-planner — Repeatable Plan-and-Delegate Skill
- **New skill**: `skills/os-evolution-planner/SKILL.md` — given a target and evolution goal, applies the self-healing diagnostic lens, writes a structured task plan (`tasks/todo/<slug>-plan.md`), and writes a dense Copilot CLI delegation prompt. Called by os-architect for Path B/C executions.

### os-architect-tester — Scenario-Based Validation Agent
- **New agent**: `agents/os-architect-tester-agent.md` — runs pre-scripted scenario transcripts through os-architect via Copilot CLI and evaluates against 4 acceptance criteria (intent classification, dispatch gating, evals HARD-GATE, audit verification). 3 built-in scenarios.

### improvement-intake-agent — Phase 4c + HANDOFF_BLOCK
- **Phase 4c added**: After writing `run-config.json` and `session-brief.md`, agent registers itself in `context/agents.json` and emits `intake-complete` lifecycle event via `plugins/agent-agentic-os/scripts/kernel.py`
- **HANDOFF_BLOCK added**: Phase 5 now emits a machine-readable handoff block consumed by `improvement-lifecycle-orchestrator`; replaces prose-only routing context
- **Routing After Handoff updated**: Now references HANDOFF_BLOCK fields rather than a separate prose context block

### triple-loop-architect — Phase 0 Intake Integration
- **Phase 0.0 added**: Checks for `improvement/run-config.json` (written by improvement-intake-agent) and auto-populates all key variables (`TARGET_SKILL`, `PARTITION_ID`, `RUN_DEPTH`, `DISPATCH`) — skips user-prompted steps 0.1 and 0.2 when intake config is present
- **Phase 0.4 added**: Seeds lab with gotchas from intake config and writes `invariants.json` into the sibling lab after Phase 1.2 initialization

### Cleanup
- Removed transitory patch files (`improvement-intake-phase4c-5-patch.md`, `triple-loop-architect-phase0-patch.md`) from source and `.agents/` — both patches are now fully applied

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
- `temp/backlog/agentic-os-backlog-embedding-routing.md` — TF-IDF / embedding-based skill routing replacing keyword heuristic

## [1.2.0] - 2026-03-19

### Security / Correctness
- **kernel.py**: Configurable lock timeout via `os-state.json["lock_timeout_seconds"]` (default 1800s). Replaces hardcoded value.
- **kernel.py**: PID stamp written inside `events_rotate.lock` directory on acquisition; startup self-heal clears orphaned rotation lock if age > 60s (prevents SIGKILL deadlock).
- **kernel.py**: `validate_event_schema()` rejects events missing required fields (`time`, `agent`, `type`, `action`) before writing to bus.
- **post_run_metrics.py**: Removed stale metric->result fallback. Kernel natively accepts `"metric"` event type.
- **post_run_metrics.py**: Added 2048-char payload truncation guard on `--summary` argument.

### Bug Fixes
- **init_agentic_os.py**: Both `load_template()` and `copy_runtime_file()` now prefer `CLAUDE_PLUGIN_ROOT` env var (set by the plugin environment) before falling back to `Path(__file__)` resolution. Fixes path breakage on Windows and symlinked legacy installs.
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
- **agents/Triple-Loop Retrospective.md**: Added 1 implicit/audit `<example>` block (proactive friction detection from event stream).

## [1.1.0] - 2026-03-18

### Fixes (from claude-review-v2 and claude-review-v6)
- **hooks/hooks.json**: Migrated to Anthropic-spec format.
- **agents/os-health-check.md**: Removed unnecessary `Write` tool.
- **agent-agentic-os-architecture.mmd**: Removed stale `mcp.json` reference node.
- **os-clean-locks/evals/evals.json**: Created initial eval suite.
- **os-memory-manager/evals/evals.json**: Schema normalized.
- **os-eval-runner/evals/evals.json**: Schema normalized.

## [1.0.0] - Initial release
