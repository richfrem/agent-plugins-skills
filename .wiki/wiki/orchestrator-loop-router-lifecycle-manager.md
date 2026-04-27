---
concept: orchestrator-loop-router-lifecycle-manager
source: plugin-code
source_file: agent-loops/skills/orchestrator/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.728555+00:00
cluster: agent
content_hash: 7b62992f00e2e06e
---

# Orchestrator: Loop Router & Lifecycle Manager

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: orchestrator
description: "(Industry standard: Routing Agent / Orchestrator Pattern) Primary Use Case: Analyzing an ambiguous trigger and routing it to one of the specific specialized implementations. Routes triggers to the appropriate agent-loop pattern. Use when: assessing a task, research need, or work assignment and deciding whether to run a simple learning loop, red team review, dual-loop delegation, or parallel swarm. Manages shared closure (seal, persist, retrospective, self-improvement)."
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Orchestrator: Loop Router & Lifecycle Manager

The **Orchestrator** assesses the incoming trigger, selects the right loop pattern, and manages the shared closure sequence (seal, persist, retrospective, self-improvement).

## The Core Loop

### Ecosystem Context
- **Patterns**: [`learning-loop`](../learning-loop/SKILL.md) | [`red-team-review`](../red-team-review/SKILL.md) | [`dual-loop`](../dual-loop/SKILL.md) | [`agent-swarm`](../agent-swarm/SKILL.md) | [`triple-loop-learning`](../triple-loop-learning/SKILL.md)
- **Inner Loop Reference**: [`cli-agent-executor.md`](../../references/cli-agent-executor.md) — Persona configs for specialized CLI execution.

## Routing Decision Tree

Use this to select the correct loop pattern:

```
1. Does the trigger mention unguided friction evaluation, tests, and self-optimization?
   └─ YES → Pattern 5: triple-loop-learning
   └─ NO → continue

2. Is this work I can do entirely myself (research, document, iterate)?
   └─ YES → Pattern 1: learning-loop
   └─ NO → continue

3. Does it need adversarial review before proceeding?
   └─ YES → Pattern 2: red-team-review
   └─ NO → continue

4. Can the work be split into parallel independent tasks?
   └─ YES → Pattern 4: agent-swarm
   └─ NO → Pattern 3: dual-loop (sequential inner/outer delegation)
```

| Signal | Pattern | Skill |
|--------|---------|-------|
| Research question, knowledge gap, documentation task | **Simple Learning** | `learning-loop` |
| Architecture decision, security review, high-risk change | **Red Team Review** | `red-team-review` |
| Feature implementation, bug fix, single work package | **Dual-Loop** | `dual-loop` |
| Large feature, bulk migration, multi-concern parallel work | **Agent Swarm** | `agent-swarm` |
| Systemic rules generation, autonomous meta-optimizations | **Triple-Loop** | `triple-loop-learning` |

### Process Flow
1.  **Plan (Strategy)**: You define the work (Spec → Plan → Tasks). When planning scripts/pipelines, default to a "Modular Building Blocks" architecture (CLI wrappers + independent core modules).
2.  **Delegate (Handoff)**: You pack the context into a **Task Packet** and assist the user in handing off to the Inner Loop.
3.  **Execute (Tactics)**: The Inner Loop agent (which has *no* git access) writes code and runs tests.
4.  **Verify (Review)**: You verify the output against acceptance criteria.
5.  **Correct (Feedback)**: If verification fails, you generate a **Correction Packet** and loop back to step 3.
6.  **Retrospective (Learning)**: You assess the loop's success and document learnings.
7.  **Primary Agent Handoff (Closure)**: You signal the repository environment to seal the session, update databases, and commit to Git.

## Roles

### You (Outer Loop / Director)
- **Responsibilities**: Planning, Git Management, Verification, Correction, Retrospective.
- **Context**: Full repo access, strategic constraints (ADRs), long-term memory.
- **Tools**: `agent-orchestrator`, `git`, and optionally any upstream planning tool.

### Inner Loop (Executor / Worker)
- **Responsibilities**: Coding, Testing, Debugging.
- **Context**: Scoped to t

*(content truncated)*

## See Also

- [[triple-loop-learning-system-outer-orchestrator-inner-execution]]
- [[concurrent-agent-loop]]
- [[dual-loop-innerouter-agent-delegation]]
- [[exploration-workflow-sme-orchestrator]]
- [[learning-loop]]
- [[learning-loop-retrospective-post-seal]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-loops/skills/orchestrator/SKILL.md`
- **Indexed:** 2026-04-27T05:21:03.728555+00:00
