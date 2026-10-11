---
name: optimize-agent-instructions
plugin: agent-agentic-os
description: >
  Audits and rewrites the canonical AGENTS.md instruction file in any repo. Strips stale
  or foreign content and applies Karpathy's four behavioral principles. It reports legacy
  CLAUDE.md, GEMINI.md, and .github/copilot-instructions.md mirrors but does not rewrite
  them by default, preventing instruction duplication and context bloat.
  Trigger when the user says "optimize my CLAUDE.md", "audit agent instructions",
  "improve my AGENTS.md", "apply Karpathy principles to my agent files", "clean up
  my copilot instructions", "review my GEMINI.md", or "update my AI instruction files".
allowed-tools: Read, Write, Bash
---

# Optimize Agent Instructions (`optimize-agent-instructions`)

Audits and rewrites the canonical `AGENTS.md` instruction file in any repository to preserve concise, high-signal behavioral constraints.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Single Canonical Authority**: `AGENTS.md` is the sole source of truth; never create separate conflicting rules in mirrors.
2. **Preserve Domain Invariants**: Never delete project-specific rules, architecture boundaries, or test commands without confirmation.
3. **No Stale Artifacts**: Strip personal usernames, dates, historical session notes, and outdated post-mortems.

## Quick start

Inspect the current instruction file for stale session notes and line count:

```bash
wc -l AGENTS.md CLAUDE.md GEMINI.md 2>/dev/null
```

## Workflow

1. **Discovery**: Inventory existing files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) and identify rules to preserve.
2. **Audit & Scoring**: Audit instruction files using `audit_agents_md.py` against progressive disclosure line budgets (target <= 100 lines), zero dates, zero ASCII trees, and inline invariants.
3. **Plan Rewrite**: Present explicit diff of removals (stale logs), additions (behavioral rules), and kept invariants.
4. **Synthesis**: Write lean, consolidated `AGENTS.md` adhering to the 5-part skeleton in `references/agents-md-contract.md`.
5. **Mirror Verification**: Ensure platform mirrors (`CLAUDE.md`) are minimal bridges (<= 5 lines) reading `AGENTS.md` (e.g. `Read [AGENTS.md](AGENTS.md)`). Never duplicate full-text rules.

## Verification

Confirm `AGENTS.md` contains core behavioral principles and zero stale notes:

```bash
head -n 40 AGENTS.md
```

## References

- [detailed-reference.md](references/detailed-reference.md) — 12-point Quality Checklist, Karpathy principles, and platform mappings.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for instruction optimizations.
- [fallback-tree.md](references/fallback-tree.md) — Remediation pathways when instruction files conflict.
