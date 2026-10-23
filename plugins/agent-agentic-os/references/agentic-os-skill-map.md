# Agentic OS Skill Map

Read this before routing to, recommending, or handing off to any `agent-agentic-os` skill. It says
what each of the 14 skills does, grouped by purpose and function into two clusters of 7, and how the
clusters relate. For Cluster 1 and Cluster 2 side by side, see
[two-improvement-paths.md](two-improvement-paths.md).

Verify the skill is installed in your active runtime harness (via `apm list` or your client's installed skills directory) before relying on it.

## Contents

- [The clusters at a glance](#the-clusters-at-a-glance)
- [How the clusters relate](#how-the-clusters-relate)
- [Cluster 1: Control Plane](#cluster-1-control-plane)
- [Cluster 2: Skill Improvement Lab](#cluster-2-skill-improvement-lab)

## The clusters at a glance

| Cluster | Skills | Job | Scope |
|---|---|---|---|
| Cluster 1: Control Plane | 7 (plus the `os-control-setup-agent` agent) | Run large engineering tasks under signed human gates | Any repository, any kind of work |
| Cluster 2: Skill Improvement Lab | 7 (plus the `os-lab-agent` agent) | Plan, run and verify experiments that improve skills and agents | Skills and agents in this ecosystem |

## How the clusters relate

**Cluster 1: Control Plane stands alone.** It is a general task pipeline: it does not depend on
Cluster 2. The one link runs the other way: when Cluster 2 updates or creates a skill, it registers
that work as a control-plane task (`agent_control.py`, task type `EVOLUTION`) and logs a prior-art
scan, so lab changes pass the same gate. Its state is `context/control_plane.db`; its authority is
the human's SSH signature at Gate 1, Gate 3 and closure. It borrows execution patterns from the
separate `agent-orchestration` plugin (`select-loop-strategy`, `graph-planner`, `graph-execution`).

**Cluster 2: Skill Improvement Lab works on the ecosystem's own skills and agents.** Its state lives
in the files `context/kernel.py` maintains: `context/events.jsonl`, `context/.locks/`,
`context/memory.md`, the improvement ledger and the experiment log. `os-lab-agent` is its front door.

```text
                    ┌──────────────────────────────────────────────────────┐
 Cluster 1          │ os-control-init ─► os-control-intake ─► Gate 1       │
 Control Plane      │   ─► os-control-worktree ─► execute                  │   context/control_plane.db
 (independent)      │   ─► Gate 3 ─► closure (DONE)                        │   + human SSH key
                    │ supported by os-control-signing-setup,               │
                    │ os-control-simulator, os-control-mode,               │
                    │ os-control-health                                    │
                    └──────────────────────────────────────────────────────┘

                         os-lab-agent (front door)
                           │  plan a change: os-lab-planner
                           ▼
 Cluster 2   os-lab-setup ─► os-lab-loop ⇄ os-lab-scorer
 Skill            ─► os-lab-backport ─► os-lab-log
 Improvement Lab  close and debrief: os-lab-memory
                  (context/events.jsonl, context/.locks/, context/memory.md)
```

`os-control-init` belongs to Cluster 1 but also installs the kernel files (`context/kernel.py`, memory folders)
that Cluster 2 uses. `os-control-health` belongs to Cluster 1 but also reports on those kernel files.

## Cluster 1: Control Plane

General-purpose pipeline for large work in any repository. Big tasks use it; quick tasks can switch it off.

### How it works

The `os-control-` prefix groups the skills that set up, run, check or govern the pipeline.

```mermaid
flowchart TD
    subgraph SETUP [Once per repository]
        IN["<b>os-control-init</b><br/><small>scaffold or retrofit the OS, control_plane.db, memory</small>"]
        SG["<b>os-control-signing-setup</b><br/><small>human creates the SSH approval key</small>"]
        HC["<b>os-control-health</b><br/><small>readiness: database, signing, kernel files</small>"]
        IN --> SG --> HC
    end
    U([User request: large task]) --> CI
    CI["<b>os-control-intake</b><br/><small>discovery, interview, TASK_SPEC.md, plan</small>"]
    CI -.->|plan topology| AO["<b>agent-orchestration</b><br/><small>select-loop-strategy, graph-planner</small>"]
    CI --> G1{{"Gate 1<br/><small>human SSH signature</small>"}}
    G1 --> WT["<b>os-control-worktree</b><br/><small>isolated worktree from origin/main</small>"]
    WT --> EX["<b>execute</b><br/><small>graph-execution or a loop pattern</small>"]
    EX --> G3{{"Gate 3<br/><small>human SSH signature</small>"}}
    G3 --> DN{{"Closure: DONE<br/><small>human SSH signature</small>"}}
    MD["<b>os-control-mode</b><br/><small>turn the pipeline on or off</small>"] -.-> CI
    SIM["<b>os-control-simulator</b><br/><small>test transitions on the simulation database</small>"] -.-> G1
```

### Skills

| Skill | What it does |
|---|---|
| `os-control-init` | Probes a repository (fresh, complete, or drifted), interviews for stack and AI platforms, makes `AGENTS.md` the single instruction file, creates the 3-layer memory and `context/control_plane.db`, and sets up the simulation signing identity. Wrapped by the `os-control-setup-agent` agent. |
| `os-control-intake` | Front door for every non-trivial task. Read-only discovery, at most one question per turn, registers the task, writes the four-pillar `TASK_SPEC.md` (the job, the why, guardrails, definition of done) and stages the plan: `INTAKE -> INTERVIEW -> DRAFT_PLAN -> PLAN_REVIEW -> AWAITING_APPROVAL`. |
| `os-control-worktree` | Picks the runtime's native worktree facility, or a portable `.worktrees/<task-id>` based on fresh `origin/main`. Reconciles uncommitted state and reports cleanup commands. |
| `os-control-signing-setup` | Walks the human through creating the SSH signing key and `allowed_signers` that authorize Gate 1, Gate 3 and closure, then runs a signing self-test. The agent never signs. |
| `os-control-simulator` | Tests the control-plane state machine without touching real state: deterministic simulation, or cheap-model dry runs that grade what the agent asks, runs, and hands to the human. Uses the separate simulation database and key. |
| `os-control-mode` | Turns Cluster 1 on or off as one unit (member skills and rule, the commit and push guards, the declared mode) and reports its status. |
| `os-control-health` | Deterministic readiness and liveness report, run by `os-control-init` and the control plane's setup checks: signing and identity readiness, plus the kernel's event log, hook errors, memory size and stale locks. |

## Cluster 2: Skill Improvement Lab

Targeted work on this ecosystem's skills and agents: plan a change, make one skill measurably better
against a locked eval set, and verify the result.

### Skills and agent

One agent holds the conversation; the skills do the steps. The `os-lab-` prefix groups the cluster's
skills so they sort together, and `os-lab-memory` is the shared close step.

```mermaid
flowchart TD
    U([User request: improve a skill or agent]) --> AG
    AG["<b>os-lab-agent</b><br/><small>one conversation: what to improve, what exists, run settings</small>"]
    AG --> PL["<b>os-lab-planner</b><br/><small>options, plan and delegation prompt</small>"]
    PL --> SU["<b>os-lab-setup</b><br/><small>build the isolated lab repo, commit baseline</small>"]
    SU --> LP["<b>os-lab-loop</b><br/><small>the only loop: orient, mutate, close</small>"]
    LP -->|each change| SC["<b>os-lab-scorer</b><br/><small>one locked KEEP / DISCARD check</small>"]
    SC -->|KEEP or DISCARD| LP
    LP -->|run complete| BP["<b>os-lab-backport</b><br/><small>review the lab diff, backport approved changes</small>"]
    LP --> LG["<b>os-lab-log</b><br/><small>run log, summary and charts</small>"]
    BP --> LG
    LP -->|close| MM["<b>os-lab-memory</b><br/><small>session log and memory promotion</small>"]
    BP -->|debrief| MM
```

| Skill or agent | What it does |
|---|---|
| `os-lab-agent` (agent) | Front door, interactive, runs in the main session. Holds one plain-language conversation: what to improve and why, what already exists, and the run settings (depth, success criteria, available tools, second-opinion check). Writes `references/program.md` and `improvement/run-config.json`, then calls the `os-lab-*` skills in order. |
| `os-lab-planner` | Non-interactive. Turns the confirmed brief into a plan: audits what already exists, chooses to orchestrate existing skills, update one or create new, brainstorms two or three options with tradeoffs, and writes the task plan and a self-contained delegation prompt. |
| `os-lab-setup` | Builds an isolated lab repository for one skill: copies the plugin with links resolved, renders `eval-instructions.md`, commits a baseline, and offers manual or autonomous launch. |
| `os-lab-loop` | The only improvement loop: orient from the ledger, `evals/results.tsv`, `references/program.md` and open map debt, mutate one thing, send every change to `os-lab-scorer`, then close with surveys, ledger update, metrics and memory promotion through `os-lab-memory`. |
| `os-lab-scorer` | The locked KEEP / DISCARD check for one change: runs `evaluate.py` headlessly, compares against the baseline in `evals/results.tsv`, applies the holdout overfitting gate, and reverts a DISCARD. Also runs a single-pass RED-GREEN-REFACTOR fix on one skill. |
| `os-lab-backport` | After a lab run, reads the lab's progress log and diff, classifies each changed file (accept, adapt, reject, review), applies approved changes to the master plugin source, and records learnings. |
| `os-lab-log` | Append-only log of runs in `context/experiment-log/` with `append`, `query` and `summary` modes, plus the improvement trend chart and progress report. |
| `os-lab-memory` | The close and debrief step of `os-lab-loop` and `os-lab-backport`, and the repository's memory manager: writes the dated session log, promotes vetted facts to `context/memory.md` with conflict checks, and archives when the file exceeds 50,000 bytes, all under the kernel's `memory` lock. |
