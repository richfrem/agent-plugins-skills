# Agentic OS Architecture

The Agentic OS is not a binary - it is a directory structure and behavioral convention that turns an LLM into a persistent, self-managing entity.

## Core Components

**1. Kernel (`CLAUDE.md`)** - Root system instruction file. Defines core identity, non-negotiable standards, and delegates deeper knowledge down the directory tree.

**2. RAM & Persistence (`context/`)** - `context/memory/`: dated markdown files storing daily events parsed by `SessionStart` / `PostToolUse` hooks via `update_memory.py`. `context/memory.md`: long-term curated memory promoted from daily logs. `context/status.md`: active register with current tasks, blockers, and loop state (see `status-file-spec.md`).

**3. Standard Library (`skills/`)** - Reusable procedural modules defined in YAML+Markdown (`SKILL.md`). Define triggers and execution paths. Extend agent capabilities without bloated context.

**4. Processes (`agents/`)** - Standalone sub-agents optimized for narrow execution (e.g. `agentic-os-setup`, `Triple-Loop Retrospective`).

---

## Initialization Architecture

Init uses the Sub-Agent Orchestration pattern (`agentic-os-setup.md`) to isolate scaffolding complexity from the primary context window.

**State Transitions:**

1. **Discovery** - Agent interviews the user to understand the project environment (Python, Node, generic).
2. **Merge vs Overwrite** - If `CLAUDE.md` exists, agent MUST use safe append strategy. Destructive overwrite of pre-existing prompt logic is strictly forbidden.
3. **Hook Wiring** - `hooks.json` mapping is mandatory. `SessionStart` and `PostToolUse` must fire `update_memory.py` to bridge stateless sessions. Init is responsible for clean wiring.

---

## Memory Architecture

The Session Memory Manager acts as the garbage collector and long-term storage controller.

**Memory Tiers:**
- **L1 (Cache)** - Current active context window. Highly transient.
- **L2 (Daily Logs)** - `context/memory/YYYY-MM-DD.md`. Populated asynchronously by `hooks/update_memory.py` on file-write events. Semi-transient.
- **L3 (Permanent Record)** - `context/memory.md`. Curated facts. Permanent.

**Conflict Resolution (Dementia Guard):** No blind appends to L3. If a promoted fact contradicts an existing fact in `memory.md`, the agent will experience conflicting rules. Architecture mandates a `Read` scan of L3 before appending, pausing for user intervention if a conflict is detected.
