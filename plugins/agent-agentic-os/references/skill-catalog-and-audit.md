# agent-agentic-os Skill Catalog and Audit (2026-10-14)

All 28 skills in this plugin, grouped by function, with how they relate and which ones look stale.
This is a point-in-time audit. Recheck the evidence before acting on any verdict, and never delete a
skill without an explicit instruction naming its path (Skill Deletion Guard).

## Contents

- [Six functional groups](#six-functional-groups)
- [How the groups relate](#how-the-groups-relate)
- [Per-skill catalog](#per-skill-catalog)
- [Cross-cutting findings](#cross-cutting-findings)
- [Recommended next steps](#recommended-next-steps)
- [Evidence and limits](#evidence-and-limits)

## Six functional groups

| Group | Skills | What it is for |
|---|---|---|
| **A. Governed delivery (control plane)** | `work-intake`, `worktree-manager`, `transition-simulator`, `os-control-plane-mode`, `os-signing-setup`, `os-init` | Large engineering work in *any* repository, under signed human gates. Not specific to this plugin ecosystem. The most-used path. |
| **B. Improvement lab** | `os-architect`, `os-environment-probe`, `os-eval-lab-setup`, `os-eval-runner`, `os-improvement-loop`, `os-skill-improvement`, `os-eval-backport`, `os-experiment-log`, `os-improvement-report` | Targeted experiments that improve one skill or agent against locked evals. |
| **C. Ecosystem self-evolution** | `os-evolution-planner`, `os-evolution-verifier`, `self-evolution`, `repository-improvement`, `evo-smoketest` | Changing the plugins and the OS itself: plan-and-delegate, a 6-node evolution controller, Tier 3 friction proposals, and the controller's smoke-test fixture. |
| **D. Runtime kernel & memory** | `os-memory-manager`, `os-health-check`, `os-clean-locks` | The event bus, locks and memory files that `context/kernel.py` maintains. |
| **E. Standalone audit utilities** | `critical-auditor`, `issue-resolution-reviewer`, `optimize-agent-instructions`, `todo-check` | One-shot reviews that use none of the workflows above. |
| **F. Guidance** | `os-guide` | Explains the OS to a new user. |

Group A and group B share no state and no mechanism. See
[two-improvement-paths.md](two-improvement-paths.md). Group C overlaps both: it changes the
ecosystem like B, but with its own gated state machine, like A.

## How the groups relate

```text
A. Governed delivery
   os-init ─► work-intake ─► (select-loop-strategy / graph-planner, agent-orchestration)
          ─► Gate 1 ─► worktree-manager ─► execute ─► Gate 3 ─► DONE
   os-signing-setup supplies the human key for the gates;
   transition-simulator tests the state machine;
   os-control-plane-mode switches the whole group on or off.

B. Improvement lab
   os-architect ─► (improvement-intake-agent) ─► os-eval-lab-setup
          ─► os-improvement-loop ⇄ os-eval-runner  (os-skill-improvement = single-skill variant)
          ─► os-eval-backport ─► os-experiment-log ─► os-improvement-report
   os-environment-probe feeds os-architect's choice of delegation backend.

C. Ecosystem self-evolution
   os-architect ─► os-evolution-planner ─► delegated change ─► os-evolution-verifier
   self-evolution: its own 6-node controller (evo-smoketest is its fixture)
   repository-improvement: consumes friction-cluster reports from dev-utils:github-issue-agent

D. Kernel & memory: used by B and C (event bus, ledger, memory promotion), not needed by A.
```

## Per-skill catalog

Enabled = `should_install: true` in this repo's `.agents/ownership/agent-agentic-os.json` on the
audit date. Verdicts: **Keep**, **Refresh** (useful, but contains stale content), **Repair**
(broken reference), **Review** (overlap or low value; decide whether to keep), **Fixture**
(supports tests, not a user capability).

### A. Governed delivery

| Skill | Enabled | Purpose | Findings | Verdict |
|---|---|---|---|---|
| `work-intake` | yes | Intake gateway: discovery, one question per turn, task registration, four-pillar `TASK_SPEC.md`, plan staging | None | Keep |
| `worktree-manager` | yes | Native or portable `.worktrees/<task-id>` from `origin/main`; dirty-state reconciliation | Only 2 eval cases | Keep |
| `transition-simulator` | yes | Simulates and grades transitions on the simulation DB and key | 4 eval cases | Keep |
| `os-control-plane-mode` | yes | Switches group A on or off as one unit; status check | None | Keep |
| `os-signing-setup` | yes | Human creates the SSH key behind Gate 1, Gate 3 and closure | None | Keep |
| `os-init` | yes | Probe, scaffold or retrofit; `AGENTS.md` canonical; 3-layer memory; simulation identity | References still mention Gemini CLI (2) and `soul.md` (4) | Refresh |

### B. Improvement lab

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

### C. Ecosystem self-evolution

| Skill | Enabled | Purpose | Findings | Verdict |
|---|---|---|---|---|
| `os-evolution-planner` | no | Brainstorms 2-3 options, writes the plan and a Copilot delegation prompt | Hard-coded `claude-sonnet-4` (3); Gemini CLI; only reachable through `os-architect` | Refresh |
| `os-evolution-verifier` | no | Checks that `os-architect` produced real artifacts | Calls `scripts/run_evolution_scenario.py`, which exists nowhere in the repo; hard-coded model ID | Repair, or Review for retirement |
| `self-evolution` | no | 6-node evolution controller: proposal, sandbox, verify, receipt | Has its own approval and worktree states, parallel to group A's control plane | Review: overlap with group A |
| `repository-improvement` | no | Turns friction-cluster hotspot reports into refactoring proposals | Input comes from `dev-utils:github-issue-agent`; `cat references/map-debt.md` has no spoke link | Review |
| `evo-smoketest` | no | Temperature-conversion fixture for `scripts/smoke_test.py` | `scripts/evaluate.py` spoke missing | Fixture |

### D. Runtime kernel & memory

| Skill | Enabled | Purpose | Findings | Verdict |
|---|---|---|---|---|
| `os-health-check` | yes | Deterministic liveness report: event log, locks, memory | Mentions `os-state.json` (4); confirm that file is still produced | Keep (verify) |
| `os-memory-manager` | no | Promotes session facts to `context/memory.md` | References still teach `soul.md` and the CLAUDE.md hierarchy | Refresh |
| `os-clean-locks` | no | Removes stale `context/.locks/` files | Only useful where kernel locks are in use | Keep |

### E. Standalone audit utilities

| Skill | Enabled | Purpose | Findings | Verdict |
|---|---|---|---|---|
| `critical-auditor` | no | Adversarial full-system audit | Calls `scripts/audit_skill.py` (an `agent-scaffolders` script, not in the folder); overlaps `agent-scaffolders` audit skills and `cli-agents` red-team personas | Review |
| `issue-resolution-reviewer` | no | Checks closed GitHub issues were really fixed | Fits `dev-utils` (GitHub issue family) better than this plugin | Review: placement |
| `optimize-agent-instructions` | no | Audits and rewrites `AGENTS.md` | Superseded by `agent-scaffolders:create-agents-md` and `audit-agents-md` (added in #696); links `references/agents-md-contract.md`, which lives in that plugin; Gemini CLI (6) | Review: strongest retirement candidate |
| `todo-check` | no | Scans a file for TODO markers | Trivial as a capability, but `os-improvement-loop`'s quick start uses it as the demo eval target | Review: keep only as a lab fixture |

### F. Guidance

| Skill | Enabled | Purpose | Findings | Verdict |
|---|---|---|---|---|
| `os-guide` | no | Explains layers, memory and loops | Body names `AGENTS.md` as canonical, but the triggers still advertise "the CLAUDE.md hierarchy" and "soul.md or user.md" (11 `soul.md` mentions); does not explain group A at all | Refresh, or Review for retirement now that [two-improvement-paths.md](two-improvement-paths.md) covers the orientation |

## Cross-cutting findings

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
5. **17 dangling path-pointer files in `references/`** at the plugin root (e.g. `architecture.md`,
   `memory-hygiene.md`). Pointer files are a supported form that the installer resolves; these point
   at targets that no longer exist, so they install as one-line path text. 14 are referenced nowhere.
6. **Groups B, C and E are entirely disabled in this repo.** Everything enabled is in group A, plus
   `os-health-check`. That matches how the plugin is used: the control plane daily, the lab
   occasionally.

## Recommended next steps

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

## Evidence and limits

- Inputs: every `SKILL.md`, its `evals/`, its folder's links, references to it across `plugins/`,
  and this repo's ownership manifest.
- **Usage counts were not measured.** A transcript scan did not reliably detect skill invocations,
  so it is not used here. The usage pattern in cross-cutting finding 6 is the owner's own account.
- **Git dates are not a staleness signal.** Almost every skill folder was last committed on
  2026-10-02 in a bulk restructure.
- Verdicts flag evidence; they do not authorize deletion.
