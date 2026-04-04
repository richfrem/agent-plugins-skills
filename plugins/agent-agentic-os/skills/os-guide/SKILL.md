---
name: os-guide
description: >
  Trigger with "explain agentic os", "how do I set up a persistent agent environment", 
  "what is the CLAUDE.md hierarchy", "explain the context folder structure", 
  "how does session memory work", "what is soul.md or user.md", "explain auto-memory or MEMORY.md", 
  "what is a loop scheduler or heartbeat", or when the user asks for the canonical guide.

  

  

  
allowed-tools: Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `../../requirements.txt` for the dependency lockfile (currently empty — standard library only).

---

# Agentic OS Guide

The core insight: LLMs are stateless functions. `CLAUDE.md` is the only file loaded by
default into every conversation. The **Agentic OS** pattern turns this constraint into a
full operating system metaphor.

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

## Skill Categories (Mental Model)

| Category | Skill | One-liner |
|---|---|---|
| **Orchestration** | `os-improvement-loop` | Multi-agent concurrent loop: ORCHESTRATOR + PEER + INNER |
| **Evaluation** | `os-eval-runner` | Autoresearch eval engine — scores and gates SKILL.md iterations |
| **Evaluation** | `os-eval-lab-setup` | Bootstraps isolated lab repos for eval runs |
| **Evaluation** | `os-eval-backport` | Reviews lab results, applies approved changes to master |
| **Mutation** | `os-skill-improvement` | RED-GREEN-REFACTOR routing accuracy improvement |
| **Memory** | `os-memory-manager` | Session log writing, L2→L3 promotion, deduplication |
| **Reporting** | `os-improvement-report` | Progress charts from results.tsv + improvement ledger |
| **Bootstrap** | `os-init` | Deploys kernel.py, agents.json, flywheel files to new project |
| **Utility** | `os-clean-locks` | Clears stale `.locks/` directories after agent crash |

Agents (not skills): `os-learning-loop` (trigger/diagnostic), `os-health-check` (liveness), `agentic-os-setup` (bootstrap interview)

## Execution Flow

Execute these phases in order. Do not skip phases. This skill uses **Progressive Disclosure**. Load only what you need:

1. For CLAUDE.md scope rules and precedence -> read `references/claude-md-hierarchy.md`
2. For context/ folder patterns (soul.md, user.md, memory.md) -> read `references/context-folder-patterns.md`
3. For /loop and heartbeat.md scheduling -> read `references/loop-scheduler.md`
4. For sub-agents, hooks, auto-memory -> read `references/sub-agents-and-hooks.md`
5. For memory hygiene (write/promote/archive rules) -> read `references/memory-hygiene.md`
6. For the full canonical directory tree -> read `references/canonical-file-structure.md`
7. For the self-improving OS flywheel and 3-file autoresearch framework -> read `references/research/optimizer-engine-patterns.md` and `references/research/karpathy-autoresearch-3-file-eval.md`

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

## Discovery: What Does the User Need?

Ask the user which aspect they need help with:

1. **Setting up** a new Agentic OS from scratch -> read `references/canonical-file-structure.md`, walk them through the setup
2. **Understanding** a specific layer (context/, hooks, /loop) -> load the matching reference file
3. **Memory management** (what to record, promote, archive) -> invoke `os-memory-manager` skill
4. **Continuous Improvement** (retrospectives, skill updates) -> invoke `os-learning-loop` agent
5. **Troubleshooting** (context not loading, skills not triggering) -> read `references/claude-md-hierarchy.md` for scope precedence

## The Improvement Flywheel (Mandatory Close Protocol)

Every significant work session — especially eval runs, skill edits, backports, and agent
loop completions — must close through this two-phase protocol. **Do not consider a session
complete without running both phases.**

> **Session Lifecycle Invariant**: The OUTER loop (`os-improvement-loop`) owns session
> lifecycle. INNER loops (`os-eval-runner`, `os-skill-improvement`) never close a session.
> A session is incomplete until Phase 6 is executed. `os-learning-loop` (agent) is the
> trigger/diagnostic layer that feeds both flywheels — it detects friction and identifies
> targets; `os-improvement-loop` (skill) is the execution protocol the agents follow once
> a target is identified.

```
Work → Backport/Ship → Phase 6: Capture → Phase 7: Improve
```

### Phase 6: Capture Learnings (os-memory-manager)

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

### Phase 7: Continuous Skill Improvement (os-skill-improvement)

> [!NOTE] Dependency: Requires **os-skill-improvement** (agent-agentic-os plugin).
> See [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md) for instructions.

After memory is captured, check whether any skill's routing or trigger accuracy was
found to be weak during the session:

```
If any skill mis-triggered, failed to trigger, or scored below 0.90 on eval:
→ Invoke os-skill-improvement on that skill
→ Run RED-GREEN-REFACTOR to harden the description and trigger phrases
→ Run os-eval-runner to verify the score improvement before committing
```

Apply the improvement filter — only invoke if:
- A skill failed to route correctly during the session
- An eval score was below threshold (< 0.90 quality_score, or accuracy/F1 below the established baseline in results.tsv)
- A trigger description was found to be too broad or too narrow
- A new `<example>` block or keyword was identified that would close a routing gap

Skip if:
- All skills routed correctly and eval scores held
- The session was purely additive (new files, no existing skill changes)

### The Full Flywheel

```
1. Work / Eval Run / Backport
2. os-eval-backport     → ACCEPT/ADAPT/REJECT each change, apply to master
3. os-memory-manager    → Session log + promote non-obvious findings (Phase 6)
4. os-skill-improvement → Harden any skill whose routing was found weak (Phase 7)
5. Commit + push        → Close the loop in git history
```

This flywheel is what makes the OS self-improving. Skipping Phase 6 or 7 means
knowledge evaporates at session end and skill quality drifts.

---

## Next Actions

- For memory write/promote/archive decisions -> invoke `os-memory-manager`
- To orchestrate an end-to-end setup of a new environment -> run `agentic-os-setup`
- To perform a retrospective and improve the OS -> run `os-learning-loop`
- To add a scheduled heartbeat -> read `references/loop-scheduler.md`

## Mandatory Close: Friction Signal (Every Invocation)

After answering the user's question, emit a friction event for anything that was unclear,
missing from the references, or required more turns than expected to explain:

```bash
# Only emit if friction was encountered — do not emit if explanation was clean
python3 context/kernel.py emit_event --agent os-guide \
  --type friction --action encountered \
  --summary "step:[which-reference] cause:[what-was-unclear]"
```

Then answer: **What one addition to the guide references would have made this explanation
clearer or faster?** Record the answer as a comment in the next session log or flag it
to `os-learning-loop` if the same gap appears across multiple sessions.
