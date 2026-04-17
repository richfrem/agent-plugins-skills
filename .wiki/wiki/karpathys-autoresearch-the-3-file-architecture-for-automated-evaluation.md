---
concept: karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-guide/references/research/karpathy-autoresearch-3-file-eval.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.158229+00:00
cluster: loop
content_hash: 35af06ea7d900e30
---

# Karpathy's `autoresearch`: The 3-File Architecture for Automated Evaluation

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
5. **Evaluate**: `prepare.py`

*(content truncated)*

## See Also

- [[karpathy-autoresearch-3-file-eval]]
- [[karpathy-autoresearch-3-file-eval]]
- [[autoresearch-architecture]]
- [[autoresearch-overview-applying-the-karpathy-loop-to-any-target]]
- [[genai-double-diamond-the-operating-system-for-discovery]]
- [[autoresearch-architecture]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-guide/references/research/karpathy-autoresearch-3-file-eval.md`
- **Indexed:** 2026-04-17T06:42:10.158229+00:00
