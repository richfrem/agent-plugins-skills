# os-guide — Detailed Reference

Extracted from SKILL.md per Layer-1 procedural-core line budget (issue #551).

## Dependencies

Requires **Python 3.8+** and standard library only. No external packages needed.

```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `../../requirements.txt` for the dependency lockfile (currently empty — standard library only).

## OS Concept Mapping (full table)

| OS Concept | Agent Equivalent |
|------------|-----------------|
| Kernel | `CLAUDE.md` hierarchy (global -> org -> project -> local) |
| RAM | `context/` folder (soul, user prefs, memory) |
| Disk | `context/memory/YYYY-MM-DD.md` dated session logs |
| Stdlib | `skills/` procedural knowledge bundles |
| Processes | `.claude/agents/` sub-agents with isolated context |
| Shell | `.claude/commands/` slash commands |
| Cron | `/loop` + `heartbeat.md` scheduled background tasks |
| Boot | `START_HERE.md` + `MEMORY.md` bootstrap on session start |
| Autoresearch Loop | `os-eval-runner` + `improvement-ledger.md` |

## Skill Categories (full table)

| Category | Skill | One-liner |
|---|---|---|
| **Orchestration** | `os-improvement-loop` | Multi-agent concurrent loop: ORCHESTRATOR + PEER + INNER |
| **Evaluation** | `os-eval-runner` | Autoresearch eval engine — scores and gates SKILL.md iterations |
| **Evaluation** | `os-eval-lab-setup` | Bootstraps isolated lab repos for eval runs |
| **Evaluation** | `os-eval-backport` | Reviews lab results, applies approved changes to master |
| **Mutation** | `os-improvement-loop` | RED-GREEN-REFACTOR routing accuracy improvement |
| **Memory** | `os-memory-manager` | Session log writing, L2→L3 promotion, deduplication |
| **Reporting** | `os-improvement-report` | Progress charts from results.tsv + improvement ledger |
| **Bootstrap** | `os-init` | Deploys kernel.py, agents.json, Triple-Loop files to new project |
| **Utility** | `os-clean-locks` | Clears stale `.locks/` directories after agent crash |
| **Diagnostic** | `os-health-check` | Scans event bus, lock state, and memory liveness (migrated from agent, 2026-09-05) |

Agents (not skills): `Triple-Loop Retrospective` (trigger/diagnostic), `agentic-os-setup` (bootstrap interview)

## Quick Orientation

### Anthropic-Native vs Community-Layered

**What Anthropic ships natively:**
- CLAUDE.md layered discovery (global, org, project, local, subdirectory scopes - most specific wins)
- Auto-memory (`MEMORY.md`) - Claude writes this itself with build commands, style prefs, architecture decisions
- `/loop` command for cron-style scheduling (up to 50 tasks per session, auto-expire after 3 days)
- Agent Skills: `SKILL.md`-based procedural knowledge bundles
- Sub-agents in `.claude/agents/` with isolated tool contexts

**What the community layered on top:**
- `context/soul.md`, `context/user.md`, `context/memory/{date}.md` folder conventions
- `START_HERE.md` bootstrap prompt pattern
- Lessons-learned -> update-skills-after-session loop
- `heartbeat.md` scheduled task definition files

## Design Principle

> Every line in `CLAUDE.md` competes for attention with actual work.
> Keep it under 300 lines. Focus on what Claude would get wrong without it.
> Use `@import context/soul.md` to load identity on demand, not always.

## Phase 6 — Capture Learnings (full detail)

> [!NOTE] Dependency: Requires **os-memory-manager** (agent-agentic-os plugin).
> See [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md) for instructions.

After any backport, eval run, or skill change:

```
Invoke os-memory-manager to write a dated session log and promote non-obvious
findings to long-term memory. Apply the non-obvious filter:
- CAPTURE: snags, footguns, scoring behaviors, architectural decisions, ADAPT patterns
- SKIP: routine score improvements, changes self-evident from the diff
```

What to capture:
- What was accomplished and what changed
- Any errors, workarounds, or unexpected behaviors encountered
- Key decisions and why (especially ACCEPT/ADAPT/REJECT rationale from backports)
- Open items and follow-up rounds

Where it writes:
- `context/memory/YYYY-MM-DD.md` — dated session log (git-tracked, not temp/)
- `context/memory.md` — promoted long-term facts with dedup IDs
- Agent's native `MEMORY.md` system — cross-session feedback entries
- Survey save path rule: lab/eval sessions write surveys to `temp/retrospectives/`; loop sessions (os-improvement-loop) write to `context/memory/retrospectives/`. post_run_metrics.py only scans `context/memory/retrospectives/` — lab surveys are not counted in loop metrics.

## The Full Triple-Loop

```
1. Work / Eval Run / Backport
2. os-eval-backport     → ACCEPT/ADAPT/REJECT each change, apply to master
3. os-memory-manager    → Session log + promote non-obvious findings (Phase 6)
4. os-improvement-loop → Harden any skill whose routing was found weak (Phase 7)
5. Commit + push        → Close the loop in git history
```

This Triple-Loop is what makes the OS self-improving. Skipping Phase 6 or 7 means
knowledge evaporates at session end and skill quality drifts.
