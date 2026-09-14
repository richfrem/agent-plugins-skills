---
name: optimize-context
plugin: dev-utils
description: >
  Reduces AI agent context bloat across three dimensions: duplicate skill deduplication, instruction file optimization (CLAUDE.md, GEMINI.md to <= 80 lines), and session token efficiency.
  USE ONLY when trimming instruction files, diagnosing duplicate skill loading, or reducing agent token overhead.
allowed_tools:
  - run_command
  - view_file
  - write_to_file
  - replace_file_content
  - multi_replace_file_content
  - grep_search
  - list_dir
---

# Optimize Context (`optimize-context`)

> **Routing Directive:** USE ONLY when diagnosing token bloat, deduplicating installed skill mirrors, trimming instruction files, or auditing session efficiency.

The `optimize-context` skill enforces context hygiene through automated duplicate scanning, instruction file minimization, and delegation pattern guidance.

---

## Operational Execution Loop

1. **Phase 1: Skill Deduplication Scan**
   Run the duplicate scanner to identify redundant project/plugin skill copies:
   ```bash
   python3 plugins/dev-utils/scripts/optimize_context.py --dry-run
   ```
   If duplicates are found in `.claude/`, clear them to prevent double-loading while preserving `.agents/`:
   ```bash
   rm -rf .claude/skills/* .claude/agents/* .claude/commands/* .claude/hooks/*
   ```

2. **Phase 2: Instruction File Optimization**
   Audit `CLAUDE.md`, `GEMINI.md`, and `.github/copilot-instructions.md`.
   Ensure each file is lean (target ≤ 80 lines), keeping only behavioral gates and removing stale inventory tables.

3. **Phase 3: Session Token Efficiency**
   Check for delegation opportunities, enforce artifact passing over raw transcripts, and recommend `/compact` between tasks.

---

## Progressive Disclosure & References

- **Discovery Topology**: [references/deduplication-topology.md](references/deduplication-topology.md) — Claude Code vs multi-IDE loading hierarchy and fix mechanics.
- **Instruction Optimization**: [references/instruction-optimization.md](references/instruction-optimization.md) — what to keep vs cut, and mirror sync protocols.
- **Session Efficiency**: [references/session-efficiency.md](references/session-efficiency.md) — delegation rules, subagent dispatch tiers, and context compounding.
- **Acceptance Criteria**: [references/acceptance-criteria.md](references/acceptance-criteria.md) — structural pass/fail criteria and verification contracts.
- **Fallback Protocol**: [references/fallback-tree.md](references/fallback-tree.md) — failure recovery procedures and fallback rules.
