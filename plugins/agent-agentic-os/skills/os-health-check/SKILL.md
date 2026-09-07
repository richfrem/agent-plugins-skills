---
name: os-health-check
plugin: agent-agentic-os
description: >
  Trigger with "run health check", "check os metrics", "system monitor", or when the user
  wants to review the Agentic OS liveness metrics across the Event Bus, locks, and memory
  arrays. Scans context/events.jsonl, os-state.json, and context/memory.md deterministically
  via kernel.py — no conversational judgment required. Migrated from the former
  os-health-check agent (2026-09-05): deterministic Bash+Read diagnostic, no interview,
  no adversarial judgment — fits the skill archetype, not the agent archetype.
allowed-tools: Bash, Read
---

<example>
<commentary>User explicitly requested a system diagnostic.</commentary>
user: "Run a system monitor check on the OS."
assistant: Scans the event bus and state file, compiles liveness metrics, and reports them.
</example>

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

# OS Health Check

Scan across the `context/events.jsonl` Event Bus stream, review `os-state.json` liveness, and
compile system metrics without mutating user files.

## Execution Flow

### Phase 0: Intent Emission (Event Bus)

```bash
python3 scripts/kernel.py emit_event --agent os-health-check --type intent --action scan_metrics
```

### Phase 1: Context Gathering & OS State Lock

```bash
python3 scripts/kernel.py state_update active_agent os-health-check
python3 scripts/kernel.py acquire_lock monitor
```

If the lock acquisition fails, abort — the kernel handles stale lock cleanup automatically
(see `os-clean-locks` if a stale lock persists).

### Phase 2: Analyze Event Bus

Inspect the recent Event Bus (`tail -n 100 context/events.jsonl`) and calculate metrics: total
intent vs. result events, hook error count (also check `context/memory/hook-errors.log`), and
any agent that emitted `intent` without a matching `result` (crash signal).

### Phase 3: Inspect Memory & File Health

Check `context/memory.md` length (`wc -l`), scan `context/.locks/` for leaked stale locks, and
determine whether `memory_gc_due` should be flagged.

### Phase 3.5: os-init Substrate Completeness Check

Verify the scaffolding artifacts `os-init --retrofit` is responsible for creating
(`control_plane.db`, `.claude/hooks/hooks.json`, `.git/hooks/pre-commit-evolution-guard`,
`.github/workflows/verify-evolution-integrity.yml`), the Phase 0 intake rule in `CLAUDE.md`,
lingering `.bak` files, and per-plugin `references/evolution-log.md`. Run this on every health
check, not just once — a stale `init_agentic_os.py` copy can reintroduce gaps (see
DEBT-20260905-12/-13/-14). Any MISSING result is a Tier 1 finding — recommend re-running
`init_agentic_os.py --target . --retrofit` (idempotent, safe to re-run). Exact commands are
in `references/detailed-reference.md`.

### Phase 4: Summarize & Lock Release

```bash
python3 scripts/kernel.py emit_event --agent os-health-check --type result --action scan_metrics --status success --summary "Metrics compiled"
python3 scripts/kernel.py release_lock monitor
```

Present the metrics to the user. Recommend `os-clean-locks` or `os-memory-manager` if health
metrics indicate deadlock or bloated state, and recommend re-running `os-init --retrofit` if
Phase 3.5 found any missing substrate. If Phase 3.5 found drifted local skills/scripts, see the
Consumer Guidance on Plugin Drift in `references/detailed-reference.md` (upstream fix vs.
local domain customization).

### Phase 5: Self-Assessment Survey (MANDATORY)

Complete the Post-Run Self-Assessment Survey (`references/memory/post_run_survey.md`) after
every run and save to
`context/memory/retrospectives/survey_[YYYYMMDD]_[HHMM]_os-health-check.md`, then emit
`--type learning --action survey_completed`. Full survey questions in
`references/detailed-reference.md`.
