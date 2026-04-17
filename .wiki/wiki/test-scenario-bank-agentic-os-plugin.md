---
concept: test-scenario-bank-agentic-os-plugin
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-improvement-report/test-scenarios-seed.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.174884+00:00
cluster: loop
content_hash: c48851100dd4251d
---

# Test Scenario Bank — Agentic OS Plugin

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Test Scenario Bank — Agentic OS Plugin

Pre-designed hypotheses for the test registry. ORCHESTRATOR reads this at orientation
and selects the highest-priority untested scenario for each cycle. As scenarios are run,
move them to `context/memory/tests/registry.md` with their results.

**Status note**: All `results.tsv` baselines are empty. The first eval run for each
skill establishes the baseline. Tests 1-N per skill should be designed as
"establish baseline + identify first improvement opportunity" — not comparison tests.

---

## Registry Index (All 50 Scenarios)

| ID | Target | Hypothesis | Priority |
|----|--------|------------|----------|
| T01 | os-eval-runner | Baseline routing: eval triggers on correct phrases, not on explain/describe | HIGH |
| T02 | os-eval-runner | KEEP/DISCARD threshold: clearly improved skill scores KEEP, degraded scores DISCARD | HIGH |
| T03 | os-eval-runner | Adversarial coverage: eval catches prompts designed to bypass routing | MEDIUM |
| T04 | os-eval-runner | Edge case: graceful failure when evals.json is missing or malformed | MEDIUM |
| T05 | os-eval-runner | Survey completion: evaluator completes self-assessment after every eval run | HIGH |
| T06 | os-improvement-loop | Baseline 1-cycle smoke: all 14 mandatory loop steps execute in order | HIGH |
| T07 | os-improvement-loop | Friction emission: agents emit type:friction events when encountering ambiguity | HIGH |
| T08 | os-improvement-loop | Loop report written: report file created after every cycle regardless of outcome | HIGH |
| T09 | os-improvement-loop | Survey completion: both ORCHESTRATOR and INNER_AGENT complete survey after cycle | HIGH |
| T10 | os-improvement-loop | Memory persistence: at least one promoted fact in context/memory.md after cycle | MEDIUM |
| T11 | os-improvement-loop | Auto-trigger: Triple-Loop Retrospective triggered when friction_events_total reaches 3 | HIGH |
| T12 | os-improvement-loop | Lock contention: second agent attempting same lock receives clear failure, not hang | HIGH |
| T13 | os-clean-locks | Baseline routing: triggers on /os-clean-locks and lock variants, not on list-locks | HIGH |
| T14 | os-clean-locks | Stale lock cleanup: lock with PID that no longer exists gets removed | HIGH |
| T15 | os-clean-locks | Active lock protection: lock held by running PID is preserved | HIGH |
| T16 | os-clean-locks | Post-clean verification: state_update clears active_agent field after cleanup | MEDIUM |
| T17 | os-clean-locks | Survey completion: os-clean-locks completes self-assessment after every run | MEDIUM |
| T18 | os-memory-manager | Baseline promotion: ephemeral state skipped, architectural decisions promoted | HIGH |
| T19 | os-memory-manager | Dedup detection: semantic duplicate caught and flagged before write | HIGH |
| T20 | os-memory-manager | Test registry preservation: registry.md skipped by archive logic, never deleted | HIGH |
| T21 | os-memory-manager | Conflict detection: <CONFLICT> marker emitted before any write with overlap | HIGH |
| T22 | os-memory-manager | Size enforcement: memory.md over 50KB triggers archive, not silent truncation | MEDIUM |
| T23 | os-memory-manager | Survey completion: memory manager completes self-assessment after every session | HIGH |
| T24 | os-memory-manager | Rollback protocol: rejected write triggers git stash pop, file reverted | MEDIUM |
| T25 | os-memory-manager | Falsified hypothesis: DO NOT RE-TEST entry added to memory.md when hypothesis falsified | HIGH |
| T26 | learning-loop | Baseline 3-phase completion: observe, hypothesize, test phases all execute | HIGH |
| T27 | learning-loop | Survey Phase V: survey completed and saved to retrospectives/ after every run | HIGH |
| T28 | learning-loop | Metrics Phase VI: post_run_metrics.py fires and emits metric event | HIGH |
| T29 | learning-loop | Memory Phase VII: os-memory-manager invoked before handoff | HIGH |
| T30 | learning-loop | Handoff gate: Phase VIII only starts after survey saved + metric

*(content truncated)*

## See Also

- [[agent-harness-learning-layer-formerly-agentic-os]]
- [[agentic-os-setup-orchestrator]]
- [[agentic-os-architecture]]
- [[canonical-agentic-os-file-structure]]
- [[agentic-os---future-vision]]
- [[agentic-os-improvement-backlog]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-improvement-report/test-scenarios-seed.md`
- **Indexed:** 2026-04-17T06:42:10.174884+00:00
