# agent-agentic-os Skill Catalog

What each of the 28 skills does, grouped into clusters, and how the clusters relate. For audit
findings (staleness, broken references, retirement candidates) see
[skill-audit-findings.md](skill-audit-findings.md). For the two main workflows
side by side, see [two-improvement-paths.md](two-improvement-paths.md).

A project installs only part of this plugin. Check `.agents/ownership/agent-agentic-os.json`
(`should_install`) and `ls .agents/skills/<name>` before relying on any skill.

## Contents

- [The clusters at a glance](#the-clusters-at-a-glance)
- [How the clusters relate](#how-the-clusters-relate)
- [1. Control plane: governed delivery](#1-control-plane-governed-delivery)
- [2. Improvement lab](#2-improvement-lab)
- [3. Ecosystem self-evolution](#3-ecosystem-self-evolution)
- [4. Runtime kernel and memory](#4-runtime-kernel-and-memory)
- [5. Standalone audit utilities](#5-standalone-audit-utilities)
- [6. Guidance](#6-guidance)

## The clusters at a glance

| Cluster | Skills | Job | Scope |
|---|---|---|---|
| 1. Control plane | 6 | Run large engineering tasks under signed human gates | Any repository, any kind of work |
| 2. Improvement lab | 9 | Run experiments that raise one skill's eval score | Skills and agents in this ecosystem |
| 3. Self-evolution | 5 | Plan, apply and verify changes to the plugins and the OS itself | This ecosystem |
| 4. Kernel and memory | 3 | Maintain the event bus, locks and memory files | Shared by clusters 2 and 3 |
| 5. Audit utilities | 4 | One-shot reviews of code, issues or instruction files | Any repository |
| 6. Guidance | 1 | Explain the OS to a new user | Orientation |

## How the clusters relate

**The control plane stands alone.** Cluster 1 is a general task pipeline: it does not depend on the
lab, the evolution skills, the kernel's event bus, or the memory skills, and none of them depend on
it. Its state is `context/control_plane.db`; its authority is the human's SSH signature at Gate 1,
Gate 3 and closure. It borrows execution patterns from the separate `agent-orchestration` plugin
(`select-loop-strategy`, `graph-planner`, `graph-execution`).

**Clusters 2, 3 and 4 form the self-improvement system.** They work on the ecosystem itself and share
state through the kernel: `context/events.jsonl`, `context/.locks/`, `context/memory.md`, the
improvement ledger and the experiment log. `os-architect` is the front door to both 2 and 3.

**Clusters 5 and 6 connect to nothing.** Each audit utility runs once against a target and reports.
`os-guide` points users to other skills but has no state.

```text
                         ┌───────────────────────────────────────────┐
 Cluster 1               │ os-init ─► work-intake ─► Gate 1          │
 Control plane           │   ─► worktree-manager ─► execute          │   context/control_plane.db
 (independent)           │   ─► Gate 3 ─► closure (DONE)             │   + human SSH key
                         │ os-signing-setup, transition-simulator,   │
                         │ os-control-plane-mode support it          │
                         └───────────────────────────────────────────┘

                         ┌───────────── os-architect (front door) ─────────────┐
                         ▼                                                     ▼
 Cluster 2   lab: os-eval-lab-setup ─► os-improvement-loop ⇄ os-eval-runner    Cluster 3
 Improvement      ─► os-eval-backport ─► os-experiment-log                     os-evolution-planner
 lab              ─► os-improvement-report                                     ─► os-evolution-verifier
                                                                               self-evolution
                         └──────────────┬──────────────────────────────────────┘  repository-improvement
                                        ▼
 Cluster 4   os-memory-manager, os-health-check, os-clean-locks
 Kernel      (context/events.jsonl, context/.locks/, context/memory.md)
```

`os-init` belongs to cluster 1 but also installs the kernel files (`context/kernel.py`, memory folders)
that clusters 2 to 4 use. `os-health-check` reports on the kernel and can run with either system.

## 1. Control plane: governed delivery

General-purpose pipeline for large work in any repository. Big tasks use it; quick tasks can switch it off.

| Skill | What it does |
|---|---|
| `os-init` | Probes a repository (fresh, complete, or drifted), interviews for stack and AI platforms, makes `AGENTS.md` the single instruction file, creates the 3-layer memory and `context/control_plane.db`, and sets up the simulation signing identity. Wrapped by the `agentic-os-setup` agent. |
| `work-intake` | Front door for every non-trivial task. Read-only discovery, at most one question per turn, registers the task, writes the four-pillar `TASK_SPEC.md` (the job, the why, guardrails, definition of done) and stages the plan: `INTAKE -> INTERVIEW -> DRAFT_PLAN -> PLAN_REVIEW -> AWAITING_APPROVAL`. |
| `worktree-manager` | Picks the runtime's native worktree facility, or a portable `.worktrees/<task-id>` based on fresh `origin/main`. Reconciles uncommitted state and reports cleanup commands. |
| `os-signing-setup` | Walks the human through creating the SSH signing key and `allowed_signers` that authorize Gate 1, Gate 3 and closure, then runs a signing self-test. The agent never signs. |
| `transition-simulator` | Tests the control-plane state machine without touching real state: deterministic simulation, or cheap-model dry runs that grade what the agent asks, runs, and hands to the human. Uses the separate simulation database and key. |
| `os-control-plane-mode` | Turns the whole cluster on or off as one unit (member skills and rule, the commit and push guards, the declared mode) and reports its status. |

## 2. Improvement lab

Targeted experiments: make one skill or agent measurably better against a locked eval set.

| Skill | What it does |
|---|---|
| `os-architect` | Front door for evolution work. Classifies intent (pattern abstraction, research application, lab setup, capability gap, multi-loop), audits what already exists, then orchestrates existing skills, updates via `os-evolution-planner`, or creates new ones. Lab requests go to the `improvement-intake-agent`. |
| `os-environment-probe` | Detects which AI CLIs are really available (Claude, Copilot, Agy, Cursor) and writes `context/memory/environment.md`, which `os-architect` and `os-evolution-planner` read to choose a delegation backend. |
| `os-eval-lab-setup` | Builds an isolated lab repository for one skill: copies the plugin with links resolved, renders `eval-instructions.md`, commits a baseline, and offers manual or autonomous launch. |
| `os-eval-runner` | The scorer. Ensures `evals.json` and `program.md` exist, then either runs the autoresearch loop (propose, evaluate, keep or discard) or a single-shot KEEP/DISCARD check, with a holdout overfitting check. |
| `os-improvement-loop` | The full cycle: orient from the ledger and history, execute, verify independently with `evaluate.py`, decide KEEP or DISCARD, then close with surveys, ledger update and memory promotion. |
| `os-skill-improvement` | A focused RED-GREEN-REFACTOR pass on one skill: baseline the failure, state a hypothesis, patch `SKILL.md`, require a KEEP verdict, close edge cases. |
| `os-eval-backport` | After a lab run, reads the lab's progress log and diff, classifies each change (accept, adapt, reject, review) and applies approved changes to the master plugin source. |
| `os-experiment-log` | Append-only log of runs in `context/experiment-log/`, with `append`, `query` and `summary` modes. |
| `os-improvement-report` | Reads the experiment log, aggregates score progression and renders a chart and summary under `context/memory/reports/`. |

## 3. Ecosystem self-evolution

Changes to the plugins and to the OS itself, beyond a single skill's score.

| Skill | What it does |
|---|---|
| `os-evolution-planner` | Brainstorms two or three approaches with the cheapest available model, checks the target for standard gaps, and writes a task plan plus a delegation prompt to `tasks/todo/`. Dispatches only after user confirmation. |
| `os-evolution-verifier` | Checks that `os-architect` actually produced artifacts, not just text: dispatches it in simulation, checks files and handoff blocks, and logs PASS or FAIL through `os-experiment-log`. |
| `self-evolution` | A 6-node controller for gated self-modification: debt scan, proposal and approval, sandboxed worktree change, controller verification (three-attempt cap), and a cryptographic completion receipt. |
| `repository-improvement` | Takes friction-cluster hotspot reports (from `dev-utils:github-issue-agent`), groups symptoms under one root cause, drafts a refactoring proposal, and hands approved work to PR lifecycle agents. |
| `evo-smoketest` | Not a user capability. A temperature-conversion fixture that `scripts/smoke_test.py` uses to test `self-evolution` end to end. |

## 4. Runtime kernel and memory

Housekeeping for the files `context/kernel.py` maintains.

| Skill | What it does |
|---|---|
| `os-memory-manager` | Writes the dated session log, promotes vetted facts to `context/memory.md` with conflict checks, and archives when the file exceeds 50,000 bytes, all under the kernel's `memory` lock. |
| `os-health-check` | Deterministic liveness report: event log, hook errors, memory size, stale locks and substrate components. |
| `os-clean-locks` | Clears stale `context/.locks/*.lock` directories left by crashed agents. |

## 5. Standalone audit utilities

One-shot reviews. Each takes a target and returns a report.

| Skill | What it does |
|---|---|
| `critical-auditor` | Adversarial review of a skill or plugin: maps its gates and mutators, tries to bypass them, writes repro scenarios, and ranks findings P0 to P2. |
| `issue-resolution-reviewer` | Checks closed GitHub issues against their fix commits, CI logs and Map Debt, and classifies each as confirmed resolved, recurring, or inconclusive. Asks before reopening anything. |
| `optimize-agent-instructions` | Audits and rewrites a repository's `AGENTS.md` to a lean skeleton and checks that `CLAUDE.md` is only a short pointer. |
| `todo-check` | Scans a file or directory for `TODO`, `FIXME`, `HACK` and `XXX` markers. Also the demo target in `os-improvement-loop`'s quick start. |

## 6. Guidance

| Skill | What it does |
|---|---|
| `os-guide` | Answers "how does the OS work" questions from its reference docs (memory layers, context folder, loop scheduling, hooks) and points the user to the right skill. |
