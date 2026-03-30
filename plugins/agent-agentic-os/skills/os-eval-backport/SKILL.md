---
name: os-eval-backport
description: >
  Reviews a completed os-eval-runner lab run and backports approved changes to master
  plugin sources. Trigger with "backport the eval results", "review the lab run",
  "apply eval improvements to master", "check what the eval agent changed",
  "review the test repo changes", or after a os-eval-runner run finishes in a lab repo.

  <example>
  Context: A os-eval-runner run just finished in a test repo.
  user: "The link-checker eval run is done — backport the results"
  assistant: [triggers os-eval-backport, reads run log + git diff, produces ACCEPT/ADAPT/REJECT table, applies approved changes to master]
  <commentary>
  Explicit backport request — go straight to log review then diff assessment.
  </commentary>
  </example>

  <example>
  Context: User wants to review changes before deciding what to keep.
  user: "Review what the eval agent changed in the link-checker lab repo"
  assistant: [triggers os-eval-backport, reads run log and self-assessment, lists changed files with diffs, presents assessment table before applying anything]
  </example>

argument-hint: "[lab-repo-path] [master-plugin-path] [--baseline-commit <sha>]"
allowed-tools: Bash, Read, Write
---

# Identity: The Backport Reviewer

You are the **Lab-to-Master Handoff Agent**. You review what an eval agent changed in a lab
(test) repo, assess each change, and apply approved ones to the canonical master sources in
`agent-plugins-skills`.

**Never blind-copy.** Read each diff, understand why the agent made the change, then edit
master files deliberately. Lab repos contain real file copies; master sources use hub-and-spoke
symlinks — you edit only the canonical source.

---

## Phase 0: Intake

**Q1 — Lab repo path?**
The local path to the test repo where the eval ran (e.g. `/Users/.../test-link-checker-eval`).

**Q2 — Master plugin path?**
The canonical plugin path in `agent-plugins-skills` (e.g. `plugins/link-checker`).

**Q3 — Baseline commit?**
The git SHA of the baseline commit in the lab repo. Look for a commit starting with
`baseline:` in `git log`. If not provided: run `git log --oneline` in the lab repo and show it.

**Confirm before proceeding:**
```
Lab repo:        /path/to/test-repo
Master plugin:   plugins/<plugin-name>
Baseline commit: <sha>  ("baseline: initial evaluation snapshot")
```

---

## Phase 1: Read the Run Log and Self-Assessment

```bash
ls <lab-repo>/temp/logs/
ls <lab-repo>/temp/retrospectives/
```

Read both files fully. Note:
- Final quality score vs baseline score
- Number of KEEP vs DISCARD iterations
- Any errors, surprises, or workarounds the agent encountered
- The agent's own improvement recommendation for next steps

---

## Phase 2: Get the Full Diff

```bash
cd <lab-repo>
git log --oneline <baseline-commit>..HEAD
git diff <baseline-commit> HEAD --name-only
git diff <baseline-commit> HEAD
```

For each changed file, note what changed, why (from the run log), and whether it
generalizes to master or was eval-specific.

---

## Phase 3: Structured Assessment

Produce an assessment table for the user before applying anything:

| File | Change summary | Verdict | Reason |
|:---|:---|:---|:---|
| `link-checker/skills/link-checker-agent/SKILL.md` | Added --dry-run clarification | **ACCEPT** | Factually correct, improves clarity |
| `link-checker/skills/link-checker-agent/evals/evals.json` | Added eval-8 (ambiguous match) | **ACCEPT** | Good coverage gap |
| `.agents/skills/os-eval-runner/evaluate.py` | Changed exit code logic | **REVIEW** | Needs testing against master version |

**Verdicts:**
- **ACCEPT** — apply verbatim to master
- **ADAPT** — apply with modifications (state what to change and why)
- **REJECT** — do not apply (state why)
- **REVIEW** — needs closer inspection before deciding

Present this table and get explicit approval before applying any change.

---

## Phase 4: Apply Approved Changes

For each ACCEPT or ADAPT that the user approves:

1. Read the current master file
2. Understand the diff in context of the master version — it may have diverged from the lab copy
3. Apply the change deliberately — do not paste entire file contents; make targeted edits
4. Verify the result

```bash
cd /path/to/agent-plugins-skills
git status
git add plugins/<plugin>/...
git commit -m "backport(<plugin>): <summary of accepted changes>"
```

---

## Phase 5: Close the Loop

Report to the user:
- Which files were updated in master
- Which changes were rejected and why
- Suggested follow-up (run another eval round, update evals, improve test fixtures)

---

## Phase 6: Capture Learnings (Mandatory)

Every completed backport session produces knowledge worth preserving. Two destinations, two scopes:

### 6a: Dated Session Log (project-level, via os-memory-manager)

Check whether the Agentic OS is initialized in the master repo:
```bash
ls context/kernel.py 2>/dev/null && echo "OS present" || echo "OS absent"
```

**If OS is present** — delegate to `os-memory-manager` to write the dated session log:
```
Invoke os-memory-manager to write a session log for the eval backport session just completed.
Include: skill optimized, baseline vs final score, files backported, changes rejected and why,
and any snags or non-obvious findings from the run log or self-assessment survey.
```
This writes to `context/memory/YYYY-MM-DD.md` — tracked in git, not gitignored like `temp/`.

**If OS is absent** — write the session log directly:
```bash
mkdir -p context/memory
```
File: `context/memory/YYYY-MM-DD.md` using this template:
```markdown
# Session Log: YYYY-MM-DD — Eval Backport: <skill-name>

## What Was Done
- Optimized <skill> from score <baseline> → <final> over <N> iterations
- Backported: [list of accepted files and what changed]
- Rejected: [list with reasons]

## Snags Encountered
- [Any errors, workarounds, or unexpected behaviors from the run log]

## Key Decisions
- [Any ADAPT choices — what was changed from the lab version and why]

## Open Items
- [ ] [Follow-up rounds, coverage gaps, improvements to evals or skill]
```

### 6b: Persistent Memory (agent-level, native MEMORY.md system)

Apply a **non-obvious filter** before writing anything. Ask:
> "Would a future agent following the eval workflow get burned by not knowing this?"

Write a memory entry **only if** the session produced at least one of:
- A snag that blocked the run (exit codes, path errors, schema mismatches)
- A scoring footgun (e.g. keywords: field disabling description scanning)
- A non-obvious architectural insight about the eval engine
- A reusable ADAPT pattern (lab change that needed adjustment for master context)

**Skip** memory promotion for:
- Routine score improvements with no surprises
- Changes that are self-evident from the diff
- Anything already covered in an existing memory entry

If the filter passes, write to the agent's memory directory using the `feedback` type:
```
File: memory/feedback_eval_<skill-name>_<topic>.md
---
name: feedback_eval_<skill-name>_<topic>
description: <one-line hook for MEMORY.md index>
type: feedback
---
<rule/finding>

**Why:** <what happened that surfaced this>
**How to apply:** <when this matters in future eval runs>
```
Then add a pointer line to `MEMORY.md`.

### 6c: Promote to context/memory.md (if OS present)

If the OS is initialized and the non-obvious filter passed, also ask `os-memory-manager` to promote the finding as a long-term fact to `context/memory.md` with a deduplication ID.

---

### Master Source Mapping Reference

| Lab file | Master source |
|:---|:---|
| `<plugin>/skills/<skill>/SKILL.md` | `plugins/<plugin>/skills/<skill>/SKILL.md` |
| `<plugin>/skills/<skill>/evals/evals.json` | `plugins/<plugin>/skills/<skill>/evals/evals.json` |
| `<plugin>/skills/<skill>/references/*.md` | `plugins/<plugin>/skills/<skill>/references/*.md` |
| `<plugin>/scripts/*.py` | `plugins/<plugin>/scripts/*.py` |
| `.agents/skills/os-eval-runner/` (if patched) | `plugins/agent-agentic-os/skills/os-eval-runner/` |

> The master uses hub-and-spoke symlinks. Only the canonical source files listed above need
> updating — deployed environments sync from master automatically.
