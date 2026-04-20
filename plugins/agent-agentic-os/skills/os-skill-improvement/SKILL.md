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

---

## Required: Hypothesis Block (before any mutation)

Before editing any file, output a hypothesis block. If you cannot fill all 5 fields from
trace data or eval history, read more traces before proposing. Mutations without a grounded
hypothesis are exploratory noise — not systematic improvement.

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

---

## Phase 1: Frontier (What failure does this skill fix?)

Before writing a single line of SKILL.md:

1. **Define the pressure scenario**: one concrete user request that should trigger this skill.
2. **Define the failure**: what does the agent do WITHOUT the skill? (One sentence.)
3. **Define the acceptance criterion**: what specific behavior proves the skill is working?
4. **Check the test registry** (`context/memory/tests/registry.md`): has this hypothesis
   been tested and falsified before? If yes, do not re-test -- pick a different approach.
5. **Add a row to the test registry as IN PROGRESS** before writing any SKILL.md content.

---

## Phase 2: GREEN -- Write the Skill

### Frontmatter (YAML header)

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

### Example blocks

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

### Body structure

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

---

## Phase 3: GREEN Verification -- os-eval-runner

After writing the SKILL.md, run the eval gate. **Do not apply the skill without a KEEP verdict.**

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

---

## Phase 4: REFACTOR -- Close Loopholes

If eval returns DISCARD or review reveals gaps:

1. **Identify the loophole**: which input caused the wrong behavior?
2. **Add a targeted `<example>` block** covering that specific input.
3. **Sharpen the trigger description**: add the specific phrase that caused mis-routing.
4. **Re-run eval**. Repeat until KEEP.
5. **Close the test scenario record** in `context/memory/tests/registry.md`.

**REFACTOR anti-patterns**:
- Adding more generic trigger words to fix routing (Goodhart's Law -- scores improve,
  routing degrades)
- Rewriting the entire skill body to fix a single loophole (too much risk)
- Skipping the re-eval after a patch (you cannot know if it fixed the problem)

---

## Skill Types Reference

| Type | When to use | Key property |
|---|---|---|
| Protocol skill | Sequential multi-step procedure | Steps are MANDATORY, order matters |
| Reference skill | Lookup table or decision guide | Agent reads it, does not execute steps |
| Gating skill | Iron Law enforcement (verification, TDD) | Must include Common Failures table |
| Coordination skill | Agent-to-agent or multi-session | Must specify event bus interaction pattern |

---

## Directory Structure (ADR-003 compliance)

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
- Never duplicate a file -- ADR-003 requires one canonical source per file

---

## Integration with Triple-Loop Retrospective

When `Triple-Loop Retrospective` proposes a new skill or skill patch, it MUST:

1. **Generate one RED scenario** -- a concrete prompt that currently produces wrong behavior.
2. **Verify the RED** -- confirm the agent violates the protocol without the skill present.
3. **Write the SKILL.md** using this guide.
4. **Run os-eval-runner** -- KEEP gate is mandatory before any Write.
5. **Present the diff with evidence**: RED scenario + score delta + verdict.

A proposal that skips the RED scenario MUST be rejected -- the learning loop cannot
improve what it cannot measure.

---

## References

- [os-eval-runner](../os-eval-runner/SKILL.md) -- eval_runner.py, KEEP/DISCARD logic
- [skill_optimization_guide.md](../../references/operations/skill_optimization_guide.md) -- routing accuracy patterns
- [Triple-Loop Retrospective agent](../../agents/Triple-Loop Retrospective.md) -- how the loop uses this skill
- [test-registry-protocol.md](../../references/testing/test-registry-protocol.md) -- how to document test scenarios
- [improvement-ledger-spec.md](../../references/memory/improvement-ledger-spec.md) -- longitudinal tracking format

---

## Cross-Plugin Relationship

## Dependencies
- **agent-scaffolders** (plugin) — required for `create-skill` (filesystem scaffolding).
- **os-eval-runner** (agent-agentic-os plugin) — required for RED-GREEN-REFACTOR scoring.

> [!TIP]
> See [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md) for instructions on how to install missing dependencies.

**How they work together:**
1. `create-skill` (agent-scaffolders) — runs the discovery interview, creates the directory, writes starter files
2. `os-skill-improvement` (this skill) — takes the scaffolded skill and drives the RED-GREEN-REFACTOR quality cycle
3. `os-eval-runner` (agent-agentic-os) — provides the objective eval gate used in step 2
