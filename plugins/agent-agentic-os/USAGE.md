# Agentic OS — Control-Plane Usage Guide

> The architectural references define the *Why* (control-plane guarantees, state machines, and learning invariants); this guide describes the *How* for a governed task from intake through retrospective.

---

## 1. The Human / Caller Entry Point

### Recommended: `/os-architect`

The practical entry point for any evolution activity is:

```
/os-architect
```

Describe what you want in plain language. The os-architect agent classifies your intent, audits existing capabilities, proposes an evolution path, and keeps the work inside the control-plane lifecycle. You do not need to know which internal state, contract, or helper to invoke.

**Intent categories os-architect handles:**
1. Pattern Abstraction — applying a new way of working to existing skills/agents
2. Research Application — incorporating techniques from papers or external research
3. Lab Setup / Improvement Loop — running eval iterations on an existing skill
4. Capability Gap Fill — creating a new skill or agent that doesn't exist yet
5. Multi-Loop Orchestration — coordinating parallel improvement loops

### Advanced: Direct sub-agent invocation

For users who know exactly what they want, sub-agents can be invoked directly:

```bash
# Configure a skill improvement run directly
# → improvement-intake-agent

# Verify that os-architect actually caused evolution (post-run)
# → os-evolution-verifier skill

# Query or summarize experiment history
# → os-experiment-log skill
```

### Low-level: kernel.py submission

For programmatic or scripted invocation, the kernel accepts direct task submissions:

```bash
python3 plugins/agent-agentic-os/scripts/kernel.py emit_event \
  --agent improvement-intake-agent \
  --type lifecycle \
  --action intake-complete \
  --status success \
  --summary "target_skill — run depth configured"
```

---

## 2. The Experiment Log

Every experiment run — whether from os-evolution-verifier, os-architect-tester,
triple-loop-orchestrator, or os-evolution-planner — is persisted to a durable, folder-based
log. This is the unified cross-cutting record across all evolution activity.

```
context/experiment-log/
  index.md                            ← one row per run (date, source, target, verdict)
  2026-04-25-verifier-round1.md       ← qualitative: PASS/FAIL/PARTIAL per scenario
  2026-04-25-orchestrator-skill.md    ← numeric: best_score, baseline, delta, KEEP/DISCARD
  2026-04-25-tester-os-architect.md   ← qualitative: AC-1–4 per scenario
  2026-04-25-planner-0024.md          ← qualitative: workstream count, gaps identified
  2026-04-25-survey-session.md        ← mixed: friction items + north_star metric
```

**Result types agents must distinguish:**
- `numeric` — carries quantitative scores suitable for charting and trending (orchestrator)
- `qualitative` — carries pass/fail verdicts and gap analysis prose (verifier, tester, planner)
- `mixed` — carries both; check which fields are present before parsing (survey)

**Appending to the log** (run after every experiment):
```bash
python3 plugins/agent-agentic-os/scripts/experiment_log.py append \
  --source-type verifier \          # verifier | tester | orchestrator | planner | survey
  --report temp/os-evolution-verifier/test-report.md \
  --session-id 2026-04-25-round1 \
  --target os-architect \
  --triggered-by os-evolution-verifier

python3 plugins/agent-agentic-os/scripts/experiment_log.py summary
python3 plugins/agent-agentic-os/scripts/experiment_log.py query FAIL
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

**Step 1:** Start with `/os-architect` or `work-intake` and describe the desired outcome.
**Step 2:** Answer the adaptive interview; after each answer, the agent updates the visible plan outline and asks the next necessary question.
**Step 3:** Review the draft plan and any independent review results; approve before implementation.
**Step 4:** Implement in the governed worktree, recording evidence as work proceeds.
**Step 5:** Run verification and retrospective gates; unresolved friction becomes a follow-up or mapped debt item.

The control plane may use native host planning and testing. Superpowers is an optional fallback, not a required installation. See [the boundary and attribution reference](./references/superpowers-boundary-and-attribution.md).

> **TL;DR:** Start with `/os-architect`. End with `os-experiment-log append`. Everything in between is logged, gated, and traceable.
