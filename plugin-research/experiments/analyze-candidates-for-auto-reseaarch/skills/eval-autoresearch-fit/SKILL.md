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

Assess whether a skill is a viable candidate for the Karpathy 3-File Autoresearch autonomous optimization loop. Scores each skill on four dimensions, proposes what the 3-file architecture would look like, and updates the canonical `summary-ranked-skills.json` via the update script.

## Background

The Karpathy autoresearch pattern requires three conditions simultaneously:
1. **A Clear Metric** - a single number with a clear optimization direction
2. **Automated Evaluation** - no human in the loop; scoring runs headlessly from a shell command
3. **One Editable File** - the agent mutates only a single predefined target per loop

Skills that lack these properties cannot run an effective autonomous loop.

## Data File

The canonical ranked skills list lives at:
```
skills/eval-autoresearch-fit/assets/resources/summary-ranked-skills.json
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
- **32-40 HIGH** - Excellent candidate, implement now
- **24-31 MEDIUM** - Good candidate, address identified gaps first
- **16-23 LOW** - Needs significant rework to be viable
- **< 16 NOT_VIABLE** - Skip or the metric is unfixable

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

**Important**: if a skill has both a script component and a prompt component, propose splitting into two separate loops. Label them Loop A (script) and Loop B (prompt). Score and barrier each separately.

### Step 4: Propose the 3-File Architecture

**The Spec (`program.md`):**
What is the optimization goal? What constraints apply? What is the NEVER STOP directive?

**The Mutation Target:**
Which single file does the agent modify per iteration? If the skill inherently requires multi-file changes, flag this as a barrier and propose how to isolate it.

**The Evaluator (`evaluate.py`):**
> Note: this `evaluate.py` is a script you would write *when implementing the autoresearch loop for the target skill* — it is NOT part of this skill. This skill only describes what it would look like. When you are ready to actually build the loop, create `evaluate.py` inside the target skill's `scripts/` directory.

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

Then update the JSON using the script:

```bash
SKILL_DIR=$(git rev-parse --show-toplevel)/plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit

python "$SKILL_DIR/scripts/update_ranked_skills.py" \
  --json-path "$SKILL_DIR/assets/resources/summary-ranked-skills.json" \
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
# List all entries with current status
python update_ranked_skills.py --json-path .../summary-ranked-skills.json --list

# Show a specific entry
python update_ranked_skills.py --json-path .../summary-ranked-skills.json \
  --plugin agent-execution-disciplines --skill verification-before-completion --show

# List only PENDING entries (next batch to evaluate)
python update_ranked_skills.py --json-path .../summary-ranked-skills.json \
  --list --filter-status PENDING
```

## Batch Mode

When the user says "evaluate next batch" or "continue the list":

1. Run `--list --filter-status PENDING` to see remaining skills
2. Take the top 3 by `total_autoresearch_viability`
3. Evaluate each using Steps 1-5
4. After every 3, show the updated status table and ask: "Continue with next 3?"

## Phase 2: Scaffold the Loop (HIGH / MEDIUM skills)

When a skill scores HIGH or MEDIUM, scaffold the actual autoresearch loop inside the target skill using an autoresearch/ convention. This folder lives inside the target skill directory and contains the program spec, a locked evaluator, and the experiment ledger and fixtures.

Directory convention (inside the target skill):
```
plugins/<plugin>/skills/<skill>/
  SKILL.md                     <- mutation target (agent edits this each iteration)
  autoresearch/                <- NEW: the loop lives here
    program.md                 <- the spec (goal + constraints + NEVER STOP)
    evaluate.py                <- LOCKED evaluator (agent must never modify this)
    results.tsv                <- experiment ledger (one row per iteration)
    tasks/                     <- golden task fixtures (LLM_IN_LOOP skills only)
    test-fixtures/             <- deterministic inputs (DETERMINISTIC skills only)
```

Why evaluate.py runs every iteration
- The loop is: agent mutates SKILL.md → run autoresearch/evaluate.py → record metric in results.tsv → decide keep vs reset/commit.
- evaluate.py is the loop engine: it executes the evaluator command, produces a single numeric metric, and writes a row to results.tsv. The agent must not edit evaluate.py (it is "locked"); the agent's responsibility is to modify the mutation target (SKILL.md) only and act on the evaluator verdict (keep the change or git reset).
- Practically: each iteration is one edit + one evaluation. The ledger makes experiments auditable.

Cost implication by loop type
- DETERMINISTIC
  - evaluate.py runs in seconds, zero LLM/API cost.
  - 100 iterations overnight is realistic for many deterministic evaluators.
- LLM_IN_LOOP
  - evaluate.py calls a cheap model (haiku) to judge or proxy outputs.
  - Typical per-iteration cost: ~3 minutes runtime and ≈ $0.01 in model cost; use N=5 trials and average to reduce noise.
- HYBRID
  - Mix of above; expect intermediate runtime and cost.

Implication: implement DETERMINISTIC candidates first where possible (fast, free, many trials).

What program.md contains (template)
```markdown
# Optimization Program: <skill-name>

Goal: maximize <metric> (lower/higher is better).
Mutation target: ../SKILL.md — you may ONLY edit this file.
Locked: autoresearch/evaluate.py, autoresearch/tasks/, autoresearch/test-fixtures/

NEVER STOP. Run until manually interrupted.
```

Scaffold steps when verdict is HIGH or MEDIUM
1. Create an autoresearch/ directory inside the target skill (relative to the skill path).
2. Write program.md from the template above, filling in the goal and metric derived from the assessment.
3. Write a stub evaluate.py implementing the evaluator command from the assessment. Use python3 subprocess calls for deterministic shell commands or a haiku-model call wrapper for LLM_IN_LOOP. evaluate.py must:
   - execute the metric-producing command,
   - parse a single numeric output,
   - append a row to results.tsv,
   - exit with success/failure codes for automation.
4. Create an empty results.tsv with header (tab-separated):
```
commit\tmetric\tstatus\tdescription
```
5. For DETERMINISTIC loops: create test-fixtures/ with at least one deterministic input file to ensure repeatability.
6. For LLM_IN_LOOP loops: create tasks/ containing at least one golden task fixture (human-validated) to anchor evaluations.
7. Ensure all paths are relative or derive the repo root via git rev-parse --show-toplevel when needed; do not hardcode absolute filesystem paths.

Notes and distinctions
- evaluate.py is NOT the same as evals/evals.json used elsewhere. evals/evals.json tests whether the skill triggers and responds correctly. autoresearch/autoresearch evaluate.py measures how well the skill's *instructions* perform in practice (the optimization metric).
- Use python3 in the evaluator scaffold and for any subprocess invocations to maintain environment consistency.
- Treat evaluate.py as authoritative and immutable for the loop; agent edits are limited to SKILL.md and experiment orchestration (commit/keep/reset).

## Edge Cases

- **Interactive skill phases**: If SKILL.md has discovery/confirmation phases, propose bypassing them in eval mode and note this as a barrier for the prompt-optimization loop
- **Existing proposed_benchmark_metric in JSON**: Use it as a starting hypothesis; validate and improve it during Step 4
- **Score 10 objectivity + 1 speed**: Flag as "needs wrapper script" and sketch what that script would look like
- **LLM-only evaluator**: Note the cost, propose a cheaper proxy metric if one exists; mark as LLM_IN_LOOP
- **Skill not found**: Search plugins/ from repo root, report the path found before proceeding

<reminder>
<sql_tables>No tables currently exist. Default tables (todos, todo_deps) will be created automatically when you first use the SQL tool.</sql_tables>
</reminder>

