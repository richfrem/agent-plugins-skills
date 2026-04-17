---
concept: exploration-output-quality
source: plugin-code
source_file: exploration-cycle-plugin/references/exploration-output-standards.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.594951+00:00
cluster: agent
content_hash: df30c875f1ecba71
---

# Exploration Output Quality

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
engineering workflow. Examples from `github.com/richfrem/agent-plugins-skills`:

- **superpowers** — write-plan / execute-plan workflow
- **spec-kitty** — specify → plan → tasks → implement lifecycle
- **agent-execution-disciplines** — TDD, debugging, verification disciplines

The handoff package format is deliberately generic — a structured markdown
document with sections for requirements, decisions, open questions, and
recommended next steps. Any tool that reads markdown can consume it.

## Skill Improvement

If you want to improve exploration skills over time:

- **agent-agentic-os** — `os-skill-improvement`, `os-eval-runner` for objective evaluation
  - https://github.com/richfrem/agent-plugins-skills/tree/main/plugins/agent-agentic-os
- **agent-loops** — `triple-loop-learning` for meta-learning via eval gates
  - https://github.com/richfrem/agent-plugins-skills/tree/main/plugins/agent-loops


## See Also

- [[output-templates]]
- [[pattern-action-forcing-output-with-deadline-attribution]]
- [[complexity-tiered-output-templating]]
- [[local-interactive-output-viewer-loop]]
- [[output-classification-tagging]]
- [[severity-stratified-output-schema-with-emoji-triage]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/references/exploration-output-standards.md`
- **Indexed:** 2026-04-17T06:42:09.594951+00:00
