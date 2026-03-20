# Acceptance Criteria: agentic-os-guide
**Version**: 2.0 | **Type**: Quality Assurance Matrix

The `agentic-os-guide` must successfully pass the following scenarios.

## ✅ Positive Scenarios (Must Execute Guide Protocol)

1. **Architectural Overview**: "What is an Agentic OS?" -> Agent successfully explains the Kernel (CLAUDE.md), RAM (context/), standard library (skills/), and processes (agents/).
2. **Setup Request Mapping**: "How do I add this OS to my repo?" -> Agent successfully directs the user to invoke `agentic-os-setup` rather than trying to perform the setup itself.
3. **Memory Explanation**: "How does Claude remember things between sessions here?" -> Agent correctly explains the dated session logs, hooks, and `session-memory-manager` promotion phase.
4. **Loop Explanation**: "What is the learning loop?" -> Agent describes the `os-learning-loop` agent and how retrospectives lead to self-improving `./SKILL.md` rules.
5. **Progressive Disclosure**: User asks a complex question about hooks. Agent actively uses the `Read` tool to load `sub-agents-and-hooks.md` reference material before answering.

## ❌ Negative Scenarios (Must Halt or Fail Cleanly)

1. **Out of Scope Execution**: User asks "Initialize the OS now." The agent tries to write the `CLAUDE.md` file itself instead of delegating to `agentic-os-setup`. (FAIL condition).
2. **Hallucinated Concepts**: Agent explains concepts (like "Soul" or "RLM") that belong to other plugins and are not part of the standard `agentic-os` architecture documented in its references. (FAIL condition).
