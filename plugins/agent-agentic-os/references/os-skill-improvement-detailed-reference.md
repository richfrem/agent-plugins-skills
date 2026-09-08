# os-skill-improvement — Detailed Reference

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
python ./scripts/eval_runner.py \
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
  - NEVER add a `keywords:` YAML field — it disables description scanning entirely (known footgun — see os-eval-runner Troubleshooting)
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

## Phase 3 — os-eval-runner (commands and result interpretation)

```bash
python ./scripts/eval_runner.py \
  --skill path/to/new/SKILL.md
```

**Interpreting results**:
- `STATUS: KEEP` -- score >= baseline. Apply the skill.
- `STATUS: BASELINE` -- first run. Record the score. Do not apply yet -- write an eval scenario
  in `evals/evals.json` targeting the pressure scenario from Phase 1.
- `STATUS: DISCARD` -- score same or lower. Do not apply. Go to Phase 4 (REFACTOR).

If the eval returns BASELINE on a new skill, write one eval scenario in `evals/evals.json`
in the autoresearch format, run again, and compare to that baseline before shipping.

## Phase 4 REFACTOR anti-patterns

- Adding more generic trigger words to fix routing (Goodhart's Law -- scores improve,
  routing degrades)
- Rewriting the entire skill body to fix a single loophole (too much risk)
- Skipping the re-eval after a patch (you cannot know if it fixed the problem)

## Skill Types Reference

| Type | When to use | Key property |
|---|---|---|
| Protocol skill | Sequential multi-step procedure | Steps are MANDATORY, order matters |
| Reference skill | Lookup table or decision guide | Agent reads it, does not execute steps |
| Gating skill | Iron Law enforcement (verification, TDD) | Must include Common Failures table |
| Coordination skill | Agent-to-agent or multi-session | Must specify event bus interaction pattern |

## Directory Structure (Single-Source Policy)

```
plugins/<your-plugin>/skills/<skill-slug>/
  SKILL.md                  <- single authoritative source (never duplicate)
  evals/
    evals.json              <- eval scenarios in autoresearch format
    results.tsv             <- longitudinal KEEP/DISCARD history (append-only)
  references/               <- supporting docs (file-level symlinks if shared)
  scripts/                  <- helper scripts (file-level symlinks if shared)
```

If a reference doc or script is shared with another skill in the same plugin:
- Canonical file lives at the plugin root `references/` or `scripts/`
- File-level symlink from the skill's subdirectory points to the canonical source
- Never duplicate a file — maintain one authoritative source per asset. Use file-level symlinks only (not directory symlinks) to avoid cross-platform failures during installation.

## Cross-Plugin Relationship

### Dependencies
- **agent-scaffolders** (plugin) — required for `create-skill` (filesystem scaffolding).
- **os-eval-runner** (agent-agentic-os plugin) — required for RED-GREEN-REFACTOR scoring.

> [!TIP]
> See [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md) for instructions on how to install missing dependencies.

**How they work together:**
1. `create-skill` (agent-scaffolders) — runs the discovery interview, creates the directory, writes starter files
2. `os-skill-improvement` (this skill) — takes the scaffolded skill and drives the RED-GREEN-REFACTOR quality cycle
3. `os-eval-runner` (agent-agentic-os plugin) — provides the objective eval gate used in step 2
