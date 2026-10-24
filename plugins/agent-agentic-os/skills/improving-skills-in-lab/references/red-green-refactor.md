# Single-Pass RED-GREEN-REFACTOR (detail)

## Contents

- [How to run a RED scenario (full steps)](#how-to-run-a-red-scenario-full-steps)
- [Skill State Snapshot (command)](#skill-state-snapshot-command)
- [Hypothesis Block (format and example)](#hypothesis-block-format-and-example)
- [Frontmatter template (Phase 2)](#frontmatter-template-phase-2)
- [Example blocks template](#example-blocks-template)
- [Body structure template](#body-structure-template)
- [Phase 3 - Score the patch (commands and result interpretation)](#phase-3---score-the-patch-commands-and-result-interpretation)
- [Phase 4 REFACTOR anti-patterns](#phase-4-refactor-anti-patterns)


Extracted from SKILL.md per Layer-1 procedural-core line budget (issue #551).

## How to run a RED scenario (full steps)

1. Identify the pressure scenario: a user prompt or agent situation where you WANT the skill
   to fire but it currently does not (or the agent takes the wrong action without it).
2. Simulate the scenario in a clean context (no SKILL.md present for this skill yet).
3. Observe: what does the agent do wrong? What specific step did it skip or violate?
4. Write down the specific violation in one sentence -- this becomes the skill's primary
   acceptance criterion and the `<example>` block's commentary.

```bash
# Document the RED scenario before writing:
# Write to: context/memory/tests/[TIMESTAMP]_[SKILL_SLUG].md
# Fields: pressure_scenario, expected_behavior, observed_failure, acceptance_criterion
```

## Skill State Snapshot (command)

```bash
python scripts/eval_runner.py \
    --skill <experiment-dir> \
    --snapshot
```

This tells you: current score, iteration history, false-positive vs false-negative rate, and
the dominant problem type (PRECISION or RECALL). If the snapshot shows PRECISION (too many
false positives), do not add more keywords — that makes it worse. If it shows RECALL, do not
add adversarial examples without also adding trigger phrases.

If `--snapshot` is not yet available (pre-Enhancement-2), read `evals/results.tsv` directly
for score trend and `evals/traces/` for the most recent DISCARD's per-input detail.

## Hypothesis Block (format and example)

```
HYPOTHESIS:
  Failure mode: [exact input that triggered incorrectly + the incorrect verdict]
  Root cause:   [which specific keyword, phrase, or missing example caused it]
  Change:       [one sentence — add/remove/modify WHAT in SKILL.md]
  Effect:       [which specific eval inputs should flip from wrong → correct]
  Risk:         [which inputs might regress — name them specifically]
```

**Acceptable example:**
```
HYPOTHESIS:
  Failure mode: "audit all hyperlinks in markdown files" triggered (should_trigger=false)
  Root cause:   keyword 'audit' in description matched this unrelated request
  Change:       Remove 'audit'; replace with 'broken-link audit' (compound, more specific)
  Effect:       iter_002 false positive should no longer trigger
  Risk:         "audit my symlink manifest" (iter_006, should_trigger=true) may also stop triggering
```

**Not acceptable** — do not write mutations based on vague hypotheses like "description too
vague, improve it." That produces random mutations and early plateau.

## Frontmatter template (Phase 2)

```yaml
---
name: skill-slug          # lowercase-hyphen, matches directory name
version: 1.0.0
description: >
  Trigger description. This is the MOST IMPORTANT field -- it determines routing accuracy.
  Rules:
  - Lead with the primary use case, not the skill name
  - Include 2-3 <example> blocks: one standard use, one adversarial (when NOT to trigger),
    one edge case
  - Use specific vocabulary in the description text — terms that only appear in this skill's domain
  - NEVER add a `keywords:` YAML field — it disables description scanning entirely (known footgun — see the score mode's Troubleshooting)
  - Avoid generic verbs (do, run, execute) as primary triggers -- they appear everywhere
trigger: comma-separated, specific trigger phrases that ONLY appear in this skill's context
allowed-tools: Read, Write, Edit, Bash   # list only what the skill actually needs
---
```

**Trigger description anti-patterns** (will degrade routing accuracy):
- Generic: "run the skill when the user asks to do X" (X appears in 10 other skills)
- Circular: "use this skill for writing skills" (not a pressure scenario)
- Keyword-stuffed: 50+ trigger words with no specificity (Goodhart's Law risk -- eval
  will score higher but routing will be worse)

## Example blocks template

Every non-trivial skill needs at least two example blocks:

```
<example>
<commentary>Standard use: agent correctly invokes this skill</commentary>
User: [exact or paraphrased pressure scenario from RED phase]
Agent: [first sentence of correct behavior -- invoke the skill, not explain it]
</example>

<example>
<commentary>Adversarial: agent correctly does NOT invoke this skill</commentary>
User: [request that SOUNDS similar but belongs to a different skill]
Agent: [correct behavior: invokes the OTHER skill instead]
</example>
```

## Body structure template

```markdown
# Skill Name

One-paragraph description of what the skill does and why.

## When to Use
- [condition 1]
- [condition 2]

## Iron Law (if applicable)
[The single most important rule that must not be violated. State it as an absolute.]

## Step-by-Step Protocol
[Numbered steps. If >7 steps, extract a sub-phase.]

## Common Failures
| Failure | Why it happens | Prevention |
|---|---|---|

## References
- [related skill or reference doc]
```

## Phase 3 - Score the patch (commands and result interpretation)

```bash
python scripts/evaluate.py --skill path/to/skill-folder --desc "what changed"
```

Interpreting results (exit code from `evaluate.py`):
- exit 0 (KEEP): accuracy and F1 are at or above baseline. Keep the patch and commit it.
- exit 1 (DISCARD): not better. `evaluate.py` already reverted `SKILL.md`; go to Phase 4 (REFACTOR) with a new hypothesis.
- No baseline yet: run `python scripts/evaluate.py --skill <folder> --baseline` first, after writing one eval scenario in `evals/evals.json` that targets the RED pressure scenario.

## Phase 4 REFACTOR anti-patterns

- Adding more generic trigger words to fix routing (Goodhart's Law -- scores improve,
  routing degrades)
- Rewriting the entire skill body to fix a single loophole (too much risk)
- Skipping the re-eval after a patch (you cannot know if it fixed the problem)
