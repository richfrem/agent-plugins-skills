---
name: fix-plugin-paths
description: >
  Fixes broken path references in plugin skill and agent files to ensure portability
  across installed environments. Use when you see "plugins/" paths in SKILL.md or agent
  files, need to standardize path references after installing a skill, want to audit and
  fix cross-plugin path dependencies, run a portability audit on a repository, neutralize
  hardcoded machine paths like /Users/, find Python scripts using PROJECT_ROOT or Path()
  to reach into plugins/<name>/ at runtime, or are preparing plugin files for
  distribution via uvx or bootstrap.py. Also handles evolving a skill in-session while
  tracking quality scores with the eval runner to continuously improve skill routing accuracy.

  

  

  

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
  ./assets/
  references/
```
No `plugins/` folder. No `CLAUDE_PLUGIN_ROOT`. No source repo structure.

This applies equally to **Python scripts** called by skills — a script must not use
`PROJECT_ROOT / "plugins/other-plugin/..."` at runtime. Cross-plugin script references
must use `.agents/skills/<skill>/scripts/<script>` or a self-contained copy.

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

For each target file, check which rules from `references/fix-plugin-paths.prompt.md` apply using the auditor script:

```bash
python3 ./scripts/audit_plugin_paths.py <directory-or-file>
```

The auditor runs **two passes**:

1. **Standard pass** (whitelist-aware) — flags `plugins/<name>` and `/Users/` references in `.md` and `.py` files. False positives can be suppressed via `scripts/plugin_paths_whitelist.json`.
2. **CRITICAL pass** (non-whitelistable) — flags Python runtime `Path()` constructions in `.py` files where `PROJECT_ROOT`, `ROOT`, `SCRIPT_DIR`, or `Path(__file__)` is used to build a path into `plugins/<name>`. These **cannot be whitelisted** and must always be fixed.

For CRITICAL violations the correct fix is always one of:
- Replace with a relative `scripts/<script>.py` path (self-contained, portable)
- Replace with `.agents/skills/<skill-name>/scripts/<script>.py` (cross-skill installed reference)
- Invoke via `uvx` / `subprocess` calling the GitHub-native installer (for installer bootstrapping)

If the standard pass flags an issue that is functionally required (like a structural diagram or explicit documentation reference), **DO NOT MUTATE THE FILE**. Instead, update `scripts/plugin_paths_whitelist.json` using the Edit tool to include a targeted pattern that squashes the false positive, then re-run the auditor to confirm it cleanly skips that item.

---

## Phase 2: Apply Fixes

Apply each rule from `references/fix-plugin-paths.prompt.md` manually using the Edit tool.
Verify with `diff` after each change.

⚠️ **Always verify the diff before applying.**
Apply only after confirming the diff is correct.

---

## Phase 3: Verify

After fixing, confirm no broken references remain by rerunning the auditor:
```bash
python3 ./scripts/audit_plugin_paths.py <directory-or-file>
```

Zero results = clean.

---

## 📋 Task Tracker Workflow (Mode B — Repository-Wide Remediation)

For repository-wide remediation, always follow this three-step cycle.

### 1. Generate Task Tracker
Initialize the `scripts/portability-audit-report.md` artifact to act as the source of truth by running the auditor script:
```bash
python3 ./scripts/audit_plugin_paths.py .
```
This script will automatically generate the `scripts/portability-audit-report.md` formatted with a checkbox per file, itemizing exactly what line contains the issue.

### 2. Process One-by-One
- **Audit**: Read the generated `scripts/portability-audit-report.md` file to identify the next unchecked rule violation.
- **Fix**: Apply corrective edits manually to the corresponding file to neutralize the reference.
- **Whitelist (False Positives)**: If the item represents a structurally necessary path (like a URL or a diagram tree leaf), do **not** mutate the source file. Instead, open `scripts/plugin_paths_whitelist.json` and add a targeted global regex or file-specific string pattern to exempt it.
- **Regenerate & Verify**: Re-run `python3 ./scripts/audit_plugin_paths.py .` to update the report. Prove your fix worked by confirming that the issue dropped off the active report.
- **Repeat**: The skill must continuously loop through these steps, repeatedly running the script, reading the updated report, and applying fixes or whitelists, until all issues are processed.

### 3. Final Verification
The loop finishes strictly only when running the auditor returns a completely clean scan:
```bash
python3 ./scripts/audit_plugin_paths.py .
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
python3 <APS_ROOT>/plugins/agent-agentic-os/skills/os-eval-runner/scripts/evaluate.py \
  --skill . \
  --baseline --desc "initial baseline"
git add evals/ && git commit -m "baseline: fix-plugin-paths eval start"
```
Report the baseline score before continuing main work.

### C.3 Score after every SKILL.md edit
After each modification to `SKILL.md`:
```bash
python3 <APS_ROOT>/plugins/agent-agentic-os/skills/os-eval-runner/scripts/evaluate.py \
  --skill . \
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
