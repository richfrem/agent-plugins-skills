---
concept: agent-harness-learning-layer
source: plugin-code
source_file: agent-agentic-os/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.686689+00:00
cluster: skill
content_hash: 3dd4b6dd3580ea9a
---

# Agent Harness & Learning Layer

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Agent Harness & Learning Layer

Persistent memory and continuous self-improvement for long-horizon AI agent workflows.
Structured memory survives and scales across hundreds of sessions; an eval-gated improvement
loop evolves your skills and agents automatically — no subjective "mental" testing.

Runs in Claude Code but orchestrates across whatever AI environments you have available:
Copilot CLI (free GPT-4o-mini tier), Gemini CLI, Cursor — using the cheapest model for
brainstorming and the right model for each job. A discipline layer, not a replacement.

> **Scope:** Designed and tested primarily with Claude Code on macOS/Linux, but the
> delegation layer works with any CLI-accessible AI. File-system only, no external services.
> See [SUMMARY.md](./SUMMARY.md) for scope, known limitations, and enterprise roadmap.

---

## Is This For You?

**Good fit:**
- Multi-session projects running across days or weeks with any primary AI environment
- Workflows with multiple agents or AI tools that need to share context and build on each other's outputs
- Developers who want objective eval-gated skill improvement — measurable, repeatable, traceable
- Users who have access to more than one AI environment and want to minimize premium token spend

**Not a fit:**
- Single-session tasks (your primary AI's native auto-memory is sufficient)
- Enterprise multi-machine deployments (see `references/architecture/vision.md`)
- Framework-agnostic portability requirements

---

## 🚀 Start Here

> **Every evolution task starts with one command:**
>
> ```
> /os-architect
> ```
>
> Describe what you want in plain language. os-architect classifies your intent,
> audits what already exists, brainstorms approach options, and dispatches work.
> You do not need to know which internal loop, lab, or intake agent to invoke.

**First-time setup (run once):**

| Step | Do this |
|------|---------|
| 1. Install & scaffold | `"Set up an agentic OS for this project"` — runs the setup interview |
| 2. Probe your environment | `/os-architect` → "probe my environment" — detects Copilot CLI, Gemini CLI, Cursor and saves a delegation strategy profile |
| 3. Start evolving | `/os-architect` → describe your goal |

**After each session:**
```bash
/os-loop      # improvement retrospective — evals, friction events, Triple-Loop trigger
/os-memory    # memory promotion (if /os-loop didn't fire it)
```

→ Full day-to-day workflow: **[USAGE.md](./USAGE.md)**

---

## Day-to-Day Usage

| I want to... | Use this |
|-------------|---------|
| Start any improvement or creation task | `/os-architect` |
| Discover which AI tools I have available | `/os-architect` → "probe my environment" |
| Propose hypotheses and design experiments for a problem | `/os-architect` → "explore why X fails" or "generate hypotheses for Y" |
| Improve a specific skill with evals | `/os-architect` → describe the skill + goal |
| Run an unattended improvement loop | `/os-architect` → "improve X skill with a lab" → os-improvement-loop |
| See eval score trends and progress charts | `os-improvement-report` skill |
| Search experiment history (what was tested, what changed) | `python3 scripts/experiment_log.py query <term>` |
| See a summary of all experiment results | `python3 scripts/experiment_log.py summary` |
| Promote session learnings to long-term memory | `/os-memory` |
| Check system health (event log, locks, memory) | `os-health-check` agent |
| Fix a deadlocked agent (stale lock files) | `os-clean-locks` skill |
| Verify os-architect still works after a change | `os-architect-tester` agent |
| Get a full explanation of how the OS works | `os-guide` skill |
| Audit files for unresolved TODOs | `todo-check` skill |

---

## What's in the Box

### Front Door

Start here for all evolution and improvement work. Everything else is called by these.

| | Invoke as | Purpose |
|-|-----------|---------|
| `os-architect` | `/os-architect` or agent dispatch | Classifies intent, audits capabilities, brainstorms o

*(content truncated)*

## See Also

- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[agent-agentic-os-hooks]]
- [[agent-bridge]]
- [[agent-loops-execution-primitives]]
- [[agent-loops-hooks]]
- [[agent-scaffolders-spec-factory]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/README.md`
- **Indexed:** 2026-04-27T05:21:03.686689+00:00
