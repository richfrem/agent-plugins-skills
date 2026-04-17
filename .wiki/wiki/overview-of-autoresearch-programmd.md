---
concept: overview-of-autoresearch-programmd
source: plugin-code
source_file: agent-agentic-os/skills/os-eval-runner/references/autoresearch-program-md-overview.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.161697+00:00
cluster: agent
content_hash: 8f3fb686e1826ea5
---

# Overview of autoresearch program.md

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Overview of autoresearch program.md

## The Role of `program.md`
The `program.md` file is the **governing specification** for an autonomous optimization loop. While `os-eval-runner` provides the scripts and engine, `program.md` defines the "DNA" of a specific experiment. It tells the agent exactly what is being measured, what the "North Star" metric is, and which files are strictly off-limits.

---

## Evolution: From Discovery to Utility
Standard autoresearch often focuses on "Discovery" (can the agent find the tool?). This V2 framework expands the focus to "Utility" (can the agent use the tool without struggling?).

### The V2 Quality Formula
The goal is to maximize the `quality_score` (0.0 to 1.0). In the enhanced V2 spec, the weight is distributed across four dimensions:

$$quality\_score = (A \cdot 0.4) + (H \cdot 0.2) + (C \cdot 0.2) + (F \cdot 0.2)$$

| Component | Metric | Metric Type | Goal |
| :--- | :--- | :--- | :--- |
| **A** | **Routing Accuracy** | Static | Ensures the skill triggers on the right prompts. |
| **H** | **Heuristic Integrity** | Static | Ensures the folder structure and tags follow spec. |
| **C** | **Operational Certainty** | Dynamic | Measures if the agent uses the right args on attempt #1. |
| **F** | **Friction Reduction** | Dynamic | Penalizes "struggle" (e.g., using `--help`, `ls`, or `cat`). |

---

## Anatomy of the File
A standard `program.md` (deployed from the `os-eval-runner` template) contains the following sections:

### 1. The Goal & Formula
Defines the mathematical KEEP/DISCARD gate. It establishes that a change is only "kept" if the new score and F1-guard meet or exceed the established baseline.

### 2. Mutation Target
Identifies the **single file** the agent is allowed to change. In most cases, this is `SKILL.md`. Changing multiple files at once is a violation of the isolation constraint.

### 3. Locked Files (The "Anchor")
Lists files the agent is strictly forbidden from modifying. This usually includes:
* `scripts/evaluate.py` and `scripts/eval_runner.py`
* `evals/evals.json` (the test prompts)
* `.lock.hashes` (the SHA256 integrity snapshot)

### 4. The Loop Protocol
Step-by-step instructions for the agent to follow:
1. **Analyze**: Read the `results.tsv` and traces to find the last failure.
2. **Mutate**: Make one focused change to the target file.
3. **Evaluate**: Run `evaluate.py` to get a KEEP/DISCARD verdict.
4. **Commit/Revert**: Based on the exit code, finalize the change or start over.

---

## Operational Readiness: Detecting "Struggle"
To improve the skill itself (not just its findability), the `program.md` now weights **Friction** heavily. The evaluator monitors the agent's interaction logs for "Struggle Signals":
* **Path Hunting**: Running `ls` or `find` to locate scripts.
* **Manual Inspection**: Running `cat` to understand code because instructions were unclear.
* **Syntax Fumbles**: Commands failing with exit codes due to poor parameter guidance.
* **Help Seeking**: Explicitly calling `--help` or `-h`.

By including these in the `program.md` formula, the agent is forced to write clearer, more "Zero-Shot" instructions to maintain a high score.



---

## Summary of File Ownership
* **Template Owner**: `os-eval-runner` (the engine).
* **Deployment Owner**: The specific experiment directory (e.g., `.agents/skills/my-skill/`).
* **Runtime Reader**: The AI agent and the `evaluate.py` gate.

## See Also

- [[autoresearch-overview-applying-the-karpathy-loop-to-any-target]]
- [[autoresearch-overview-applying-the-karpathy-loop-to-any-target]]
- [[triple-loop-learning-system---architecture-overview]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[autoresearch-architecture]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/skills/os-eval-runner/references/autoresearch-program-md-overview.md`
- **Indexed:** 2026-04-17T06:42:09.161697+00:00
