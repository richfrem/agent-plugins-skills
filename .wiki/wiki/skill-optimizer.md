---
concept: skill-optimizer
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/exploration-optimizer/references/spec-kitty-skill-optimizer-program.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.080368+00:00
cluster: files
content_hash: 44b72f0a329466bb
---

# skill-optimizer

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# skill-optimizer

This is an autoresearch-style experiment loop to autonomously improve the Spec Kitty agent and workflow skill files.

Inspired by Karpathy's autoresearch: propose one change, evaluate against a fixed rubric, keep if better, revert if not. Loop indefinitely.

---

## Setup

To set up a new optimization run, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `mar14`). The branch `skillopt/<tag>` must not already exist.
2. **Create the branch**: `git checkout -b skillopt/<tag>` from current master.
3. **Read the in-scope files** (all 4 must be read before starting):
   - `.agents/agents/spec-kitty-agent.md` — standalone agent card (compact)
   - `.agents/skills/spec-kitty-workflow/SKILL.md` — workflow SOP (main editable target)
   - `.agents/skills/spec-kitty-agent/SKILL.md` — full lifecycle + bridge sync skill
   - `.agents/skills/spec-kitty-workflow/pure-spec-kitty-workflow.mmd` — lifecycle diagram
4. **Read the fixed reference files** (DO NOT modify):
   - `.agents/skills/analyze-plugin/references/maturity-model.md` — scoring rubric
   - `.agents/skills/spec-kitty-agent/references/` — AUGMENTED.md files and known-good behavior
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

Score how rigorously the files prevent agen

*(content truncated)*

## See Also

- [[continuous-skill-optimizer-protocol-reference]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[optimizer-engine-patterns-reference-design]]
- [[skill-optimization-guide-karpathy-loop]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[quickstart-how-to-run-an-optimization-loop-on-any-skill]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/exploration-optimizer/references/spec-kitty-skill-optimizer-program.md`
- **Indexed:** 2026-04-17T06:42:10.080368+00:00
