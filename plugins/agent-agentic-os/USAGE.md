# Agentic OS — Operational Guide & Usage
> While the architectural blueprints define the *Why* (the control-plane guarantees, state machines, and learning invariants), this document dictates the *How*. It maps out how a human or external caller interacts with the system to start the full improvement lifecycle.

---

## 1. The Human / Caller Entry Point

### Recommended: `/os-architect`

The practical entry point for any evolution activity is:

```
/os-architect
```

Describe what you want in plain language. The os-architect agent classifies your intent into one of 5 categories, audits what capabilities already exist, proposes the right evolution path (orchestrate existing / update existing / create new), and dispatches implementation work via your available CLI tools. You do not need to know which sub-agent to invoke, whether a capability exists, or how to configure a run.

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

# Set up a full triple-loop eval lab
# → triple-loop-architect agent

# Run unattended overnight iterations
# → triple-loop-orchestrator agent
```

### Low-level: kernel.py submission

For programmatic or scripted invocation, the kernel accepts direct task submissions:

```bash
# Example low-level invocation
python3 plugins/agent-agentic-os/scripts/kernel.py emit_event \
  --agent improvement-intake-agent \
  --type lifecycle \
  --action intake-complete \
  --status success \
  --summary "target_skill — run depth configured"
```

This translates directly into the `IDLE → RUNNING` state transition. The `kernel.py` acquires a lease, registers the partition as `RUNNING`, and the evaluation loop begins. Everything else — circuit breakers, gotchas, clean-room backports — is governed autonomously inside that lifecycle.

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
