# Agentic OS Control Plane

Agentic OS is a governed execution control plane for long-horizon AI agent workflows. It records
task state, human decisions, transition evidence, verification receipts, worktree status, and
retrospective learning in a local, portable runtime.

It works around the host agent rather than replacing it: native planning, coding, delegation, and
test capabilities remain available while Agentic OS supplies the boundaries and evidence needed
for reliable execution.

> **Scope:** Designed and tested primarily with Claude Code on macOS/Linux, but the
> delegation layer works with any CLI-accessible AI. File-system only, no external services.
> See [SUMMARY.md](./SUMMARY.md) for architecture and limits. See the
> [Superpowers boundary and attribution](./references/superpowers-boundary-and-attribution.md)
> for the optional relationship to `obra/superpowers`.

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

## Two Paths — Pick One

This plugin holds two unrelated workflows. Neither requires the other. See
[references/two-improvement-paths.md](./references/two-improvement-paths.md) for the full comparison, and
[references/agentic-os-skill-map.md](./references/agentic-os-skill-map.md) for what every skill does,
grouped into two clusters.

| | Governed task pipeline | Improvement lab |
|---|---|---|
| Use it to | Deliver real engineering work under approval gates | Measure and improve one skill or agent against evals |
| Start with | `os-control-init` once, then `os-control-intake` per task | `os-lab-agent` (one conversation, then `os-lab-planner`) |
| State | `context/control_plane.db` | `evals/results.tsv`, improvement ledger, `context/events.jsonl` |
| Human authority | SSH-signed approval at plan, code-acceptance and closure | Human review of the lab diff before backport |
| Switch | `os-control-mode` | Select skills via APM install |

> **Skills are installed per client or globally.** The skill list below describes the plugin source.
> Before relying on a skill, confirm it is installed: check `apm list` or your active client harness.

**First-time setup (run once):**

| Step | Do this |
|------|---------|
| 1. Install & scaffold | `"Set up an agentic OS for this project"` — runs the `os-control-init` / `os-control-setup-agent` interview |
| 2. Human signing key (control plane) | `os-control-signing-setup` — human only; creates the key behind the approval gates |
| 3. Probe your environment (lab path) | `cli-agents:cli-agent` project setup — builds the provider capability profile |

**After each session (lab path):** run `os-lab-loop` for the retrospective, then
`os-lab-memory` to promote learnings, if those skills are installed.

→ Full day-to-day workflow: **[USAGE.md](./USAGE.md)**

---

## Day-to-Day Usage

| I want to... | Use this |
|-------------|---------|
| Start any non-trivial engineering task | `os-control-intake` |
| Turn the control plane (os-control-intake gating, commit/push guards) on or off, or check its mode | `os-control-mode` |
| Work in an isolated worktree based on `origin/main` | `os-control-worktree` |
| Test a control-plane transition without touching real state | `os-control-simulator` |
| Start any skill improvement or creation task | `os-lab-agent` |
| Discover which AI tools I have available | `cli-agents:cli-agent` (project setup) |
| Improve a specific skill with evals | `os-lab-agent` → describe the skill + goal |
| Run an unattended improvement loop | `os-lab-agent` → `os-lab-planner` → `os-lab-setup` → `os-lab-loop` |
| Score one change (KEEP / DISCARD) | `os-lab-scorer` |
| Review and backport a finished lab run | `os-lab-backport` |
| See eval score trends and progress charts | `os-lab-log` |
| Search experiment history | `python3 scripts/experiment_log.py query <term>` |
| Promote session learnings to long-term memory | `os-lab-memory` |
| Check system health (event log, locks, memory) | `os-control-health` |
| Fix a deadlocked agent (stale lock files) | Automatic: `kernel.py` `acquire_lock` clears stale locks; `os-control-health` reports them |
| Understand how the OS fits together | [Skill map](./references/agentic-os-skill-map.md) and [two improvement paths](./references/two-improvement-paths.md) |

---

## What's in the Box

### Agents

| Agent | Purpose |
|-------|---------|
| `os-control-setup-agent` | Conversational setup guide; wraps `os-control-init` in discovery, plan and approve phases |
| `os-lab-agent` | Front door for the skill improvement lab; one plain-language conversation (what to improve, what exists, run settings); writes `references/program.md` and `improvement/run-config.json`, then calls the `os-lab-*` skills in order |

### Skills (14)

What each skill does and how the clusters relate: [Agentic OS Skill Map](./references/agentic-os-skill-map.md).

#### Governed task pipeline (control plane)

| Skill | Purpose |
|-------|---------|
| `os-control-intake` | Intake gateway: read-only discovery, one question per turn, task registration, four-pillar `TASK_SPEC.md`, plan staging |
| `os-control-worktree` | Picks a native or portable (`.worktrees/<task-id>`) worktree based on `origin/main`; reconciles dirty state |
| `os-control-simulator` | Simulates and grades control-plane transitions on a separate simulation database and key |
| `os-control-mode` | Enables, disables or checks the control plane as one unit (member skills and rule, the two git guards, declared mode) |
| `os-control-signing-setup` | Guides the human through creating the SSH key that authorizes the plan-approval, code-acceptance and closure gates |

#### Setup & readiness

| Skill | Purpose |
|-------|---------|
| `os-control-init` | Probes, scaffolds or retrofits the OS and 3-layer memory; keeps `AGENTS.md` canonical; creates the simulation identity |
| `os-control-health` | Deterministic readiness and liveness report: signing and identity readiness, event log, hook errors, memory size and stale locks |

#### Evolution planning

| Skill | Purpose |
|-------|---------|
| `os-lab-planner` | Non-interactive planner: audits what exists, chooses orchestrate / update / create, brainstorms 2-3 options, writes the task plan and delegation prompt |

#### Eval lab & improvement loop

| Skill | Purpose |
|-------|---------|
| `os-lab-setup` | Bootstraps an isolated sibling-repo eval lab: `evals.json`, `results.tsv`, `program.md` |
| `os-lab-loop` | The only improvement loop: orient, mutate, close; sends every change to `os-lab-scorer` |
| `os-lab-scorer` | Locked KEEP / DISCARD check for one change; also a single-pass RED-GREEN-REFACTOR fix for one skill |
| `os-lab-backport` | Reviews a completed lab run and backports approved changes to master plugin sources |
| `os-lab-log` | Persistent dated log of experiment runs in `context/experiment-log/`, plus charts and trend summaries |

#### Memory

| Skill | Purpose |
|-------|---------|
| `os-lab-memory` | Deduplicates and promotes session facts to long-term memory (`context/memory.md`) |

---

### Invoking

No separate slash-command files ship with this plugin. Invoke any skill by name (for example
`/os-lab-planner`, `/os-control-init`) or describe the goal and let routing pick it.

---

### Automatic Hooks — no action needed

These fire without any user invocation.

| Event | Script | Effect |
|-------|--------|--------|
| `SessionStart` | `session_start.py` | Surfaces memory context at the start of each session |
| `PostToolUse` | `update_memory.py` | Triggers memory promotion after significant tool use |
| `Stop` | `turn_evolution_guard.py` | Enforces map-debt and wiki updates at turn end |
| `Stop` | `post_run_metrics.py` | Captures session errors and friction events to `context/events.jsonl` |

---

## How It Works

### Learning Loop

The core learning cycle: **os-lab-loop** orchestrates multi-iteration improvement
runs against a locked eval set. **os-lab-scorer** scores each mutation (KEEP/DISCARD).
**os-lab-setup** isolates each run in a sibling repo. **os-lab-backport** provides
the human review gate before any winning change reaches production.

Execution pattern delegates to [agent-orchestration Pattern 5](../agent-orchestration/skills/triple-loop-learning/)
for inner loop mechanics. agent-orchestration/ provides the loop substrate; this plugin adds the
eval gate, experiment log, and lab isolation.

→ Full detail: [references/operations/triple-loop.md](./references/operations/triple-loop.md)

### Memory System

Every session writes structured logs to `context/events.jsonl`. At end-of-session,
`os-lab-memory` deduplicates and promotes the most important facts to `context/memory.md` —
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
Lee et al., arXiv:2603.28052 (2026),
which demonstrates that code-space search over harness definitions — using an LLM proposer
gated by objective evaluation — outperforms hand-designed harnesses across benchmarks.

→ Full research library: [references/meta/research/](./references/meta/research/)

---

## Governed task lifecycle

The normal path is:

```text
Intake → Interview → Draft plan → Plan review / optional independent review
→ Human approval → Worktree implementation → Code review / recorded skip
→ Verification → Retrospective → Done
```

The interview captures plan-ready bullets and maintains a plan-outline artifact before the draft
plan is written. Every legal transition is checked against its contract and persisted in SQLite.
When evidence is incomplete, the task returns to the state that can repair the gap rather than
silently bypassing the gate.

The control plane is native to this plugin. Superpowers is optional; the exact boundary and
attribution are documented in [the companion reference](./references/superpowers-boundary-and-attribution.md).

## References

| Document | Contents |
|---------|---------|
| [USAGE.md](./USAGE.md) | Day-to-day workflow, experiment log close steps, append commands |
| [SUMMARY.md](./SUMMARY.md) | Full architecture, OS analogy, three-tier lazy loading, scope and limitations |
| [references/agentic-os-skill-map.md](./references/agentic-os-skill-map.md) | What every skill does, grouped into two clusters, and how the clusters relate |
| [references/two-improvement-paths.md](./references/two-improvement-paths.md) | Control plane vs skill improvement lab, side by side |
| [references/superpowers-boundary-and-attribution.md](./references/superpowers-boundary-and-attribution.md) | Runtime boundary, optional fallback conditions, adapted practices, and attribution |
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
| **`agent-agentic-os`** | **Operations — eval-gated improvement loop, experiment log, memory** |
| `agent-orchestration` | Execution patterns — loop substrate used by os-lab-loop |
