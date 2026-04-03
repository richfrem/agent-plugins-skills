---
name: fix-plugin-paths
description: >
  Fixes broken path references in plugin skill and agent files to ensure portability
  across installed environments. Use when you see "plugins/" paths in SKILL.md or agent
  files, need to standardize path references after installing a skill, want to audit and
  fix cross-plugin path dependencies, or are preparing plugin files for distribution via
  npx skills add or uvx.

  <example>
  Context: Agent just wrote a SKILL.md with a hardcoded source repo path.
  user: "Fix the plugin path references in this SKILL.md"
  assistant: [triggers fix-plugin-paths, audits file against portability rules, applies corrections]
  <commentary>
  Explicit path fix request on a skill file — run audit then apply fixes.
  </commentary>
  </example>

allowed-tools: Bash, Read, Write, Edit
---

# Identity: Plugin Path Portability Enforcer

You audit and fix path references in plugin skill and agent files to ensure they work
correctly when installed via `npx skills add`, the plugin installer, or `uvx`.

**The core rule:** When a skill is installed, only its own directory exists:
```
.agents/skills/<skill-name>/
  SKILL.md
  scripts/
  assets/
  references/
```
No `plugins/` folder. No `CLAUDE_PLUGIN_ROOT`. No source repo structure.

The full ruleset is in `references/fix-plugin-paths.prompt.md`.

---

## Phase 0: Identify Target

If the user specifies a file or directory, use those. Otherwise:
```bash
# Find all .md files in the current plugin folder with broken path references
grep -rl "plugins/[a-z][a-z-]*/" . --include="*.md" \
  | grep -v "CHANGELOG\|broken_symlinks\|repair_report" \
  | sort > /tmp/files_to_fix.txt
wc -l /tmp/files_to_fix.txt
```

---

## Phase 1: Audit a File

For each target file, check which rules from `references/fix-plugin-paths.prompt.md` apply:

```bash
grep -n "plugins/[a-z][a-z-]*/" <file> | grep -v "github.com\|\$\|<APS_ROOT>\|plugins/my-\|plugins/<"
grep -n "\.agents/skills/[a-z]" <file>
grep -n "/Users/" <file>
grep -n "{{PLUGIN_DIR}}" <file>
```

---

## Phase 2: Apply Fixes

Apply each rule from `references/fix-plugin-paths.prompt.md` manually using the Edit tool.
Verify with `diff` after each change.

⚠️ **Always verify the diff before applying.**
Apply only after confirming the diff is correct.

---

## Phase 3: Verify

After fixing, confirm no broken references remain:
```bash
grep -n "plugins/[a-z][a-z-]*/" <file> | grep -v "github.com\|\$\|<APS_ROOT>\|plugins/my-\|plugins/<"
grep -n "/Users/" <file>
```

Zero results = clean.

---

## 📋 Task Tracker Workflow (Standard Operating Procedure)

For repository-wide remediation, always follow this three-step cycle to ensure no files are missed and all fixes are verified.

### 1. Generate Task Tracker
Initialize a `portability-audit-report.md` artifact (or file) to act as the source of truth.
```bash
# Scan for all genuine issues (excluding false positive examples/github links)
grep -rn "plugins/" plugins/ --include="*.md" | \
grep -vE "github.com|\$|<APS_ROOT>|plugins/my-|plugins/<|plugins/\$" | \
grep -v "CHANGELOG\|broken_symlinks\|repair_report" | \
cut -d: -f1 | sort | uniq > /tmp/files_with_issues.txt

# Add absolute machine paths
grep -rl "/Users/" plugins/ --include="*.md" >> /tmp/files_with_issues.txt
sort -u /tmp/files_with_issues.txt -o /tmp/files_with_issues.txt
```
Populate the report with a checklist of these files.

### 2. Process One-by-One
- **Audit**: View the next file on the list and identify rule violations.
- **Fix**: Apply corrective edits manually.
- **Update**: Check off the file in the Task Tracker immediately after the fix is applied.
- **Repeat**: Proceed through every item on the list.

### 3. Final Verification
Perform a project-wide sweep to ensure zero remaining violations.
```bash
# Project-wide compliance sweep
grep -rn "plugins/" plugins/ --include="*.md" | \
grep -vE "github.com|\$|<APS_ROOT>|plugins/my-|plugins/<|plugins/\$" | \
grep -v "CHANGELOG\|broken_symlinks\|repair_report"
```
**Goal: Zero results found.**
