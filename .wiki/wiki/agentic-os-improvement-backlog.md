---
concept: agentic-os-improvement-backlog
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-improvement-loop/references/meta/backlog.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.164179+00:00
cluster: cycle
content_hash: 879cdf08991ca875
---

# Agentic OS Improvement Backlog

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Agentic OS Improvement Backlog

> Append-only triage log. ORCHESTRATOR adds entries at Triple-Loop cycle step 6.5.
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
- A) Add Triple-Loop cycle step 6.5: ORCHESTRATOR answers 5 fixed meta-questions, appends to `context/memory/backlog.md`. ~5 min per loop. Simple, low overhead.
- B) Add a full ORCHESTRATOR self-assessment survey parallel to INNER/PEER surveys (Standard Cycle only). More thorough but slower — only runs on Standard Cycle, misses Triple-Loop cycle observations.
- C) Both: step 6.5 for quick triage observations (Triple-Loop cycle), full survey for deep reflection (Standard Cycle).
**Recommendation**: Option C. Step 6.5 is the speed path; full survey is optional depth. The two serve different purposes.
**Applies to**: `.agents/skills/os-improvement-loop/SKILL.md`, new `references/orchestrator-meta-survey.md` template, `init_Triple-Loop_files.py` (seed backlog.md)
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
**Applies to**: `.agents/skills/os-eval-runner/scripts/eval_runner.py`
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
- C) PEER reads score from INNER's event summary rather than from TSV. PEER's job is independent verification of the number, not independent TSV acc

*(content truncated)*

## See Also

- [[agent-harness-learning-layer-formerly-agentic-os]]
- [[agentic-os-setup-orchestrator]]
- [[agentic-os-architecture]]
- [[canonical-agentic-os-file-structure]]
- [[agentic-os---future-vision]]
- [[test-scenario-bank-agentic-os-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-improvement-loop/references/meta/backlog.md`
- **Indexed:** 2026-04-17T06:42:10.164179+00:00
