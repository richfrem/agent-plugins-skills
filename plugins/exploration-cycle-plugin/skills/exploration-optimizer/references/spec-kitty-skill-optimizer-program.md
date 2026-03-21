# skill-optimizer

This is an autoresearch-style experiment loop to autonomously improve the Spec Kitty agent and workflow skill files.

Inspired by Karpathy's autoresearch: propose one change, evaluate against a fixed rubric, keep if better, revert if not. Loop indefinitely.

---

## Setup

To set up a new optimization run, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `mar14`). The branch `skillopt/<tag>` must not already exist.
2. **Create the branch**: `git checkout -b skillopt/<tag>` from current master.
3. **Read the in-scope files** (all 4 must be read before starting):
   - `temp/agent-plugins-skills/plugins/spec-kitty-plugin/agents/spec-kitty-agent.md` — standalone agent card (compact)
   - `temp/agent-plugins-skills/plugins/spec-kitty-plugin/skills/spec-kitty-agent/SKILL.md` — full lifecycle + bridge sync skill
   - `temp/agent-plugins-skills/plugins/spec-kitty-plugin/skills/spec-kitty-workflow/SKILL.md` — workflow SOP (main editable target)
   - `temp/agent-plugins-skills/plugins/spec-kitty-plugin/skills/spec-kitty-workflow/pure-spec-kitty-workflow.mmd` — lifecycle diagram
4. **Read the fixed reference files** (DO NOT modify):
   - `temp/agent-plugins-skills/plugins/agent-plugin-analyzer/skills/analyze-plugin/references/maturity-model.md` — scoring rubric
   - `temp/agent-plugins-skills/plugins/spec-kitty-plugin/skills/spec-kitty-agent/references/` — AUGMENTED.md files and known-good behavior
5. **Initialize skill-results.tsv**: Create it with just the header row. The baseline score is established in the first iteration.
6. **Confirm and go**.

---

## What You CAN and CANNOT Do

**You CAN:**
- Modify any of the 4 in-scope files listed above. All content is fair game: fix bugs, restructure steps, improve clarity, remove duplication, add examples, fix CLI flags, improve gate enforcement wording.

**You CANNOT:**
- Modify this file (`spec-kitty-skill-optimizer-program.md`). It is the fixed scoring rubric — equivalent to `prepare.py` in autoresearch.
- Modify any `AUGMENTED.md` files. They are hand-maintained project-specific overlays.
- Modify any file outside the 4 in-scope files.
- Add new files. Work within the existing files only.
- Change the scoring rubric (defined below). The rubric is ground truth.

---

## The Goal

**Maximize `quality_score`** (0–100, higher is better).

Unlike `val_bpb`, this score is evaluated by you against the fixed rubric below. To keep scoring consistent, re-read the rubric before every evaluation and apply it literally. When in doubt, score conservatively.

**Simplicity criterion**: All else being equal, simpler is better. A tiny improvement that adds verbose prose is not worth it. Removing a paragraph and keeping the same score is a win. Fixing a bug in 2 words beats explaining it in 20. When evaluating whether to keep a change, weigh the improvement against the noise added.

---

## Scoring Rubric (FIXED — DO NOT MODIFY)

Evaluate the **4 in-scope files together** as a unit after every change. Score each dimension independently, then compute the weighted total.

### Dimension 1 — CLI Accuracy (20 pts)

Score the correctness of all CLI commands and flags in the 4 files.

| Score | Criteria |
|-------|----------|
| 20 | Every CLI command matches the current `spec-kitty-cli` API. No deprecated flags. No flags documented in the files' own failure-modes table as "not supported". |
| 15 | 1–2 minor discrepancies (e.g. an optional flag that is sub-optimal but not broken). |
| 10 | 1–2 real errors: a flag documented as unsupported is still present as an instruction, or a command references a non-existent subcommand. |
| 5  | 3+ CLI errors OR one command that will reliably fail. |
| 0  | Core commands are wrong and would immediately break the workflow. |

Known red flags to check:
- `--actor` and `--test` flags on `spec-kitty agent feature accept` — these do NOT exist in the current CLI (documented in failure modes). Instructing agents to use them = score hit.
- `spec-kitty init . --ai windsurf` hardcoded — only valid if Windsurf is the IDE. Should document the general form `spec-kitty init . [--ai <agent>]`.

### Dimension 2 — Anti-Simulation Enforcement (20 pts)

Score how rigorously the files prevent agents from faking execution.

| Score | Criteria |
|-------|----------|
| 20 | Every numbered step that runs a CLI command is immediately followed by a **PROOF** requirement: what output to paste, what to verify. No step can be "checked off" without real tool output. The anti-simulation rule header appears prominently. |
| 15 | Most steps have PROOF. 1–3 steps are missing it but are low-risk steps. |
| 10 | PROOF requirements exist but are inconsistently applied. Several important steps (kanban transitions, merge, accept) lack them. |
| 5  | Anti-simulation section present but PROOF requirements missing from majority of steps. |
| 0  | No PROOF requirements. Anti-simulation is declared but not enforced at step level. |

### Dimension 3 — Human Gate Clarity (15 pts)

Score the clarity and enforceability of the HITL gates.

| Score | Criteria |
|-------|----------|
| 15 | Each gate specifies: (1) exact trigger phrase required ("Proceed", "Go", "Execute"), (2) what artifact to show, (3) explicit negative examples of phrases that are NOT approval. The gate enforcement table is present and accurate. |
| 10 | Gates are present with trigger phrases but missing negative examples OR the table is incomplete. |
| 5  | Gates are described in prose but not enforced with a clear table or trigger phrase list. |
| 0  | Human gates are mentioned but not actionable. |

### Dimension 4 — Failure Mode Coverage (15 pts)

Score the completeness of the known failure modes table.

| Score | Criteria |
|-------|----------|
| 15 | All failures known from production use are documented: `@require_main_repo` error, missing `shell_pid`, `--actor`/`--test` rejection, orphaned worktrees, research files deleted on worktree remove, unchecked tasks blocking accept, `??` untracked files blocking merge preflight, skeleton WPs invisible to lane tracking. Each entry has: Failure \| Root Cause \| Fix. |
| 10 | Most known failures covered. 1–2 missing or lacking the cause/fix detail. |
| 5  | Table present but missing several common failures or entries lack actionable fixes. |
| 0  | No failure modes table OR table exists but is empty/trivial. |

### Dimension 5 — Signal Density (15 pts)

Score the ratio of useful instruction to noise (artifacts, duplication, stale text).

| Score | Criteria |
|-------|----------|
| 15 | No stray artifacts. No duplicate step labels. No repeated content between files beyond intentional cross-references. No placeholder text. No line-number artifacts. Every sentence earns its place. |
| 10 | 1–2 minor cosmetic issues (a stray character, minor phrasing duplication) that do not confuse an agent. |
| 5  | A duplicate step label (e.g. two "Step 4f"), OR a stray line-number artifact (e.g. `282.` as a standalone line), OR significant prose duplication within a single file. |
| 0  | Multiple structural artifacts, widespread duplication, or text that actively contradicts itself. |

### Dimension 6 — IDE/Tool Agnosticism (15 pts)

Score how well the instructions work regardless of which AI IDE or agent is in use.

| Score | Criteria |
|-------|----------|
| 15 | No hardcoded IDE assumptions. Where IDE-specific examples are given (e.g. Windsurf), a generic fallback form is also shown. The init command is shown in its general form. Dependencies that reference non-existent skills are either resolved or removed. |
| 10 | 1–2 IDE assumptions that a non-Windsurf user would need to adapt, but the intent is still clear. |
| 5  | Multiple Windsurf-specific paths or commands without fallbacks. |
| 0  | Instructions are Windsurf-only and would fail completely in any other environment. |

**Known red flags**: `spec-kitty init . --ai windsurf` without the `[--ai <agent>]` general form. `dependencies: ["skill:agent-bridge"]` pointing to a skill that does not exist in this plugin (a dependency the agent cannot resolve).

---

## Computing the Score

```
quality_score = round(
    dim1_cli_accuracy          +   # out of 20
    dim2_anti_simulation       +   # out of 20
    dim3_human_gate_clarity    +   # out of 15
    dim4_failure_mode_coverage +   # out of 15
    dim5_signal_density        +   # out of 15
    dim6_ide_agnosticism           # out of 15
)
# Max = 100
```

Record each dimension score alongside the total in `skill-results.tsv`.

---

## Output Format

After scoring, print a summary in this exact format:

```
---
quality_score:   78
dim1_cli:        15
dim2_antisim:    18
dim3_hitl:       12
dim4_failures:   13
dim5_density:    10
dim6_agnostic:   10
change:          "fix: remove stray 282. artifact and relabel duplicate Step 4f -> Step 4g"
---
```

---

## Logging Results

Log every experiment to `skill-results.tsv` (tab-separated, NOT comma-separated).

Header and columns:

```
commit	quality_score	dim1_cli	dim2_antisim	dim3_hitl	dim4_failures	dim5_density	dim6_agnostic	status	change
```

1. `commit` — short git hash (7 chars)
2. `quality_score` — total 0–100
3. `dim1_cli` through `dim6_agnostic` — individual dimension scores
4. `status` — `keep`, `discard`, or `error`
5. `change` — brief description of what this experiment tried

Example:
```
commit	quality_score	dim1_cli	dim2_antisim	dim3_hitl	dim4_failures	dim5_density	dim6_agnostic	status	change
a1b2c3d	62	10	18	12	13	5	4	keep	baseline
b2c3d4e	67	10	18	12	13	10	4	keep	fix: remove 282. artifact and relabel duplicate Step 4f
c3d4e5f	72	15	18	12	13	10	4	keep	fix: remove unsupported --actor flag from accept instructions
d4e5f6g	72	15	18	12	13	10	4	discard	refactor: merged agent files (no score improvement, net complexity loss)
```

**Do NOT commit `skill-results.tsv`** — leave it untracked by git, same as autoresearch `results.tsv`.

---

## The Experiment Loop

The loop runs on a dedicated branch (e.g. `skillopt/mar14`).

**LOOP FOREVER:**

1. Review the current git state and re-read the current versions of all 4 in-scope files.
2. Choose **one focused improvement** to try. Smaller and more targeted is better — do not make 5 changes at once. Pick the highest-impact fix remaining.
3. Apply the change to the relevant file(s).
4. `git commit -m "fix: <description>"`
5. Re-read all 4 in-scope files, then score them against the rubric above.
6. If `quality_score` improved (strictly higher): **keep** — advance the branch. Log to TSV.
7. If `quality_score` did not improve (equal or lower): **discard** — `git reset --hard HEAD~1`. Log to TSV with `discard`.
8. Move to the next idea.

**Known issues to work through** (not exhaustive — read the files yourself for more):
- `282.` stray line in `spec-kitty-workflow/SKILL.md`
- Duplicate "Step 4f" labels in `spec-kitty-workflow/SKILL.md`
- `--actor`/`--test` flags referenced as instructions despite being in the failure modes table as unsupported
- `spec-kitty init . --ai windsurf` hardcoded — no general form shown
- `dependencies: ["skill:agent-bridge"]` and `["skill:dual-loop"]` point to non-existent skills
- Near-identical content between `agents/spec-kitty-agent.md` and `skills/spec-kitty-agent/SKILL.md` — reduce duplication or clarify the distinction

**Errors**: If a change breaks the internal logic of a skill (e.g. a step now references a section that no longer exists), treat it as an error. Log `error`, `git reset --hard HEAD~1`, and move on.

**NEVER STOP**: Once the loop begins, do NOT pause to ask the user if you should continue. The user may be away. Run indefinitely, autonomously, until manually interrupted. If you run out of the known issues above, look harder — read the files again, look for subtle contradictions, unclear wording, missing PROOF steps, or inconsistencies between the 4 files that a real agent would stumble on. The loop runs until the human interrupts you, period.

Each iteration (read → change → score) takes roughly 2–5 minutes. In an overnight session you can realistically run 20–50 iterations and produce a materially improved skill suite.

---

## Sync Back to Master

After the human reviews and approves the accumulated improvements on the `skillopt/<tag>` branch, sync the improved files back to the master plugin location:

```bash
cp temp/agent-plugins-skills/plugins/spec-kitty-plugin/agents/spec-kitty-agent.md \
   /Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/spec-kitty-plugin/agents/spec-kitty-agent.md

cp temp/agent-plugins-skills/plugins/spec-kitty-plugin/skills/spec-kitty-workflow/SKILL.md \
   /Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/spec-kitty-plugin/skills/spec-kitty-workflow/SKILL.md

cp temp/agent-plugins-skills/plugins/spec-kitty-plugin/skills/spec-kitty-workflow/pure-spec-kitty-workflow.mmd \
   /Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/spec-kitty-plugin/skills/spec-kitty-workflow/pure-spec-kitty-workflow.mmd

cp temp/agent-plugins-skills/plugins/spec-kitty-plugin/skills/spec-kitty-agent/SKILL.md \
   /Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/spec-kitty-plugin/skills/spec-kitty-agent/SKILL.md
```

Then redeploy:
```bash
npx skills add ./temp/agent-plugins-skills/plugins/spec-kitty-plugin --force
```