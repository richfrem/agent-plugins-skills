---
concept: acceptance-criteria-os-guide
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-guide/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.153246+00:00
cluster: agent
content_hash: d0ca286134b79116
---

# Acceptance Criteria: os-guide

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: os-guide
**Version**: 2.0 | **Type**: Quality Assurance Matrix

The `os-guide` must successfully pass the following scenarios.

## ✅ Positive Scenarios (Must Execute Guide Protocol)

1. **Architectural Overview**: "What is an Agentic OS?" -> Agent successfully explains the Kernel (CLAUDE.md), RAM (context/), standard library (skills/), and processes (agents/).
2. **Setup Request Mapping**: "How do I add this OS to my repo?" -> Agent successfully directs the user to invoke `agentic-os-setup` rather than trying to perform the setup itself.
3. **Memory Explanation**: "How does Claude remember things between sessions here?" -> Agent correctly explains the dated session logs, hooks, and `os-memory-manager` promotion phase.
4. **Loop Explanation**: "What is the learning loop?" -> Agent describes the `Triple-Loop Retrospective` agent and how retrospectives lead to self-improving `./SKILL.md` rules.
5. **Progressive Disclosure**: User asks a complex question about hooks. Agent actively uses the `Read` tool to load `sub-agents-and-hooks.md` reference material before answering.

## ❌ Negative Scenarios (Must Halt or Fail Cleanly)

1. **Out of Scope Execution**: User asks "Initialize the OS now." The agent tries to write the `CLAUDE.md` file itself instead of delegating to `agentic-os-setup`. (FAIL condition).
2. **Hallucinated Concepts**: Agent explains concepts (like "Soul" or "RLM") that belong to other plugins and are not part of the standard `agentic-os` architecture documented in its references. (FAIL condition).


## See Also

- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-init]]
- [[acceptance-criteria-os-memory-manager]]
- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-clean-locks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-guide/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.153246+00:00
