# Agentic OS — Provably Stable Adaptive Control System
> **v5 Architecture (State-Driven Learning Engine with Guided Intake):** The final synthesis bridging strict control-system guarantees, extreme-low-latency knowledge capture, and a conversational human-to-system boundary.

> **Implementation task:** `tasks/todo/0017-enhance-os-eval-runner-skill.md` — Workstreams A–D translate this theory into concrete agent patches.
> **Scope split:** This doc defines WHAT the system must be. 0017 defines WHERE in the agents to implement it and in what order.

---

## Executive Summary: States Output Knowledge, Fronted by Conversation

The architecture has fully matured past an experimental loop. We are designing a **State-Driven Learning Engine**. The crucial paradigm shift is that the State Machine isn't merely a traffic cop preventing race conditions—it is the structural mechanism that guarantees learning.

However, a strict control system is fragile if its inputs are malformed. To prevent configuration drift, the entire rigorous lifecycle operates behind a conversational firewall: the **Improvement Intake Agent**. The user manages intent in plain language; the intake agent translates it into strict configuration; and the control plane governs the execution.

---

## Part 1: The Human-to-System Boundary (The Intake Agent)

Before the State Machine engages, the human must invoke the loop. Instead of requiring complex CLI flags, the system dictates a conversational pre-flight layer.

**The Intake Flow:**
1. **Plain-Language Interview:** `improvement-intake-agent` intercepts the session, mapping vague user intent ("make memory faster") into formal metrics.
2. **Configuration Synthesis:** It isolates the user from the architecture, producing strict JSON inputs (`improvement/run-config.json` defining depth, models, and baselines) and `improvement/session-brief.md`.
3. **The Handoff:** Once the user approves the generated config, the Intake Agent emits an `intake-complete` event to `context/events.jsonl` and hands off via a machine-readable `HANDOFF_BLOCK`. This triggers the transition from `IDLE` to `RUNNING`. The Intake Agent completely steps back.

*This separation isolates execution from ideation, preventing the strict engine from choking on human ambiguity.*

---

## Part 2: The System Invariants (The 6 Inviolable Rules)

To prove what the system will never do, we establish 6 hard invariants. The event bus (`scripts/kernel.py`, writing to `context/events.jsonl`) enforces these directly via a **Two-Layer Protocol**: fast synchronous pre-condition gating on the hot path, backed by an asynchronous periodic invariant auditor to catch insidious state drift.

1. **Single Active Executor:** At most one `RUNNING` agent per partition_id. Enforced via directory locks in `context/.locks/`.
2. **No Unvalidated Promotion:** `PROMOTING` state can only be entered if previously `VALIDATING` AND `validation_passed == true`.
3. **Execution Freeze:** If `state == CIRCUIT_BREAK`, no new proposals may be executed. `triple-loop-orchestrator` must read `context/os-state.json` before every iteration.
4. **Memory Bounding:** `∀ memory_store : size ≤ MAX_SIZE` (Value-based compression MUST trigger before overflow).
5. **Lease Sovereignty:** Only the confirmed `lease_owner_id` may extend an active lease. `kernel.py` already checks PID aliveness + TTL expiry — the gap is the missing `heartbeat_counter` monotonicity check.
6. **Transition-Triggered Learning:** *Every state transition exiting `CIRCUIT_BREAK` or `DEGRADED` MUST output a `gotcha_candidate` or skill artifact before permitted entry into `RECOVERY`.*

---

## Part 3: The Global State Machine

A Minimal Global State Machine governs all multi-agent coordination. No node acts without reading its state; no node advances without successfully committing a transition via `kernel.py state_update`.

**The States:**
`IDLE`, `RUNNING`, `DEGRADED`, `CIRCUIT_BREAK`, `RECOVERY`, `VALIDATING`, `PROMOTING`, `FAILED`

**Crucial Arcs & Rollbacks:**
- **The Entry Arc:** Intake `HANDOFF_BLOCK` → `kernel.py state_update` → `IDLE` → `RUNNING`.
- **The Recovery Arc:** `DEGRADED | CIRCUIT_BREAK` → *produces gotcha artifact* → `RECOVERY` → `RUNNING`.
- **The Rollback Arc:** `PROMOTING` → `FAILED`. WAL compensation handler reverses partial writes, transitions back to `VALIDATING`, logs high-rarity gotcha.
- **The Failure Arc:** `FAILED` is not an absorbing state. Manual intervention or global reset → `FAILED` → `IDLE`.

---

## Part 4: Core Control Mechanics (Grounded in Current Plugin State)

### 1. Clock-Disciplined Leases (AND, Not OR)
**Mechanism:** `scripts/kernel.py` `acquire_lock()`.
- **What exists:** PID aliveness check + TTL expiry in `meta.json`. Lock directories under `context/.locks/`.
- **What's missing:** `heartbeat_counter` monotonicity — the second half of the AND that prevents a live but frozen process from holding a lease indefinitely.
- **The Rule:** A lease is valid ONLY if `(time < expiry + tolerance) AND (heartbeat_counter is monotonically increasing)`.

### 2. Scoped Circuit Breakers & Search-Space Mutation
**Mechanism:** `triple-loop-orchestrator` + `context/os-state.json`.
- **What exists:** `consecutive_discards` counter in orchestrator loop state. Stop condition at >= 4.
- **What's missing:** Formal `CIRCUIT_BREAK` state written to `context/os-state.json`, hierarchical scope escalation (`hypothesis` → `skill` → `system_halt`), and the mandatory gotcha emission that gates RECOVERY.
- **Escape Path:** Breaking at `hypothesis` scope → orchestrator mutates `copilot_proposer_prompt.md` (second-order mutation). Breaking at `skill` scope → operator review required.

### 3. Idempotency & WAL Atomicity
**Mechanism:** `scripts/kernel.py`.
- **What exists:** Directory-based spinlocks on `state_write.lock` and `events_write.lock`. Stale lock detection via PID + mtime.
- **What's missing:** True WAL pattern — write intent before executing side-effect, complete marker after. Currently `state_update` applies in-place without an intent log. If a process dies mid-write, state corruption is undetectable.
- **Target WAL:** append `INTENT: <from>→<to>` to `context/wal.log` → execute → append `COMPLETE: <from>→<to>`.

### 4. Memory Distillation & Provenance Shielding
**Mechanism:** `os-memory-manager` GC compression (`compress()`, `promote()`, `evict()`).
- **Value Function:** `value = f(frequency, severity, recency, impact, rarity, provenance)`.
- **Rarity & Provenance:** `rarity_score` (inverse global frequency) protects severe edge-cases. Memory tagged `discovery_source: agent_discovered` receives GC invulnerability shield — empirical runtime discoveries override human-authored priors.

### 5. V2 Quality Score (eval_runner.py → evaluate.py pipeline)
**Mechanism:** `scripts/eval_runner.py` → `scripts/evaluate.py`.
- **What exists:** `quality_score = (routing_accuracy × 0.7) + (heuristic_score × 0.3)` plus F1 guard. SHA256 hash guardian (`.lock.hashes`) already blocks tampered evaluators. Per-iteration trace JSON in `evals/traces/`.
- **What's missing:** V2 formula adds two new dimensions:
  - **C (Execution Efficiency):** success rate on attempt #1 with zero fumbles — not currently tracked
  - **F (Friction Reduction):** `1 - min(1, StruggleEvents / 10)` — struggle signals not emitted or counted
  - **V2 target:** `quality_score = (A × 0.4) + (H × 0.2) + (C × 0.2) + (F × 0.2)` where A=routing accuracy, H=heuristic score
- **Struggle Signals:** Tier 1 (Hard Fail, +2): retry, error, output mismatch. Tier 2 (Soft Signal, +1): exploratory commands (ls, find, cat, --help).

### 6. Clean-Room Cross-Persona Backporting
**Mechanism:** `os-eval-backport` validation gate.
- **Environment Isolation:** `eval_env != validation_env != production_env`.
- **Cross-Persona Validation:** Secondary LLM persona (e.g., Gemini evaluating Copilot's work) disrupts confirmation bias before backport is approved.

---

## Part 5: Self-Healing Patterns Abstracted from Browser-Harness

> Reference: `temp/repos/browser-harness/` — ~592 lines of Python. Self-healing CDP harness where the agent edits the harness itself mid-task. The harness has 70+ domain skills and 17 interaction skills. Five patterns abstract to the agentic OS.

### Pattern 1 — Self-Editing Execution Layer
**Browser-harness:** When `upload_file()` is missing from `helpers.py`, the agent writes it mid-task and continues. The harness is its own mutation target.

**Applied here:** The `triple-loop-orchestrator` Step B.1 already permits mutating `copilot_proposer_prompt.md` when the loop stalls. This must become a first-class circuit-break escape path — when `consecutive_discards >= 4`, the orchestrator MUST propose a second-order mutation (proposer prompt or `references/domain-patterns/<type>.md`) before escalating scope. This mirrors browser-harness: extend the tool mid-use, not after.

### Pattern 2 — Contribute-Back Reflex
**Browser-harness:** "If figuring something out cost you a few steps, the next run should not pay the same tax." Agent-authored domain skills, filed automatically on discovery.

**Applied here:** Every `CIRCUIT_BREAK` exit must produce a structured `## Gotchas` entry — not just a log in `gotchas.md` (staging area) but a direct write to the target skill's `SKILL.md` under `## Gotchas`. The `os-eval-backport` step is the publish gate. A gotcha that stays in `gotchas.md` and never lands in the SKILL.md is invisible to the next run and violates the contribute-back reflex.

### Pattern 3 — Thin Core, Extensible Domain Layer
**Browser-harness:** `run.py` is 36 lines. `helpers.py` is ~195 lines. Domain knowledge in `domain-skills/<site>/`. Interaction mechanics in `interaction-skills/`. Core never grows; skills do.

**Applied here:** `evaluate.py` + `eval_runner.py` = the thin core (already correct at ~500 lines total). Domain-specific mutation strategies for different skill types (routing skills, Python scripts, config files) should live in `references/domain-patterns/<skill-type>.md`. The orchestrator searches these before inventing a hypothesis — mirroring "search domain-skills/ first." This layer does not exist yet.

### Pattern 4 — Gotchas Embedded in the Artifact
**Browser-harness:** `## Gotchas` section lives directly in `SKILL.md`. Field-tested failures are part of the skill, not an external log.

**Applied here:** High-value circuit-break gotchas must be backported INTO the target skill's `SKILL.md` under `## Gotchas`. The `gotchas.md` file is staging only; backport is mandatory. The `triple-loop-orchestrator` Phase 2 Morning Handoff must include a `## Gotchas` patch as a required output alongside the progress chart.

### Pattern 5 — Search Patterns Before Inventing
**Browser-harness:** "After cloning the repo, search `domain-skills/` first for the domain you are working on before inventing a new approach."

**Applied here:** At Phase 1 Step A (failure classification), the orchestrator must check `references/domain-patterns/<skill-type>.md` before constructing a hypothesis. Known successful mutation patterns for that skill category should be the default proposal; unknown territory triggers a fresh hypothesis. The orchestrator notes whether the hypothesis was pattern-sourced or novel — novel ones that KEEP become new domain-pattern entries.

---

## Part 6: Sprint Plan (Status vs. Reality)

> Canonical operations reference: `plugins/agent-agentic-os/references/operations/triple-loop.md`

### ✅ Already Implemented
- Directory-based lock system with PID + TTL leases (`kernel.py`)
- Event emission to `context/events.jsonl` (`kernel.py emit_event`)
- State reads/writes with spinlock (`kernel.py state_update`)
- SHA256 hash guardian preventing tampered evaluators (`evaluate.py`)
- Per-iteration trace JSON files in `evals/traces/` (`evaluate.py`)
- Multi-metric KEEP logic: quality_score, f1, precision, recall, heuristic (`evaluate.py`)
- Auto-revert on DISCARD via `git checkout -- .` (`evaluate.py`)
- Agent registry validation — only permitted agents emit events (`kernel.py`)
- Second-order mutation target: `copilot_proposer_prompt.md` (`triple-loop-orchestrator` Step B.1)

### 🔥 P0 — Agent-Layer Gaps (Workstreams A–D in 0017)
1. **CIRCUIT_BREAK state in `context/os-state.json`:** `consecutive_discards >= 4` must write `circuit_break_scope: hypothesis` to state, not just stop the loop.
2. **Invariant 6 — Gotcha Gate:** Exiting CIRCUIT_BREAK requires a `## Gotchas` entry written to target SKILL.md before RECOVERY is permitted.
3. **WAL logging:** `context/wal.log` — intent written before each state transition, complete marker after. Compensation handler on startup reads incomplete WAL entries.
4. **V2 Score (C + F dimensions):** `eval_runner.py` adds struggle signal counting. C = attempt-1 success rate. F = `1 - min(1, StruggleEvents / 10)`.
5. **Intake agent → machine-readable HANDOFF_BLOCK:** `improvement-intake-agent` emits kernel event to `context/events.jsonl` and outputs `HANDOFF_BLOCK` code fence, not prose handoff.
6. **Architect reads run-config.json:** `triple-loop-architect` Phase 0 checks `improvement/run-config.json` first; only prompts user if not found.
7. **Domain pattern layer:** `references/domain-patterns/<skill-type>.md` — orchestrator searches before proposing.

### 🟠 P1 — Control Plane Gaps
1. **Heartbeat counter monotonicity:** Add to `kernel.py` lease check — heartbeat counter must increment between TTL checks.
2. **Cross-persona validation gate:** Before KEEP, if `cross_persona_validation: true` in run-config, pipe proposed SKILL.md through secondary model judge.
3. **Backport gotchas mandatory:** `os-eval-backport` Phase 2 must include SKILL.md `## Gotchas` patch; gotchas.md alone is insufficient.

### 🟡 P2 & 🟢 P3 — Evolution & Visibility
- **Anti-Gamed Memory GC:** Full `os-memory-manager` Value Function (rarity + provenance shielding).
- **Event Bus Lineage:** `idempotency_keys` and `parent_event_id` in `context/events.jsonl` entries.
- **Friction-to-Skill Generation:** Clustered friction events (3+ same cause) trigger `create-skill` protocol automatically.
- **Domain patterns seeded from KEEPs:** Novel hypotheses that KEEP become new entries in `references/domain-patterns/`.
