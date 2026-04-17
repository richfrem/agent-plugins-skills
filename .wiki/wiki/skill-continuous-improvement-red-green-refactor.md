---
concept: skill-continuous-improvement-red-green-refactor
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-skill-improvement/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.183398+00:00
cluster: eval
content_hash: beb33d5e31be1e80
---

# Skill Continuous Improvement: RED-GREEN-REFACTOR

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: os-skill-improvement
version: 1.0.0
description: >
  Continuously improves an existing agent skill based on eval results using the
  RED-GREEN-REFACTOR cycle. Apply when a skill's routing accuracy is low, trigger
  descriptions need sharpening, or os-eval-runner scores are below target.
  (1) run a RED baseline to observe the failure mode,
  (2) apply a focused patch and verify with os-eval-runner (GREEN),
  (3) refactor to close loopholes until score meets threshold.
  Integrates with os-eval-runner as the objective eval gate.
  NOT for scaffolding new skills — use create-skill (agent-scaffolders) for that.
trigger: improve a skill, improve skill routing, fix routing accuracy, skill is not triggering,
  skill triggers too often, improve trigger description, update a skill trigger, skill patch,
  improve triggers, route a skill, routing precision, fix skill description, skill scoring low,
  eval score low, skill improvement, continuous skill improvement, refactor skill triggers,
  tdd for documentation, skill not routing correctly
allowed-tools: Read, Write, Edit, Bash
---

# Skill Continuous Improvement: RED-GREEN-REFACTOR

Adapts the RED-GREEN-REFACTOR cycle from software testing to skill authoring.
The key insight: a skill is a testable contract. The failure to follow the contract
is observable. Always observe the failure BEFORE writing the fix.

**Integrated with**:
- `os-eval-runner` -- runs `eval_runner.py` as the GREEN verification step
- `Triple-Loop Retrospective` -- uses this methodology to gate every proposed skill patch
- `evals/evals.json` + `results.tsv` -- autoresearch eval format for longitudinal tracking

---

## The TDD Mapping

| Software TDD | Skill Authoring Equivalent |
|---|---|
| Test case | Pressure scenario: a user prompt that should trigger the skill |
| RED phase | Run a baseline WITHOUT the skill. Observe: does the agent violate the intended protocol? |
| GREEN phase | Write the skill. Run `os-eval-runner`. KEEP only if score >= baseline. |
| REFACTOR phase | Identify loopholes from eval failures. Patch frontmatter or examples. Re-eval. |

---

## Iron Law: Run a RED Scenario BEFORE Writing

**Never write a new skill without first observing a failure.**

The RED scenario is the evidence that the skill is needed. Without it:
- You cannot know what specific failure the skill is fixing
- You cannot know if the skill actually fixes it (no before/after comparison)
- You cannot write examples that address real failure modes (they become generic)

### How to run a RED scenario

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

---

## Required: Skill State Snapshot (before any mutation)

Before proposing any change in an active improvement loop, run:
```bash
python3 ./scripts/eval_runner.py \
    --skill <experiment-dir> \
    --snapshot
```

This tells you: current score, iteration history, false-positive vs false-negative rate, and
the dominant problem type (PRECISION or RECALL). If the snapshot shows PRECISION (too many
false positives), do not add more keywords — that makes it worse. If it shows RECALL, do not
add adversarial examples without also adding trigger phrases.

If `--snapshot` is not yet available (pre-Enhancement-2), read `evals/results.tsv` directly
for score trend and `evals/traces/` for the most recent DISCARD's per-input detail.

*(content truncated)*

## See Also

- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[metrics-workflow-health-continuous-improvement]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[continuous-skill-optimizer-protocol-reference]]
- [[red-team-bundler-skill]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-skill-improvement/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.183398+00:00
