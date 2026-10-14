# Agentic OS Skill Map

Read this before routing to, recommending, or handing off to any `agent-agentic-os` skill. It says
what each of the 28 skills does, grouped by purpose and function, how the clusters relate, and
review findings for each skill. For the two main workflows side by side, see
[two-improvement-paths.md](two-improvement-paths.md).

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
- [Review findings](#review-findings)

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

## Review findings

Observations from reading every skill, its folder and its references. Verdicts flag evidence for
review; they do not authorize deleting any skill.

Enabled = `should_install: true` in this repo's `.agents/ownership/agent-agentic-os.json` on the
audit date. Verdicts: **Keep**, **Refresh** (useful, but contains stale content), **Repair**
(broken reference), **Review** (overlap or low value; decide whether to keep), **Fixture**
(supports tests, not a user capability).

#### A. Governed delivery

| Skill | Enabled | Purpose | Findings | Verdict |
|---|---|---|---|---|
| `work-intake` | yes | Intake gateway: discovery, one question per turn, task registration, four-pillar `TASK_SPEC.md`, plan staging | None | Keep |
| `worktree-manager` | yes | Native or portable `.worktrees/<task-id>` from `origin/main`; dirty-state reconciliation | Only 2 eval cases | Keep |
| `transition-simulator` | yes | Simulates and grades transitions on the simulation DB and key | 4 eval cases | Keep |
| `os-control-plane-mode` | yes | Switches group A on or off as one unit; status check | None | Keep |
| `os-signing-setup` | yes | Human creates the SSH key behind Gate 1, Gate 3 and closure | None | Keep |
| `os-init` | yes | Probe, scaffold or retrofit; `AGENTS.md` canonical; 3-layer memory; simulation identity | References still mention Gemini CLI (2) and `soul.md` (4) | Refresh |

#### B. Improvement lab

| Skill | Enabled | Purpose | Findings | Verdict |
|---|---|---|---|---|
| `os-architect` | no | Front door: classifies intent into six categories, audits, routes, dispatches | Calls `scripts/run_agent.py`, which belongs to `cli-agents` and is not in the skill folder (ADR-001: delegate via skill) | Repair |
| `os-environment-probe` | no | Detects available AI CLIs; writes `context/memory/environment.md` | Hard-coded `claude-sonnet-4` model IDs (4); Gemini CLI | Refresh |
| `os-eval-lab-setup` | no | Bootstraps an isolated lab repo: `evals.json`, `results.tsv`, `program.md` | Gemini CLI mentions (2) | Refresh |
| `os-eval-runner` | no | Stateless scorer; KEEP / DISCARD against locked evals | 15 results rows (the only lab skill with real run history); Gemini CLI mention | Keep |
| `os-improvement-loop` | no | Five-stage improvement cycle | Does not read the intake agent's `run-config.json` (open map debt) | Keep |
| `os-skill-improvement` | no | RED-GREEN-REFACTOR on one skill | Same eval gate as `os-improvement-loop`, smaller scope | Review: merge into the loop as a single-cycle mode? |
| `os-eval-backport` | no | Human review of a lab run; backport to master source | Gemini CLI mention | Keep |
| `os-experiment-log` | no | Dated experiment log in `context/experiment-log/` | None | Keep |
| `os-improvement-report` | no | Charts and trends across cycles | `SKILL.md` commands use repo-root paths (`plugins/agent-agentic-os/scripts/generate_report.py`), but the skill already has the `scripts/generate_report.py` spoke | Repair (small) |

#### C. Ecosystem self-evolution

| Skill | Enabled | Purpose | Findings | Verdict |
|---|---|---|---|---|
| `os-evolution-planner` | no | Brainstorms 2-3 options, writes the plan and a Copilot delegation prompt | Hard-coded `claude-sonnet-4` (3); Gemini CLI; only reachable through `os-architect` | Refresh |
| `os-evolution-verifier` | no | Checks that `os-architect` produced real artifacts | Calls `scripts/run_evolution_scenario.py`, which exists nowhere in the repo; hard-coded model ID | Repair, or Review for retirement |
| `self-evolution` | no | 6-node evolution controller: proposal, sandbox, verify, receipt | Has its own approval and worktree states, parallel to group A's control plane | Review: overlap with group A |
| `repository-improvement` | no | Turns friction-cluster hotspot reports into refactoring proposals | Input comes from `dev-utils:github-issue-agent`; `cat references/map-debt.md` has no spoke link | Review |
| `evo-smoketest` | no | Temperature-conversion fixture for `scripts/smoke_test.py` | `scripts/evaluate.py` spoke missing | Fixture |

#### D. Runtime kernel & memory

| Skill | Enabled | Purpose | Findings | Verdict |
|---|---|---|---|---|
| `os-health-check` | yes | Deterministic liveness report: event log, locks, memory | Mentions `os-state.json` (4); confirm that file is still produced | Keep (verify) |
| `os-memory-manager` | no | Promotes session facts to `context/memory.md` | References still teach `soul.md` and the CLAUDE.md hierarchy | Refresh |
| `os-clean-locks` | no | Removes stale `context/.locks/` files | Only useful where kernel locks are in use | Keep |

#### E. Standalone audit utilities

| Skill | Enabled | Purpose | Findings | Verdict |
|---|---|---|---|---|
| `critical-auditor` | no | Adversarial full-system audit | Calls `scripts/audit_skill.py` (an `agent-scaffolders` script, not in the folder); overlaps `agent-scaffolders` audit skills and `cli-agents` red-team personas | Review |
| `issue-resolution-reviewer` | no | Checks closed GitHub issues were really fixed | Fits `dev-utils` (GitHub issue family) better than this plugin | Review: placement |
| `optimize-agent-instructions` | no | Audits and rewrites `AGENTS.md` | Superseded by `agent-scaffolders:create-agents-md` and `audit-agents-md` (added in #696); links `references/agents-md-contract.md`, which lives in that plugin; Gemini CLI (6) | Review: strongest retirement candidate |
| `todo-check` | no | Scans a file for TODO markers | Trivial as a capability, but `os-improvement-loop`'s quick start uses it as the demo eval target | Review: keep only as a lab fixture |

#### F. Guidance

| Skill | Enabled | Purpose | Findings | Verdict |
|---|---|---|---|---|
| `os-guide` | no | Explains layers, memory and loops | Body names `AGENTS.md` as canonical, but the triggers still advertise "the CLAUDE.md hierarchy" and "soul.md or user.md" (11 `soul.md` mentions); does not explain group A at all | Refresh, or Review for retirement now that [two-improvement-paths.md](two-improvement-paths.md) covers the orientation |

### Cross-cutting findings

1. **Gemini CLI references in 12 skills.** Gemini CLI consumer access ended on June 18, 2026
   (`architecture.md`); `agy-cli-agent` is the stated replacement.
2. **Hard-coded model IDs** (`claude-sonnet-4*`) in `os-environment-probe`, `os-evolution-planner` and
   `os-evolution-verifier`. Model choice belongs in `cli-agents/references/copilot-models.json` tiers.
3. **Scripts owned by other plugins.** `os-architect` (`run_agent.py`), `critical-auditor`
   (`audit_skill.py`) and `optimize-agent-instructions` (`agents-md-contract.md`) reference files that
   are not in their skill folder. Under ADR-001 they should delegate to the owning skill by name.
4. **22 symlinks not recorded in `symlinks.json`.** They resolve and are relative, so install works,
   but Section 5 of the plugin architecture policy requires every link to be in the manifest, and
   `symlink_manager.py diagnose` only checks recorded links.
5. **Pointer chains install as one-line stubs.** Skill links such as
   `os-guide/references/architecture.md` point at plugin-root pointer files such as
   `references/architecture.md`, whose text is `../../../references/architecture/architecture.md`.
   That path is correct from the skill folder, but `plugin_installer.py` resolves a pointer relative
   to the pointer file itself (`real_src.parent`), where it points outside the plugin. The target is
   not found, so the installer copies the pointer text. Already visible in installed, enabled skills:
   `.agents/skills/os-init/references/architecture.md` and `project-setup-guide.md`, plus one file
   each in `dependency-management`, `create-skill` and `audit-plugin`. 17 such pointers sit in this
   plugin's `references/`. Fix either the pointer text or the installer's resolution base.
6. **Groups B, C and E are entirely disabled in this repo.** Everything enabled is in group A, plus
   `os-health-check`. That matches how the plugin is used: the control plane daily, the lab
   occasionally.

### Recommended next steps

Small, safe fixes (no design decision needed):
- `os-improvement-report`: change its commands to `scripts/generate_report.py`.
- Add the missing spoke links: `evo-smoketest/scripts/evaluate.py` and
  `repository-improvement/references/map-debt.md`, through `symlink_manager.py create`.
- Record the 22 existing links in `symlinks.json`.
- Replace Gemini CLI references with `agy-cli-agent`, and hard-coded model IDs with catalog tiers.

Decisions for the owner:
- Retire `optimize-agent-instructions` in favor of the `agent-scaffolders` AGENTS.md skills?
- Fold `os-skill-improvement` into `os-improvement-loop`, and keep `todo-check` only as a fixture?
- Repair or retire `os-evolution-verifier` (its scenario script does not exist)?
- Rewrite `os-guide` around the two paths, or retire it?
- Move `issue-resolution-reviewer` to `dev-utils`?
- Remove or repoint the 17 dangling pointer files?

### Evidence and limits

- Inputs: every `SKILL.md`, its `evals/`, its folder's links, references to it across `plugins/`,
  and this repo's ownership manifest.
- **Usage counts were not measured.** A transcript scan did not reliably detect skill invocations,
  so it is not used here. The usage pattern in cross-cutting finding 6 is the owner's own account.
- **Git dates are not a staleness signal.** Almost every skill folder was last committed on
  2026-10-02 in a bulk restructure.
- Verdicts flag evidence; they do not authorize deletion.
