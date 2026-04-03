---
name: fix-plugin-paths
description: >
  Fixes broken path references in plugin skill and agent files to ensure portability
  across installed environments. Use when you see "plugins/" paths in SKILL.md or agent
  files, need to standardize path references after installing a skill, want to audit and
  fix cross-plugin path dependencies, run a portability audit on a repository, neutralize
  hardcoded machine paths like /Users/, or are preparing plugin files for distribution via
  npx skills add or uvx. Also handles evolving a skill in-session while tracking quality
  scores with the eval runner to continuously improve skill routing accuracy.

  <example>
  Context: Agent just wrote a SKILL.md with a hardcoded source repo path.
  user: "Fix the plugin path references in this SKILL.md"
  assistant: [triggers fix-plugin-paths, audits file against portability rules, applies corrections]
  <commentary>
  Explicit path fix request on a skill file — run audit then apply fixes.
  </commentary>
  </example>

  <example>
  Context: User wants all plugin files ready for distribution.
  user: "Run a portability audit on all SKILL.md files in this repo"
  assistant: [triggers fix-plugin-paths, generates task tracker, audits each file one-by-one, marks complete, runs final sweep]
  <commentary>
  Repository-wide remediation request — use the Task Tracker Workflow.
  </commentary>
  </example>

  <example>
  Context: Agent is mid-session doing related work and wants continuous skill improvement.
  user: "Evolve the fix-plugin-paths skill while you work"
  assistant: [triggers fix-plugin-paths Mode C, scaffolds evals if missing, establishes baseline, scores after each SKILL.md edit]
  <commentary>
  In-session evolution request — use Mode C: Direct Evolution Protocol.
  </commentary>
  </example>

allowed-tools: Bash, Read, Write, Edit
---

# Identity: Plugin Path Portability Enforcer

You audit, fix, and continuously improve plugin path portability in skill and agent files.
You ensure they work correctly when installed via `npx skills add`, the plugin installer, or `uvx`.

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

## Phase 0: Intake

If the user specifies a file or directory, confirm and proceed. Otherwise ask one question:

```
Scope:  <single file | plugin directory | full repository>
Mode:   A) Single audit     — fix one file now
        B) Repository audit — generate task tracker, fix all flagged files
        C) In-session evolve — continuously score SKILL.md after each edit
```

Auto-detect the scope if inferable from context. If mode is clear from the request, skip the question.

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

## 📋 Task Tracker Workflow (Mode B — Repository-Wide Remediation)

For repository-wide remediation, always follow this three-step cycle.

### 1. Generate Task Tracker
Initialize a `portability-audit-report.md` artifact to act as the source of truth.
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
Populate the report with a checkbox per file.

### 2. Process One-by-One
- **Audit**: View the next unchecked file and identify rule violations.
- **Fix**: Apply corrective edits manually.
- **Update**: Check off the file in the Task Tracker **immediately** after the fix is applied.
- **Repeat**: Proceed through every item on the list without skipping.

### 3. Final Verification
```bash
grep -rn "plugins/" plugins/ --include="*.md" | \
grep -vE "github.com|\$|<APS_ROOT>|plugins/my-|plugins/<|plugins/\$" | \
grep -v "CHANGELOG\|broken_symlinks\|repair_report"
```
**Goal: Zero results found.**

---

## 📊 Mode C: In-Session Direct Evolution Protocol

Use when evolving this skill's own `SKILL.md` as a background thread during an active session.
No worktree. No external repo. The agent itself is the proposer.

### C.1 Scaffold evals (if missing)
```bash
ls evals/evals.json 2>/dev/null || echo "MISSING"
```
If missing: draft 8 `should_trigger: true` + 4 `should_trigger: false` cases from the description
and `<example>` blocks. Write to `evals/evals.json`, `evals/results.tsv` (header), and
`references/program.md`.

### C.2 Establish baseline
```bash
python3 plugins/agent-agentic-os/skills/os-eval-runner/scripts/evaluate.py \
  --skill plugins/agent-plugin-analyzer/skills/fix-plugin-paths \
  --baseline --desc "initial baseline"
git add evals/ && git commit -m "baseline: fix-plugin-paths eval start"
```
Report the baseline score before continuing main work.

### C.3 Score after every SKILL.md edit
After each modification to `SKILL.md`:
```bash
python3 plugins/agent-agentic-os/skills/os-eval-runner/scripts/evaluate.py \
  --skill plugins/agent-plugin-analyzer/skills/fix-plugin-paths \
  --desc "<what changed>"
```
- **KEEP (exit 0)**: `git add SKILL.md && git commit -m "keep: score=<X> <desc>"`
- **DISCARD (exit 1)**: auto-reverted — try a different approach next edit
- **Report inline**: `📊 score: <prev> → <new> (<delta>) KEEP|DISCARD`

### C.4 Session close
When done or when the user says "stop":
- Print the full score trajectory from `evals/results.tsv`
- Flag for backport review if score improved >0.05

---

## Self-Assessment Survey (Mandatory after major runs)

After completing a full repository audit or a significant in-session evolution batch, record:

1. **Which files were hardest to classify?** (false positive risk)
2. **Which rule violations were most common?** (inform future evals)
3. **Did the task tracker stay accurate throughout?** (any missed updates)
4. **What one change to `fix-plugin-paths.prompt.md` would improve the next run?**

Write to: `temp/retrospectives/audit_<YYYYMMDD>_fix-plugin-paths.md`

---

## Operating Principles

- **One file at a time**: Never batch-apply fixes across multiple files in a single edit.
- **Zero tolerance**: A file is not "done" until `grep` confirms zero violations.
- **Tracker fidelity**: Update the task tracker immediately — never retroactively.
- **Score everything**: Every SKILL.md change gets scored before committing.
- **Strict rigor**: False positives (flagging correct paths) are as harmful as misses.
