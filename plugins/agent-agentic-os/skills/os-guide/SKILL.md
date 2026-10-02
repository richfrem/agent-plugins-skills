---
name: os-guide
plugin: agent-agentic-os
description: >
  Trigger with "explain agentic os", "how do I set up a persistent agent environment",
  "what is the CLAUDE.md hierarchy", "explain the context folder structure",
  "how does session memory work", "what is soul.md or user.md", "explain auto-memory or MEMORY.md",
  "what is a loop scheduler or heartbeat", or when the user asks for the canonical guide.
allowed-tools: Read, Write
---

# Agentic OS Guide (`os-guide`)

Explains the Agentic OS pattern, mapping operating system primitives (kernel, RAM, storage, processes, scheduler) onto stateless LLM development environments.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Layer Mapping](#layer-mapping)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Explanatory Only**: This skill guides and explains; delegate automated setups to `agentic-os-setup` or `os-init`.
2. **Canonical Terminology**: Do not invent external metaphors; preserve standard kernel/RAM/disk architecture.
3. **Progressive Disclosure**: Load specific architectural reference documents only when requested by user queries.

## Quick start

Inspect the canonical Agentic OS directory layout:

```bash
cat references/canonical-file-structure.md
```

## Workflow

1. **Classify User Query**: Determine whether user is setting up, troubleshooting, or exploring memory/scheduling.
2. **Consult Layer Reference**: Load relevant topic doc (`claude-md-hierarchy.md`, `context-folder-patterns.md`, etc.).
3. **Provide Architectural Guidance**: Explain concepts using the core OS metaphor and file paths.
4. **Direct Next Action**: Recommend appropriate execution skill (`os-init`, `os-memory-manager`, etc.).

## Layer Mapping

| OS Concept | Agentic OS Implementation |
|---|---|
| Kernel | Canonical instruction file (`AGENTS.md`) |
| RAM / Volatile | Session context (`context/status.md`, scratchpads) |
| Non-volatile Disk | Dated session logs (`context/memory/YYYY-MM-DD.md`) |
| Processes / Daemons | Sub-agents and periodic cron heartbeat scripts |

## Verification

Confirm reference documentation is readable and accessible:

```bash
test -f "references/canonical-file-structure.md" && echo "Documentation verified"
```

## References

- [detailed-reference.md](references/detailed-reference.md) — Comprehensive guide to Agentic OS design patterns.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for guidance accuracy.
- [fallback-tree.md](references/fallback-tree.md) — Remediation pathways when inquiries diverge from core architecture.
- [canonical-file-structure.md](references/canonical-file-structure.md) — Definitive folder structure specification.
