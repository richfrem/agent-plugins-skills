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

---

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

1. `tail -n 100 context/events.jsonl` (or `Read`) to inspect the recent Event Bus.
2. Calculate metrics: total intent events vs. result events, hook error count (also check
   `context/memory/hook-errors.log`), and any agent that emitted `intent` without a matching
   `result` (crash signal).

### Phase 3: Inspect Memory & File Health

1. `wc -l context/memory.md` to read the current memory file length.
2. `ls -la context/.locks/` to check for leaked stale locks.
3. Determine whether `memory_gc_due` should be flagged based on length.

### Phase 4: Summarize & Lock Release

```bash
python3 scripts/kernel.py emit_event --agent os-health-check --type result --action scan_metrics --status success --summary "Metrics compiled"
python3 scripts/kernel.py release_lock monitor
```

Present the metrics to the user. Recommend `os-clean-locks` or `os-memory-manager` if health
metrics indicate deadlock or bloated state.

### Phase 5: Self-Assessment Survey (MANDATORY)

Complete the Post-Run Self-Assessment Survey (`references/memory/post_run_survey.md`) after
every run — reflect on what was found so the OS can improve its own diagnostics.

**Count-Based Signals**: How many anomalies were detected? How many false positives? How many
times was a metric ambiguous or hard to interpret?

**Qualitative Friction**:
1. Which metric was hardest to interpret — why?
2. Was any anomaly detected that the current metrics don't capture well?
3. What pattern in `events.jsonl` was most surprising or concerning?
4. What one additional metric would make the next health check more useful?

**Improvement Recommendation**: What one change to this skill or the metrics definition
should be tested before the next run?

Save to: `${CLAUDE_PROJECT_DIR}/context/memory/retrospectives/survey_[YYYYMMDD]_[HHMM]_os-health-check.md`

```bash
python3 scripts/kernel.py emit_event --agent os-health-check \
  --type learning --action survey_completed \
  --summary "retrospectives/survey_[DATE]_[TIME]_os-health-check.md"
```
