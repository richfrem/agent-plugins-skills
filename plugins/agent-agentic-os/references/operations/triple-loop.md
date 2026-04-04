# Triple-Loop Learning System (Outer Orchestrator + Inner Execution)

Canonical reference for the overarching orchestrator, strategy packet (Double-Loop), and tactical verification protocol (Single-Loop) used by `os-improvement-loop`.

Diagram: [`references/diagrams/triple-loop-learning-system.mmd`](../assets/diagrams/triple-loop-learning-system.mmd)

---

## Workflow

**Step 1 - Plan (TRIPLE-LOOP ORCHESTRATOR):** Orient, decompose goal into atomic iteration targets across experiments, formulate cross-session learning hypotheses.

**Step 2 - Strategy Packet (DOUBLE-LOOP PLANNER):** Write `handoffs/packet-${CID}.md` containing: goal + target path, required file paths only, strict NO GIT constraint, acceptance criteria. Emit `task.assigned`.

**Step 3 - Execute (INNER_AGENT):** Read packet, do work, emit `friction` events immediately on uncertainty, run `eval_runner.py`, write `handoffs/out-${CID}.md`, emit `task.complete`.

**Step 4 - Verify (PEER_AGENT):** Run `os-eval-runner` independently (do not read score from event). Compare to `results.tsv` baseline.

- **KEEP**: ORCHESTRATOR applies changes, emits `orchestrator.decision`.
- **DISCARD**: Generate correction packet (`handoffs/correction-${CID}.md`) with severity (CRITICAL / MODERATE / MINOR). Re-signal INNER_AGENT. Do not emit `orchestrator.decision` until KEEP.

**Step 5 - Survey (all agents):** Complete Post-Run Self-Assessment Survey. Save to `${CLAUDE_PROJECT_DIR}/context/memory/retrospectives/survey_[DATE]_[TIME]_[AGENT].md`. Emit `learning / survey_completed`. If any friction cause appears 3+ times: flag for `Triple-Loop Retrospective`.

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
