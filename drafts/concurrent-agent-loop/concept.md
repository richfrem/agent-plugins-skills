# Concept: Concurrent Event-Driven Multi-Agent Loop

> Status: DRAFT - pre-experiment vision document
> Location: drafts/concurrent-agent-loop/concept.md
> Target plugin: TBD (see Plugin Home section at bottom)

---

## The Vision

Every existing agent loop pattern in this ecosystem is **sequential**:

| Pattern | Mode | Concurrency |
|---|---|---|
| Learning Loop | Solo | None |
| Red Team Review | Sequential dual-agent | One at a time |
| Dual-Loop | Sequential inner/outer | One at a time |
| Agent Swarm | Parallel BUT isolated | No shared state during exec |

None of them model what an actual operating system does: **multiple threads sharing memory, synchronizing via events, running concurrently on the same address space.**

This concept proposes **Pattern 5: Concurrent Event-Driven Loop** - agents as OS threads, not as sequential actors or isolated processes.

---

## The OS Analogy (Extended)

The existing Agentic OS draws an analogy between agent infrastructure and OS concepts. This pattern extends that analogy one level deeper:

| OS Concept | Existing Agentic OS | New: Thread Model |
|---|---|---|
| Process | Project repo | Claude session |
| Thread | (not modeled) | Claude session sharing event bus |
| Shared memory | `context/` folder | Shared `events.jsonl` + `context/` across sessions |
| Mutex | `kernel.py` atomic `os.mkdir()` lock | Same, but cross-session |
| Semaphore | (not modeled) | Counting lock in `os-state.json` |
| Message queue | `events.jsonl` (single project) | Cross-project event bus |
| Signal | CURRENT_TURN file flip (polling) | `signal` event type on bus (push) |
| Scheduler | `/loop` cron | Event-driven wakeup (no polling) |
| Process table | `agents.json` (per-project) | Global `agent-registry.json` across sessions |
| IPC | `AGENT_COMMS.md` (polling) | Pub/sub on shared event bus (push) |
| Virtual memory | Session context window | L1/L2/L3 memory tiers in agentic-os |

The critical difference: current patterns communicate by **polling** (check file, wait, check again). The thread model communicates by **subscription** (register interest, get notified on event fire).

---

## Architecture

### Layer 1: Agent Threads (Actors)

Each Claude session is a thread. A thread has:
- **Identity** - registered name in `agent-registry.json` (e.g., UPSTREAM, LAB, AUDITOR)
- **Role** - what events it handles, what state it owns
- **Context window** - its private stack (not shared)
- **Bus subscription** - which event types wake it up

Threads do NOT poll. They publish intents, and react to subscribed event types when they fire.

### Layer 2: Shared Address Space (Filesystem)

All threads share:
- `context/events.jsonl` - the event bus (append-only log)
- `context/memory.md` - long-term curated facts
- `context/memory/YYYY-MM-DD.md` - dated session logs
- `context/os-state.json` - lock state + semaphore counters
- `agent-registry.json` - who is registered + subscriptions

Each thread owns privately:
- Its Claude Code session context window
- Its CLAUDE.md hierarchy (project-local rules)

### Layer 3: Kernel (Synchronization Primitive)

`kernel.py` (already exists in agentic-os-init) is extended to:

1. **Emit** - write a structured event to `events.jsonl`
2. **Subscribe** - register interest in an event type pattern
3. **Lock** - acquire mutex via atomic `os.mkdir()`
4. **Unlock** - release mutex
5. **Signal** - emit a targeted wakeup event to a named agent
6. **Notify** - broadcast to all subscribers of an event type

### Layer 4: Event Bus Protocol

Events in `events.jsonl` follow this schema:

```jsonc
{
  "ts": "2026-03-21T14:32:01Z",
  "id": "evt_a3f9",
  "type": "task.assigned",         // dot-namespaced event type
  "from": "UPSTREAM",              // emitting agent ID
  "to": "LAB",                     // target agent ID (or "*" for broadcast)
  "payload": { ... },              // event-type-specific data
  "reply_to": "evt_a2c1"           // optional: correlates to a prior event
}
```

Event type taxonomy:

| Namespace | Types | Description |
|---|---|---|
| `task.*` | `assigned`, `started`, `complete`, `failed` | Work assignment lifecycle |
| `eval.*` | `requested`, `running`, `result` | Evaluation requests and scores |
| `memory.*` | `promoted`, `expired`, `conflict` | Memory state changes |
| `agent.*` | `registered`, `ready`, `busy`, `gone` | Agent lifecycle |
| `lock.*` | `acquired`, `released`, `contended` | Mutex state |
| `signal.*` | `wakeup`, `stop`, `suspend` | Control signals |
| `fix.*` | `proposed`, `applied`, `rejected` | Code change lifecycle |

### Layer 5: Synchronization Patterns

Three patterns for coordinating concurrent agents:

**Pattern A: Turn Signal (replaces AGENT_COMMS.md CURRENT_TURN)**
```
UPSTREAM emits: { type: "signal.wakeup", to: "LAB" }
LAB is subscribed to signal.wakeup events targeting "LAB"
LAB wakes, runs eval, emits: { type: "eval.result", from: "LAB", to: "UPSTREAM" }
UPSTREAM reacts, applies fix, emits: { type: "signal.wakeup", to: "LAB" }
```
No polling. No file flipping. Push-based.

**Pattern B: Broadcast Fan-Out (replaces swarm dispatch)**
```
ORCHESTRATOR emits: { type: "task.assigned", to: "*", payload: { task_id, partition } }
All registered agents with subscription "task.assigned" wake up
Each claims a partition via lock: kernel.lock("partition.N")
Each executes, emits: { type: "task.complete", from: "AGENT_N" }
ORCHESTRATOR counts completions (semaphore), merges when all done
```

**Pattern C: Request-Reply (replaces inner-agent CLI pipe)**
```
UPSTREAM emits: { type: "task.assigned", to: "INNER_AGENT", reply_to: null }
INNER_AGENT executes, emits: { type: "task.complete", reply_to: "evt_xyz", payload: { findings } }
UPSTREAM reads findings from bus, applies fixes
```
Same as dual-loop but event-native - no CLI pipe required if agent has bus access.

---

## What This Enables That Didn't Exist Before

1. **No polling overhead** - agents sleep until their event fires; no wasted turns checking CURRENT_TURN
2. **Concurrent execution** - UPSTREAM can be applying fix A while LAB is running eval B simultaneously
3. **Observable audit trail** - full event log shows exactly what every agent did and why, in order
4. **Deadlock detection** - kernel can detect when a lock is held too long and emit `lock.contended`
5. **Agent health monitoring** - `agent.gone` event when a session dies; other agents can reassign
6. **Cross-project scope** - event bus can span multiple project directories (UPSTREAM + LAB share one bus)
7. **Replay** - events are append-only; a new session can replay history and reconstruct current state

---

## What Needs to Be Built

### Minimal viable experiment

1. **Shared bus location** - define a canonical cross-project `events.jsonl` path (e.g., `~/Projects/.agent-bus/events.jsonl`)
2. **Emit function** - extend `kernel.py` to accept a `to` field and write to shared bus
3. **Poll-to-push bridge** - a `/loop 30s` job that reads new events from bus and checks if any target current agent
4. **UPSTREAM + LAB test** - replace AGENT_COMMS.md with bus: UPSTREAM assigns task, LAB picks it up, returns result

True push (no polling at all) requires file-system watchers (`watchdog` Python library or `fswatch` on macOS). Experiment can start with short-interval polling (10s) as a proxy.

### Full implementation (post-experiment)

1. Extend `kernel.py` with subscribe/signal/notify primitives
2. `agent-registry.json` with cross-session agent table and subscriptions
3. `os-clean-locks` extended to detect cross-session deadlocks
4. New skill: `concurrent-agent-loop` (SKILL.md with Stage 1/2/3 guidance)
5. New diagram set (see diagrams/ folder)
6. Evals for the new skill

---

## Experiments to Run

**Experiment 1: Basic signal** (low risk)
- Write a shared `events.jsonl` to `~/Projects/.agent-bus/`
- UPSTREAM emits `{ type: "signal.wakeup", to: "LAB" }` after a commit
- LAB polls bus every 30s, detects event, runs eval
- Measure: did LAB pick up the event without AGENT_COMMS.md?

**Experiment 2: Concurrent execution** (medium risk)
- UPSTREAM applies a fix to skill A
- Simultaneously, LAB runs eval on skill B
- Both write to shared bus without collision
- Measure: zero write conflicts; both tasks complete independently

**Experiment 3: Fan-out to N inner agents** (high complexity)
- UPSTREAM emits 3 task.assigned events (one per skill to audit)
- 3 Claude CLI inner agents pick up one each, execute in parallel
- UPSTREAM collects all 3 `task.complete` events, applies fixes
- Measure: wall-clock time vs. sequential dual-loop

**Experiment 4: Deadlock recovery** (stress test)
- Force a lock contention scenario
- Verify kernel detects and emits `lock.contended`
- `os-clean-locks` clears the deadlock
- Measure: system recovers without human intervention

---

## Plugin Home Recommendation

| Option | Rationale | Against |
|---|---|---|
| **New plugin: `agent-concurrent-os`** | Clean separation; owns the threading model end-to-end; can have its own kernel extensions | Another plugin to maintain |
| **Extend `agent-loops` as Pattern 5** | Fits the existing pattern catalog; orchestrator can route to it | agent-loops is loop-execution, not OS-level synchronization |
| **Extend `agent-agentic-os`** | Event bus and kernel already live here; natural home | agentic-os is single-project ops; this is multi-project/multi-session |

**Recommendation: start as extension of `agent-agentic-os`** (the kernel and bus already exist), with a new skill `concurrent-agent-loop`. If it grows beyond single-project scope, spin it out as `agent-concurrent-os`. Do NOT put it in `agent-loops` - that plugin is about execution patterns inside a loop, not about the synchronization layer between agents.

---

## Open Questions for Experiments

1. Can `events.jsonl` safely handle concurrent appends from two Claude sessions? (Needs test)
2. Is 30s polling acceptable latency for the MVP, or do we need `watchdog`?
3. Should the shared bus live in `~/Projects/.agent-bus/` or inside one of the project repos?
4. How do we handle a session dying mid-task? (Heartbeat event + timeout detection?)
5. Does the inner-agent CLI pipe (current dual-loop) become redundant once event-native request-reply works?

---

## Relation to Existing Work

- **Replaces**: `AGENT_COMMS.md` CURRENT_TURN polling protocol
- **Extends**: `kernel.py` atomic lock + emit broker
- **Complements**: `agent-swarm` (parallel but isolated -> concurrent but shared)
- **Complements**: `dual-loop` (sequential inner/outer -> event-native request-reply)
- **Uses**: `session-memory-manager` for memory promotion events
- **Uses**: `os-clean-locks` for deadlock recovery
