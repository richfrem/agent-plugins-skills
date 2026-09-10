# Agentic OS Control Plane

<!-- ECOSYSTEM_STATS_START -->**Current ecosystem:** 10 plugins · 141 skills · 46 sub-agents<!-- ECOSYSTEM_STATS_END -->

**A governed execution harness for AI coding agents.** This repository lets Claude Code, Codex,
GitHub Copilot, Agy, and compatible tools use their native planning, coding, orchestration, and
worktree capabilities while the **Agentic OS Control Plane** provides the boundaries around that
work: recorded decisions, human authority, deterministic checks, isolated execution, verification,
and continuous improvement.

It is not just a skills catalog. It is a portable system for making agent-driven engineering work
more reliable without attempting to replace the model's reasoning.

## What the control plane does

For governed work, the control plane persists task state in local SQLite and permits only valid,
evidenced transitions. It makes the important decisions visible and durable:

- **Understand first:** intake and adaptive interview questions establish scope, acceptance criteria,
  verification, and whether a request is trivial or standard.
- **Plan deliberately:** plan artifacts have a recorded identity; review is either performed or
  explicitly skipped with a reason.
- **Keep people in charge:** implementation requires a real human approval gate. Reset, escalation,
  and recovery paths are also governed.
- **Execute safely:** implementation normally happens in an isolated worktree, with recorded
  exceptions rather than silent bypasses.
- **Verify outcomes:** focused checks, repository-wide test receipts, policy checks, and completion
  evidence are required before a task can close.
- **Learn continuously:** retrospectives, friction records, evaluation loops, map debt, and durable
  playbooks turn failures and successful patterns into improvements.

The normal lifecycle is:

```text
Intake → Interview → Draft plan → Plan review / optional independent review
→ Human approval → Worktree implementation → Code review / recorded skip
→ Verification → Retrospective → Done
```

Tasks can return to interview, planning, review, implementation, escalation, or reset when evidence
calls for it. See the canonical [happy-path diagram](docs/diagrams/control-plane-pipeline-happy-path.mermaid)
and [complete state machine](docs/diagrams/control-plane-pipeline.mermaid).

## Governance around native capability

The control plane governs **before, around, and after** agent execution. It does not prescribe a
model's chain of thought or force every runtime into one implementation style. A capable native
agent may create plans, manage worktrees, delegate, review, or execute in its best available way;
the harness establishes the task boundaries, required evidence, human decisions, and exit criteria.

This separation matters: frontier capabilities can improve without weakening approvals,
deterministic verification, or the audit trail.

## Start here

### I want governed agent work in my repository

Install the plugins, then initialize and check the Agentic OS substrate:

```bash
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills
```

Then ask your agent to set up Agentic OS for the repository, or use `os-init`, followed by
`os-health-check`. Start a governed task through `interview-spec` when the work needs a
plan-to-completion lifecycle. [Installation and onboarding](INSTALL.md) has platform-specific and
local-development instructions.

### I want one capability or plugin

Plugins are independently installable. Choose only the parts you need—the control plane is not a
runtime dependency of standalone skills. Use the interactive installer above or install a specific
plugin from `plugins/<plugin-name>`; see [INSTALL.md](INSTALL.md).

### I am contributing to this repository

Clone the repository, install local plugin sources, and follow [START_HERE.md](START_HERE.md) to
initialize the local control-plane substrate. Read [architecture.md](architecture.md) and the
binding [ADRs](docs/ADRs/) before changing plugin structure, scripts, or shared resources.

## The system at a glance

| Layer | Responsibility | Primary components |
| --- | --- | --- |
| Control plane | State transitions, human gates, policy checks, verification receipts, retrospectives | [`agent-agentic-os`](plugins/agent-agentic-os/README.md) |
| Native runtime integration | Discover available CLIs, select suitable models, and delegate without hard runtime coupling | [`cli-agents`](plugins/cli-agents/README.md) |
| Execution patterns | Composable loops, graph execution, swarms, adversarial review | [`agent-orchestration`](plugins/agent-orchestration/README.md) |
| Learning and memory | Filesystem-native memory, retrieval options, experiment and improvement loops | [`agent-memory`](plugins/agent-memory/README.md), `agent-agentic-os` |
| Plugin lifecycle | Create, audit, install, synchronize, and maintain reusable plugins | [`agent-scaffolders`](plugins/agent-scaffolders/README.md), [`plugin-manager`](plugins/plugin-manager/README.md) |

## Continuous improvement is part of the product

The control plane follows a practical improvement discipline inspired by Karpathy-style
autoresearch: make a bounded change, measure it with an objective verifier, keep or discard it,
and preserve the learning either way. This repository applies that discipline at multiple levels:

- task retrospectives identify friction, follow-ups, and issue-worthy work;
- evaluation loops use explicit KEEP/DISCARD outcomes instead of subjective claims;
- map debt and evolution logs preserve unresolved constraints and confirmed lessons;
- architecture, policy, diagram, and test contracts keep the documented system aligned with the
  executable one.

The goal is compounding reliability—not blind autonomy. Human approval remains required where
authority matters, and evidence is more important than an agent saying that work is complete.

## Plugin map

The repository is an upstream source monorepo. `plugins/` is authoritative; installers materialize
self-contained runtime copies into `.agents/`.

| Plugin | Use it for |
| --- | --- |
| [`agent-agentic-os`](plugins/agent-agentic-os/README.md) | Governed task lifecycle, health checks, evaluation, continuous improvement, and repository evolution |
| [`cli-agents`](plugins/cli-agents/README.md) | CLI-agent discovery, delegation, model catalogs, and project/runtime setup |
| [`agent-orchestration`](plugins/agent-orchestration/README.md) | Reusable orchestration and multi-agent execution primitives |
| [`agent-memory`](plugins/agent-memory/README.md) | Filesystem memory, RLM, and vector-data capabilities |
| [`agent-scaffolders`](plugins/agent-scaffolders/README.md) | Creating, auditing, packaging, and maintaining plugins and skills |
| [`dev-utils`](plugins/dev-utils/README.md) | Repository utilities: issues, worktrees, symlinks, context, documentation, and more |
| [`exploration-cycle-plugin`](plugins/exploration-cycle-plugin/README.md) | Discovery, requirements, prototyping, and handoff into engineering work |
| [`obsidian-wiki-engine`](plugins/obsidian-wiki-engine/README.md) | Obsidian vault, graph, and wiki workflows |
| [`dependency-management`](plugins/dependency-management/README.md) | Python dependency and environment management |
| [`plugin-manager`](plugins/plugin-manager/README.md) | Installing, synchronizing, and maintaining the plugin ecosystem |

For individual skills, agents, supported surfaces, and version detail, use each plugin's README
and manifest rather than treating this landing page as a volatile inventory.

## Architectural commitments

- **Portable source, self-contained installs:** individual skills cannot depend at runtime on a
  sibling plugin or this source checkout.
- **One canonical owner for shared resources:** plugins use managed file-level symlinks in source;
  installation dereferences them into portable copies.
- **Human authority is explicit:** approval, skip, reset, and recovery decisions are recorded—not
  inferred from agent behavior.
- **Policy is executable:** transition templates, SQLite state, Python policy checks, tests, and
  diagrams are maintained as a single contract.
- **No silent bypasses:** a failed or missing capability is friction to diagnose and improve, not
  permission to quietly work around it.

Read the full [architecture overview](architecture.md), the
[control-plane module diagram](docs/diagrams/control-plane-architecture.mermaid), and the
[ADRs](docs/ADRs/) for the detailed contracts.

## What this is not

- Not a replacement for Claude Code, Codex, Copilot, Agy, or another capable native runtime.
- Not a requirement to install every plugin to use one useful skill.
- Not a claim that a local control plane can protect a repository from actors who deliberately
  circumvent it outside the configured workflow.
- Not static process documentation: the system is tested, measured, reviewed, and evolved.

## Repository layout

```text
plugins/                  canonical plugin sources
  <plugin>/skills/        portable skill definitions
  <plugin>/scripts/       canonical shared Python helpers
  <plugin>/agents/        sub-agent definitions
.agents/                  installer output; generated runtime copies, not source of truth
docs/diagrams/            control-plane and architecture diagrams
docs/ADRs/                binding architectural decisions
context/                  local control-plane state and memory in a consuming repository
temp/                     local scratch output
```

## Further reading

- [Install plugins](INSTALL.md)
- [Contributor/session bootstrap](START_HERE.md)
- [Repository architecture](architecture.md)
- [Agentic OS control-plane plugin](plugins/agent-agentic-os/README.md)
- [Control-plane happy path](docs/diagrams/control-plane-pipeline-happy-path.mermaid)
- [Complete transition graph](docs/diagrams/control-plane-pipeline.mermaid)
- [Architectural decision records](docs/ADRs/)
