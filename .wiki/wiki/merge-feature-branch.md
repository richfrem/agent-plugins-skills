---
concept: merge-feature-branch
source: plugin-code
source_file: spec-kitty-plugin/assets/templates/merge.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.360056+00:00
cluster: plugin-code
content_hash: b5fbf5a1ba310aa5
---

# Merge Feature Branch

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Merge a completed feature into the main branch and clean up worktree
---

# Merge Feature Branch

This command merges a completed feature branch into the main/target branch and handles cleanup of worktrees and branches.

## Prerequisites

Before running this command:

1. ✅ Feature must pass `/spec-kitty.accept` checks
2. ✅ All work packages must be in `tasks/`
3. ✅ Working directory must be clean (no uncommitted changes)
4. ✅ You must be on the feature branch (or in its worktree)

## ⛔ Location Pre-flight Check (CRITICAL)

**BEFORE PROCEEDING:** You MUST be in the feature worktree, NOT the main repository.

Verify your current location:
```bash
pwd
git branch --show-current
```

**Expected output:**
- `pwd`: Should end with `.worktrees/001-feature-name` (or similar feature worktree)
- Branch: Should show your feature branch name like `001-feature-name` (NOT `main` or `release/*`)

**If you see:**
- Branch showing `main` or `release/`
- OR pwd shows the main repository root

⛔ **STOP - DANGER! You are in the wrong location!**

**Correct the issue:**
1. Navigate to your feature worktree: `cd .worktrees/001-feature-name`
2. Verify you're on the correct feature branch: `git branch --show-current`
3. Then run this merge command again

**Exception (main branch):**
If you are on `main` and need to merge a workspace-per-WP feature, run:
```bash
spec-kitty merge --feature <feature-slug>
```

---

## Location Pre-flight Check (CRITICAL for AI Agents)

Before merging, verify you are in the correct working directory by running this validation:

```bash
python3 -c "
from specify_cli.guards import validate_worktree_location
result = validate_worktree_location()
if not result.is_valid:
    print(result.format_error())
    print('\nThis command MUST run from a feature worktree, not the main repository.')
    print('\nFor workspace-per-WP features, run from ANY WP worktree:')
    print('  cd /path/to/project/.worktrees/<feature>-WP01')
    print('  # or any other WP worktree for this feature')
    raise SystemExit(1)
else:
    print('✓ Location verified:', result.branch_name)
"
```

**What this validates**:
- Current branch follows the feature pattern like `001-feature-name`
- You're not attempting to run from `main` or any release branch
- The validator prints clear navigation instructions if you're outside the feature worktree

**Path reference rule:** When you mention directories or files, provide either the absolute path or a path relative to the project root (for example, `kitty-specs/<feature>/tasks/`). Never refer to a folder by name alone.

## Final Research Integrity Check

Before merging research to main, perform final validation:

```bash
# Quick citation validation
python -c "
from pathlib import Path
from specify_cli.validators.research import validate_citations, validate_source_register

feature_dir = Path('kitty-specs/$FEATURE_SLUG')
evidence = feature_dir / 'research' / 'evidence-log.csv'
sources = feature_dir / 'research' / 'source-register.csv'

if evidence.exists():
    result = validate_citations(evidence)
    if result.has_errors:
        print('ERROR: Evidence log has citation errors')
        exit(1)

if sources.exists():
    result = validate_source_register(sources)
    if result.has_errors:
        print('ERROR: Source register has errors')
        exit(1)

print('✓ Citations validated')
"
```

## What This Command Does

1. **Detects** your current feature branch and worktree status
2. **Runs** pre-flight validation across all worktrees and the target branch
3. **Determines** merge order based on WP dependencies (workspace-per-WP)
4. **Forecasts** conflicts during `--dry-run` and flags auto-resolvable status files
5. **Verifies** working directory is clean (legacy single-worktree)
6. **Switches** to the target branch (default: `main`)
7. **Updates** the target branch (`git pull --ff-only`)
8. **Merges** the feature using your chosen strategy
9. **Auto-resolves** status file conflicts after each WP mer

*(content truncated)*

## See Also

- [[finishing-a-development-branch]]
- [[finishing-a-development-branch]]
- [[checklist-type-checklist-feature-name]]
- [[checklist-type-checklist-feature-name]]
- [[implementation-plan-feature]]
- [[feature-specification-feature-name]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/assets/templates/merge.md`
- **Indexed:** 2026-04-17T06:42:10.360056+00:00
