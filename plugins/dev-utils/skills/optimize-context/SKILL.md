---
name: optimize-context
plugin: dev-utils
description: >
  Reduces AI agent context bloat across three dimensions: duplicate skill deduplication, canonical AGENTS.md optimization, and session token efficiency.
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

# Optimize Context (optimize-context)

Reduces AI agent context bloat through duplicate skill deduplication, canonical AGENTS.md optimization, and session token hygiene.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Scope Boundary**: USE ONLY for diagnosing token bloat, deduplicating installed skill mirrors, trimming instruction files, or auditing session efficiency.
- **Destructive Action Gate**: Never delete duplicate skills or platform instruction files autonomously; deletions require explicit user confirmation.
- **Canonical Instruction Anchor**: Treat `AGENTS.md` as the sole canonical instruction authority; avoid blind synchronizations to legacy mirrors.
- **Artifact Passing**: Pass bounded structured artifacts rather than raw terminal traces between subagent boundaries.

## Quick start

```bash
# Scan for duplicate skills and context bloat (dry-run)
python3 plugins/dev-utils/skills/optimize-context/scripts/optimize_context.py --dry-run
```

## Workflow

1. **Phase 1: Skill Deduplication Scan**: Run `optimize_context.py --dry-run` to detect duplicate skill declarations across `.claude/` and workspace plugin roots.
2. **Phase 2: Instruction File Audit**: Review `AGENTS.md` against the target line budget and identify duplicate mirror surfaces.
3. **Phase 3: Session Token Efficiency**: Verify lean delegation patterns and enforce artifact passing over raw transcript dumps.
4. **Phase 4: Hygiene Verification**: Re-run diagnostic checks to confirm duplicate elimination and verify zero broken references.

## Verification

```bash
# Run context hygiene verification
python3 plugins/dev-utils/skills/optimize-context/scripts/optimize_context.py --dry-run

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/dev-utils/skills/optimize-context --mode source
```

## References
- [deduplication-topology.md](references/deduplication-topology.md) - Loading hierarchy and deduplication mechanics.
- [instruction-optimization.md](references/instruction-optimization.md) - Pruning guidelines and mirror sync rules.
- [session-efficiency.md](references/session-efficiency.md) - Delegation rules and subagent context boundaries.
- [acceptance-criteria.md](references/acceptance-criteria.md) - Verification contracts and test criteria.
- [fallback-tree.md](references/fallback-tree.md) - Failure recovery and fallback procedures.
