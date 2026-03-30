# Dual-Loop (Inner/Outer Agent Delegation)

Canonical reference for the strategy packet, correction packet, and verification protocol used by `os-improvement-loop` Pattern D.

Diagram: [`references/diagrams/dual-loop-flow.mmd`](../assets/diagrams/dual-loop-flow.mmd)

---

## Workflow

**Step 1 - Plan (ORCHESTRATOR):** Orient, decompose goal into atomic WPs, confirm non-overlapping.

**Step 2 - Strategy Packet:** Write `handoffs/packet-${CID}.md` containing: goal + target path, pre-execution diagram, required file paths only, strict NO GIT constraint, acceptance criteria. Emit `task.assigned`.

**Step 3 - Execute (INNER_AGENT):** Read packet, do work, emit `friction` events immediately on uncertainty, run `eval_runner.py`, write `handoffs/out-${CID}.md`, emit `task.complete`.

**Step 4 - Verify (PEER_AGENT):** Run `os-eval-runner` independently (do not read score from event). Compare to `results.tsv` baseline.

- **KEEP**: ORCHESTRATOR applies changes, emits `orchestrator.decision`.
- **DISCARD**: Generate correction packet (`handoffs/correction-${CID}.md`) with severity (CRITICAL / MODERATE / MINOR). Re-signal INNER_AGENT. Do not emit `orchestrator.decision` until KEEP.

**Step 5 - Survey (all agents):** Complete Post-Run Self-Assessment Survey. Save to `${CLAUDE_PROJECT_DIR}/context/memory/retrospectives/survey_[DATE]_[TIME]_[AGENT].md`. Emit `learning / survey_completed`. If any friction cause appears 3+ times: flag for `os-learning-loop`.

---

## Task Lane Transitions

| Transition | Trigger |
|-----------|---------|
| Backlog -> Doing | Strategy Packet generated |
| Doing -> Review | `task.complete` emitted |
| Review -> Done | KEEP verdict |
| Review -> Doing | DISCARD + Correction Packet |

---

## Constraints

- INNER_AGENT: code and tests only. No git.
- ORCHESTRATOR: git, architecture, human interactions only.
- Strategy Packets must be minimal -- only what INNER_AGENT needs for the specific WP.
- Validations must be actually performed, not described as if performed.
