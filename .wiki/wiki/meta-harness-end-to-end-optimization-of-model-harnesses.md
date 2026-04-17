---
concept: meta-harness-end-to-end-optimization-of-model-harnesses
source: research-docs
source_file: meta-harness/summary.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.457803+00:00
cluster: research-docs
content_hash: c3e142f23ea80a0b
---

# Meta-Harness: End-to-End Optimization of Model Harnesses

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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

Task: solve 200 IMO-level math problems with retrieval over a 500,000+ probl

*(content truncated)*

## See Also

- [[implementation-plan-meta-harness-enhancements-to-os-eval-runner-os-skill-improvement]]
- [[quickstart-how-to-run-an-optimization-loop-on-any-skill]]
- [[quickstart-how-to-run-an-optimization-loop-on-any-skill]]
- [[meta-harness-artifact-code-analysis]]
- [[meta-harness-enhancement-task-tracker]]
- [[agent-harness-learning-layer-formerly-agentic-os]]

## Raw Source

- **Source:** `research-docs`
- **File:** `meta-harness/summary.md`
- **Indexed:** 2026-04-17T06:42:10.457803+00:00
