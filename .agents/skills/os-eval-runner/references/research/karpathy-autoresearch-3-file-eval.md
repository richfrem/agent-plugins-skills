# Karpathy's `autoresearch`: The 3-File Architecture for Automated Evaluation

**Reference Repository:** [karpathy/autoresearch](https://github.com/karpathy/autoresearch)

Andrej Karpathy's `autoresearch` project represents a foundational design pattern for building reliable, autonomous AI agents. While originally designed for iterating on Machine Learning code, the core methodology—the "3-File Architecture"—is a universal pattern that applies to **any automated evaluation system**, whether you are refining RAG pipelines, front-end code, or data processing scripts.

## 🏗️ The 3-File Architecture

This architecture separates the orchestrator's constraints, the mutated logic, and the immutable evaluation criteria into three distinct trust boundaries:

### 1. The Spec (`program.md` / `prompt.md`)
This is the human-authored instruction file. It defines the goal, the constraints, and the specific guidelines the agent must follow. 
- **Role:** The strategic prompt.
- **Rules:** The agent reads this but cannot permanently alter its core intent. It explicitly defines which files are locked (e.g., "Do not modify `prepare.py`") and dictates the golden rule of autonomy: **"NEVER STOP."** Once the loop begins, the agent is instructed to *never* pause to ask the human for permission to continue. It runs indefinitely until manually terminated.

### 2. The Mutation Target (Any other file)
This is the living environment where the agent performs its work (e.g., `train.py`, or in web development, the HTML/CSS/JS files).
- **Role:** The execution ground.
- **Rules:** The agent is explicitly authorized to modify **any file** in the project, with the strict exception of the Spec (`program.md`) and the Evaluator (`benchmark.mjs`). It iteratively modifies these files one variable at a time based on feedback from the evaluator.

### 3. The Evaluator (`prepare.py` / `evaluate.py`)
This is the immutable scoring script. It runs against the Mutation file to produce a deterministic metric.
- **Role:** The objective judge.
- **Rules:** **The agent cannot touch this file.** It is strictly locked. Without this limitation, an LLM would inevitably rewrite the scoring function to fake better results rather than actually improving the code. By locking `prepare.py`, you ensure the agent **can't game the metric**.

---

## 🎯 The Core Requirement: A Baseline Metric

For this system to function, all three of these conditions must be met concurrently. If even one is missing, the loop breaks:
1. **A Clear Metric:** You need a single number with a clear direction for optimization.
2. **Automated Evaluation:** Absolutely no human-in-the-loop. The scoring must run headlessly.
3. **One Editable File:** The agent must only be allowed to change a single predefined file per loop.

In Karpathy's original repo, the metric is `val_bpb` (Validation Bits Per Byte—where lower is better). 

> [!IMPORTANT]
> **The "NEVER STOP" Protocol**
> The most critical rule in the `program.md` file is the mandate for true autonomy: *"Once the experiment loop has begun... do NOT pause to ask the human if you should continue... The loop runs until the human interrupts you, period."* If the agent pauses to ask for permission, the overnight recursive loop breaks.

### 🔄 "The Loop" Workflow
The agent operates in a continuous recursive self-improvement loop:
1. **The Baseline Commit**: Before any changes occur, the initial state is evaluated and committed (e.g., `git commit -m "baseline"`). This locks the unoptimized state as the starting metric.
2. **Hypothesis**: The agent reads `program.md` and previous results to theorize an improvement.
3. **Modify One Variable**: The agent edits `train.py` (or the target file), strictly changing *only one variable at a time* to maintain scientific isolation.
4. **Execute (Fixed Budget)**: The system runs the test. By enforcing a **fixed time budget** (e.g., 5 minutes for a micro-epoch), every experiment becomes directly comparable.
5. **Evaluate**: `prepare.py` (or `benchmark.mjs`) scores the result.
6. **Log to Ledger**: The agent maintains a strictly formatted `results.tsv` file to track the historical record of every experiment. It logs the commit hash, the primary metric (`load_time_ms`), secondary metrics (`total_size_kb`), the status (`keep` or `discard`), and a short description of the hypothesis.
7. **Keep or Discard**: If the new score is better than the previous baseline, the system keeps the state. If worse or if the run crashes, it immediately runs a `git reset --hard HEAD~1` to revert to the baseline.
8. **Repeat**: The agent starts again, adhering to the "never stop" rule.

> [!TIP]
> **100 Experiments Overnight**: Because execution is entirely automated and each run takes just 5 minutes, you can reliably execute ~100 distinct experiments while you sleep.

### 🌍 Applying This Beyond ML
"If you think this only applies to training AI models... you are badly mistaken. This has massive implications across **every domain of your life**." 

You can build a recursive self-improvement loop for *nearly anything that can be measured*. To adapt it to other domains, you only need to change the Evaluator's metric.

#### 📈 Trading Strategy Use Case
Instead of improving an ML model, point the loop at a trading strategy.
- **The Loop:** The agent tweaks your buy/sell rules.
- **The Evaluator:** Backtests the changes against years of market data.
- **The Metric:** Scores each iteration by its **Sharpe ratio**.

#### 🎯 Marketing on Steroids
Apply the loop to marketing: email copy, ad creatives, landing pages, headlines, and automated A/B testing.
- **The Loop:** The agent generates new copy variations and tests them.
- **The Metric:** Click-through rate (CTR) or conversion rate.
> *"Most marketing teams run ~30 experiments a year. The next generation will run 36,500+"* — Eric Siu

#### 💻 Developer Use Case ("Make it Faster")
You can point the loop at *any codebase* equipped with a benchmarking suite and simply say: "Make it faster."
- **Example:** Tuning open-source AI models to run faster for optimal on-device deployment (reducing layer norm overhead, swapping to fused softmax kernels, etc.).

#### 🚀 Website Load-Time Optimization
You can use the exact same loop to optimize front-end web performance.
- **The Setup:** Start with a deliberately slow site (e.g., Express.js serving uncompressed 9MB PNGs, bloated dependencies like full `lodash`, synchronous scripts in the head, no gzip).
- **The Evaluator (`benchmark.mjs`):** Write a strict evaluation script using Puppeteer to measure the exact `loadEventEnd - startTime` metric. The script launches a headless browser, runs the load test multiple times, and outputs a median `load_time_ms` to avoid network jitter anomalies.
- **The Loop:** Run an autonomous CLI agent (e.g., executing `claude --dangerously-skip-permissions`) so the loop can iterate unattended. The agent changes **one variable at a time** (e.g., compressing one image, testing, then minifying CSS, testing). If the median `load_time_ms` decreases, the system automatically commits the change. If it gets worse or breaks, it resets.

#### 🧠 Prompt Engineering (Agent Context)
AutoResearch can be used to tune the system instructions behind your AI agents.
- **The Context:** As LangChain founder Harrison Chase notes: *"Agents mess up because they don't have the right context."*
- **The Optimization:** The loop iteratively tests new language, clearer phrasing, and formatting adjustments to make your system prompts significantly more robust, scoring against an LLM-as-a-judge `Prompt Effectiveness` score.

## 🏆 The End Goal
Karpathy predicts that: *"All LLM frontier labs will do this. It's the final boss battle."*

If you think about it, this is what **recursive self-improvement** will actually look like. The irony of the current AI arms race is that frontier AI labs (OpenAI, Anthropic, Google) are spending millions on researchers trying to build this exact capability internally... and Karpathy made it open-source.

## 🌌 Karpathy's Vision: SETI@home for AI
In the early 2000s, **SETI@home** let anyone donate their spare computer power to search for alien life. Karpathy envisions the exact same model for AI research. 

Instead of a centralized GPU cluster running a single massive job, you would have *thousands of agents running on thousands of distributed consumer machines*, independently exploring distinct branches of the hypothesis tree.

> *"The goal is not to emulate a single PhD student. It's to emulate a research community of them."* — Karpathy

## 💡 The Bottleneck Shifts
This 3-file architecture is the clearest example yet of what AI agents actually look like in practice—**not chatbots, but autonomous loops that do real work.**

Because the loop acts autonomously, **execution becomes free**. 
The scarce skill is no longer writing the code; the scarce skill is now **knowing what to measure**—picking the right metric and setting the right constraints. 

> As Garry Tan said:
> *"The bottleneck isn't compute. It's your `program.md`."*

---

## 🔬 Real-World Implementation: Skill Optimization (2026-03-28)

This section documents how the 3-file architecture was applied to optimize agent skill files (SKILL.md) in this plugin ecosystem.

### The Setup

**What is being optimized:** A SKILL.md file that teaches an agent when to trigger the `os-eval-runner` skill.

**Why this works:** A skill file's trigger language is a mutation target with a clear objective metric — keyword routing accuracy against golden test cases.

### Mapping to the 3-File Architecture

| Karpathy concept | This implementation |
|---|---|
| `program.md` (spec) | `autoresearch/program.md` inside each target skill |
| Mutation target (`train.py`) | `SKILL.md` — the agent rewrites trigger language and examples |
| Locked evaluator (`prepare.py`) | `autoresearch/evaluate.py` — calls `eval_runner.py`, never touched by agent |
| `results.tsv` ledger | `autoresearch/results.tsv` — one row per iteration (commit, score, baseline, status) |

### The Metric

```
quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)
```

- `routing_accuracy`: fraction of golden prompts correctly routed via keyword overlap with frontmatter
- `heuristic_score`: structural check (has `<example>` blocks, min content length)
- KEEP requires: `score >= baseline AND f1 >= baseline_f1` (dual condition prevents keyword-stuffing)

This is DETERMINISTIC — no LLM calls. Same SKILL.md always produces the same score.

### The Loop in One Iteration

```
Agent reads program.md
    -> edits SKILL.md (one change: add example, reword trigger phrase, remove ambiguous keyword)
    -> python autoresearch/evaluate.py --desc "what I changed"
    -> evaluate.py calls eval_runner.py, parses {"quality_score": N}
    -> compares to baseline in autoresearch/results.tsv
    -> writes row: timestamp | commit | score | baseline | f1 | KEEP/DISCARD
    -> exits 0 (KEEP) or 1 (DISCARD)
Agent: if KEEP -> git commit; if DISCARD -> git checkout -- SKILL.md
Repeat (NEVER STOP)
```

### The Two-Layer Discovery Step

Before building the loop, a separate assessment skill (`eval-autoresearch-fit`) scores every skill on four dimensions to decide if a loop is worth building:

1. **Objectivity** — can the outcome be captured as a single number from shell?
2. **Execution Speed** — how fast does one iteration run?
3. **Frequency of Use** — how often is the skill triggered?
4. **Potential Utility** — what is the downstream impact of optimizing it?

Skills scoring 32-40 (HIGH) get loops built immediately. 24-31 (MEDIUM) after addressing barriers. Below 24 — skip.

This mirrors Karpathy's prerequisite check: "If you can't write a deterministic evaluator, don't start the loop."

### What "Locked" Actually Prevents

Without locking `evaluate.py`, an agent would inevitably:
- Rewrite the scoring function to return 1.0 for any input (Goodhart's Law)
- Remove hard test cases from `evals.json` to inflate accuracy
- Lower the KEEP threshold to make every run succeed

The lock on the evaluator is what makes the metric trustworthy. The agent's ONLY lever is the mutation target.

### Directory Layout

```
plugins/<plugin>/skills/<skill>/
  SKILL.md                       <- mutation target (agent edits this each loop)
  evals/evals.json               <- locked: golden test cases
  scripts/eval_runner.py         <- locked: the scoring engine
  autoresearch/
    program.md                   <- spec (goal, constraints, NEVER STOP)
    evaluate.py                  <- locked evaluator (agent never touches this)
    eval_runner.py -> ../scripts <- symlink for visibility
    results.tsv                  <- experiment ledger
```

---

## ⚠️ Where AutoResearch Fails

This architecture is not magic; it has rigid anti-patterns:
- **Subjective "Better":** It fails at brand design, UI/UX aesthetics, strategic pricing, or anything where "better" is a human judgment call. The loop demands **objective metrics**. If success is subjective, the agent will optimize in random directions.
- **Goodhart’s Law:** If you supply a flawed or incomplete metric, the agent will confidently and ruthlessly optimize the wrong thing.

---

## 📖 How We Actually Built It: Full Tour of `os-eval-runner`

This section is a complete annotated walkthrough of the first autoresearch loop built in this repo, warts and all. It is intended as a learning reference — connecting every file back to the Karpathy concepts above.

---

### What We Are Optimizing (and Why)

We are optimizing the trigger language in a SKILL.md file. A SKILL.md tells an agent:
- **When** to trigger this skill (the `description:` frontmatter block with example prompts)
- **What** to do once triggered (the body instructions)

The autoresearch loop only touches the first part — the trigger language. This is purely a prompt-engineering optimization problem with a measurable outcome.

**Why this is a valid Karpathy target:**
- Clear metric: routing accuracy is a number (0.0 to 1.0)
- Automated evaluation: keyword overlap against golden test cases, no LLM call needed
- One editable file: SKILL.md

---

### Every File in `os-eval-runner` and What It Does

```
plugins/autoresearch-improvement/skills/os-eval-runner/
```

#### `SKILL.md`
**Role:** Mutation target — the ONLY file the agent changes during the loop.

Contains the YAML frontmatter `description:` block with trigger phrases and `<example>` blocks. The routing evaluator extracts keywords from the frontmatter to decide if a prompt should trigger this skill.

The agent’s job: rewrite the trigger language so the routing evaluator routes all 9 golden prompts correctly (5 should trigger, 4 should not).

---

#### `evals/evals.json`
**Role:** The golden test set — LOCKED during the loop.

9 prompts with `should_trigger: true/false`. These define ground truth. The loop is meaningless without these staying fixed.

```json
{"prompt": "evaluate this skill", "should_trigger": true}
{"prompt": "what is the weather?", "should_trigger": false}
```

If the agent could edit this file, it could remove hard cases and inflate accuracy. That is why it is locked.

---

#### `scripts/eval_runner.py`
**Role:** The scoring engine — LOCKED during the loop.

Called by `autoresearch/evaluate.py`. Does two things:

1. **Routing eval** (`run_routing_eval`): extracts keywords from the SKILL.md frontmatter, checks each golden prompt for keyword overlap, computes accuracy / precision / recall / F1.

2. **Heuristic check** (`calculate_heuristic_score`): checks that SKILL.md has at least 2 `<example>` blocks and is above minimum length.

Final score formula:
```
quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)
```

With `--json` flag: prints `{"quality_score": 0.8444}` and exits.
Without `--json` flag: prints a human-readable report AND appends a row to `evals/results.tsv`.

**Important side effect:** every call to `eval_runner.py` (with or without `--json`) appends a row to `evals/results.tsv`. See "Known Issues" below.

---

#### `evals/results.tsv`
**Role:** eval_runner’s own log of every run.

Columns: `timestamp | score | accuracy | heuristic | llm_routing_score | status | description`

Note: the column called `llm_routing_score` is actually F1 score (legacy name from when this file was written). This confused the initial autoresearch evaluate.py which looked for `f1_score` and got 0 instead.

**This file is NOT the autoresearch ledger.** It is eval_runner’s own output. The autoresearch ledger is in `autoresearch/results.tsv`.

---

#### `autoresearch/program.md`
**Role:** The spec — equivalent to Karpathy’s `program.md`.

Tells the loop agent:
- What to maximize (quality_score)
- Which file to mutate (../SKILL.md — only this file)
- Which files are locked (evaluate.py, evals/evals.json, scripts/eval_runner.py)
- NEVER STOP

This is the human-authored constraint document. Once written, it does not change for the duration of the experiment.

---

#### `autoresearch/evaluate.py`
**Role:** The locked evaluator — equivalent to Karpathy’s `prepare.py` / `benchmark.mjs`.

The loop agent NEVER modifies this file. It:

1. Calls `scripts/eval_runner.py --skill ../SKILL.md --json` and parses `{"quality_score": N}`
2. Reads the first BASELINE row from `autoresearch/results.tsv` to get `(baseline_score, baseline_f1)`
3. Calls `eval_runner.py` a second time (without `--json`) to read the F1 score from `evals/results.tsv`
4. Decides: KEEP if `score >= baseline AND f1 >= baseline_f1`, else DISCARD
5. Appends a row to `autoresearch/results.tsv`
6. Exits 0 (KEEP) or 1 (DISCARD) so the calling agent knows what to do

Run from the skill root:
```bash
python autoresearch/evaluate.py --desc "what you changed"
python autoresearch/evaluate.py --baseline   # record a new baseline
```

---

#### `autoresearch/eval_runner.py`
**Role:** Symlink to `../scripts/eval_runner.py`.

Just for visibility — so someone standing in the `autoresearch/` directory can see what the evaluator uses, without hunting through parent directories.

---

#### `autoresearch/results.tsv`
**Role:** The experiment ledger — the autoresearch loop’s own record.

Columns: `timestamp | commit | score | baseline | f1 | status | description`

One row per call to `autoresearch/evaluate.py`. The first row with `status=BASELINE` anchors all future comparisons.

Current state (2026-03-28):
```
baseline commit abeb626: score=0.8444, f1=0.8333
```

---

#### `evals.json` (skill root)
**Role:** Symlink to `evals/evals.json`. Exists for legacy convenience. Not used by the loop.

---

### The Complete Data Flow

```
Agent edits SKILL.md
        |
        v
python autoresearch/evaluate.py --desc "my change"
        |
        +--[call 1]--> scripts/eval_runner.py --skill SKILL.md --json
        |                   |
        |                   +--> reads SKILL.md frontmatter keywords
        |                   +--> matches against evals/evals.json prompts
        |                   +--> writes row to evals/results.tsv   <-- side effect
        |                   +--> prints {"quality_score": 0.8444}
        |
        +--[reads]--> autoresearch/results.tsv (first BASELINE row)
        |                   baseline_score=0.8444, baseline_f1=0.8333
        |
        +--[call 2]--> scripts/eval_runner.py --skill SKILL.md --desc "_f1_probe"
        |                   |
        |                   +--> writes another row to evals/results.tsv  <-- side effect
        |                   +--> (output captured, not printed)
        |
        +--[reads]--> evals/results.tsv (last row, column llm_routing_score = f1)
        |
        +--> KEEP/DISCARD decision
        +--> appends row to autoresearch/results.tsv
        +--> exits 0 (KEEP) or 1 (DISCARD)
                |
        KEEP:   git add SKILL.md && git commit -m "keep: score=X <description>"
        DISCARD: git checkout -- SKILL.md
```

---

### Known Issues and What to Ask About

**Issue 1: eval_runner.py is called twice per iteration**
`evaluate.py` calls `eval_runner.py` once with `--json` to get the quality_score, then calls it again without `--json` to extract the F1 from `evals/results.tsv`. This means every autoresearch iteration adds 2 noisy rows to `evals/results.tsv` (the skill’s primary eval log).

The root cause: `eval_runner.py` with `--json` only outputs `quality_score`, not F1. A cleaner fix would be to output both in the JSON: `{"quality_score": 0.84, "f1": 0.83}`. But that requires modifying `eval_runner.py`, which is locked during the loop.

**Issue 2: Two results.tsv files that look similar**
- `evals/results.tsv` — eval_runner’s own log, written on every eval_runner call
- `autoresearch/results.tsv` — the loop ledger, one row per agent iteration

These are different things. `evals/results.tsv` is the skill’s eval history. `autoresearch/results.tsv` is the optimization experiment ledger. The column `llm_routing_score` in `evals/results.tsv` is actually F1 (legacy naming from before F1 was added).

**Issue 3: Baseline required separate re-run**
The first `--baseline` call produced `f1=0.0000` because the column name lookup bug (Issue 1 + wrong column name). After fixing the column name in `evaluate.py`, the baseline was re-run. There are now two BASELINE rows in `autoresearch/results.tsv`. `evaluate.py` uses the FIRST BASELINE row for comparisons, so the second re-run baseline (with correct f1) is the one that matters — but `load_baseline()` returns the FIRST row it finds. This is a latent bug: the first BASELINE row has f1=0.0, which means the f1 guard is currently disabled.

---

### The Baseline Numbers

| file | what it tracks | baseline |
|---|---|---|
| `autoresearch/results.tsv` row 1 | Loop experiment (first baseline, f1 bug) | score=0.8444, f1=0.0000 |
| `autoresearch/results.tsv` row 2 | Loop experiment (re-run after fix) | score=0.8444, f1=0.8333 |
| `evals/results.tsv` | eval_runner history | last score=0.8444, f1=0.8333 |

The loop currently compares against row 1 (f1=0.0), meaning the F1 guard is off. To fix: either delete row 1, or modify `load_baseline()` to use the LAST BASELINE row instead of the first.
