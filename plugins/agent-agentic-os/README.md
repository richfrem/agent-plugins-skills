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
[references/two-improvement-paths.md](./references/two-improvement-paths.md) for the full comparison.

| | Governed task pipeline | Improvement lab |
|---|---|---|
| Use it to | Deliver real engineering work under approval gates | Measure and improve one skill or agent against evals |
| Start with | `os-init` once, then `work-intake` per task | `/os-architect` (Category 3, lab setup) |
| State | `context/control_plane.db` | `evals/results.tsv`, improvement ledger, `context/events.jsonl` |
| Human authority | SSH-signed approval at plan, code-acceptance and closure | Human review of the lab diff before backport |
| Switch | `os-control-plane-mode` | Enable its skills in `.agents/ownership/` |

> **Skills are installed per project.** The skill list below describes the plugin source. A project
> may install only some of it (`.agents/ownership/agent-agentic-os.json`, `should_install`). Before
> relying on a skill, confirm it is installed: `ls .agents/skills/<name>`.

**First-time setup (run once):**

| Step | Do this |
|------|---------|
| 1. Install & scaffold | `"Set up an agentic OS for this project"` — runs the `os-init` / `agentic-os-setup` interview |
| 2. Human signing key (control plane) | `os-signing-setup` — human only; creates the key behind the approval gates |
| 3. Probe your environment (lab path) | `/os-architect` → "probe my environment" — saves a delegation strategy profile |

**After each session (lab path):** run `os-improvement-loop` for the retrospective, then
`os-memory-manager` to promote learnings, if those skills are installed.

→ Full day-to-day workflow: **[USAGE.md](./USAGE.md)**

---

## Day-to-Day Usage

| I want to... | Use this |
|-------------|---------|
| Start any non-trivial engineering task | `work-intake` |
| Turn the control plane (work-intake gating, commit/push guards) on or off, or check its mode | `os-control-plane-mode` |
| Work in an isolated worktree based on `origin/main` | `worktree-manager` |
| Test a control-plane transition without touching real state | `transition-simulator` |
| Start any skill improvement or creation task | `/os-architect` |
| Discover which AI tools I have available | `/os-architect` → "probe my environment" |
| Improve a specific skill with evals | `/os-architect` → describe the skill + goal |
| Run an unattended improvement loop | `/os-architect` → "improve X skill with a lab" → `os-improvement-loop` |
| See eval score trends and progress charts | `os-improvement-report` |
| Search experiment history | `python3 scripts/experiment_log.py query <term>` |
| Promote session learnings to long-term memory | `os-memory-manager` |
| Check system health (event log, locks, memory) | `os-health-check` |
| Fix a deadlocked agent (stale lock files) | `os-clean-locks` |
| Verify os-architect still works after a change | `os-architect-tester` agent |
| Get a full explanation of how the OS works | `os-guide` |

---

## What's in the Box

### Agents

| Agent | Purpose |
|-------|---------|
| `agentic-os-setup` | Conversational setup guide; wraps `os-init` in discovery, plan and approve phases |
| `os-architect` (`agents/os-architect-agent.md`) | Front-door agent for ecosystem evolution; classifies intent into six categories and routes |
| `improvement-intake-agent` | Plain-language intake for a skill improvement run; writes `improvement/run-config.json` and `session-brief.md` (called by `os-architect` for Category 3) |
| `os-architect-tester` | Validates `os-architect` against pre-scripted scenario transcripts; run after any change to it |

### Skills (27)

#### Governed task pipeline (control plane)

| Skill | Purpose |
|-------|---------|
| `work-intake` | Intake gateway: read-only discovery, one question per turn, task registration, four-pillar `TASK_SPEC.md`, plan staging |
| `worktree-manager` | Picks a native or portable (`.worktrees/<task-id>`) worktree based on `origin/main`; reconciles dirty state |
| `transition-simulator` | Simulates and grades control-plane transitions on a separate simulation database and key |
| `os-control-plane-mode` | Enables, disables or checks the control plane as one unit (member skills and rule, the two git guards, declared mode) |
| `os-signing-setup` | Guides the human through creating the SSH key that authorizes the plan-approval, code-acceptance and closure gates |

#### Setup, environment & guidance

| Skill | Purpose |
|-------|---------|
| `os-init` | Probes, scaffolds or retrofits the OS and 3-layer memory; keeps `AGENTS.md` canonical; creates the simulation identity |
| `os-environment-probe` | Discovers available AI environments; writes the delegation profile to `context/memory/environment.md` |
| `os-guide` | Full OS reference: layers, interactions, patterns |

#### Evolution planning

| Skill | Purpose |
|-------|---------|
| `os-architect` | SME-facing front door: classifies intent, audits capabilities, proposes orchestrate / update / create, dispatches |
| `os-evolution-planner` | Brainstorms 2-3 approaches with the cheapest model, then writes the task plan and delegation prompt |
| `os-evolution-verifier` | Checks that `os-architect` produced real artifacts; PASS / PARTIAL / FAIL with evidence |
| `self-evolution` | Deterministic 6-node graph controller for self-evolution: worktree isolation, verifier sovereignty, Layer 2 persistence |
| `repository-improvement` | Turns friction-cluster hotspot reports into systemic refactoring proposals for human review (Tier 3 friction) |

#### Eval lab & improvement loop

| Skill | Purpose |
|-------|---------|
| `os-eval-lab-setup` | Bootstraps an isolated sibling-repo eval lab: `evals.json`, `results.tsv`, `program.md` |
| `os-eval-runner` | Stateless eval engine; scores a proposed change against locked `evals.json`; KEEP / DISCARD |
| `os-improvement-loop` | Five-stage improvement cycle: orient, execute, verify, decide, close |
| `os-skill-improvement` | RED-GREEN-REFACTOR cycle for one skill whose routing accuracy or score is low |
| `os-eval-backport` | Reviews a completed lab run and backports approved changes to master plugin sources |
| `os-experiment-log` | Persistent dated log of experiment runs in `context/experiment-log/` |
| `os-improvement-report` | Charts and trend summaries across improvement cycles |
| `evo-smoketest` | Fixture skill (temperature conversion) for the evolution end-to-end smoke test; not a user capability |

#### Memory & observability

| Skill | Purpose |
|-------|---------|
| `os-memory-manager` | Deduplicates and promotes session facts to long-term memory (`context/memory.md`) |
| `os-health-check` | Deterministic liveness report over the event log, locks and memory |
| `os-clean-locks` | Removes stale lock files left by crashed agents |

#### Audit & quality

| Skill | Purpose |
|-------|---------|
| `critical-auditor` | Full-system adversarial audit of plugins, skills, specs and orchestration |
| `optimize-agent-instructions` | Audits and rewrites the canonical `AGENTS.md`; reports legacy mirrors |
| `todo-check` | Scans a file for TODOs and debt markers |

---

### Invoking

No separate slash-command files ship with this plugin. Invoke any skill by name (for example
`/os-architect`, `/os-init`) or describe the goal and let routing pick it.

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

The core learning cycle: **os-improvement-loop** orchestrates multi-iteration improvement
runs against a locked eval set. **os-eval-runner** scores each mutation (KEEP/DISCARD).
**os-eval-lab-setup** isolates each run in a sibling repo. **os-eval-backport** provides
the human review gate before any winning change reaches production.

Execution pattern delegates to [agent-orchestration Pattern 5](../agent-orchestration/skills/triple-loop-learning/)
for inner loop mechanics. agent-orchestration/ provides the loop substrate; this plugin adds the
eval gate, experiment log, and lab isolation.

→ Full detail: [references/operations/triple-loop.md](./references/operations/triple-loop.md)

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
| `agent-orchestration` | Execution patterns — loop substrate used by os-improvement-loop |
