# ADR-005: Plugin Separation of Concerns and Loose Coupling

## Status
Accepted

## Context
This repository houses an extensive ecosystem of agent plugins and skills, ranging from pure functional utilities (`context-bundler`, `mermaid-to-png`) to complex orchestration frameworks (`spec-kitty-plugin`, `agent-agentic-os`, `agent-loops`).

The landscape of frontier AI agent development (Anthropic, OpenAI, GitHub Copilot) is evolving aggressively. Frameworks like `spec-kitty` or `agent-agentic-os` act as **Transitional Architectures**. They currently provide desperately needed low-level plumbing—like deterministic TDD workflows, memory hierarchies, and continuous learning loops—that native Agent SDKs lack today. 

However, we anticipate that model providers will eventually subsume this plumbing directly into their core native environments. When that happens, tightly coupled ecosystems will break. If a foundational skill natively hardcodes a requirement to use `spec-kitty-plugin` or `agent-agentic-os` for its execution or memory persistence, it cannot be easily extracted, ported, or transitioned to superior native native tools when they are released.

## Decision
**We mandate strict Separation of Concerns and Loose Coupling across all plugins.** 

1. **Skills are Applications; Frameworks are the OS**: Functional skills (e.g., `mermaid-to-png`, `task-agent`) must never hard-depend on orchestration frameworks (e.g., `spec-kitty`, `agent-loop`, `agent-agentic-os`). They must remain perfectly agnostic to *how* they are executed.
2. **Pluggable Execution**: Sub-system plugins must operate in total isolation. For example, `agent-loops` must not require an awareness of `agent-agentic-os` to function. If a user only installs `agent-loops`, the plugin must work flawlessly on its own.
3. **Graceful Degradation**: If an advanced framework (like `spec-kitty`) is uninstalled or replaced by a superior native Claude Code feature in the future, the surrounding plugins must continue to operate via standard API surfaces and natural language without failing.
4. **No Deep State Entanglement**: Plugins must not directly manipulate the memory structures natively owned by other frameworks unless explicitly mediated by the target framework's documented interface.

## Consequences
**Positive:**
- **Future-Proofing**: When native SDks mature, we can violently replace frameworks like `spec-kitty` or `agentic-os` without requiring a rewrite of our pure functional skills.
- **Portability**: End-users can install `agent-loops` or `rlm-factory` in isolation without being forced to adopt our entire monolithic workflow stack.
- **Modularity**: We can swap out implementations (e.g., migrating from a custom memory manager to native Claude memory) completely transparently.

**Negative:**
- Requires highly disciplined interface boundaries.
- Cross-plugin workflows must rely entirely on loose Agent Delegation (via Natural Language or decoupled event logs) rather than direct code bindings or shared state dependencies.
