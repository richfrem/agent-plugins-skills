---
concept: meta-harness-enhancement-task-tracker
source: research-docs
source_file: meta-harness/task-tracker.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.458277+00:00
cluster: done
content_hash: bffa689817c81080
---

# Meta-Harness Enhancement Task Tracker

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Meta-Harness Enhancement Task Tracker

**Based on:** arXiv:2603.28052 (Lee et al., March 2026)
**Plan:** [implementation-plan.md](./implementation-plan.md)
**Target:** `plugins/agent-agentic-os/`

---

## Status Summary

| # | Enhancement | Priority | Status |
|---|---|---|---|
| 1 | Per-input trace storage (`eval_runner.py` + `evaluate.py`) | HIGH | ✅ Done (already implemented) |
| 2 | Skill state snapshot (`--snapshot` flag) | MEDIUM | ✅ Done (already implemented) |
| 3 | Hypothesis block in `os-skill-improvement` SKILL.md | MEDIUM | ✅ Done (already implemented) |
| 4 | Milestone summary files (`generate_milestone.py`) | LOW | ✅ Done |
| 5 | Two-gate backport confirmation in `os-eval-runner` Stage 6 | LOW | ✅ Done (already implemented) |

---

## Enhancement 1 — Per-Input Trace Storage

**Status:** ✅ Done
**Files:** `scripts/eval_runner.py`, `scripts/evaluate.py`, `skills/os-eval-runner/SKILL.md`

Already fully implemented:
- `eval_runner.py --json` outputs `routing_detail` (per-input: input, should_trigger, matched_keywords, triggered, correct, failure_reason) and `heuristic_detail`
- `evaluate.py` has `write_trace()` — writes `evals/traces/iter_NNN_VERDICT_scoreX.XX.json` after every iteration
- `os-eval-runner` SKILL.md documents the `traces/` directory and includes grep troubleshooting commands

---

## Enhancement 2 — Skill State Snapshot

**Status:** ✅ Done
**Files:** `scripts/eval_runner.py`, `skills/os-skill-improvement/SKILL.md`

Already fully implemented:
- `eval_runner.py --snapshot` calls `build_snapshot()` — reads `results.tsv` + latest trace, outputs markdown block with score trend, KEEP/DISCARD counts, fp/fn rates, dominant problem (PRECISION/RECALL), and recommended action
- `os-skill-improvement` SKILL.md has "Required: Skill State Snapshot" step before any mutation

---

## Enhancement 3 — Hypothesis Block Requirement

**Status:** ✅ Done
**Files:** `skills/os-skill-improvement/SKILL.md`

Already fully implemented:
- "Required: Hypothesis Block" section in `os-skill-improvement` SKILL.md with 5-field format (Failure mode, Root cause, Change, Effect, Risk)
- Acceptable and not-acceptable examples included

---

## Enhancement 4 — Milestone Summary Files

**Status:** ✅ Done
**Files:** `scripts/generate_milestone.py` (new), `skills/os-eval-runner/SKILL.md` (updated)

`generate_milestone.py` created. Reads `evals/results.tsv` + `evals/traces/*.json`. Writes
`evals/traces/milestone_NNN.md` every N iterations (default 25, `--force` to override).
Sections: score trajectory, top KEEPs, worst DISCARDs (with repeat-attempt flagging),
recurring false-positive inputs from last 5 traces, dominant problem, recommended focus.
`os-eval-runner` SKILL.md updated with milestone directory entry and usage commands.

---

## Enhancement 5 — Two-Gate Backport Confirmation

**Status:** ✅ Done
**Files:** `skills/os-eval-runner/SKILL.md`

Already fully implemented:
- Stage 6 in `os-eval-runner` SKILL.md has two-gate protocol: Gate 1 (machine — evaluate.py exit 0) and Gate 2 (three-perspective commentary: test engineer view, routing precision view, regression view)
- Unattended run handling: writes commentary to `temp/retrospectives/` and flags for human review before auto-applying


## See Also

- [[meta-harness-end-to-end-optimization-of-model-harnesses]]
- [[meta-harness-end-to-end-optimization-of-model-harnesses]]
- [[meta-harness-artifact-code-analysis]]
- [[implementation-plan-meta-harness-enhancements-to-os-eval-runner-os-skill-improvement]]
- [[meta-harness-end-to-end-optimization-of-model-harnesses]]
- [[agent-harness-learning-layer-formerly-agentic-os]]

## Raw Source

- **Source:** `research-docs`
- **File:** `meta-harness/task-tracker.md`
- **Indexed:** 2026-04-17T06:42:10.458277+00:00
