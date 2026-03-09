# ADR-001: Cross-Plugin Script Dependencies

## Status
Proposed

## Context
Historically within the `agent-plugins-skills` ecosystem, we have solved cross-plugin capabilities by directly executing another plugin's python scripts via relative paths or deep symlinks. For example, `tool-inventory` running `python ../../rlm-factory/scripts/distiller.py`. 

This tight coupling violates separation of concerns and breaks plugin encapsulation. It causes fragile dependencies (e.g., if a directory structure changes, the symlink breaks), makes it impossible to cleanly export or replicate a single plugin in isolation, and causes generic logic analyzers to throw false positives when scanning plugin directories.

We need a standardized architectural principle that governs how independent plugins share functionality without resorting to brittle file-path executions.

## Decision
**We will utilize Agent Skill Delegation instead of direct cross-plugin script execution.**

Instead of Plugin A physically executing Plugin B's python scripts via `subprocess` or `symlinks`, Plugin A will interact with the conversational layer (the Agent) to trigger Plugin B's defined **Skills**.

Implementation Rules:
1. **No Cross-Plugin Symlinks**: A plugin's `scripts/` directory must only contain scripts or symlinks that resolve *inside* that specific plugin's boundary.
2. **No Relative Python Executions**: `SKILL.md` workflows and internal python files must not execute `python ../../other-plugin/scripts/foo.py`.
3. **Decoupled Instructions**: If `tool-inventory` requires an RLM functionality (like cache clearing), it must prompt/instruct the Agent: *"Please trigger the `rlm-curator` skill to clear the cache."*

## Consequences
**Positive:**
- Perfect plugin encapsulation (plugins can be exported standalone).
- Eradicates brittle relative paths and deep symlinks.
- Eliminates code duplication (no "vendoring" scripts into multiple plugins).

**Negative:**
- Requires the Agent to orchestrate the step between the two tools, which may cost one additional inference cycle.
- Demands refactoring existing CLI tools to return prompts for the LLM rather than attempting to auto-invoke secondary scripts.

## Alternatives Considered
- **Script Vendoring**: Copying required scripts (e.g. `distiller.py`) directly into every plugin that needs it. Rejected due to extreme code duplication and high maintenance burden.
- **Shared Core Library**: Moving overlapping functionality into an installable `pip` dependency. Rejected because it shifts the system away from localized skills and towards monolithic software engineering, adding immense version control overhead.
