---
concept: capabilities-matrix-plugin-comparison
source: research-docs
source_file: superpowers/capabilities-matrix.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.462031+00:00
cluster: missing
content_hash: b97e1c52f1d15436
---

# Capabilities Matrix: Plugin Comparison

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Capabilities Matrix: Plugin Comparison

Columns: **agent-agentic-os** | **exploration-cycle-plugin** | **superpowers**
Rating scale: Full / Partial / Missing / Not Applicable

---

## 1. Session Memory and Persistence

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| Session-to-session memory persistence | **Full** - Three-tier model: MEMORY.md (auto), context/memory.md (curated L3), context/memory/YYYY-MM-DD.md (L2 session logs). Deduplication and conflict detection built in. | **Partial** - Relies on agentic-os kernel.py for event emission; exploration/session-brief.md persists session intent. No independent memory stack. | **Missing** - No persistent memory layer. Session context is injected via the SessionStart hook (using-superpowers SKILL.md content only). No cross-session learning or retention. |
| Memory promotion and garbage collection | **Full** - session-memory-manager skill drives deliberate promotion from L2 to L3. Includes conflict resolution guard ("dementia guard"). | **Missing** - No promotion logic. Hook only suggests starting intake if brief is absent. | **Missing** - Not a concern in the design. Skills are stateless. |
| Memory deduplication and dedup IDs | **Full** - Conflict detection and dedup IDs explicitly specified in session-memory-manager and memory-hygiene reference. | **Missing** | **Missing** |
| Structured event log (audit trail) | **Full** - context/events.jsonl as the system event bus. kernel.py emits structured events with agent, type, action, status fields. | **Partial** - Uses kernel.py emit_event if present; exploration events emitted to the same log. Dependent on agentic-os being initialized. | **Missing** - No event log. No audit trail. |

---

## 2. Learning Loops and Retrospectives

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| Post-session retrospective mechanism | **Full** - os-learning-loop agent mines events.jsonl, proposes SKILL.md and CLAUDE.md patches. Fast Path and Full Loop modes. | **Full** - exploration-optimizer skill runs autoresearch-style iteration loops on exploration artifacts. results.tsv records keep/discard decisions. | **Missing** - No retrospective. No session closure workflow. Skills are authored once and updated manually. |
| Objective eval gate before applying changes | **Full** - skill-improvement-eval runs eval_runner.py against evals.json. KEEP/DISCARD verdict gates any write. | **Full** - exploration-optimizer enforces baseline-first, one-variable iteration with results.tsv ledger. Demonstrated in 12+ real iterations in evals/results.tsv. | **Missing** - No eval gate. writing-skills uses TDD-for-documentation approach (run agent without skill, observe failure, write skill, verify compliance), but this is a manual one-time authoring process, not a continuous loop. |
| Friction event capture and threshold triggering | **Full** - post_run_metrics.py counts friction events and emits metric. If friction_events_total >= 3, os-learning-loop auto-triggers on next session start. | **Partial** - No friction event infrastructure. exploration-optimizer runs on-demand. | **Missing** |
| Self-improvement ledger (longitudinal tracking) | **Full** - improvement-ledger.md records eval score progression, survey-to-action trace, and Autonomous Workflow Completion Rate across cycles. Specified in improvement-ledger-spec.md. | **Partial** - evals/results.tsv provides longitudinal keep/discard history. Less structured than improvement-ledger.md. | **Missing** |
| Post-run self-assessment survey | **Full** - post_run_survey.md is mandatory after every eval run. Agents save surveys to context/memory/retrospectives/. Friction counts feed the improvement loop. | **Partial** - Referenced in architecture docs. exploration-optimizer specifies survey data as a quality signal. Not as rigidly enforced as in agentic-os. | **Missing** |

---

## 3. Multi-Agent Orchestration

| Dimension | agent-ag

*(content truncated)*

## See Also

- [[adr-manager-plugin]]
- [[test-scenario-bank-agentic-os-plugin]]
- [[agent-plugin-analyzer]]
- [[adr-001-cross-plugin-script-dependencies]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[adr-004-self-contained-plugins---no-cross-plugin-script-dependencies]]

## Raw Source

- **Source:** `research-docs`
- **File:** `superpowers/capabilities-matrix.md`
- **Indexed:** 2026-04-17T06:42:10.462031+00:00
