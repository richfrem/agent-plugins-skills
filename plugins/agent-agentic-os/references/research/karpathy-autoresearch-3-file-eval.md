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

**What is being optimized:** A SKILL.md file that teaches an agent when to trigger the `skill-improvement-eval` skill.

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
