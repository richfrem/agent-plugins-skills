# Agentic OS — Provably Stable Adaptive Control System
> **v5 Architecture (State-Driven Learning Engine with Guided Intake):** The final synthesis bridging strict control-system guarantees, extreme-low-latency knowledge capture, and a conversational human-to-system boundary.

---

## Executive Summary: States Output Knowledge, Fronted by Conversation

The architecture has fully matured past an experimental loop. We are designing a **State-Driven Learning Engine**. The crucial paradigm shift is that the State Machine isn't merely a traffic cop preventing race conditions—it is the structural mechanism that guarantees learning.

However, a strict control system is fragile if its inputs are malformed. To prevent configuration drift, the entire rigorous lifecycle operates behind a conversational firewall: the **Improvement Intake Agent**. The user manages intent in plain language; the intake agent translates it into strict configuration; and the control plane governs the execution.

---

## Part 1: The Human-to-System Boundary (The Intake Agent)

Before the State Machine engages, the human must invoke the loop. Instead of requiring complex CLI flags, the system dictates a conversational pre-flight layer.

**The Intake Flow:**
1. **Plain-Language Interview:** `improvement-intake-agent` intercepts the session, mapping vague user intent ("make memory faster") into formal metrics.
2. **Configuration Synthesis:** It isolates the user from the architecture, producing strict JSON inputs (`run-config.json` defining depth, models, and baselines) and a `session-brief.md` context document.
3. **The Handoff:** Once the user approves the generated config, the Intake Agent hands off to the orchestrator. This triggers the transition from `IDLE` to `RUNNING`. The Intake Agent completely steps back.

*This separation isolates execution from ideation, preventing the strict engine from choking on human ambiguity.*

---

## Part 2: The System Invariants (The 6 Inviolable Rules)

To prove what the system will never do, we establish 6 hard invariants. The event bus (`kernel.py`) enforces these directly via a **Two-Layer Protocol**: fast synchronous pre-condition gating on the hot path, backed by an asynchronous periodic invariant auditor to catch any insidious state drift.

1. **Single Active Executor:** At most one `RUNNING` agent per partition_id.
2. **No Unvalidated Promotion:** `PROMOTING` state can only be entered if previously `VALIDATING` AND `validation_passed == true`.
3. **Execution Freeze:** If `state == CIRCUIT_BREAK`, no new proposals may be executed.
4. **Memory Bounding:** `∀ memory_store : size ≤ MAX_SIZE` (Value-based compression MUST trigger before overflow).
5. **Lease Sovereignty:** Only the confirmed `lease_owner_id` may extend an active lease.
6. **Transition-Triggered Learning:** *Every state transition exiting `CIRCUIT_BREAK` or `DEGRADED` MUST output a `gotcha_candidate` or skill artifact before permitted entry into `RECOVERY`.*

---

## Part 3: The Global State Machine

A Minimal Global State Machine governs all multi-agent coordination. No node acts without reading its state; no node advances without successfully committing a transition.

**The States:**
`IDLE`, `RUNNING`, `DEGRADED`, `CIRCUIT_BREAK`, `RECOVERY`, `VALIDATING`, `PROMOTING`, `FAILED`

**Crucial Arcs & Rollbacks:**
- **The Entry Arc:** Intake configurations generate initial `submit()` commands → `IDLE` → `RUNNING`.
- **The Recovery Arc:** `DEGRADED | CIRCUIT_BREAK` → *produces artifact* → `RECOVERY` → `RUNNING`.
- **The Rollback Arc:** `PROMOTING` → `FAILED`. If code passes clean-room validation but fails during production-state merge (e.g., git collision), the WAL compensation handler cleanly reverses partial writes, transitions back to `VALIDATING`, and logs a high-rarity gotcha.
- **The Failure Arc:** `FAILED` is not an absorbing state. Manual intervention or a specialized global reset sequence transitions `FAILED` → `IDLE`.

---

## Part 4: Core Control Mechanics

### 1. Clock-Disciplined Leases (AND, Not OR)
**The Mechanism:** The `os-liveness-daemon`.
- **Drift Protection:** Distributed clocks and process pauses make pure timestamps dangerous. 
- **The Rule:** A lease is valid ONLY if `(time < expiry + tolerance) AND (heartbeat_counter is monotonically increasing)`. 
- An `OR` validation would allow an entirely frozen process with an advancing wall clock to hold a lease forever. Using `AND` ensures we measure actual execution progress.

### 2. Scoped Circuit Breakers & Search-Space Mutation
**The Mechanism:** Semantic oscillation detection in `os-eval-runner`.
- **Scope Limits:** Breakers trip hierarchically: `hypothesis` → `skill` → `system_halt`. This scopes the blast radius of interventions.
- **Escape Path:** Breaking at the `hypothesis` scope mandates an immediate search-space mutation constraint (e.g., *invert assumption*, *change abstraction level*) effectively halting the failure loop by forcing a new coordinate in the solution space.

### 3. Idempotency & WAL Atomicity
**The Mechanism:** `kernel.py` event routing.
- **Idempotency:** A `hash(action + inputs)` key drops duplicate requests stemming from daemon restarts.
- **Atomicity:** To prevent half-applied state corruption, `kernel.py` enforces a Write-Ahead Log (WAL). Log intent → Execute side-effect → Complete. If the sequence breaks, a compensation handler rolls it back.

### 4. Memory Distillation & Provenance Shielding
**The Mechanism:** `os-memory-manager` GC compression (`compress()`, `promote()`, `evict()`).
- **The Value Function:** `value = f(frequency, severity, recency, impact, rarity, provenance)`.
- **Rarity & Provenance:** Agents naturally "game" frequency checks. `rarity_score` (inverse global frequency) protects severe edge-cases. Concurrently, memory tagged with `discovery_source: agent_discovered` receives a massive GC invulnerability shield, as empirical runtime discoveries strictly override human-authored priors.

### 5. Clean-Room Cross-Persona Backporting
**The Mechanism:** `os-eval-backport` validation gate.
- **Environment Isolation:** Evaluation success means nothing if caching drove the result. Validation must execute in `eval_env != validation_env != production_env`.
- **Cross-Persona Validation:** The validation pass **must** utilize a secondary LLM persona (e.g., Gemini evaluating Copilot's work) to violently disrupt confirmation bias. 

---

## Part 5: Final Executable Sprint Plan

### 🔥 True P0 (Intake, Architecture & Governance)
1. **The Human Gateway:** Activate the `improvement-intake-agent` to ensure all system runs start with validated, plain-language sourced configuration.
2. **Global State Machine + Defined Arcs:** Implement the formal state map in `os-state.json`. Define the Rollback (`PROMOTING`->`FAILED`) and Recovery Arcs safely natively in the orchestration path.
3. **Two-Layer Invariant Validation:** Inject the 6 invariant checks into `kernel.py` (fast synchronous precondition AND slow asynchronous background auditor).
4. **Atomic Execution Layer:** Add WAL (write-ahead log) intent markers to state transitions to prevent partial application.
5. **Clock-Disciplined Leases:** Implement the `os-liveness-daemon` validating leases strictly with `time AND heartbeat` progression.

### 🟠 P1 (Causal Learning & Safety)
1. **Transition-Triggered Gotchas (Invariant 6):** Enforce the rule that exiting a broken state natively triggers `write-gotcha`. This structurally guarantees learning.
2. **Clean-Room Cross-Persona Backporting:** Enforce the distinct environment boundary and mandate the secondary persona check in `os-eval-backport`.
3. **Mid-Loop Heartbeat Integration:** The steady pulse confirming the executing environment remains healthy between executions.

### 🟡 P2 & 🟢 P3 (Evolution & Visibility)
- **Anti-Gamed Memory GC:** Implement the full `os-memory-manager` Value Function (rarity + provenance shielding).
- **Event Bus Lineage:** Implement `idempotency_keys` and `parent_event_id` tracking into telemetry to track race-condition causality.
- **Friction-to-Skill Generation:** Route clustered `missing-skill` friction directly into `create-skill` protocols.
