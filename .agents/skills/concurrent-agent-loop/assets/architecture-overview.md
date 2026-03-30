# Concurrent Agent Loop - Architecture Overview

> Pattern 5: Agents as OS Threads with Shared Event Bus
> Status: v2 - revised after 4-model red team review (Claude 4.6, Grok 4, GPT-5, Gemini 2.5 Pro)
> Plugin home: `agent-agentic-os` (kernel + bus already here)
> Updated: 2026-03-22 (deployment topology added, AGENT_COMMS.md retired)

---

## What This Is

A concurrent agent coordination pattern that treats Claude sessions as OS threads sharing a
filesystem address space. Multiple agents execute simultaneously, coordinate via a shared event
bus, and synchronize using atomic kernel primitives.

The filesystem IS the OS. No external daemon, no message broker, no polling file.
Proven more efficient than file-flip coordination: 2.17s round-trip vs AGENT_COMMS.md
turn-based protocol. The kernel spinlock provides atomic writes; cursor-based reads give
near-push semantics with no background process.

---

## Deployment Topology (Two-Project Setup)

This OS spans two repos by design. Source code and runtime context are deliberately separated.

```
UPSTREAM repo: agent-plugins-skills
  plugins/agent-agentic-os/          <- plugin source (SKILL.md, scripts, kernel.py)
  ORCHESTRATOR session runs here     <- owns git, applies KEEP changes, manages versions

LAB repo: spec-kitty-improvements
  context/                           <- ALL runtime state lives here
    events.jsonl                     <- shared event bus
    os-state.json                    <- task registry, counters, lock metadata
    agents.json                      <- permitted agent registry
    memory/improvement-ledger.md     <- longitudinal improvement record
    memory/tests/                    <- test scenarios and registry
    memory/retrospectives/           <- agent self-assessment surveys
    memory/loop-reports/             <- per-cycle loop reports
  INNER_AGENT / PEER_AGENT sessions run here (child Claude CLI)
```

**CLAUDE_PROJECT_DIR must always point at LAB**, never UPSTREAM.
Runtime context written to UPSTREAM is a deployment error.

### Why two repos

- Plugin source (UPSTREAM) is committed and versioned. Changes are reviewed and gated.
- Runtime context (LAB) is ephemeral session state. It accumulates, gets promoted to memory,
  and is never committed to the plugin repo.
- Keeping them separate prevents runtime noise from polluting the source commit history.

---

## AGENT_COMMS.md is Retired

The turn-based file-flip protocol (`spec-kitty-improvements/AGENT_COMMS.md`) has been
superseded by this OS. The kernel event bus provides:

- Structured, typed events vs free-form markdown log entries
- Atomic writes with spinlock vs manual "only one agent edits at a time" discipline
- Cursor-based reads (no re-reading entire file) vs full-file parse each poll
- 2.17s round-trip latency (validated E2) vs ~60s turn-based polling cadence
- Correlation IDs for multi-cycle sessions vs linear log ordering

**Do not use AGENT_COMMS.md for coordination.** If you find a reference to it in a skill or
workflow doc, it is outdated. All inter-agent coordination uses `emit_event` and `read_events`
via `kernel.py`.

## Red Team Review Summary (4 models)

Four AI reviewers (Claude 4.6, Grok 4, GPT-5, Gemini 2.5 Pro) independently reviewed v30.
All four agreed on the following issues. This architecture revision addresses all of them.

---

## Roles

| Role | Description | Lifecycle |
|---|---|---|
| ORCHESTRATOR | Outer loop coordinator. Assigns tasks, applies fixes, owns git, drives cycle. | Persistent |
| PEER_AGENT | Long-lived co-session. Runs evals, syncs skills, reports results. | Persistent |
| INNER_AGENT | Registered short-lived executor. Owns locks and identity. Exits after task.complete. | Ephemeral |
| WORKER | Stateless fire-and-forget unit. No locks, no registry entry, no identity. (GPT-5 distinction) | Ephemeral |

Note: INNER_AGENT and WORKER are now distinct. INNER_AGENT acquires locks and emits validated
events. WORKER does pure computation and returns output via stdout/file - not via the bus.

---

## Shared Address Space

**Bus location: project-scoped by default** (all 4 reviewers flagged global bus as isolation failure)

```
{project_root}/context/
  events.jsonl          <- L1 event bus (append-only, kernel-gated)
  os-state.json         <- semaphore counters, lock holders, task registry
  agents.json           <- permit list + guest token store
  .locks/               <- per-resource mutex dirs (lease-based, not timeout-based)
  agents/
    <id>.cursor         <- per-agent read offset (cursor-based consumption)
    <id>.inbox.jsonl    <- per-agent targeted event inbox (push-lite)
```

For explicit cross-project coordination only:
```
~/.agent-bus/context/   <- opt-in global bus (requires AGENT_BUS_GLOBAL=true)
```

---

## Key Architecture Changes from v30

### 1. Lease-Based Locking (replaces static timeout)

All 4 reviewers flagged the 1800s static timeout as unsafe for concurrent use.

Each lock dir now contains a metadata file:
```json
{
  "agent_id": "INNER_AGENT_1",
  "pid": 48291,
  "acquired_at": "2026-03-21T14:32:01Z",
  "lease_expires_at": "2026-03-21T14:34:01Z",
  "ttl_seconds": 120
}
```

Kernel checks `os.kill(pid, 0)` on any lock access - if process is dead, lock is stolen
immediately regardless of timeout. Short-lived agents use short TTLs (60-120s).
General `acquire_lock` now accepts `--ttl` argument (Gemini).

### 2. Kernel Blocking Wait (replaces LLM polling)

Gemini's strongest proposal: instead of LLM polling bus every 2-30s, the kernel does
the blocking internally. LLM invokes one tool call and gets result when event fires.

```bash
# LLM calls this once - Python blocks until event detected or timeout
kernel.py wait_for_event \
  --to PEER_AGENT \
  --action signal.wakeup \
  --timeout 60
# Returns immediately when matching event found, or after timeout
```

This eliminates poll-loop context consumption. The LLM is not involved during the wait.

### 3. Cursor-Based Event Consumption (replaces full-bus scan)

GPT-5 and Grok both flagged O(N) full scan as unscalable. Each agent now tracks its
read offset in `context/agents/<id>.cursor`. Kernel provides:

```bash
kernel.py read_events --agent PEER_AGENT --since-cursor
# Returns only new events since last read, updates cursor atomically
```

Combined with `wait_for_event`, this gives near-push semantics with no external daemon.

### 4. Per-Agent Inboxes (push-lite delivery)

Grok's recommendation: kernel routes targeted events to `context/agents/<id>/inbox.jsonl`
at emit time. Agents read only their own inbox - no filtering needed, no bus noise.

```bash
kernel.py deliver_event --to PEER_AGENT --event-json '{"type":"signal.wakeup",...}'
# Atomically appends to context/agents/PEER_AGENT/inbox.jsonl
```

Broadcast events still go to the main `events.jsonl`.

### 5. Extended Event Schema

All 4 reviewers required `to`, `reply_to`, `correlation_id`. Gemini added `partition_id`
for fan-out. Full schema:

```json
{
  "id": "evt_a3f9c2",
  "time": "2026-03-21T14:32:01Z",
  "agent": "ORCHESTRATOR",
  "type": "task.assigned",
  "action": "audit_skill",
  "to": "INNER_AGENT_1",
  "reply_to": null,
  "correlation_id": "job_skill_audit_20260321",
  "partition_id": "skill-A",
  "status": "success",
  "summary": "audit user-story-capture"
}
```

### 6. Atomic Task Claiming for Fan-Out

GPT-5 identified the race: two agents reading before lock acquisition both think a
partition is free. Fix: `claim_task` is a single atomic kernel operation:

```bash
kernel.py claim_task --task-id job_001 --partition skill-A --agent INNER_AGENT_1
# Acquires lock AND records claim in os-state.json task registry in one critical section
# Returns success or fail - never partial
```

Task registry in `os-state.json`:
```json
{
  "tasks": {
    "job_001": {
      "expected": 3,
      "completed": 0,
      "partitions": {
        "skill-A": {"claimed_by": "INNER_AGENT_1", "status": "running"},
        "skill-B": {"claimed_by": null, "status": "pending"},
        "skill-C": {"claimed_by": null, "status": "pending"}
      }
    }
  }
}
```

ORCHESTRATOR waits until `completed == expected`, not by counting bus events.

### 7. INNER_AGENT Registration - Guest Token Model

Gemini proposed cryptographic delegation. Practical implementation:

ORCHESTRATOR generates a short-lived token before spawning INNER_AGENT:
```bash
kernel.py issue_guest_token --ttl 300 --permissions "emit:task.complete,acquire_lock"
# Returns: AGENTIC_GUEST_TOKEN=tok_xyz123
```

INNER_AGENT passes token with every kernel call:
```bash
kernel.py emit_event --agent INNER_AGENT_1 --guest-token tok_xyz123 ...
```

Kernel validates token against `agents.json` guest token store (not static registry).
Tokens expire, cannot be reused after TTL, and are scoped to declared permissions.

Immediate bridge (before token system is built): add `"INNER_AGENT"` as a shared
identity to `agents.json`. Loses per-agent auditability but unblocks usage now.

### 8. ORCHESTRATOR Failover (SPOF fix)

Gemini identified: ORCHESTRATOR crash during fan-out = deadlock. INNER_AGENTs complete
and exit, merge never happens.

Fix: PEER_AGENT monitors ORCHESTRATOR heartbeat. If ORCHESTRATOR misses 2 consecutive
heartbeats during an active job, PEER_AGENT can claim orchestrator duties:

```bash
kernel.py claim_role --role ORCHESTRATOR --correlation-id job_001
# Acquires ORCHESTRATOR role lock, assumes pending merges
```

Each agent emits `agent.heartbeat` every 30s. Absence = presumed dead.

### 9. Project-Scoped Bus as Default

All 4 reviewers flagged `~/.agent-bus/` as wrong default. Cross-project contamination
is a real isolation failure. Default is now `${CLAUDE_PROJECT_DIR}/context/`.

To opt into cross-project bus: set `AGENT_BUS_GLOBAL=~/.agent-bus` explicitly.

---

## Kernel Command Set (revised)

| Command | Purpose | Status |
|---|---|---|
| `emit_event` | Validated append to bus | Exists |
| `acquire_lock --ttl N` | Lease-based mutex with per-lock TTL | Needs --ttl arg |
| `release_lock` | Release mutex | Exists |
| `state_update` | Write key to os-state.json | Exists |
| `state_increment` | Atomic counter increment (semaphore) | Needs adding |
| `wait_for_event` | Blocking wait until matching event fires | Needs adding |
| `read_events` | Cursor-based read, returns only new events | Needs adding |
| `deliver_event` | Route targeted event to agent inbox | Needs adding |
| `claim_task` | Atomic lock + registry claim in one op | Needs adding |
| `issue_guest_token` | Generate scoped TTL token for INNER_AGENT | Needs adding |
| `claim_role` | Acquire a named role for failover | Needs adding |

---

## What Remains in Draft vs. Validated

| Component | Status |
|---|---|
| Concurrent bus writes (kernel spinlock) | Validated E1: 30 events, zero corruption |
| Turn signal round-trip latency | Validated E2: 2.17s, 28x faster than file-flip |
| Lease-based locking | Architecture defined, kernel changes needed |
| Blocking wait_for_event | Architecture defined, kernel changes needed |
| Cursor-based consumption | Architecture defined, kernel changes needed |
| Per-agent inboxes | Architecture defined, kernel changes needed |
| Guest token model | Architecture defined, kernel changes needed |
| Atomic claim_task | Architecture defined, kernel changes needed |
| ORCHESTRATOR failover | Architecture defined, protocol needed |

---

## Issues Not Yet Addressed (Backlog)

From Gemini: `eval_runner.py` keyword stuffing incentive. The learning loop will game its
own eval metric by stuffing keywords. eval_runner must either use a real LLM router or
penalize word count. This is a `skill-improvement-eval` issue, not a concurrent-loop issue,
but it undermines the whole self-improvement pipeline. Tracked separately.

From Claude: `update_memory.py` kernel fallback impersonates system agent. Tracked in
agentic-os security backlog.

From all: empty `results.tsv` baselines for session-memory-manager, agentic-os-guide,
agentic-os-init. P0 before self-improvement loop is meaningful.

---

## Positioning vs Existing Patterns (unchanged)

| Pattern | Mode | Shared State | Concurrency |
|---|---|---|---|
| Learning Loop (P1) | Solo | None | None |
| Red Team Review (P2) | Sequential dual | None | None |
| Dual-Loop (P3) | Sequential inner/outer | None | None |
| Agent Swarm (P4) | Parallel isolated | None | Parallel but isolated |
| **Concurrent Loop (P5)** | **Concurrent** | **Yes - shared bus + memory** | **True concurrent with sync** |
