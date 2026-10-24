# Vector DB Cleanup (`vector-db-cleanup`)

Removes stale and orphaned chunks from the ChromaDB vector store when source files no longer exist on disk.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)

## Critical Constraints

1. **Write Operation**: Always specify the target `--profile` to prune the intended semantic space.
2. **API Integrity**: NEVER manipulate SQLite files directly; always execute `scripts/cleanup.py`.
3. **Transparency**: Report which profile was pruned and the total number of chunks removed.

## Quick start

Preview orphaned chunks for the intended wiki profile (no deletion):

```bash
python3 scripts/cleanup.py --profile wiki
```

## Workflow

1. **Identify Profile**: Verify active profiles in `.agent/learning/vector_profiles.json` (default: `wiki`).
2. **Preview Cleanup**: Run `scripts/cleanup.py --profile wiki` (default dry run), and review the candidate sources/chunks.
3. **Apply Authorized Cleanup**: Run `scripts/cleanup.py --profile wiki --apply` only within the approved deletion scope.
4. **Report Output**: State the target profile and total chunks removed.

## Verification

Verify store integrity and index consistency after cleanup:

```bash
python3 scripts/vector_consistency_check.py --profile wiki --topic .agent/learning/
```

## Interactive cleanup

Run this mode directly in the main conversation. Read collection configuration, compare indexed source metadata against current files, and preview orphan chunks before applying authorized deletions. Preserve supported API access and report candidate/removed counts and final collection health. Do not launch a dedicated cleanup agent.
