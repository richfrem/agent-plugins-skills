---
concept: triple-loop-learning-system---architecture-overview
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-improvement-loop/assets/architecture-overview.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.162003+00:00
cluster: kernel
content_hash: c75ac261dca25bae
---

# Triple-Loop Learning System - Architecture Overview

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Triple-Loop Learning System - Architecture Overview

> Core Architecture: Agents as OS Threads with Shared Event Bus
> Status: v2 - unified Triple-Loop architecture (Claude 4.6, Grok 4, GPT-5, Gemini 2.5 Pro)
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
  agent-agentic-os/          <- plugin source (SKILL.md, scripts, kernel.py)
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
| ORCHESTRATOR | Triple-Loop Meta-Coordinator. Evaluates trends, drives Double-loop/Single-loop, manages memory. | Persistent |
| PEER_AGENT | Runs objective evaluations independently (`evaluate.py`). Single-Loop Gate. | Persistent |
| INNER_AGENT | Short-lived executor (Strategic Planner). Emits proposed file patches via CLI (Gemini/Copilot). | Ephemeral |
| WORKER | Stateless fire-and-forget unit. No locks, no registry entry. | Ephemeral |

Note: INNER_AGENT and WORKER are now distinct. INNER_AGENT acquires locks and emits validated
events. WORKER does pure computation and returns ou

*(content truncated)*

## See Also

- [[triple-loop-learning-system-outer-orchestrator-inner-execution]]
- [[triple-loop-learning-meta-learning-system]]
- [[triple-loop-learning-system-outer-orchestrator-inner-execution]]
- [[triple-loop-learning-system-outer-orchestrator-inner-execution]]
- [[triple-loop-learning-meta-learning-system]]
- [[learning-loop---detailed-phase-instructions]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-improvement-loop/assets/architecture-overview.md`
- **Indexed:** 2026-04-17T06:42:10.162003+00:00
