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
| Run an unattended overnight eval loop | `triple-loop-architect` agent → then `triple-loop-orchestrator` |
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
| `os-architect` | `/os-architect` or agent dispatch | Classifies intent, audits capabilities, brainstorms options using cheapest available model, dispatches work across Copilot CLI, Gemini CLI, or primary AI subagent — whichever fits your environment profile |
| `os-environment-probe` | via os-architect or directly | Discovers available AI tools (Copilot CLI, Gemini CLI, Cursor), probes each, writes `context/memory/environment.md` with cheapest-model-per-task delegation strategy |

---

### Agents

**Invoke directly:**

| Agent | Purpose |
|-------|---------|
| `agentic-os-setup` | Conversational setup guide — scaffolds memory, hooks, and CLAUDE.md hierarchy for a new project |
| `os-health-check` | System diagnostics — inspects event log, memory state, lock status |
| `triple-loop-architect` | Interactive setup for a full skill eval lab (Triple-Loop Learning System) |
| `triple-loop-orchestrator` | Unattended overnight improvement orchestrator — oversees autonomous INNER loop iterations |

**Internal (called by os-architect — do not invoke directly):**

| Agent | Called for |
|-------|-----------|
| `improvement-intake-agent` | Category 3 (Lab Setup) requests — configures a skill improvement run |
| `os-architect-tester` | Validation after any change to os-architect — runs 8 pre-scripted scenario transcripts |

---

### Skills

#### Setup & Environment

| Skill | Purpose |
|-------|---------|
| `os-init` | Scaffolds the OS environment — called by the setup agent or `/os-init` |
| `os-environment-probe` | Discovers AI environments; writes delegation strategy to `context/memory/environment.md` |
| `os-guide` | Full OS reference — layers, interactions, patterns. Trigger: "explain agentic os" |

#### Planning & Evolution

| Skill | Purpose |
|-------|---------|
| `os-architect` | SME-facing front-door skill — invokes the os-architect interview flow |
| `os-evolution-planner` | Brainstorms 2-3 approach options (cheapest model), presents for selection, writes task plan + Copilot CLI delegation prompt |
| `os-evolution-verifier` | Verifies os-architect causes actual evolution — simulation dispatch, artifact checks, PASS/PARTIAL/FAIL with evidence |
| `os-experiment-log` | Persistent folder-based log of all experiment runs; `append / query / summary`; `result_type: numeric\|qualitative\|mixed` |

#### Evaluation & Improvement

| Skill | Purpose |
|-------|---------|
| `os-eval-lab-setup` | Bootstraps an isolated sibling-repo eval lab for safe iteration |
| `os-eval-runner` | Stateless eval engine — scores proposed skill patches against locked `evals.json`; KEEP/DISCARD gate |
| `os-eval-backport` | Reviews completed lab run; backports approved changes to master plugin sources |
| `os-improvement-loop` | Orchestrates the full eval → mutate → re-eval cycle (Triple-Loop Pattern 5) |
| `os-skill-improvement` | RED-GREEN-REFACTOR cycle for a single skill — no full lab required |
| `os-improvement-report` | Generates improvement charts and trend data from eval history |

#### Memory & Observability

| Skill | Purpose |
|-------|---------|
| `os-memory-manager` | Deduplicates and promotes session facts to long-term memory (`context/memory.md`) |

#### Utilities

| Skill | Purpose |
|-------|---------|
| `optimize-agent-instructions` | Audits and rewrites AI agent instruction files (CLAUDE.md, GEMINI.md, copilot-instructions.md) in any repo |
| `os-clean-locks` | Removes stale lock files from `context/.locks/` to resolve deadlocked agents |
| `todo-check` | Audits files for TODO comments and unresolved technical debt markers |

---

### Slash Commands

| Command | What it does |
|---------|-------------|
| `/os-init` | Bootstrap the project — triggers `agentic-os-setup` conversational architect |
| `/os-loop` | Run full OS improvement cycle: eval, emit friction events, trigger Triple-Loop Retrospective if threshold crossed |
| `/os-memory` | Force memory garbage collection and conflict resolution on the tiered memory system |

---

### Automatic Hooks — no action needed

These fire on every session without any user invocation.

| Event | Script | Effect |
|-------|--------|--------|
| `SessionStart` | `session_start.py` | Surfaces memory context at the start of each session |
| `PostToolUse` | `update_memory.py` | Triggers memory promotion after significant tool use |
| `Stop` | `post_run_metrics.py` | Captures session errors and friction events to `context/events.jsonl` |

---

## How It Works

### Triple-Loop Learning System

Three nested loops run over your skills: the **outer Triple-Loop** (meta-learning orchestrator)
manages strategy and targets; the **middle Double-Loop** (os-skill-improvement) formulates
hypotheses and patches; the **inner Single-Loop** (os-eval-runner) tests each patch against
locked evals and keeps or discards it. The eval gate defeats Goodhart's Law — no subjective
testing, no test registry re-use.

→ Full detail: [references/operations/triple-loop.md](./references/operations/triple-loop.md)
→ Diagram: [assets/diagrams/triple-loop-learning-system.mmd](./assets/diagrams/triple-loop-learning-system.mmd)

### Memory System

Every session writes structured logs to `context/events.jsonl`. At end-of-session,
`os-memory-manager` deduplicates and promotes the most important facts to `context/memory.md` —
a curated long-term store that bootstraps every future session. Dedup IDs and size limits
prevent drift and contradiction over hundreds of sessions.

→ Diagram: [assets/diagrams/agentic-os-memory-subsystem.mmd](./assets/diagrams/agentic-os-memory-subsystem.mmd)

### Agent Coordination

Agents share state through `context/events.jsonl` and `context/.locks/` — not tight
coupling. Outer supervisors set goals and review results; inner workers execute and signal
completion in the shared log. Background agents surface findings in the next foreground
session through promoted memory.

→ Full architecture: **[SUMMARY.md](./SUMMARY.md)**

---

## Research Foundation

The improvement loop implements the [Karpathy 3-file autoresearch pattern](./references/meta/research/karpathy-autoresearch-3-file-eval.md)
(eval / program / results). The architecture is independently validated by
[Lee et al., arXiv:2603.28052 (2026)](./references/meta/research/meta-harness-lee-2026.md),
which demonstrates that code-space search over harness definitions — using an LLM proposer
gated by objective evaluation — outperforms hand-designed harnesses across benchmarks.

→ Full research library: [references/meta/research/](./references/meta/research/)

---

## References

| Document | Contents |
|---------|---------|
| [USAGE.md](./USAGE.md) | Day-to-day workflow, experiment log close steps, append commands |
| [SUMMARY.md](./SUMMARY.md) | Full architecture, OS analogy, three-tier lazy loading, scope and limitations |
| [references/architecture/](./references/architecture/) | Canonical file structure, CLAUDE.md hierarchy, context folder patterns |
| [references/operations/](./references/operations/) | Triple-loop strategy, operating protocols, loop scheduler, skill optimization guide |
| [references/memory/](./references/memory/) | Memory specs, hygiene guide, promotion guide, metrics |
| [references/testing/](./references/testing/) | Test registry protocol, test scenario seeds |
| [references/meta/research/](./references/meta/research/) | Karpathy autoresearch, Lee 2026 Meta-Harness, Koubaa 2025, Sharma 2026 |
| [CHANGELOG.md](./CHANGELOG.md) | Version history |

---

## Part of the Plugin Triad

| Plugin | Role |
|--------|------|
| `agent-scaffolders` | Spec + Factory — what ecosystem artifacts are and how to create them |
| **`agent-agentic-os`** | **Operations — how to run and continuously improve the environment** |
