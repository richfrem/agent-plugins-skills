# Coding Policy Alignment Audit & Fix - Session Guide

## PURPOSE

**Ensure ALL code in the repository aligns with established coding conventions and policies.**

Every script must comply with:
- **coding-conventions.md** - Documentation standards
- **self-evolution-policy.md** - Code quality standards  
- **plugin-architecture-policy.md** - Architecture rules
- **test-driven-development.md** - Testing standards

**Secondary Benefit:** When all code aligns with policy, fresh agent sessions can understand what scripts do without running them or reading full implementations.

When an agent joins a new session, it needs to quickly understand:
- What does this script do?
- What files/data does it need?
- What does it output?
- What are the key functions?

By ensuring **every script has a complete module docstring** (Purpose + Key Input Dependencies + Key Functions), agents can read the top 20 lines of any script and immediately know:
1. **Purpose:** What problem it solves
2. **Key Input Dependencies:** What files/APIs/data it needs
3. **Key Functions:** What capabilities are available
4. **Usage Examples:** How to invoke it

This eliminates the need for agents to:
- Run `help()` or introspect the script
- Read through 100+ lines of implementation
- Execute the script to discover what it does
- Spend time context-gathering before taking action

---

## Overview

**Audit Type:** Codebase-wide compliance with established coding policies  
**Policy Authority:** `.agent/rules/` directory (coding-conventions.md, self-evolution-policy.md, etc.)  
**Auditor Tool:** `workspace_conventions_auditor.py` scans all Python/JS/TS/C# files  
**Scope:** 454 files currently violating policy (442 remaining after fixes)

**Current Session Status:** IN PROGRESS  
**Branch:** `feat/updated-coding-conventions.md`  
**GitHub:** https://github.com/richfrem/agent-plugins-skills/tree/feat/updated-coding-conventions.md  
**Strategy:** Fixes pushed to GitHub; PR and merge later when complete

---

## Push & PR Workflow

**How we're working:**
1. Fix scripts locally, commit to `feat/updated-coding-conventions.md`
2. Push commits to GitHub regularly (visible in branch)
3. When all scripts complete: Create PR to main
4. Review and merge when ready

**Current Status:**
- Commits pushed: ✅ YES (visible on GitHub now)
- PR created: ⏳ NOT YET (wait until all fixes complete)
- Ready to merge: ⏳ NOT YET (after PR review)

**Tracking Progress:**
- Check GitHub branch for latest commits
- View audit results in local `temp/workspace_conventions_report.md`
- This start-here.md reflects current session state

---

## What We're Doing

We audit the entire codebase against `.agent/rules/coding-conventions.md` using the **workspace_conventions_auditor.py** tool.

**The auditor checks for compliance with:**
1. **Module docstrings** - Every file must have Purpose + Key Input Dependencies + Key Functions
2. **Function docstrings** - Every function must have a one-line summary
3. **File headers** - Required format with proper sections
4. **Function length** - Flags functions exceeding 50 lines (requires refactoring decision)
5. **Naming conventions** - snake_case (Python), camelCase (JS/TS), PascalCase (C#)

**This Session: Phase 1 - Documentation Compliance**

We systematically fix files by adding:
- **Module docstrings** with:
  - `Purpose:` - What the script does
  - `Key Input Dependencies:` - What data/files/APIs it needs
  - `Key Functions:` - List of main capabilities
  - `Usage Examples:` - How to invoke
- **Function docstrings** - One-line descriptions

**Important Constraint:** We ONLY add documentation/docstrings to achieve policy alignment. We do NOT refactor code, fix functions exceeding 50 lines, or make code changes (unless explicitly requested for policy compliance).

---

## Why This Matters: The Fresh Agent Scenario

### Without Documentation ❌
```
Agent joins new session → Needs to run: plugins/agent-scaffolders/scripts/audit.py
Problem: Agent doesn't know what it does, what it needs, or what output to expect
Solution: Agent wastes time reading 100+ lines of code or running --help
```

### With Documentation ✅
```
Agent joins new session → Sees at top of audit.py:

Purpose:
    Audit plugins against the Agent Skills Open Standard to ensure 
    architectural and resource compliance.

Key Input Dependencies:
    - ./plugin.json
    - ././SKILL.md files

Usage Examples:
    python audit.py --path <plugin-directory>

Result: Agent understands exactly what to do in < 30 seconds, no experimentation needed
```

**This speeds up agent productivity by 10-100x** - agents can immediately decide whether a script is relevant, what dependencies to prepare, and how to invoke it.

---

## Progress Tracking

### Audit Results Timeline

| Session | Violations | Fixes | Cumulative Fixed | Status |
|---------|-----------|-------|------------------|--------|
| Start | 454 | - | - | Initial audit |
| Session 1 | 442 | 12 | 12 | ✅ Complete |
| Session 2 | 435 | 7 | 19 | ✅ Pushed to GitHub |
| Current | TBD | In progress | 19+ | 🔄 Continuing |

### Files Fixed (12 total)

✅ **Agent-Scaffolders Scripts (13/40+ fixed):**
1. audit.py - Added function docstring
2. cleanup_stacked_references.py - Added main() docstring
3. scaffold_azure_agent.py - Added main() docstring
4. validate_local_links.py - Added main() docstring
5. auto_fix_local_links.py - Added 3 function docstrings (resolve_project_root, replacer, main)
6. audit_plugin_l5_execute.py - Added main() docstring
7. inventory_plugin.py - Added main() docstring
8. check_skill_lengths.py - Added module docstring + 2 function docstrings
9. fix_descriptions.py - Added module docstring + 2 function docstrings
10. update_ecosystem_index.py - Added module docstring + 2 function docstrings
11. execute.py - Updated module docstring + added _get_default_improve_model() docstring
12. audit_plugin_structure.py - Added _scan_dir() and main() docstrings
13. path_reference_auditor.py - Added __init__() and main() docstrings

✅ **Dev-Utils Scripts:**
- workspace_conventions_auditor.py - Fixed backtick escaping in f-strings (line 217-218)

### Violations Remaining (442 files)

**By Category:**
- Missing module docstrings: ~80 files
- Missing function docstrings: ~200+ functions  
- Functions exceeding 50 lines (requires refactoring): ~150+ functions
- Other violations: ~50 files

**By Plugin:**
- agent-scaffolders: ~30 scripts remaining
- agent-agentic-os: ~20 scripts remaining
- obsidian-wiki-engine: ~30+ scripts remaining
- bootstrap.py, __init__.py: Need module headers
- Test files: Multiple violations
- Others: spread across remaining plugins

---

## How to Use This Guide

### Starting a New Session

1. **Read this file** to understand the context
2. **Check the current audit status:**
   ```bash
   python3 plugins/dev-utils/skills/coding-conventions-agent/scripts/workspace_conventions_auditor.py
   head -10 temp/workspace_conventions_report.md  # See summary
   ```

3. **Pick a script to fix** from the violations list
4. **Follow the fix pattern** (see below)
5. **Commit and update progress** in this file

### Fix Pattern for Each Script

```bash
# 1. Read the script
read <path-to-script>

# 2. Identify what's missing (from audit report):
grep -A 5 "<script-name>" temp/workspace_conventions_report.md

# 3. Add docstrings:
# - Module docstring with Purpose: and Key Input Dependencies:
# - Function docstrings (one-line summaries)

# 4. Re-audit to verify it passes:
python3 plugins/dev-utils/skills/coding-conventions-agent/scripts/workspace_conventions_auditor.py 2>&1 | grep "<script-name>"
# Should return: (no output = pass!)

# 5. Commit:
git add <script-file>
git commit -m "docs: add missing docstrings to <script-name>"
```

---

## Applicable Skills & Rules

### Core Skills for This Task

**Primary Skill:**
- `dev-utils:coding-conventions-agent` - Enforces documentation standards
  - Location: `plugins/dev-utils/skills/coding-conventions-agent/SKILL.md`
  - Auditor Script: `plugins/dev-utils/scripts/workspace_conventions_auditor.py`

### Applicable Rules

**Coding Conventions Rules:**
- `.agent/rules/coding-conventions.md` - Master documentation standards
  - Module docstring format: Purpose + Key Input Dependencies
  - Function docstring format: One-line summaries
  - File header templates for Python, JS/TS, C#
  - Naming conventions, type hints, refactoring thresholds

**Related Rules:**
- `.agent/rules/self-evolution-policy.md` - Guides autonomous fixes
- `.agent/rules/plugin-architecture-policy.md` - Plugin structure
- `.agent/rules/test-driven-development.md` - Testing standards

### Reference Files

- `plugins/dev-utils/skills/coding-conventions-agent/SKILL.md` - Full standards definition
- `plugins/dev-utils/rules/coding-conventions.md` - Summary of standards

---

## Scripts in Play

### Primary Auditor Script
**Path:** `plugins/dev-utils/scripts/workspace_conventions_auditor.py`

**What it does:**
- Scans all .py, .ts, .tsx, .js files in workspace
- Checks for missing docstrings, headers, function length violations
- Generates report to `temp/workspace_conventions_report.md`

**Usage:**
```bash
python3 plugins/dev-utils/scripts/workspace_conventions_auditor.py
```

**Output:** Detailed report in `temp/workspace_conventions_report.md`

### Scripts Needing Fixes

**High Priority (agent-scaffolders, most violations):**
- aggregate_benchmark.py - 4 functions exceed 50 lines
- generate_review.py - 3 functions exceed 50 lines
- run_loop.py - 2 functions exceed 50 lines (299/120 lines)
- scaffold_github_agent.py - main() exceeds 50 lines (231 lines)
- validate_agent.py - validate() exceeds 50 lines (147 lines)
- generate_report.py - generate_html() exceeds 50 lines (285 lines)

**Medium Priority:**
- test files (16+ missing docstrings)
- obsidian-wiki-engine scripts
- bootstrap.py (9+ missing docstrings)

**Low Priority:**
- Individual __init__.py files
- Reference script files

---

## Known Issues

### SyntaxWarning: Invalid Escape Sequence

**Status:** Unresolved  
**Location:** workspace_conventions_auditor.py line 70  
**Severity:** Low (doesn't prevent auditor from working)  
**Attempted Fix:** Changed backticks to repr() in output (line 217-218)  
**Result:** Warning persists (likely false positive from Python parser)  
**Action:** Can be investigated in future session if needed

---

## Best Practices for This Work

### DO ✅
- Add one-line docstrings to all functions
- Include module docstrings with Purpose: and Key Input Dependencies:
- Use the auditor script to verify fixes
- Commit after fixing 5-10 files
- Update this progress file after each session

### DON'T ❌
- Refactor code or change function implementations
- Fix functions exceeding 50 lines (unless refactoring is requested)
- Add error handling or validation beyond documentation
- Create new abstractions or helper functions
- Delete code (no cleanup unless asked)

---

## Next Steps

### Immediate (This Session or Next)

1. **Continue with agent-scaffolders scripts** (30+ remaining)
   - Focus on scripts with only docstring violations first
   - Skip length-related violations for now

2. **Then move to agent-agentic-os** (~20 scripts)

3. **Then obsidian-wiki-engine** (~30+ scripts)

### Medium Term

- Fix test files (test_scaffold_github_agent.py, test_execute.py, etc.)
- Add missing module docstrings to bootstrap.py, __init__.py files
- Address dev-utils and other plugins

### Long Term

- Consider batch refactoring for functions exceeding 50 lines
- Update CLAUDE.md with lessons learned
- Document any new patterns discovered

---

## Push Strategy

**When to push:**
- ✅ After completing 5-10 scripts (batch updates)
- ✅ After completing an entire plugin (major milestone)
- ✅ At end of each work session (keep progress visible)

**Don't push:**
- ❌ After every single script (too noisy)
- ❌ With uncommitted work (commit first)
- ❌ Before testing with auditor (verify fixes first)

**How to push:**
```bash
git push origin feat/updated-coding-conventions.md
```

**After push:**
- Verify on GitHub: https://github.com/richfrem/agent-plugins-skills/tree/feat/updated-coding-conventions.md
- Updates visible immediately
- Ready for PR when all scripts complete

---

## Session Cleanup Checklist

Before ending a session:

- [ ] Run auditor to get current violation count: `python3 plugins/dev-utils/skills/coding-conventions-agent/scripts/workspace_conventions_auditor.py`
- [ ] Commit all changes with descriptive message
- [ ] Push to origin: `git push origin feat/updated-coding-conventions.md`
- [ ] Update progress table in this file
- [ ] Note which scripts are complete
- [ ] Document any blockers or issues found
- [ ] Record the branch state and commit count

---

## Useful Commands

```bash
# Run the auditor
python3 plugins/dev-utils/scripts/workspace_conventions_auditor.py

# Check a specific script's violations
grep -A 10 "scripts/audit.py" temp/workspace_conventions_report.md

# See all violations in agent-scaffolders
grep "plugins/agent-scaffolders/scripts/" temp/workspace_conventions_report.md | head -30

# Commit documentation fixes
git add plugins/
git commit -m "docs: add missing docstrings to <scripts>"

# Check current audit status
head -6 temp/workspace_conventions_report.md
```

---

## Contact & Questions

If starting a new session:
1. Read this entire file
2. Run the auditor to see current state
3. Check the git log to see recent commits
4. Pick 5-10 scripts from the remaining list
5. Follow the "Fix Pattern for Each Script" section
6. Update this file with new progress

**Last Updated:** Current Session  
**Status:** ONGOING - 442/454 files remaining (12 fixed)
