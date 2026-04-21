# Agentic OS — Operational Guide & Usage
> While the architectural blueprints define the *Why* (the control-plane guarantees, state machines, and learning invariants), this document dictates the *How*. It maps out how a human or external caller interacts with the system to start the full improvement lifecycle.

---

## 1. The Human / Caller Entry Point
The Agentic OS is a "Control-Plane as a Service." The caller does not need to manage the State Machine directly. The practical entry point is a task submission command that kicks off the sequence:

```bash
# Example invocation
os-runner submit \
  --skill "refactor-memory-gc" \
  --partition "os-memory-manager" \
  --hypothesis "rarity_score should weight inverse global frequency"
```

**What this does:**
This command translates directly into the `IDLE → RUNNING` state transition. 
A caller submits a scoped task targeting a specific skill, assigns it to a partition ID, and supplies an initial hypothesis. The `kernel.py` acquires a lease, registers the partition as `RUNNING`, and the evaluation loop begins. Everything else—circuit breakers, gotchas, clean-room backports—is governed autonomously inside that lifecycle.

---

## 2. The Skill as the Unit of Work (Lifecycle)
The "Skill" is the atomic unit the improvement lifecycle operates on. It is the durable knowledge artifact that a run both consumes as prior context, and produces as output.

The lifecycle for a single submitted skill run is entirely governed by the State Machine:

1. **Submission:** `submit(skill, hypothesis)`
2. **Start:** Kernel acquires lease → State: `RUNNING`
3. **Execution:** `os-eval-runner` executes the hypothesis against the skill.
4. **[Success Path]** → State: `VALIDATING`
    - `os-eval-backport` executes clean-room isolation + cross-persona validation check.
    - If validated → State: `PROMOTING`
    - Skill updated in target directory → State: `RUNNING/IDLE`
5. **[Failure Path]** → State: `CIRCUIT_BREAK`
    - **Invariant 6 enforces learning:** The agent natively outputs a `write-gotcha` or a new handler skill artifact.
    - The search space is mutated (e.g., *invert assumption*).
    - State: `RECOVERY` → `RUNNING` (system automatically retries with the new mutated hypothesis).

---

## 3. The Cold Start / Bootstrap Problem
On initial installation (before any agent-discovered skills or gotchas have accumulated), there is a cold-start bootstrap sequence. The improvement lifecycle assumes a prior skill already exists to improve. 

**The Cold Start Sequence:**
1. `os-state.json` is initialized explicitly → State: `IDLE`.
2. The `os-liveness-daemon` is started and begins polling the heartbeat.
3. Seed skills are loaded. (These are the initial human-authored `.md` files present in the repo, tagged implicitly with `discovery_source: human_authored`).
4. **First Submission:** The user sends a known-good learning task against one of the seed skills.
5. The system runs, inevitably hits a `CIRCUIT_BREAK`, and produces the very first `discovery_source: agent_discovered` gotcha.
6. The learning flywheel is now live. Those acquired, high-rarity discoveries automatically become the prior-context for all subsequent cycles.

---

## 4. Day-to-Day Operation Summary
If you are picking up this plugin today to run a full improvement cycle:

**Step 1:** Ensure `os-liveness-daemon` is running and `os-state.json` shows `IDLE`.
**Step 2:** Execute a submission targeting the desired skill with your starting hypothesis.
**Step 3:** Observe the telemetry. The first few laps will likely trip the `CIRCUIT_BREAK` path on novel hypothesis failures. *This is correct behavior.* This is exactly when your first agent-discovered gotchas are written.
**Step 4:** A hypothesis that eventually clears and hits `VALIDATING` will automatically enter the clean-room backport gate. If the cross-persona check passes, it is promoted and the run closes safely.
**Step 5:** The newly promoted skill now possesses dense `agent_discovered` memory entries. The next run will consume these, enforcing much smarter subsequent hypothesis generation.

> **TL;DR:** The practical entry point is extraordinarily simple: `submit(skill, hypothesis)`. The architectural complexity guarantees what happens between that submission and its final promotion.
