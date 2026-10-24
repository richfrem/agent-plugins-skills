# Agentic OS: Usage Guide

> The architectural references define the *Why* (control-plane guarantees, state machines, and learning invariants); this guide describes the *How* for a governed task from intake through retrospective.

## Contents

- [1. The Human / Caller Entry Point](#1-the-human--caller-entry-point)
- [2. The Experiment Log](#2-the-experiment-log)
- [3. The Task as the Unit of Work (Lifecycle)](#3-the-task-as-the-unit-of-work-lifecycle)
- [4. The Cold Start / Bootstrap Problem](#4-the-cold-start--bootstrap-problem)
- [5. Day-to-Day Operation Summary](#5-day-to-day-operation-summary)


---

## 1. The Human / Caller Entry Point

Two skills, each a router with modes. Describe what you want in plain language; routing picks the skill, and the skill picks the mode.

### Control plane: `running-control-plane`

Start any non-trivial engineering task with the skill's `intake` mode. It classifies the work, reads before acting, asks one question per turn, registers the task and writes the four-pillar `TASK_SPEC.md`. Other modes: `init` (set up or retrofit a project), `mode` (gating on or off), `health`, `signing-setup` (human only), `simulator`, `worktree`.

### Skill lab: `improving-skills-in-lab`

Start any evolution activity with the skill's interview. It captures the goal in your words, audits what exists, and agrees the run settings; then `plan` takes over. You do not need to know the other modes.

**Intent categories the `plan` mode handles:**
1. Pattern Abstraction: applying a new way of working to existing skills/agents
2. Research Application: incorporating techniques from papers or external research
3. Lab Setup / Improvement Loop: running eval iterations on an existing skill
4. Capability Gap Fill: creating a new skill or agent that doesn't exist yet
5. Multi-Loop Orchestration: coordinating parallel improvement loops

### Low-level: `kernel.py` event submission

For programmatic or scripted use, the installed event bus accepts direct events (run from the project root, where init installed it):

```bash
python3 context/kernel.py emit_event \
  --agent improving-skills-in-lab \
  --type lifecycle \
  --action intake-complete \
  --status success \
  --summary "target_skill — run depth configured"
```

---

## 2. The Experiment Log

Every experiment run, whether from the lab's `loop`, `plan` or `score` mode or the triple-loop orchestrator, is persisted to a durable, folder-based
log. This is the unified cross-cutting record across all evolution activity.

```
context/experiment-log/
  index.md                            ← one row per run (date, source, target, verdict)
  2026-04-25-verifier-round1.md       ← qualitative: PASS/FAIL/PARTIAL per scenario
  2026-04-25-orchestrator-skill.md    ← numeric: best_score, baseline, delta, KEEP/DISCARD
  2026-04-25-planner-0024.md          ← qualitative: workstream count, gaps identified
  2026-04-25-survey-session.md        ← mixed: friction items + north_star metric
```

**Result types agents must distinguish:**
- `numeric` — carries quantitative scores suitable for charting and trending (orchestrator)
- `qualitative` — carries pass/fail verdicts and gap analysis prose (verifier, tester, planner)
- `mixed` — carries both; check which fields are present before parsing (survey)

**Appending to the log** (run after every experiment, from the `improving-skills-in-lab` skill folder):
```bash
python3 scripts/experiment_log.py append \
  --source-type planner \          # verifier | tester | orchestrator | planner | survey
  --report tasks/todo/0024-plan.md \
  --session-id 0024 \
  --target improving-skills-in-lab \
  --triggered-by plan

python3 scripts/experiment_log.py summary
python3 scripts/experiment_log.py query FAIL
```

---

## 3. The Task as the Unit of Work (Lifecycle)

The governed task is the unit of work. A skill-improvement run is one kind of task, not the control
plane's only lifecycle:

1. **Intake:** register the task and classify its scope.
2. **Interview:** gather intent, constraints, acceptance criteria, verification, and plan-ready bullets.
3. **Draft plan:** write and persist the plan-outline-backed draft.
4. **Plan review and approval:** record review outcomes and obtain human approval before implementation.
5. **Implementation:** work in the governed worktree and record the implementation ledger.
6. **Verification:** collect deterministic receipts and check completeness.
7. **Retrospective:** record friction, map debt, follow-ups, and the improvement decision before `DONE`.

If a contract fails, the transition is rejected and the task returns to the state that can repair the missing evidence.

---

## 4. The Cold Start / Bootstrap Problem

On initial installation (before any agent-discovered skills or gotchas have accumulated), there is a cold-start bootstrap sequence.

**The Cold Start Sequence:**
1. `os-state.json` is initialized explicitly → State: `IDLE`.
2. The `os-liveness-daemon` is started and begins polling the heartbeat.
3. Seed skills are loaded (initial human-authored `.md` files, tagged `discovery_source: human_authored`).
4. **First Submission:** The user sends a known-good learning task against one of the seed skills.
5. The system runs, inevitably hits a `CIRCUIT_BREAK`, and produces the very first `discovery_source: agent_discovered` gotcha.
6. The learning flywheel is now live.

---

## 5. Day-to-Day Operation Summary

**Step 1:** Start with `running-control-plane` (intake mode) for engineering work, or `improving-skills-in-lab` for skill improvement, and describe the desired outcome.
**Step 2:** Answer the adaptive interview; after each answer, the agent updates the visible plan outline and asks the next necessary question.
**Step 3:** Review the draft plan and any independent review results; approve before implementation.
**Step 4:** Implement in the governed worktree, recording evidence as work proceeds.
**Step 5:** Run verification and retrospective gates; unresolved friction becomes a follow-up or mapped debt item.

The control plane uses the host's native planning and testing and depends on no external workflow package; see [acknowledgments](./acknowledgments.md).

> **TL;DR:** Start with the skill for your goal. End with the lab's `log` mode (`experiment_log.py append`). Everything in between is logged, gated, and traceable.
