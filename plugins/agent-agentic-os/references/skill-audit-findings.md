# agent-agentic-os Skill Audit Findings

Staleness, broken references and retirement candidates for all 28 skills. For what each skill does
and how the clusters relate, see [skill-catalog.md](skill-catalog.md).
This is a point-in-time audit. Recheck the evidence before acting on any verdict, and never delete a
skill without an explicit instruction naming its path (Skill Deletion Guard).

## Contents

- [Per-skill verdicts](#per-skill-verdicts)
- [Cross-cutting findings](#cross-cutting-findings)
- [Recommended next steps](#recommended-next-steps)
- [Evidence and limits](#evidence-and-limits)

## Per-skill verdicts

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
