# Agentic OS Control Plane

Agentic OS is a governed execution control plane for long-horizon AI agent workflows. It records
task state, human decisions, transition evidence, verification receipts, worktree status, and
retrospective learning in a local, portable runtime.

It works around the host agent rather than replacing it: native planning, coding, delegation, and
test capabilities remain available while Agentic OS supplies the boundaries and evidence needed
for reliable execution.

> **Scope:** Designed and tested primarily with Claude Code on macOS/Linux, but the
> delegation layer works with any CLI-accessible AI. File-system only, no external services.
> See [summary.md](./references/summary.md) for architecture and limits. See the
> [Acknowledgments](./references/acknowledgments.md) for the projects whose ideas shaped it.

---

## Is This For You?

**Good fit:**
- Multi-session projects running across days or weeks with any primary AI environment
- Workflows with multiple agents or AI tools that need to share context and build on each other's outputs
- Developers who want objective eval-gated skill improvement — measurable, repeatable, traceable
- Users who have access to more than one AI environment and want to minimize premium token spend

**Not a fit:**
- Single-session tasks (your primary AI's native auto-memory is sufficient)
- Enterprise multi-machine deployments (see [vision.md](./skills/running-control-plane/references/architecture/vision.md))
- Framework-agnostic portability requirements

---

## Two Skills

This plugin ships two skills. Neither requires the other, though the lab's evolution work registers
itself with the control plane, and the control plane's evolution cycle runs the lab's evaluator. Each
is a router: its modes were separate skills before version 2.0.0, and each mode's full workflow is a
reference loaded when that mode starts. See [the skill map](./skills/running-control-plane/references/agentic-os-skill-map.md)
and, for the comparison of the two improvement paths, `two-improvement-paths` in the lab skill.

| | `running-control-plane` | `improving-skills-in-lab` |
|---|---|---|
| Use it to | Deliver real engineering work under signed approval gates; set up and check the substrate | Measure and improve one skill or agent against evals |
| Modes | `intake`, `init`, `mode`, `health`, `signing-setup`, `simulator`, `worktree` | `plan`, `setup`, `loop`, `score`, `log`, `backport`, `memory` |
| Start with | `init` once per project, then `intake` per task | the interview in `SKILL.md` (one conversation, then `plan`) |
| State | `context/control_plane.db` | `evals/results.tsv`, improvement ledger, `context/events.jsonl` |
| Human authority | SSH-signed approval at plan, code-acceptance and closure | Human review of the lab diff before backport |
| Switch | `control_plane_mode.py enable / disable` (per clone) | install or leave out with APM `--skill` |

> **Skills are installed per client or globally.** Before relying on a skill, confirm it is installed:
> check `apm list` or your active client harness.

**First-time setup (run once):**

| Step | Do this |
|------|---------|
| 1. Install & scaffold | `"Set up an agentic OS for this project"`: runs the `init` mode of `running-control-plane` |
| 2. Human signing key | `signing-setup` mode: human only; creates the key behind the approval gates |
| 3. Probe your environment (lab) | `cli-agent` project setup (in `agent-orchestration`): builds the provider capability profile |

**After each lab session:** the `loop` mode does the retrospective, then the `memory` mode promotes learnings.

→ Full day-to-day workflow: **[usage.md](./references/usage.md)**

---

## Day-to-Day Usage

| I want to... | Use this |
|-------------|---------|
| Start any non-trivial engineering task | `running-control-plane` (intake) |
| Turn commit/push gating on or off, or check its mode | `running-control-plane` (mode): `control_plane_mode.py` |
| Check health, test a transition, pick a worktree | `running-control-plane` (health, simulator, worktree) |
| Improve a skill or agent with evals | `improving-skills-in-lab` (interview, then plan, setup, loop) |
| Score a change, see trends, backport a run, promote memory | `improving-skills-in-lab` (score, log, backport, memory) |

Full workflows: [references/usage.md](./references/usage.md).

## What's in the Box

```text
agent-agentic-os/
├── skills/
│   ├── running-control-plane/    intake, init, mode, health, signing-setup, simulator, worktree
│   └── improving-skills-in-lab/  plan, setup, loop, score, log, backport, memory
├── hooks/                        session_start.py, update_memory.py, scripts/ (Stop hooks)
├── rules/                        11 governance rules (copied into .agent/rules/ by init)
├── references/                   plugin governance and architecture (below)
└── plugin.yaml, .claude-plugin/plugin.json
```

Each skill is a router whose modes were separate skills before version 2.0.0; a mode's workflow is a
reference loaded when it starts. No agents ship with this plugin: the two former agents became
interactive flows inside their skills. Invoke a skill by name or describe the goal and let routing pick it.

### Automatic hooks (no action needed)

| Event | Script | Effect |
|-------|--------|--------|
| `SessionStart` | `session_start.py` | Surfaces memory context at the start of each session |
| `PostToolUse` | `update_memory.py` | Triggers memory promotion after significant tool use |
| `Stop` | `turn_evolution_guard.py` | Enforces map-debt and wiki updates at turn end |
| `Stop` | `post_run_metrics.py` | Captures session errors and friction events to `context/events.jsonl` |

## References

| Document | Contents |
|---------|---------|
| [usage.md](./references/usage.md) | Day-to-day workflow, experiment log close steps, append commands |
| [summary.md](./references/summary.md) | Architecture, OS analogy, three-tier lazy loading, scope and limitations |
| [how-it-works.md](./references/how-it-works.md) | Learning loop, memory, agent coordination, research, governed task lifecycle |
| [agentic-os-skill-map.md](./skills/running-control-plane/references/agentic-os-skill-map.md) | The two skills, their modes, and how they relate |
| [acknowledgments.md](./references/acknowledgments.md) | Projects whose ideas shaped Agentic OS (Superpowers, research) |

## Part of the Plugin Triad

| Plugin | Role |
|--------|------|
| `agent-extension-authoring` | Spec and factory: what ecosystem artifacts are and how to create them |
| **`agent-agentic-os`** | **Operations: gated task pipeline, eval-gated improvement loop, memory** |
| `agent-orchestration` | Execution patterns: the loop substrate used by the lab's `loop` mode |
