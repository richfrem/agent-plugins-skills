# Implementation Plan: Meta-Harness Enhancements to os-eval-runner & os-skill-improvement

**Self-contained — can be executed on any machine with a fresh clone of `agent-plugins-skills`.**

**Repo:** https://github.com/richfrem/agent-plugins-skills
**Research basis:** arXiv:2603.28052 (Lee et al., March 2026) — see `summary.md` and `code-analysis.md` in this folder
**Enhancement rationale:** `enhancement-recommendations.md` in this folder

---

## Observed Emergent Behavior (Important Prior Art from Weekend Experimentation)

Before implementing anything, note this validated pattern from direct experimentation:

When a lab repo (subproject) has **both** the target skill and `os-eval-runner` installed as peer copies, the autoresearch loop naturally improves **both** — not just the target. This happened unexpectedly during a weekend run and was welcomed, not a bug.

**Why it's safe:**
- The lab repo contains installed copies (physical files, not symlinks to master)
- The loop mutates the local copies freely — worst case it breaks the lab copy, not master
- `os-eval-backport` skill is the explicit human review gate before anything returns to the canonical source in `agent-plugins-skills`
- Master only ever receives mutations that passed both `evaluate.py` (machine gate) and backport review (human gate)

**Why this matters for the enhancements:**
- The nightly evolver (`os-nightly-evolver`) hard-blocks modification of anything outside the target skill folder — by design for safety in master-adjacent environments
- But in a lab repo, that restriction is unnecessarily conservative — the backport gate provides the safety guarantee
- This pattern is structurally identical to Meta-Harness: the proposer can modify the harness itself (not just the target), operating in an isolated search space, with a human Pareto gate before changes reach production
- Enhancement 1 (trace storage) makes this even more powerful: when `eval_runner.py` writes richer traces, the proposer in the lab can read those traces and propose improvements to `eval_runner.py` itself — the very kind of harness self-improvement Meta-Harness was built to discover

**Practical implication for this implementation:**
When running the enhancements in a lab repo, expect the loop to propose changes to `eval_runner.py` and `evaluate.py` alongside changes to the target SKILL.md. This is correct behavior in lab context. Review those changes in `os-eval-backport` with extra care — the evaluator modifying its own scoring logic is high-leverage and high-risk.

---

## Context for a Cold-Start Agent

This repo is a monorepo of AI agent plugins and skills. The key plugin for this work is:

```
plugins/agent-agentic-os/
  skills/
    os-eval-runner/       ← stateless evaluation engine (scorer + loop gate)
    os-skill-improvement/ ← RED-GREEN-REFACTOR improvement methodology
  scripts/
    eval_runner.py        ← pure scorer: reads SKILL.md + evals.json → outputs metrics JSON
    evaluate.py           ← loop gate: calls eval_runner.py, reads baseline, exits 0 (KEEP) or 1 (DISCARD)
    init_autoresearch.py  ← template deployer: scaffolds experiment dirs
```

The autoresearch loop works like this:
1. Agent reads `<experiment-dir>/references/program.md` (goal, rules)
2. Agent edits one file (SKILL.md or a script) — one change per iteration
3. Agent runs `python plugins/agent-agentic-os/scripts/evaluate.py --skill <experiment-dir> --desc "what changed"`
4. `evaluate.py` calls `eval_runner.py --json`, compares to baseline, writes row to `results.tsv`, exits 0 or 1
5. Agent: exit 0 → commit the change; exit 1 → `evaluate.py` already reverted via `git checkout`
6. Repeat

**The gap (from Meta-Harness research):** The agent proposer only sees scores in `results.tsv`. It does not see *which specific eval inputs failed*, *what keywords caused false positives*, or *what the mutation diff was*. The Meta-Harness ablation proves that raw execution traces are worth +15 accuracy points over scores-only or summaries.

---

## What We Are Building

Five enhancements, in priority order. Each is self-contained and can be implemented independently.

### Enhancement 1 (HIGH): Per-Input Trace Storage
### Enhancement 2 (MEDIUM): Skill State Snapshot Injection
### Enhancement 3 (MEDIUM): Hypothesis Block Requirement in os-skill-improvement
### Enhancement 4 (LOW): Milestone Summary Files
### Enhancement 5 (LOW): Two-Gate Backport Confirmation

---

## Enhancement 1: Per-Input Trace Storage

**Why:** The #1 finding from Meta-Harness. Proposer needs to `grep` raw traces, not read aggregated scores.

**Files to modify:**
- `plugins/agent-agentic-os/scripts/eval_runner.py` — add per-input detail to `--json` output
- `plugins/agent-agentic-os/scripts/evaluate.py` — write trace file after scoring

**Files to create:**
- None (trace files are generated at runtime into `<experiment-dir>/evals/traces/`)

### 1a. Modify `eval_runner.py`

Current `--json` output (line ~44 in the file docstring):
```json
{"quality_score": N, "accuracy": N, "f1": N, "heuristic": N}
```

Target `--json` output (add `routing_detail` and `heuristic_detail` keys):
```json
{
  "quality_score": 0.71,
  "accuracy": 0.70,
  "f1": 0.75,
  "heuristic": 0.73,
  "routing_detail": [
    {
      "input": "my symlinks are showing up as text files",
      "should_trigger": true,
      "matched_keywords": ["symlinks", "text", "files"],
      "triggered": true,
      "correct": true
    },
    {
      "input": "audit all hyperlinks in markdown files",
      "should_trigger": false,
      "matched_keywords": ["audit", "files"],
      "triggered": true,
      "correct": false,
      "failure_reason": "keyword 'audit' caused false positive (should_trigger=false)"
    }
  ],
  "heuristic_detail": [
    {"check": "example_blocks", "penalty": 0.0, "passed": true},
    {"check": "py_compile:foo.py", "penalty": -0.20, "passed": false}
  ]
}
```

**Implementation:** Find `run_routing_eval()` in `eval_runner.py`. Currently it returns `(accuracy, f1)`. Extend to also return the per-input list. When `--json` is set, include it in the output dict.

Locate the routing eval function — search for `def run_routing_eval` in `eval_runner.py`. The per-input data is already computed inside that function's loop; it just needs to be captured and returned.

For `heuristic_detail`, the `calculate_heuristic_score()` function already builds a `feedback` list. Add a parallel `penalties` list: each item is `{check, penalty, passed}`. Return it alongside the score.

**Key constraint:** The `--json` flag is parsed and output at the bottom of `eval_runner.py`. The JSON output path must include both new keys when `--json` is set. The non-`--json` (human-readable) path does not need to change.

### 1b. Modify `evaluate.py`

After calling `eval_runner.py --json` and getting the result, write a trace file:

```python
# After parsing eval_runner output and determining verdict:
traces_dir = evals_dir / "traces"
traces_dir.mkdir(exist_ok=True)

# Get iteration number from results.tsv row count
iteration = sum(1 for _ in open(results_tsv)) - 1  # subtract header row

# Read current git diff for the mutation target
diff_result = subprocess.run(
    ["git", "diff", "HEAD", str(mutation_target)],
    capture_output=True, text=True, cwd=skill_root
)
mutation_diff = diff_result.stdout[:4000]  # cap at 4KB

trace = {
    "iteration": iteration,
    "verdict": "KEEP" if verdict == "KEEP" else "DISCARD",
    "score": score,
    "baseline_score": baseline_score,
    "delta": round(score - baseline_score, 4),
    "desc": description,
    "mutation_diff": mutation_diff,
    "routing_detail": metrics.get("routing_detail", []),
    "heuristic_detail": metrics.get("heuristic_detail", []),
    "timestamp": datetime.utcnow().isoformat()
}

trace_filename = f"iter_{iteration:03d}_{verdict}_score{score:.2f}.json"
trace_path = traces_dir / trace_filename
trace_path.write_text(json.dumps(trace, indent=2))
```

**Key constraint:** `evaluate.py` is marked `DO NOT MODIFY` in its docstring for good reason — it is the locked evaluator. However, the trace write is *output*, not evaluation logic — it does not affect KEEP/DISCARD decisions and does not change exit codes. The SHA256 lock check in `check_locked_files()` will detect if this file changes and block future runs with exit 3 until a new baseline is established. Therefore: after modifying `evaluate.py`, immediately run `--baseline` to re-anchor. The trace write must happen *after* the verdict is determined and the TSV row is written, so it cannot affect the loop gate.

### 1c. Update `os-eval-runner` SKILL.md

In the "What Lives Where" section, add the traces directory:
```
<experiment-dir>/evals/
  evals.json           ← test prompts (locked during loop)
  results.tsv          ← loop ledger — one row per iteration
  .lock.hashes         ← SHA256 snapshot
  traces/              ← NEW: per-iteration diagnostic trace files
    iter_001_KEEP_score0.87.json
    iter_002_DISCARD_score0.71.json
```

In the Troubleshooting section, add:
```
### Reading traces to diagnose DISCARD iterations
grep -l "DISCARD" evals/traces/*.json | xargs -I{} jq '.routing_detail[] | select(.correct==false)' {}
```

---

## Enhancement 2: Skill State Snapshot Injection

**Why:** Eliminates proposer warm-up turns. Proposer immediately knows if it's a precision (false positives) or recall (false negatives) problem.

**Files to modify:**
- `plugins/agent-agentic-os/scripts/eval_runner.py` — add `--snapshot` flag

**Files to modify:**
- `plugins/agent-agentic-os/skills/os-skill-improvement/SKILL.md` — add snapshot step

### 2a. Add `--snapshot` flag to `eval_runner.py`

```python
# New CLI flag: --snapshot
# Reads results.tsv + most recent trace, prints a compact markdown block
```

Output of `python eval_runner.py --skill <path> --snapshot`:
```
## Skill State Snapshot
- Current score:      0.71  (baseline: 0.84, delta: -0.13)
- Iterations run:     12    (4 KEEP, 8 DISCARD)
- Last 3 verdicts:    DISCARD, DISCARD, KEEP
- Best ever score:    0.89  (iter 7, "added junction point trigger phrase")
- False-positive rate: 0.30  (3/10 should_trigger=false inputs misfire)
- False-negative rate: 0.00  (0/7 should_trigger=true inputs missed)
- Dominant problem:   PRECISION — too many false positives
  → Recommendation: remove broad keywords, add adversarial <example> blocks
```

The "Dominant problem" line is computed:
- fp_rate > fn_rate → PRECISION problem → "remove keywords, add adversarial examples"
- fn_rate > fp_rate → RECALL problem → "add trigger phrases, check keyword floor (≥4 chars)"
- Both zero → HEURISTIC problem → "check structural penalties in last trace"
- Both high → BOTH → "add more specific trigger phrases AND adversarial examples"

**Implementation:** `--snapshot` reads `results.tsv` for history, reads the most recent `traces/*.json` file (sort by name, take last) for `routing_detail`. No changes to `--json` path.

### 2b. Update `os-skill-improvement` SKILL.md

In Phase 1 (Frontier), add as Step 0 before "Define the pressure scenario":

```markdown
### Step 0: Read the Skill State Snapshot

Before proposing any mutation, run:
```bash
python plugins/agent-agentic-os/scripts/eval_runner.py \
    --skill <experiment-dir> \
    --snapshot
```

This tells you: current score, iteration history, false-positive vs false-negative breakdown,
and whether the dominant problem is precision or recall. Read this output before writing
a single word of the mutation. If the snapshot shows a PRECISION problem, do not add
more trigger keywords — that makes precision worse. If it shows RECALL, do not add
adversarial examples without also adding trigger phrases.
```

---

## Enhancement 3: Hypothesis Block Requirement

**Why:** Forces structured chain-of-thought before action. From Meta-Harness: `analysis` + `plan` fields in the tool schema reduced poorly-planned action sequences.

**Files to modify:**
- `plugins/agent-agentic-os/skills/os-skill-improvement/SKILL.md` — add hypothesis block requirement

**No code changes needed.**

### 3a. Add to `os-skill-improvement` SKILL.md

Before Phase 2 (GREEN — Write the Skill), add:

```markdown
## Required Hypothesis Block (write this BEFORE any mutation)

The proposer MUST output a hypothesis block before editing any file. If you cannot fill
all 5 fields from trace data, read more traces before proposing. Mutations without a
grounded hypothesis are exploratory — not scientific — and will degrade over iterations.

```
HYPOTHESIS:
  Failure mode: [exact input that triggered incorrectly + the incorrect verdict]
  Root cause:   [which specific keyword, phrase, or missing example caused it]
  Change:       [one sentence — add/remove/modify WHAT in SKILL.md]
  Effect:       [which specific eval inputs should flip from wrong → correct]
  Risk:         [which inputs might regress — name them specifically]
```

**Example (acceptable):**
```
HYPOTHESIS:
  Failure mode: "audit all hyperlinks in markdown files" triggered (should_trigger=false)
  Root cause:   keyword 'audit' in description matched this unrelated request
  Change:       Remove 'audit' from description; replace with 'broken-link audit' (3+ words, specific)
  Effect:       iter_002 false positive should no longer trigger
  Risk:         "audit my symlink manifest" (iter_006, should_trigger=true) may also stop triggering
```

**Example (not acceptable — do not write mutations without this):**
```
HYPOTHESIS:
  Failure mode: score dropped
  Root cause:   description too vague
  Change:       improve the description
  Effect:       better routing
  Risk:         none
```
The second example contains no falsifiable claim and will produce random mutations.
```

---

## Enhancement 4: Milestone Summary Files

**Why:** For long runs (25+ iterations), the proposer loses context on early experiments. Milestone summaries provide selective compression of distant history.

**Files to create:**
- `plugins/agent-agentic-os/scripts/generate_milestone.py` — new script

**Files to modify:**
- `plugins/agent-agentic-os/skills/os-eval-runner/SKILL.md` — document the milestone pattern
- `plugins/agent-agentic-os/skills/os-eval-runner/references/autoresearch-overview.md` — add milestone step

### 4a. `generate_milestone.py`

```python
#!/usr/bin/env python
"""
generate_milestone.py -- Write a milestone summary every N iterations.

Usage:
    python generate_milestone.py --experiment-dir <path> [--every 25]

Reads: evals/results.tsv, evals/traces/*.json
Writes: evals/traces/milestone_NNN.md

Call this after each iteration in the loop, or manually when needed.
It only writes a new milestone when the iteration count crosses a multiple of --every.
"""
```

Output format (`evals/traces/milestone_025.md`):
```markdown
# Milestone Summary: Iterations 1–25

Generated: 2026-03-31T14:22:00

## Score Trajectory
- Baseline: 0.71
- Best achieved: 0.89 (iter 7)
- Current: 0.82
- Net delta: +0.11

## KEEP/DISCARD Breakdown
- 9 KEEP, 16 DISCARD (36% acceptance rate)

## What Worked
- Adding "junction point" and "Windows Developer Mode" to description (+0.18 delta)
- Adding adversarial <example> for documentation link requests (fixed 3 false positives)

## What Never Worked (do not retry)
- Adding "audit" as a standalone keyword → always caused false positives on markdown link checkers
- Expanding description beyond 1024 chars → heuristic penalty every time

## Current False-Positive Sources (from last 5 traces)
- "check if URLs in README are still valid" — still triggering despite not being a symlink request

## Recommended Focus for Next 25 Iterations
- Dominant problem: PRECISION (fp_rate=0.20, fn_rate=0.00)
- Try: more adversarial <example> blocks, not more keywords
```

**Implementation:** The script reads `results.tsv` to get KEEP/DISCARD history and scores. It reads trace JSON files for `routing_detail`. It uses a simple heuristic to populate "What Worked" (highest positive delta KIEPs), "What Never Worked" (highest negative delta DISCARDs that appeared >2 times). It does not use an LLM — purely deterministic summary from structured data.

---

## Enhancement 5: Two-Gate Backport Confirmation

**Why:** Prevents marginal KEEPs from silently landing in master. From Meta-Harness: double-confirmation task completion with multi-perspective checklist reduced false-completion errors.

**Files to modify:**
- `plugins/agent-agentic-os/skills/os-eval-runner/SKILL.md` — update Stage 6 (Backport)

### 5a. Update Stage 6 in `os-eval-runner` SKILL.md

Replace the current Stage 6 backport section with:

```markdown
### Stage 6: Backport to Master Repo (Two-Gate Protocol)

**Gate 1 — Machine:** `evaluate.py` must have exited 0 (KEEP) with score ≥ baseline AND f1 ≥ baseline_f1.
Do not proceed to Gate 2 if this is not confirmed.

**Gate 2 — Human-in-the-loop commentary (required before applying to master):**

Before applying any KEEP change to the master source, print a 3-perspective diff analysis:

```
BACKPORT REVIEW: iter_NNN — "<desc>"
Score delta: +0.07 (0.82 → 0.89)

Test engineer view:
  Which eval inputs changed verdict? [list them]
  Are these the inputs we were targeting, or collateral?

Routing precision view:
  What similar-but-wrong request could now trigger this skill?
  [name at least one plausible mis-similar query]

Regression view:
  Which other installed skills have overlapping keywords with the change?
  Run: grep -r "junction point" .agents/skills/*/SKILL.md
  [list any conflicts found]

APPLY TO MASTER? (y/n)
```

Only proceed to apply after this commentary is written. For unattended (`os-nightly-evolver`) runs,
write the commentary to `temp/retrospectives/backport_[YYYYMMDD]_iter_NNN.md` and flag for human review
before the next nightly run. Do not auto-apply to master from unattended runs.
```

---

## Implementation Order and Dependencies

```
Enhancement 1 (eval_runner.py + evaluate.py)
  ├── No dependencies on 2–5
  ├── Must re-baseline after modifying evaluate.py
  └── Unlocks: trace files for Enhancements 2, 3, 4

Enhancement 2 (eval_runner.py --snapshot + os-skill-improvement SKILL.md)
  ├── Depends on: Enhancement 1 (reads trace files)
  └── Can be partially implemented (TSV-only snapshot) before Enhancement 1

Enhancement 3 (os-skill-improvement SKILL.md only)
  ├── No code changes
  ├── No dependencies
  └── Can be done first — editing SKILL.md, zero risk

Enhancement 4 (generate_milestone.py)
  ├── Depends on: Enhancement 1 (reads trace files)
  └── Can skip to after Enhancement 1 completes

Enhancement 5 (os-eval-runner SKILL.md only)
  ├── No code changes
  ├── No dependencies
  └── Can be done any time
```

**Recommended execution order:**
1. Enhancement 3 — SKILL.md edit, zero risk, immediate value
2. Enhancement 5 — SKILL.md edit, zero risk, immediate value
3. Enhancement 1 — core code change; re-baseline required after
4. Enhancement 2 — depends on Enhancement 1 traces existing
5. Enhancement 4 — depends on Enhancement 1 traces; lowest urgency

---

## File Inventory: What to Read Before Starting

Read these files in order before writing any code:

```bash
# 1. The evaluation engine (pure scorer)
cat plugins/agent-agentic-os/scripts/eval_runner.py

# 2. The loop gate
cat plugins/agent-agentic-os/scripts/evaluate.py

# 3. The skill definitions being enhanced
cat plugins/agent-agentic-os/skills/os-eval-runner/SKILL.md
cat plugins/agent-agentic-os/skills/os-skill-improvement/SKILL.md

# 4. The autoresearch overview
cat plugins/agent-agentic-os/skills/os-eval-runner/references/autoresearch-overview.md

# 5. The research this is based on
cat plugin-research/meta-harness/summary.md
cat plugin-research/meta-harness/code-analysis.md
cat plugin-research/meta-harness/enhancement-recommendations.md
```

---

## Testing After Implementation

### Test Enhancement 1 (trace storage)

```bash
# Run a single eval against any skill with existing evals.json
python plugins/agent-agentic-os/scripts/evaluate.py \
    --skill plugins/agent-agentic-os/skills/os-eval-runner \
    --desc "test trace write"

# Verify trace file was created
ls plugins/agent-agentic-os/skills/os-eval-runner/evals/traces/

# Verify trace JSON is valid and has routing_detail
cat plugins/agent-agentic-os/skills/os-eval-runner/evals/traces/iter_001_*.json | python -m json.tool
```

Expected: trace JSON file with `routing_detail` array containing one entry per eval input.

### Test Enhancement 2 (snapshot)

```bash
python plugins/agent-agentic-os/scripts/eval_runner.py \
    --skill plugins/agent-agentic-os/skills/os-eval-runner \
    --snapshot
```

Expected: markdown block with score, iteration count, fp_rate, fn_rate, dominant problem.

### Test Enhancement 4 (milestone)

```bash
# After 25+ iterations have been run in a target experiment:
python plugins/agent-agentic-os/scripts/generate_milestone.py \
    --experiment-dir plugins/agent-agentic-os/skills/os-eval-runner

ls plugins/agent-agentic-os/skills/os-eval-runner/evals/traces/milestone_*.md
```

---

## Commit Strategy

Each enhancement should be a separate commit:

```bash
# Enhancement 3 and 5 (SKILL.md only)
git add plugins/agent-agentic-os/skills/os-skill-improvement/SKILL.md
git commit -m "feat: add hypothesis block requirement to os-skill-improvement (Meta-Harness Rec 3)"

git add plugins/agent-agentic-os/skills/os-eval-runner/SKILL.md
git commit -m "feat: add two-gate backport protocol to os-eval-runner Stage 6 (Meta-Harness Rec 5)"

# Enhancement 1 (code change)
git add plugins/agent-agentic-os/scripts/eval_runner.py
git add plugins/agent-agentic-os/scripts/evaluate.py
git add plugins/agent-agentic-os/skills/os-eval-runner/SKILL.md
git commit -m "feat: add per-input trace storage to eval_runner.py and evaluate.py (Meta-Harness Rec 1)"

# Then re-baseline (REQUIRED after evaluate.py change)
python plugins/agent-agentic-os/scripts/evaluate.py \
    --skill plugins/agent-agentic-os/skills/os-eval-runner \
    --baseline --desc "re-baseline after trace storage addition"
git add plugins/agent-agentic-os/skills/os-eval-runner/evals/
git commit -m "baseline: re-baseline os-eval-runner after evaluate.py modification"
```

---

## Credit

This implementation plan is derived from:

**Karpathy 3-file autoresearch pattern** — the foundational architecture this eval loop implements. Referenced in `plugins/agent-agentic-os/skills/os-eval-runner/references/research/karpathy-autoresearch-3-file-eval.md`.

**Meta-Harness (Lee et al., 2026)**
Yoonho Lee, Roshen Nair, Qizheng Zhang, Kangwook Lee, Omar Khattab, Chelsea Finn.
*"Meta-Harness: End-to-End Optimization of Model Harnesses"*
arXiv:2603.28052, March 30, 2026.
Paper: https://arxiv.org/abs/2603.28052
Artifact: https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact
Reference file: `plugins/agent-agentic-os/skills/os-eval-runner/references/research/meta-harness-lee-2026.md`
