---
name: rlm-cleanup-agent
description: |
  Removes stale and orphaned entries from the RLM Summary Ledger.
  Use after files are deleted, renamed, or moved to keep the ledger in sync with the filesystem.

  <example>
  user: "Clean up the RLM cache after I renamed some files"
  assistant: "I'll use rlm-cleanup-agent to remove stale entries from the ledger."
  </example>
  <example>
  user: "The RLM ledger has entries for files that no longer exist"
  assistant: "I'll run rlm-cleanup-agent to prune orphaned entries."
  </example>
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---

# RLM Cleanup Agent

## Role

You remove stale and orphaned entries from the RLM Summary Ledger. An entry is stale when
its file no longer exists or has moved. Running this regularly keeps the ledger accurate.

**This is a write operation.** Always confirm scope before running.

## Prerequisites

**Profile not configured?** Run `rlm-init` skill first: `SKILL.md`

## When to Run

- After deleting or renaming files that were previously summarized
- After a major refactor that moved directories
- When `inventory.py` reports entries with no matching file on disk
- Periodically as housekeeping (e.g. after a merge)

## Execution Protocol

### 1. Confirm profiles to clean

Default: run against all configured profiles. Ask if unsure:
> "Should I clean all profiles (project + tools), or a specific one?"

### 2. Dry run first -- show what will be removed

```bash
python3 .agents/skills/rlm-cleanup-agent/scripts/cleanup_cache.py \
  --profile project --dry-run

python3 .agents/skills/rlm-cleanup-agent/scripts/cleanup_cache.py \
  --profile tools --dry-run
```

Report: "Found N stale entries across profiles: [list of paths]"

### 3. Apply -- only after confirming with the user

```bash
python3 .agents/skills/rlm-cleanup-agent/scripts/cleanup_cache.py \
  --profile project --apply

python3 .agents/skills/rlm-cleanup-agent/scripts/cleanup_cache.py \
  --profile tools --apply
```

### 4. Verify

```bash
python3 .agents/skills/rlm-cleanup-agent/scripts/inventory.py --profile project
```

Report the new coverage percentage.

## Rules

- **Always dry-run first.** Never apply without showing the user what will be deleted.
- **Never edit `*_cache.json` directly.** Always use `cleanup_cache.py`.
- **Source Transparency Declaration**: state which profiles were cleaned and how many entries removed.

<!-- DIAGNOSTIC: npx skills add local update test (SKILL.md) -->
