# Exploration Output Quality

The exploration cycle produces portable, high-quality artifacts that any
downstream engineering process can consume. The exploration plugin does not
depend on or require any specific engineering framework.

## Output Artifacts

Exploration sessions produce:

- **Spec drafts** — structured problem/solution specifications
- **Plan outlines** — implementation approach with phases and milestones
- **Business requirements** — captured BRDs, user stories, constraints
- **Prototype observations** — validated assumptions and edge cases
- **Handoff packages** — bundled deliverables ready for engineering intake

## Downstream Consumers

These outputs are designed to be consumed by any spec-driven or plan-driven
engineering workflow, including this repository's own control plane (entry: the `os-control-intake` skill). Third-party examples are surveyed in [external-spec-frameworks.md](external-spec-frameworks.md).


The handoff package format is deliberately generic — a structured markdown
document with sections for requirements, decisions, open questions, and
recommended next steps. Any tool that reads markdown can consume it.

## Skill Improvement

If you want to improve exploration skills over time:

- The `os-lab-*` skills (scorer, loop, planner) in `agent-agentic-os`: objective evaluation and baseline-first improvement loops.
- The `orchestrating-agent-work` skill in `agent-orchestration`: the learning-loop modes (the former `triple-loop-learning`) for meta-learning behind eval gates.
