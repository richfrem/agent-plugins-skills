# Experiment Plan: Concurrent Event-Driven Loop

> Run these in order. Each builds on the previous. Stop if an experiment fails and diagnose before continuing.

---

## Experiment 1: Shared Bus Write (Baseline)

**Goal**: Verify two Claude sessions can append to the same `events.jsonl` without corruption.

**Setup**:
```bash
mkdir -p ~/Projects/.agent-bus
touch ~/Projects/.agent-bus/events.jsonl
```

**Steps**:
1. UPSTREAM session appends 10 events rapidly via `kernel.py emit()`
2. LAB session appends 10 events simultaneously (use `/loop 5s` to simulate)
3. After 30 seconds, check event count and JSON validity

**Success criteria**:
- `wc -l ~/Projects/.agent-bus/events.jsonl` == 20
- `python3 -c "import json; [json.loads(l) for l in open('~/Projects/.agent-bus/events.jsonl')]"` exits 0
- No duplicate event IDs

**Failure mode**: File corruption from concurrent writes. Fix: kernel.py must use `fcntl.flock()` for append atomicity.

---

## Experiment 2: Turn Signal (Replace AGENT_COMMS.md)

**Goal**: UPSTREAM signals LAB via bus, LAB picks it up without polling AGENT_COMMS.md.

**Steps**:
1. LAB starts `/loop 30s` that reads last N events from bus and checks if any `signal.wakeup` target `LAB`
2. UPSTREAM emits `{ type: "signal.wakeup", to: "LAB", payload: { assignment: "run eval on user-story-capture" } }`
3. Observe: does LAB pick up the event within 30 seconds and start the eval?

**Success criteria**:
- LAB reacts within 1 poll cycle (30s) without human intervention
- LAB emits `eval.result` event back to bus
- UPSTREAM detects `eval.result` on its next poll

**Measurement**: Compare latency vs. AGENT_COMMS.md flip (was ~1-2 min with missed turns)

---

## Experiment 3: Concurrent Execution (No Collision)

**Goal**: UPSTREAM edits skill A while LAB evals skill B simultaneously. No race condition.

**Steps**:
1. UPSTREAM locks `skill.user-story-capture` via `os.mkdir("context/locks/skill.user-story-capture")`
2. LAB starts eval on `skill.exploration-handoff` (different skill, no lock needed)
3. Both run for ~2 minutes
4. UPSTREAM commits, unlocks
5. Check: did LAB's eval score match expected? Any file corruption?

**Success criteria**:
- Both tasks complete without interfering
- `events.jsonl` shows interleaved events from both agents, correct order
- No `lock.contended` events emitted

---

## Experiment 4: Fan-Out to 3 Inner Agents

**Goal**: UPSTREAM dispatches 3 skill audits in parallel to 3 Claude CLI inner agents.

**Steps**:
```bash
# UPSTREAM emits 3 task.assigned events (simulated with 3 CLI calls in parallel)
cat plugins/.../user-story-capture/SKILL.md | claude -p "<audit prompt>" --dangerously-skip-permissions > /tmp/audit1.md &
cat plugins/.../business-workflow-doc/SKILL.md | claude -p "<audit prompt>" --dangerously-skip-permissions > /tmp/audit2.md &
cat plugins/.../exploration-optimizer/SKILL.md | claude -p "<audit prompt>" --dangerously-skip-permissions > /tmp/audit3.md &
wait
```

**Steps**:
1. Run all 3 in background
2. Measure wall-clock time vs. sequential
3. Read all 3 outputs, apply valid fixes

**Success criteria**:
- All 3 complete successfully
- Wall-clock time < 2x single audit time (parallelism benefit demonstrated)
- No output corruption

---

## Experiment 5: Heartbeat + Dead Agent Recovery

**Goal**: Simulate an agent dying mid-lock; verify kernel detects and clears.

**Steps**:
1. UPSTREAM acquires `lock(skill.X)`, then kill the session
2. LAB tries to acquire the same lock, blocks
3. Heartbeat monitor detects UPSTREAM stopped emitting `agent.heartbeat`
4. `os-clean-locks` clears the stale lock
5. LAB acquires lock, proceeds

**Success criteria**:
- Lock cleared within 2x heartbeat interval without human intervention
- `lock.contended` + `lock.released` events in bus
- LAB unblocks

---

## Decision Gate

After Experiments 1-3 pass:
- Formalize the event schema
- Write `kernel.py` extensions
- Draft `concurrent-agent-loop` SKILL.md
- Add to `agent-agentic-os` or spin out as new plugin

After Experiment 4 passes:
- Update `dual-loop` skill to offer event-native path as alternative to CLI pipe

After Experiment 5 passes:
- The pattern is production-ready for multi-agent projects
