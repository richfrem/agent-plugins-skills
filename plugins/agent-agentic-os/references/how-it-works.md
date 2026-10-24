# How Agentic OS Works

Architecture notes for the plugin as a whole: the learning loop, memory, agent coordination, the research it builds on, and the governed task lifecycle. Skill-level procedures live in each skill's workflows.

## Contents

- [Learning loop](#learning-loop)
- [Memory system](#memory-system)
- [Agent coordination](#agent-coordination)
- [Research foundation](#research-foundation)
- [Governed task lifecycle](#governed-task-lifecycle)

## Learning loop

The core learning cycle lives in the `improving-skills-in-lab` skill. Its `loop` mode orchestrates multi-iteration improvement runs against a locked eval set, its `score` mode scores each mutation (KEEP or DISCARD), its `setup` mode isolates each run in a sibling repo, and its `backport` mode provides the human review gate before any winning change reaches production.

The execution pattern delegates inner-loop mechanics to the `orchestrating-agent-work` skill of the `agent-orchestration` plugin. That plugin supplies the loop substrate; this plugin adds the eval gate, the experiment log and lab isolation.

→ Full detail: [triple-loop.md](../skills/improving-skills-in-lab/references/triple-loop.md)

## Memory system

Every session writes structured logs to `context/events.jsonl`. At end of session the `memory` mode of `improving-skills-in-lab` deduplicates and promotes the most important facts to `context/memory.md`, a curated long-term store that bootstraps every future session. Dedup IDs and size limits prevent drift and contradiction over hundreds of sessions.

→ Diagram: [agentic-os-memory-subsystem.mmd](../skills/running-control-plane/references/diagrams/agentic-os-memory-subsystem.mmd)

## Agent coordination

Agents share state through `context/events.jsonl` and `context/.locks/`, not tight coupling. Outer supervisors set goals and review results; inner workers execute and signal completion in the shared log. Background agents surface findings in the next foreground session through promoted memory.

→ More detail: [summary.md](summary.md)

## Research foundation

The improvement loop implements the [Karpathy 3-file autoresearch pattern](../skills/improving-skills-in-lab/references/karpathy-autoresearch-3-file-eval.md) (eval, program, results). The architecture is independently validated by Lee et al., arXiv:2603.28052 (2026), which shows that code-space search over harness definitions, using an LLM proposer gated by objective evaluation, outperforms hand-designed harnesses across benchmarks.

→ Lab research: [lab references](../skills/improving-skills-in-lab/references/) • Control-plane research: [koubaa-2025](research/koubaa-2025-agent-os-blueprint.md), [sharma-2026](research/sharma-2026-aos-control-plane.md)

## Governed task lifecycle

The normal path is:

```text
Intake → Interview → Draft plan → Plan review / optional independent review
→ Human approval → Worktree implementation → Code review / recorded skip
→ Verification → Retrospective → Done
```

The interview captures plan-ready bullets and maintains a plan-outline artifact before the draft plan is written. Every legal transition is checked against its contract and persisted in SQLite. When evidence is incomplete, the task returns to the state that can repair the gap rather than silently bypassing the gate.

The control plane is native to this plugin and depends on no external workflow package. See [acknowledgments.md](acknowledgments.md) for the projects that shaped it.
