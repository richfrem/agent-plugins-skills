---
name: destructive-action-guard
description: Pre-verification protocol required before any file deletion, bulk cleanup, or stand-in conversion. Prevents data loss from blind cleanup passes.
metadata:
  type: feedback
---

# Destructive Action Guard

Before deleting files, bulk-removing stand-ins, or resolving broken references, run the full verification protocol below. **No exceptions.**

## Scope

This rule applies to:
- Deleting files (any file, anywhere)
- Removing stand-in / text-file pointer files
- Bulk cleanup operations (`rm`, `git rm`, script-driven deletion)
- Converting stand-ins to symlinks (targets may have moved)
- "Dead reference" cleanup from consolidation or migration

## Protocol

### Step 1 — Extract the target from each file

For a single-line text stand-in at path `P` containing relative path `T`:
```bash
cat P  # confirm single line, relative path
```

### Step 2 — Repo-wide target search

```bash
git ls-files | grep -i "<filename>"
```

**Decision:**
- Target found in repo → classify as **MISLOCATED_REFERENCE** — do not delete; propose correct path
- Target not found → proceed to Step 3

### Step 3 — Git history check

```bash
git log --all --oneline --full-history -- "**/filename"
```

**Decision:**
- File existed and was recently deleted → classify as **POSSIBLE_ACCIDENTAL_DELETION** — add to Map Debt; do not delete
- File only appears in consolidation/migration commits with no subsequent history → likely safe, classify as **DEAD_CROSS_REPO_REFERENCE**

### Step 4 — SKILL_ALIAS check (commands/ and agents/)

If content matches `../skills/<name>/SKILL.md` pattern AND the target SKILL.md exists:
- Classify as **SKILL_ALIAS** → convert to symlink, do not delete

### Step 5 — Produce audit table before any change

Output this table and wait for implicit confirmation (no new instruction = proceed, conflict = stop):

| File | Target | Exists in Repo | Classification | Action |
|------|--------|----------------|----------------|--------|

### Step 6 — Kill switch

**Stop and output the audit table only (no changes)** if any of the following:
- 5+ files classified POSSIBLE_ACCIDENTAL_DELETION
- Any ambiguity in target resolution
- Content is multi-line (not a stand-in)
- Target path resolves outside the repo

## Classification → Action Map

| Classification | Action |
|----------------|--------|
| DEAD_CROSS_REPO_REFERENCE | Delete |
| MISLOCATED_REFERENCE | Propose corrected path; do not modify |
| POSSIBLE_ACCIDENTAL_DELETION | Escalate to Map Debt; do not modify |
| SKILL_ALIAS | Convert to symlink via `symlink_manager create` |

## Why

The consolidation from 26 → 11 plugins left pre-consolidation stand-ins with cross-repo paths
that never existed post-merge. Blind deletion passes treat MISLOCATED and DEAD references
identically — but only DEAD ones are safe to remove. The distinction requires a git search.

This incident was caught during the dev-utils Opus review (2026-06-28): 19 stand-ins identified,
repo search revealed MISLOCATED and SKILL_ALIAS cases that would have been incorrectly deleted.
