# Two Paths in agent-agentic-os: Governed Task Pipeline vs Improvement Lab

`agent-agentic-os` contains two unrelated workflows. They share a plugin, not a mechanism. Neither
requires, enables, or implies the other. Read this before routing, recommending a skill, or
writing a handoff.

## Contents

- [At a glance](#at-a-glance)
- [Path 1: Governed task pipeline (control plane)](#path-1-governed-task-pipeline-control-plane)
- [Path 2: Improvement lab (autoresearch loop)](#path-2-improvement-lab-autoresearch-loop)
- [Rules that prevent the common mistakes](#rules-that-prevent-the-common-mistakes)
- [Known gap between the paths](#known-gap-between-the-paths)

## At a glance

| | Path 1: Control plane | Path 2: Improvement lab |
|---|---|---|
| Purpose | Do real engineering work under approval gates | Measure and improve one skill or agent against evals |
| Entry point | `os-init`, then `work-intake` | `os-architect` (Category 3), then intake and lab setup |
| State store | `context/control_plane.db` (SQLite) | `evals/results.tsv`, `improvement-ledger.md`, `context/events.jsonl` |
| What changes | The user's repository, in an isolated worktree | A skill's `SKILL.md` in a lab repo, then backported |
| Human authority | SSH-signed `transition_request` at Gate 1, Gate 3 and closure | Human reviews the diff and approves the backport |
| Success signal | Task reaches `DONE` with verified evidence | `evaluate.py` verdict KEEP, score above baseline |
| Toggled by | `os-control-plane-mode` | Enabling its skills in `.agents/ownership/` |

`os-control-plane-mode` flips only Path 1 (`work-intake`, `transition-simulator`,
`os-signing-setup`, the guidance-compliance rule, and the two git guards). A control plane that
reports `ENABLED` says nothing about whether any Path 2 skill is installed.

## Path 1: Governed task pipeline (control plane)

Use for any non-trivial feature, refactor or multi-file fix.

1. **`os-init`** (agent wrapper: `agentic-os-setup`). Probe the repo (`installation_probe.py`),
   interview, make `AGENTS.md` the single canonical instruction file, provision the 3-layer
   memory, `context/control_plane.db` and `context/kernel.py`, and create the simulation identity.
   Human signing key setup stays a human job (`os-signing-setup`).
2. **`work-intake`**. Read-only discovery, at most one question per turn, register the task, write the
   four-pillar `TASK_SPEC.md` under `docs/plans/work-tasks/<task-id>/`. States:
   `INTAKE -> INTERVIEW -> DRAFT_PLAN -> PLAN_REVIEW -> AWAITING_APPROVAL`.
3. **Plan the execution shape** (agent-orchestration): `select-loop-strategy` picks the topology;
   `graph-planner` compiles `graph-manifest.json` when the work is a DAG.
4. **Gate 1** (`AWAITING_APPROVAL -> APPROVED`): cryptographic, human only.
5. **`worktree-manager`**. Probe native worktree support or fall back to `.worktrees/<task-id>` based
   on `origin/main`; reconcile dirty state (`APPROVED -> IN_WORKTREE`).
6. **Execute** with `graph-execution`, `orchestrator`, or a loop pattern. Never merge autonomously.
7. **Gate 3** (`WORKTREE_REVIEW` or `MULTI_AGENT_CODE_REVIEW -> VERIFY_EXIT`) and **closure**
   (any edge into `DONE`): cryptographic, human only.

Supporting skills: `transition-simulator` tests the state machine against a separate simulation
database and key; `os-health-check` reports readiness. Agents never sign, never record human
approvals, and never use a skip or force-close path.

## Path 2: Improvement lab (autoresearch loop)

Use to raise a skill's routing accuracy or quality score. It is not task delivery.

1. **`os-architect`** (front door; agent `os-architect-agent`). Classifies intent. Category 3
   ("improve X skill", "run eval on Y", "stress test") routes to the lab path.
2. **`improvement-intake-agent`**. Plain-language interview. Writes `improvement/run-config.json`
   and `improvement/session-brief.md`.
3. **`os-eval-lab-setup`**. Creates an isolated sibling lab repo with `evals/evals.json` (routing
   cases use `should_trigger: true/false`), `evals/results.tsv` (baseline ledger) and
   `references/program.md` (goal, target score, iteration cap). See `lab-space-protocol.md`.
4. **`os-improvement-loop`**. Five stages per cycle: orientation, execution, independent
   verification, decision, close.
   - Stage 0 reads the improvement ledger, the target's `results.tsv`, the test registry,
     long-term memory, recent retrospectives, and open Map Debt.
   - Stage 2 runs `evaluate.py` (via `os-eval-runner`) independently. The verdict is KEEP or DISCARD.
   - Stage 4 closes with surveys, ledger update and memory promotion (`os-memory-manager`).
5. **`os-eval-backport`**. A human reviews the lab diff; approved changes are backported to the
   master plugin source. Persist results with `os-experiment-log`.

Hard rules: every mutation passes the eval gate before it is kept; no manual rollback mid-cycle;
`evals.json` and the scoring scripts are locked from the mutating agent.

## Rules that prevent the common mistakes

- **Plugin source is not runtime.** `plugins/` holds every skill. Only what is installed in
  `.agents/skills/` and set `should_install: true` in `.agents/ownership/<plugin>.json` can run.
  Many skills are disabled on purpose to save context.
- **Verify before routing.** Before recommending a skill or writing a handoff to it:
  `ls .agents/skills/<name>` and `grep '"<name>"' .agents/ownership/*.json`. If it is disabled,
  say so and ask. Do not route through it, and do not substitute another disabled skill.
- **Path 2 needs a different skill set.** `os-architect`, `os-eval-lab-setup`, `os-eval-runner`,
  `os-eval-backport`, `os-improvement-loop` and `os-experiment-log` must each be enabled. They are
  independent of Path 1.
- **Sync pulls from the registry, not your branch.** `plugin-syncer` runs
  `sync_with_inventory.py`, which installs from the sources in `plugin-sources.json` (a GitHub
  remote for most plugins). Edits on an unmerged branch reach `.agents/` only after merge.
- **Read counts from `plugins/`.** Use `find plugins -name SKILL.md | wc -l` and
  `find plugins/*/agents -maxdepth 1 -name '*.md' | wc -l`; never copy a count from another doc.

## Known gap between the paths

`improvement-intake-agent` writes `run-config.json` and `session-brief.md`, but no skill reads them.
`os-improvement-loop` orients from the ledger, `results.tsv` and `program.md`. Until intake writes
`program.md` (or the loop reads the run config), the intake output is a record for the human, not
machine input. Tracked in `references/map-debt.md` as `DEBT-20261014-DANGLING-ORCHESTRATOR-REF-AND-DRIFTED-COUNTS`.
