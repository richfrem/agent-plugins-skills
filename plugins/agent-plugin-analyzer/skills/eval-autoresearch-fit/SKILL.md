---
name: eval-autoresearch-fit
description: >
  Trigger with "evaluate autoresearch fit", "score this skill for karpathy loop",
  "is this a good autoresearch candidate", "assess autoresearch viability for",
  "which skills are best for autonomous loop optimization", "score skills for 3-file architecture",
  or when the user wants to determine if a skill is a good candidate for applying the
  Karpathy autoresearch autonomous optimization loop pattern.
user-invocable: true
argument-hint: "[skill-name-or-path] | --batch | --list | --status"
allowed-tools: Bash, Read, Write
---

# Evaluate Autoresearch Fit

Assess whether a skill is a viable candidate for the Karpathy 3-File Autoresearch autonomous
optimization loop. Scores each skill on four dimensions, proposes what the 3-file architecture
would look like, and updates the canonical `summary-ranked-skills.json` via the update script.

## Background

The Karpathy autoresearch pattern requires three conditions simultaneously:
1. **A Clear Metric** — a single number with a clear optimization direction
2. **Automated Evaluation** — no human in the loop; scoring runs headlessly from a shell command
3. **One Editable File** — the agent mutates only a single predefined target per loop

Skills that lack these properties cannot run an effective autonomous loop.

## Data File

The canonical ranked skills list lives at:
```
plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/assets/resources/summary-ranked-skills.json
```

After every evaluation, update it with the update script (see Step 5).

## Scoring Dimensions

Each dimension is scored 1-10. Max total = 40.

| Dimension | 10 (Best) | 1 (Worst) |
|---|---|---|
| **Objectivity** | Binary pass/fail or exact numeric output from a shell command | Purely subjective, requires human taste judgment |
| **Execution Speed** | Completes in seconds | Requires 30+ min or human input |
| **Frequency of Use** | Triggered multiple times per day | Rarely needed (monthly or less) |
| **Potential Utility** | Prevents systemic failures or saves hours per session | Nice-to-have improvement |

**Viability thresholds:**
- **32-40 HIGH** — Excellent candidate, implement now
- **24-31 MEDIUM** — Good candidate, address identified gaps first
- **16-23 LOW** — Needs significant rework to be viable
- **< 16 NOT_VIABLE** — Skip or the metric is unfixable

## Evaluation Steps

### Step 1: Locate the Skill

If `$ARGUMENTS` is a path to a directory containing `SKILL.md`, read it directly.

Otherwise find it by name from the repo root:
```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
find "$PROJECT_ROOT/plugins" -name "SKILL.md" | grep "$ARGUMENTS" | head -5
```

Read the SKILL.md fully before scoring.

### Step 2: Score Each Dimension

Reason through each dimension explicitly before assigning a number.

**Objectivity (1-10)**
- Can the outcome be captured as a single number from a shell command?
- Is there a binary pass/fail condition requiring no LLM judgment?
- Deductions: -2 if LLM-as-judge is needed, -4 if no numeric proxy exists, -7 if purely aesthetic
- Flag: if the only evaluator is an LLM call, note non-determinism cost

**Execution Speed (1-10)**
- <10s = 10, 10-60s = 9, 1-5min = 7, 5-15min = 5, 15-30min = 3, >30min = 1
- Ask: does the skill have interactive phases (confirmations, interviews)? Those must be bypassed in eval mode.

**Frequency of Use (1-10)**
- Multiple times per session = 10, Daily = 8, Few/week = 6, Weekly = 4, Monthly = 2, Rare = 1
- Base this on the skill's description trigger phrases and use context

**Potential Utility (1-10)**
- If this skill's behavior were optimized 50% more reliably, what's the downstream impact?
- Does it gate other work? Is it in a critical path?
- Systemic/prevents failures = 10, Saves significant time = 7, Moderate = 5, Minor = 2

### Step 3: Identify Loop Type and Split Loops if Needed

Determine the loop type:
- **DETERMINISTIC**: evaluator is pure shell (no LLM call). Preferred.
- **LLM_IN_LOOP**: evaluator must call Claude/API to score. Non-deterministic, needs N averaging.
- **HYBRID**: script produces partial score, LLM judges the rest.

**Important**: if a skill has both a script component and a prompt component, propose splitting into
two separate loops. Label them Loop A (script) and Loop B (prompt). Score and barrier each separately.

### Step 4: Propose the 3-File Architecture

**The Spec (`program.md`):**
What is the optimization goal? What constraints apply? What is the NEVER STOP directive?

**The Mutation Target:**
Which single file does the agent modify per iteration? If the skill inherently requires multi-file
changes, flag this as a barrier and propose how to isolate it.

**The Evaluator (`evaluate.py`):**
> Note: this `evaluate.py` is a script you would write *when implementing the autoresearch loop
> for the target skill* — it is NOT part of this skill. This skill only describes what it would
> look like. When ready to build the loop, create `evaluate.py` inside the target skill's
> `autoresearch/` directory.

- What shell command produces the metric?
- Is it deterministic? (Same input always produces same output?)
- If LLM-in-loop: propose a cheaper deterministic proxy if one exists

### Step 5: Output Assessment and Update JSON

Produce the assessment in this format:

```markdown
## Autoresearch Fit Assessment: [Skill Name]

**Plugin:** [plugin-name]
**Skill path:** [relative path from repo root]

### Scores
| Dimension | Score | Rationale |
|---|---|---|
| Objectivity | X/10 | [one line] |
| Execution Speed | X/10 | [one line] |
| Frequency of Use | X/10 | [one line] |
| Potential Utility | X/10 | [one line] |
| **TOTAL** | **X/40** | |

**Verdict: [HIGH / MEDIUM / LOW / NOT_VIABLE]**
**Loop type: [DETERMINISTIC / LLM_IN_LOOP / HYBRID]**

### Proposed 3-File Architecture

**Spec (`program.md`):**
> [2-3 sentences: optimization goal + constraints + NEVER STOP directive]

**Mutation Target:** `[path/to/file]`

**Evaluator command:**
```bash
[shell command that outputs a single number]
```
> Deterministic: [YES / NO + explanation]

### Key Barriers
- [Barrier 1]
- [Barrier 2 if any]

### Recommendation
[1-2 sentences. If MEDIUM: what to address first.]
```

Then update the JSON using the update script:

```bash
DATA_JSON=$(git rev-parse --show-toplevel)/plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/assets/resources/summary-ranked-skills.json
SKILL_DIR=.

python "$SKILL_DIR/scripts/update_ranked_skills.py" \
  --json-path "$DATA_JSON" \
  --plugin <plugin> \
  --skill <skill> \
  --objectivity X --speed X --frequency X --utility X \
  --verdict HIGH|MEDIUM|LOW|NOT_VIABLE \
  --loop-type DETERMINISTIC|LLM_IN_LOOP|HYBRID \
  --mutation-target "path/to/file" \
  --evaluator-command "python evaluate.py ..." \
  --barriers "Barrier 1" "Barrier 2" \
  --eval-notes "Key insight from this evaluation" \
  --status EVALUATED
```

### Useful script commands

```bash
DATA_JSON=$(git rev-parse --show-toplevel)/plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/assets/resources/summary-ranked-skills.json

# List all entries with current status
python ./scripts/update_ranked_skills.py --json-path "$DATA_JSON" --list

# Show a specific entry
python ./scripts/update_ranked_skills.py --json-path "$DATA_JSON" \
  --plugin agent-execution-disciplines --skill verification-before-completion --show

# List only PENDING entries (next batch to evaluate)
python ./scripts/update_ranked_skills.py --json-path "$DATA_JSON" \
  --list --filter-status PENDING

# Generate morning report (full ranked table + recommendation)
python ./scripts/update_ranked_skills.py --json-path "$DATA_JSON" --morning-report
```

## Batch Mode

When the user says "evaluate next batch" or "continue the list":

1. Run `--list --filter-status PENDING` to see remaining skills
2. Take the top 3 by `total_autoresearch_viability`
3. Evaluate each using Steps 1-5
4. After every 3, show the updated status table and ask: "Continue with next 3?"

## Phase 2: Scaffold the Loop (HIGH / MEDIUM skills)

When a skill scores HIGH or MEDIUM, scaffold the actual autoresearch loop inside the target skill
using the `autoresearch/` convention. This folder lives inside the target skill directory.

Directory convention (inside the target skill):
```
plugins/<plugin>/skills/<skill>/
  SKILL.md                     ← mutation target (agent edits this each iteration)
  autoresearch/                ← the loop lives here
    program.md                 ← the spec (goal + constraints + NEVER STOP)
    evaluate.py                ← LOCKED evaluator (agent must never modify this)
    results.tsv                ← experiment ledger (one row per iteration)
    tasks/                     ← golden task fixtures (LLM_IN_LOOP skills only)
    test-fixtures/             ← deterministic inputs (DETERMINISTIC skills only)
```

**Why evaluate.py runs every iteration:**
The loop is: agent mutates SKILL.md → run `autoresearch/evaluate.py` → record metric in
`results.tsv` → KEEP (commit) or DISCARD (git reset). `evaluate.py` is locked — the agent only
touches the mutation target.

**Cost by loop type:**
- **DETERMINISTIC** — seconds, zero LLM cost. 100 iterations overnight is realistic.
- **LLM_IN_LOOP** — ~3 min/iteration, ~$0.01 model cost. Use N=5 trials and average.
- **HYBRID** — intermediate runtime and cost.

Implement DETERMINISTIC candidates first where possible (fast, free, many trials).

**Scaffold steps for HIGH/MEDIUM verdicts:**
1. Create `autoresearch/` inside the target skill directory
2. Write `program.md` from the template (goal, metric, mutation target, NEVER STOP)
3. Write `evaluate.py` implementing the evaluator command from the assessment
4. Create empty `results.tsv` with header: `commit\tmetric\tstatus\tdescription`
5. For DETERMINISTIC: add `test-fixtures/` with at least one deterministic input
6. For LLM_IN_LOOP: add `tasks/` with at least one human-validated golden task

## Edge Cases

- **Interactive skill phases**: propose bypassing them in eval mode; note as a barrier
- **Score 10 objectivity + 1 speed**: flag as "needs wrapper script" and sketch what it would look like
- **LLM-only evaluator**: note cost, propose cheaper proxy if one exists; mark as LLM_IN_LOOP
- **Skill not found**: search `plugins/` from repo root, report path before proceeding
- **NOT_VIABLE threshold**: score < 16 = NOT_VIABLE. A high-scoring skill with barriers is still HIGH or MEDIUM — do not conflate barriers with viability verdict.
