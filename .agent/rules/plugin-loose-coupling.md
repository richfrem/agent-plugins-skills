---
description: Universal rules enforcing Separation of Concerns and Loose Coupling across all plugins.
globs: ["plugins/**/*.md", "plugins/**/scripts/*.py"]
---

## 🏛️ Separation of Concerns & Loose Coupling

**Full ADR context → `ADRs/005_plugin_separation_of_concerns_and_loose_coupling.md`**

### The Core Principle
1. **Transitional Architectures**: Heavy orchestration frameworks (e.g., `spec-kitty-plugin`, `agent-agentic-os`, `agent-loops`) are treated as *Transitional Architectures*. They exist only until native AI SDKs (like Claude or GitHub Copilot) build these operational features inherently. 
2. **Strict Decoupling (Skills are Apps)**: Functional skills and scripts must **NEVER** hard-code dependencies on transitional frameworks to execute.
3. **Pluggable Independence**: If a user runs `npx skills add <some-plugin>`, that plugin MUST function completely in isolation. It cannot crash or halt because `spec-kitty` or the `agent-agentic-os` memory manager happens to be missing.
4. **Agent Delegation over Code Interfaces**: If a plugin requires coordination with another plugin, it must do so via Natural Language agent instructions (e.g., *"Please invoke the `spec-kitty-agent` to..."*) rather than hardcoded Python imports, hidden filesystem state manipulations, or rigid cross-plugin bindings.
