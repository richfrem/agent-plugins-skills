---
concept: evaluate-autoresearch-fit
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/eval-autoresearch-fit/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.074133+00:00
cluster: skill
content_hash: 578e6311dddd84a7
---

# Evaluate Autoresearch Fit

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
- **DETERMINISTIC**: evaluator is pure shell (no LLM

*(content truncated)*

## See Also

- [[optimization-program-eval-autoresearch-fit]]
- [[optimization-program-eval-autoresearch-fit]]
- [[autoresearch-fit-batch-evaluation-results]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[autoresearch-architecture]]
- [[autoresearch-overview-applying-the-karpathy-loop-to-any-target]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/eval-autoresearch-fit/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.074133+00:00
