# ADR-001: Cross-Plugin Script Dependencies

## Status
Accepted

## Context
Within the `agent-plugins-skills` monorepo, a single Plugin often needs logic that another Plugin has already implemented. Historically this was solved by directly executing another plugin's python scripts via relative paths or deep symlinks -- for example, `tool-inventory` running `python ../../rlm-factory/scripts/distiller.py`.

This tight coupling violates separation of concerns and breaks plugin encapsulation. It causes fragile dependencies (e.g., if a directory structure changes, the symlink breaks), makes it impossible to cleanly export or replicate a single plugin in isolation, and causes generic logic analyzers to throw false positives when scanning plugin directories.

The ecosystem now operates on a **3-layer principle**:

1. **Source repo (dev time) - DRY**: One canonical file per resource, no duplication. Cross-plugin sharing in source is done via file-level symlinks. The mono-repo has all plugins present, so cross-plugin symlinks resolve correctly during development.
2. **Deploy time - Self-contained**: The bridge installer (`bridge_installer.py`) and `npx skills add` resolve all file-level symlinks to physical copies when installing into `.agents/`. Each installed skill is fully self-contained regardless of what other plugins are present.
3. **Runtime - Agent-orchestrated**: When a skill needs a capability from another plugin at runtime, it instructs the Agent to invoke that plugin's skill via the conversation layer -- not by calling scripts directly.

This combination eliminates both code duplication in source AND fragile runtime dependencies.

## Decision
**We will utilize Agent Skill Delegation instead of direct cross-plugin script execution.**

Instead of Plugin A physically executing Plugin B's python scripts via `subprocess` or `symlinks`, Plugin A will interact with the conversational layer (the Agent) to trigger Plugin B's defined **Skills**.

Implementation Rules:
1. **No Cross-Plugin Symlinks**: A plugin's `scripts/` directory must only contain scripts or symlinks that resolve *inside* that specific plugin's boundary.
2. **No Relative Python Executions**: `SKILL.md` workflows and internal python files must not execute `python ../../other-plugin/scripts/foo.py`.
3. **Decoupled Instructions**: If `tool-inventory` requires an RLM functionality (like cache clearing), it must prompt/instruct the Agent: *"Please trigger the `rlm-curator` skill to clear the cache."*

## Consequences
**Positive:**
- Perfect plugin encapsulation at deploy time (each installed skill runs standalone).
- DRY is maintained in the source repo -- no script is duplicated; cross-plugin file-level symlinks in source are resolved to physical copies at install time by the bridge installer and npx.
- Eradicates brittle relative paths and deep symlinks in deployed artifacts.
- Agent-level delegation keeps runtime coordination flexible and loosely coupled.

**Negative:**
- Agent-layer orchestration between plugins costs one additional inference cycle compared to a direct script call.
- Cross-plugin symlinks in source require both plugins to be present locally to resolve correctly during development (guaranteed in this mono-repo; only an issue if plugins are checked out in isolation).

## Related ADRs
- **ADR-002**: Governs within-plugin multi-skill script sharing (Hub-and-Spoke pattern).
- **ADR-003**: Governs file-level symlink structure within a plugin (file-level only, never directory-level).
- **ADR-004**: Governs self-containment mandate for the installed artifact; migration guide for removing legacy CONNECTORS.md cross-plugin dependencies.

## Alternatives Considered
- **Script Vendoring**: Copying required scripts (e.g. `distiller.py`) directly into every plugin that needs it. Rejected due to extreme code duplication and high maintenance burden.
- **Shared Core Library**: Moving overlapping functionality into an installable `pip` dependency. Rejected because it shifts the system away from localized skills and towards monolithic software engineering, adding immense version control overhead.
