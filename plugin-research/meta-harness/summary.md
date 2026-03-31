# Meta-Harness: End-to-End Optimization of Model Harnesses

**Authors:** Yoonho Lee, Roshen Nair, Qizheng Zhang (Stanford), Kangwook Lee (KRAFTON), Omar Khattab (MIT), Chelsea Finn (Stanford)
**Date:** March 30, 2026
**Source:** https://arxiv.org/abs/2603.28052
**PDF:** [2603.28052v1.pdf](./2603.28052v1.pdf)
**Project page:** https://yoonholee.com/meta-harness/
**Optimized harness artifact:** https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact

---

## What Is a Harness?

A **harness** is the code that wraps a language model and controls what information it sees — what to store, retrieve, and present at each step. It governs prompting, context management, retrieval logic, memory updates, and tool-use orchestration. The paper argues that harness design matters as much as model weights: a 6× performance gap on the same benchmark has been observed simply by changing the harness.

Despite this, harnesses are still designed largely by hand. Existing text optimizers are poorly suited to automated harness engineering because they compress feedback too aggressively — conditioning only on scalar scores, short summaries, or the last candidate — discarding the diagnostic signal needed to trace failures back to earlier harness decisions.

---

## The Core Idea: Meta-Harness

**Meta-Harness** is an outer-loop system that searches over harness code automatically. Instead of a fixed search structure, it gives a coding-agent proposer unrestricted access to a growing **filesystem** containing every prior candidate's source code, evaluation scores, and execution traces. The proposer reads this history selectively (via `grep`, `cat`, etc.), reasons about failure modes, and writes a new harness candidate. Each iteration adds to the filesystem. The loop repeats.

### The Search Loop (Algorithm 1)

1. Initialize a population of seed harnesses and an empty filesystem `D`
2. For each iteration:
   - Proposer queries `D` (reads prior code, scores, traces)
   - Proposer writes `k` new harness candidates
   - Each candidate is evaluated on a search set of task instances
   - Code, scores, and execution traces are stored back to `D`
3. Return the Pareto frontier of discovered harnesses

The proposer in experiments is **Claude Code** (Opus 4.6 with max reasoning), guided by a minimal domain-specific skill describing where to write harnesses and which files it can inspect.

### Why Filesystem Access Is the Key Ingredient

Prior text optimizers provide 100–30,000 tokens of context per iteration. A single Meta-Harness evaluation can produce up to **10,000,000 tokens** of diagnostic information. Rather than compressing this into a summary, Meta-Harness lets the proposer selectively retrieve what it needs. In ablation experiments:

| Interface | Median Acc | Best Acc |
|---|---|---|
| Scores Only | 34.6 | 41.3 |
| Scores + Summary | 34.9 | 38.7 |
| Meta-Harness (full filesystem) | **50.0** | **56.7** |

Access to raw execution traces is the single most important component — summaries do not recover the missing diagnostic signal and can even hurt by compressing away useful details.

---

## Results Across Three Domains

### 1. Online Text Classification

Task: classify text into many categories (LawBench 215 classes, Symptom2Disease 22 classes, USPTO-50k 180 classes). Base model: GPT-OSS-120B.

- Meta-Harness reaches **48.6% accuracy**, outperforming the prior best hand-designed harness (ACE) by **7.7 points** and MCE by **8.6 points**
- Achieves this using only **11.4K context tokens** vs 50.8K for ACE and 28.5K for MCE
- Matches the best prior text optimizer (TTT-Discover, OpenEvolve) after only **4 evaluations** vs their 40–60
- Achieves a stronger **Pareto frontier** on accuracy vs context cost than all baselines
- Generalizes to 9 out-of-distribution datasets, outperforming the next best method by **2.9 points** on average

### 2. Retrieval-Augmented Math Reasoning

Task: solve 200 IMO-level math problems with retrieval over a 500,000+ problem corpus. Evaluated across 5 held-out models (GPT-5.4-nano, GPT-5.4-mini, Gemini-3.1-Flash-Lite, Gemini-3-Flash, GPT-OSS-20B).

- The discovered retrieval harness improves accuracy by **4.7 points on average** over no retrieval across all five held-out models
- Matches or exceeds fixed BM25 retrieval (+1.3 points overall) while avoiding regressions from dense retrieval
- The harness was discovered operating entirely in code space on top of the BM25 stack — no additional dense encoder needed

### 3. Agentic Coding on TerminalBench-2

Task: 89 long-horizon coding tasks requiring autonomous execution under complex dependencies. Base models: Claude Opus 4.6 and Claude Haiku 4.5.

- On **Opus 4.6**: Meta-Harness achieves **76.4% pass rate**, surpassing hand-engineered Terminus-KIRA (74.7%), ranking **#2 among all Opus 4.6 agents** on the leaderboard
- On **Haiku 4.5**: Meta-Harness achieves **37.6%**, outperforming the next-best reported agent (Goose, 35.5%) by 2.1 points — **#1 among all Haiku 4.5 agents**
- Qualitative analysis shows the proposer formed causal hypotheses about confounded regressions and pivoted to structural fixes — behavior only possible with full filesystem access to prior experience

---

## Why Code-Space Search Works

Representing harnesses as programs provides a natural regularization bias: coding models tend to propose coherent algorithms rather than brittle hard-coded solutions. The search space is aligned with the read–write–execute workflows that frontier coding assistants are trained on. The proposer can make changes ranging from small prompt edits to full algorithmic rewrites — including retrieval strategy, memory structure, and tool-use orchestration.

Crucially, Meta-Harness imposes **no fixed parent-selection rule**: the proposer is free to inspect any prior harness and its execution trace. This keeps the outer loop deliberately minimal and lets the system improve automatically as coding agents become more capable.

---

## Comparison to Prior Text Optimizers

| Method | History | Log Content | MTok/iter |
|---|---|---|---|
| OPRO | Window | (solution, score) pairs | 0.002 |
| TextGrad | Last | textual feedback | 0.015 |
| AlphaEvolve | Window | program DB + scores | 0.022 |
| GEPA | Summary | reflective feedback | 0.008 |
| TTT-Discover | Window | prev. solution fragment | 0.026 |
| **Meta-Harness** | **Full** | **all logs and scores** | **10.0** |

Meta-Harness uses three orders of magnitude more context per iteration than the largest prior method — and this richer access is the source of its advantage.

---

## Key Takeaways for Agent System Builders

1. **Harness engineering is as important as model selection.** The code controlling what an LLM sees can produce a 6× performance gap on the same benchmark.

2. **Compressed feedback is a fundamental bottleneck.** Scalar scores and summaries lose the diagnostic information needed to improve context-management decisions that affect behavior many steps downstream.

3. **Filesystem access to prior experience enables automated harness engineering.** Giving a coding agent unrestricted access to all prior candidates' code, scores, and traces — rather than a curated summary — is the key ingredient.

4. **Code-space search generalizes.** Discovered harnesses transfer to unseen models and out-of-distribution tasks, producing readable, reusable strategies rather than brittle overfits.

5. **The proposer matters.** Meta-Harness works because frontier coding agents (Claude Code) can navigate large filesystems, form causal hypotheses, and write coherent algorithmic improvements. The approach will improve automatically as coding agents improve.

6. **This paper directly validates the plugin/skill improvement flywheel pattern.** The outer loop described here — propose harness → evaluate → log traces → inspect → improve — is structurally identical to the autoresearch loop used in this repo's `os-eval-runner` and `os-skill-improvement` skills.
