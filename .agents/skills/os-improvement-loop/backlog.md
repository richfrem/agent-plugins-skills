# Agentic OS Improvement Backlog

> Append-only triage log. ORCHESTRATOR adds entries at Fast Cycle step 6.5.
> Never edit prior entries. Add a resolution note and move to Resolved when closed.
>
> Classes: S = simple fix (<5 min, clear solution) | M = requires thought, no arch change | L = architecture/options/trade-offs
> Criticality: P0 = blocking | P1 = degrades quality | P2 = nice to have
> Effort: (1) trivial | (2) small | (3) medium | (4) large | (5) research needed

---

## Active

---

### [2026-03-22] session-20260322 | P1 | M | Effort 3
**ID**: BL-001
**Title**: ORCHESTRATOR has no meta-assessment step in the loop
**Observed in**: All loops this session — nobody captures system-level health: are agents struggling with tooling, is the protocol too heavy, is the eval gate meaningful, are patterns repeating?
**Impact**: Systemic friction is invisible. Issues are noticed per-run but never logged, triaged, or tracked. The backlog itself doesn't exist until now.
**Options**:
- A) Add Fast Cycle step 6.5: ORCHESTRATOR answers 5 fixed meta-questions, appends to `context/memory/backlog.md`. ~5 min per loop. Simple, low overhead.
- B) Add a full ORCHESTRATOR self-assessment survey parallel to INNER/PEER surveys (Standard Cycle only). More thorough but slower — only runs on Standard Cycle, misses Fast Cycle observations.
- C) Both: step 6.5 for quick triage observations (Fast Cycle), full survey for deep reflection (Standard Cycle).
**Recommendation**: Option C. Step 6.5 is the speed path; full survey is optional depth. The two serve different purposes.
**Applies to**: `os-improvement-loop/SKILL.md`, new `references/orchestrator-meta-survey.md` template, `init_flywheel_files.py` (seed backlog.md)
**Decision needed**: Which 5 meta-questions go in step 6.5? (draft in options section above — needs user sign-off before implementation)

---

### [2026-03-22] session-20260322 | P1 | S | Effort 1
**ID**: BL-002
**Title**: Sub-agents ran eval_runner.py during survey writing without `--desc`, producing spurious TSV rows
**Observed in**: L004 loops — 2 extra "Manual iteration" rows in results.tsv with `llm_routing_score: 1.0000` (wrong column label)
**Impact**: results.tsv accumulates noise. Score history becomes unreliable. Chart shows extra KEEP dots that aren't real improvement cycles.
**Options**:
- A) Add `--cycle-id` as a required flag to `eval_runner.py` — hard-fail if absent. Clean, explicit. Breaking change for any caller that doesn't pass it.
- B) Add `--cycle-id` as optional but log a warning to stderr when absent. Non-breaking.
- C) Add a guard in the strategy packet instructions: "do not run eval_runner.py except at the designated eval step." Procedural only, not enforced.
**Recommendation**: Option B first (non-breaking warning), then make required after all callers are updated.
**Applies to**: `os-eval-runner/scripts/eval_runner.py`
**Blocks**: Nothing currently. Noise issue only.

---

### [2026-03-22] session-20260322 | P2 | M | Effort 3
**ID**: BL-003
**Title**: PEER_AGENT ran before INNER_AGENT in L003 — parallel race condition on results.tsv writes
**Observed in**: L003 — PEER wrote at 01:08:22, INNER wrote at 01:11:35. TSV ordering reflects whichever agent finished first, not logical cycle order.
**Impact**: `last_score` read by the second agent reflects the first agent's write, not the prior cycle's score. In L003 this caused the INNER's DISCARD verdict to be ambiguous (0.9 >= 0.9 should be KEEP, showed DISCARD — likely floating-point comparison after TSV round-trip).
**Options**:
- A) ORCHESTRATOR serializes agent runs: INNER writes first, then signals PEER. Eliminates race, adds latency.
- B) Add file lock around `results.tsv` reads/writes in `eval_runner.py`. Allows parallelism, prevents interleaved reads.
- C) PEER reads score from INNER's event summary rather than from TSV. PEER's job is independent verification of the number, not independent TSV access.
- D) Accept the race — it only matters at score boundaries (ties). Add `>` instead of `>=` for DISCARD to avoid tie ambiguity. One-character fix.
**Recommendation**: Option D as immediate mitigation (S-class), Option A or C as proper fix (M-class, decide with user).
**Applies to**: `eval_runner.py` (Option D), `os-improvement-loop/SKILL.md` (Options A/C)
**Note**: Option D changes KEEP semantics — equal score becomes DISCARD. Evaluate carefully.

---

### [2026-03-22] session-20260322 | P1 | L | Effort 5
**ID**: BL-004
**Title**: `llm_routing_score` column is N/A in every eval run — eval gate is entirely self-graded
**Observed in**: All 8 canonical eval runs this session. Every KEEP/DISCARD verdict was made by keyword matching, not semantic judgment.
**Impact**: The improvement ledger can show rising scores for a skill that is getting worse at its actual job. Keyword stuffing would pass F1 gate if negative evals don't cover the stuffed words. The F1 fix (v38) closes one vector but the fundamental problem remains: no LLM judge.
**Options**:
- A) One LLM API call per eval cycle via `claude-api` skill: submit the SKILL.md diff + one positive prompt and get a one-sentence routing judgment. Fills `llm_routing_score`. Cost: ~$0.001 per cycle. Requires API key in env.
- B) Use the existing `gemini-cli-agent` or `copilot-cli-agent` as a free-tier judge. More setup, less reliable, but zero API cost.
- C) Add LLM-based routing to `eval_runner.py` as an optional `--llm-judge` flag. Only fires when explicitly requested (Standard Cycle). Fast Cycle stays keyword-only.
- D) Accept keyword-only for now. The F1 gate + adversarial negative evals provide meaningful regression protection even without semantic judgment. Add LLM judge when a skill passes keyword eval but fails in practice (event-driven).
**Recommendation**: Option C + D combined. Default to keyword-only (fast). Add `--llm-judge` flag for Standard Cycle. Trigger it when a KEEP skill degrades in practice (a new friction event pattern).
**Applies to**: `eval_runner.py`, `os-improvement-loop/SKILL.md` Standard Cycle step 4, `os-eval-runner/SKILL.md`
**Research needed**: Which model, what prompt, how to score the response, how to normalize against keyword score.

---

### [2026-03-22] session-20260322 | P1 | M | Effort 3
**ID**: BL-005
**Title**: Tasks integration for L-effort backlog items — no defined path from backlog to `/tasks/`
**Observed in**: This session — BL-004 (LLM judge) and BL-003 (race condition fix) are L/M class but have no formal task created. They will be forgotten without a promotion path.
**Options**:
- A) ORCHESTRATOR manually promotes L-class P0/P1 items to `/tasks/` via task-manager skill at end of each Standard Cycle. Explicit, controlled.
- B) Add a rule to Fast Cycle step 6.5: if any new backlog item is L-class + P0/P1, emit a `task_promotion_needed` event. ORCHESTRATOR creates the task at next session start during orientation.
- C) Keep everything in `backlog.md`. Simple but the backlog gets long and tasks board stays unused.
**Recommendation**: Option B. Keeps Fast Cycle fast (no task creation during loop), defers to session start where ORCHESTRATOR has full context.
**Applies to**: `os-improvement-loop/SKILL.md` step 6.5, step 1 Orientation (check for `task_promotion_needed` events)
**Decision needed**: Task format for `/tasks/` — does task-manager skill need a specific template?

---

### [2026-03-22] session-20260322 | P2 | S | Effort 1
**ID**: BL-006
**Title**: runtime context written to UPSTREAM repo (`agent-plugins-skills/context/`) instead of LAB
**Observed in**: This session — improvement-ledger, surveys, loop reports, test registry all created in UPSTREAM. Had to manually delete.
**Impact**: Low — caught and corrected. But the demo instructions (HOW-TO-RESTART.md) don't make the `CLAUDE_PROJECT_DIR` requirement explicit enough.
**Options**:
- A) Update HOW-TO-RESTART.md to explicitly state `CLAUDE_PROJECT_DIR` must point at LAB, with a failing example.
- B) Add a guard in `init_flywheel_files.py` that warns if `CLAUDE_PROJECT_DIR` appears to be a plugin-source repo (heuristic: contains `plugins/` directory at root).
**Recommendation**: Option A immediately (S-class). Option B later if it recurs.
**Applies to**: `temp/agent-agentic-os-review/HOW-TO-RESTART.md`, optionally `init_flywheel_files.py`

---

## In Progress

*(none)*

---

## Resolved

*(none yet — first backlog entry)*

---

## Triage Key

```
Class:       S = fix in-loop (<5 min)   M = defer, next 3 loops   L = formal task + research
Criticality: P0 = blocking now          P1 = degrades quality      P2 = nice to have
Effort:      1 = trivial  2 = small  3 = medium  4 = large  5 = research/options needed
```

## Writing Protocol

ORCHESTRATOR appends to **Active** at Fast Cycle step 6.5. One entry per observed issue or opportunity.
Move to **In Progress** when a task is created or work begins.
Move to **Resolved** with a one-line resolution note when closed.
Never edit prior entries — add a follow-up entry if findings change.
