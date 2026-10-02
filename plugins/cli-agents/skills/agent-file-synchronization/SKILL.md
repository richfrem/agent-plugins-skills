---
name: agent-file-synchronization
plugin: cli-agents
description: >
  Maintains AGENTS.md as the single canonical project instruction file and reports legacy
  CLAUDE.md, GEMINI.md, and .github/copilot-instructions.md mirrors without copying into them
  by default. Explicit target syncing remains an opt-in compatibility operation. Also reports
  drift between .agent/rules/ and matching plugins/*/rules/ sources. Triggers: "sync instructions",
  "sync AGENTS.md", "check instruction drift", "replicate instruction files", "check rule drift".
allowed-tools: Bash, Read, Write
---

# Agent File Synchronization (`agent-file-synchronization`)

Maintains AGENTS.md as the canonical project instruction file and inspects rule drift without blind overwrites.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [Target Preservations](#target-preservations)
- [References](#references)

## Constraints

1. **Dry-run first**: Always execute with `--dry-run` before `--execute`.
2. **Canonical authority**: `AGENTS.md` is the sole canonical source; legacy mirrors are opt-in compatibility targets only.
3. **No blind copies**: Preserve platform-specific sections (headers/tool mapping) automatically.
4. **Scope boundary**: This skill owns mechanical replication and drift detection, not instruction authoring or optimization.

## Quick start

Preview instruction synchronization across project instruction files:

```bash
python3 scripts/sync_instruction_files.py --dry-run
```

## Workflow

1. **Dry-Run Inspection**: Run `python3 scripts/sync_instruction_files.py --dry-run` and review diff summary.
2. **Execute Sync**: After human confirmation, run `python3 scripts/sync_instruction_files.py --execute`.
3. **Rule Drift Check**: Compare `.agent/rules/*.md` against matching `plugins/<plugin>/rules/*.md` sources:
   ```bash
   python3 scripts/sync_instruction_files.py --check-rules
   ```
4. **Reconcile Diffs**: On detected diffs, manually reconcile stale copies.

## Verification

Run the test suite to verify synchronization logic and preserved sections:

```bash
pytest plugins/cli-agents/skills/agent-file-synchronization/tests/test_sync_instruction_files.py
```

## Target Preservations

| Target | Preserved Section | Detection |
|---|---|---|
| `GEMINI.md` | `## Gemini CLI Tool Mapping` table | Tail marker match |
| `.github/copilot-instructions.md` | `# Copilot Instructions` header block | Header before body anchor |
| `AGENTS.md` | Custom header lines before anchor | Header before anchor |
| `CLAUDE.md` | Custom header lines before anchor | Header before anchor |

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for canonical instruction synchronization.
