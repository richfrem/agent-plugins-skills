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
- `os-improvement-loop` -- uses this methodology to gate every proposed skill patch
- `evals/evals.json` + `results.tsv` -- autoresearch eval format for longitudinal tracking

## The TDD Mapping

| Software TDD | Skill Authoring Equivalent |
|---|---|
| Test case | Pressure scenario: a user prompt that should trigger the skill |
| RED phase | Run a baseline WITHOUT the skill. Observe: does the agent violate the intended protocol? |
| GREEN phase | Write the skill. Run `os-eval-runner`. KEEP only if score >= baseline. |
| REFACTOR phase | Identify loopholes from eval failures. Patch frontmatter or examples. Re-eval. |

## Iron Law: Run a RED Scenario BEFORE Writing

**Never write a new skill without first observing a failure.**

The RED scenario is the evidence that the skill is needed. Without it you cannot know the
specific failure being fixed, cannot do a before/after comparison, and examples become
generic rather than addressing real failure modes. Full steps for running a RED scenario are
in `references/detailed-reference.md`.

## Required before any mutation

1. **Skill State Snapshot** — run `eval_runner.py --skill <experiment-dir> --snapshot` to see
   current score, iteration history, and whether the dominant problem is PRECISION (too many
   false positives — don't add more keywords) or RECALL (don't add adversarial examples without
   also adding trigger phrases). Full detail in `references/detailed-reference.md`.
2. **Hypothesis Block** — output failure mode, root cause, change, expected effect, and named
   regression risk before editing any file. Format and worked example in
   `references/detailed-reference.md`. Vague hypotheses ("description too vague") are not
   acceptable — they produce random mutations and early plateau.

## Phase 1: Frontier (What failure does this skill fix?)

Before writing a single line of SKILL.md:

1. Define the pressure scenario (one concrete user request that should trigger this skill).
2. Define the failure the agent exhibits WITHOUT the skill.
3. Define the acceptance criterion — what specific behavior proves the skill is working.
4. Check the test registry (`context/memory/tests/registry.md`) for prior falsified hypotheses.
5. Add a row to the test registry as IN PROGRESS before writing any SKILL.md content.

## Phase 2: GREEN -- Write the Skill

Write the frontmatter (name, description as the primary routing signal, trigger phrases,
allowed-tools), at least two `<example>` blocks (standard use + adversarial non-trigger), and
the body (When to Use, Iron Law, Step-by-Step Protocol, Common Failures table, References).
Exact templates and anti-patterns are in `references/detailed-reference.md`.

## Phase 3: GREEN Verification -- os-eval-runner

After writing the SKILL.md, run the eval gate via `eval_runner.py --skill path/to/new/SKILL.md`.
**Do not apply the skill without a KEEP verdict.** `KEEP` (score >= baseline) applies the skill;
`BASELINE` (first run) records the score and requires an eval scenario before shipping;
`DISCARD` (same or lower score) goes to Phase 4.

## Phase 4: REFACTOR & Loop Integration

If eval returns DISCARD: identify the loophole input, add an `<example>` block, sharpen trigger
descriptions, and re-eval until KEEP. When `os-improvement-loop` proposes patches, it MUST
generate a RED scenario, verify it fails without the skill, apply the patch, and verify via
`os-eval-runner`. Proposals skipping the RED scenario must be rejected. Anti-patterns in
`references/detailed-reference.md`.

## References

- [os-eval-runner](../os-eval-runner/SKILL.md) -- eval_runner.py, KEEP/DISCARD logic
- [skill_optimization_guide.md](references/operations/skill_optimization_guide.md) -- routing accuracy patterns
- [test-registry-protocol.md](references/testing/test-registry-protocol.md) -- test scenario documentation
- Skill Types Reference and Directory Structure policy are in `references/detailed-reference.md`.
