```markdown
# 🤖 Autonomous Ubiquity Sweep Agent Prompt (Eval Initialization)

## **Objective**
You are a Senior Agent Systems Engineer. Your mission is to perform a "Ubiquity Sweep" across a large repository of AI agent capabilities. You must ensure that 100% of the 120 skills in the repository have a baseline evaluation suite defined, bridging the gap between our current state and a strict "Continuous Evaluation" CI gate.

## **Repository Architecture & Context**
* **Structure:** The repository contains 29 plugins under `plugins/`. Each plugin has a `skills/` directory. There are roughly 120 skills in total.
* **Hub-and-Spoke Model:** Shared scripts live at `plugins/<plugin>/scripts/`. Skills link to them via file-level symlinks. 
* **The Mutation Target:** A skill is represented by a folder (e.g., `plugins/my-plugin/skills/my-skill/`). The primary definition file is `SKILL.md`, containing a YAML frontmatter definition and `<example>` tags.

## **The Evaluation Protocol (Karpathy AutoResearch Adaptation)**
We employ a continuous improvement loop inspired by Karpathy's AutoResearch protocol, adapted for agent skill routing. Our evaluation machinery relies on two primary scripts:
1.  **`eval_runner.py` (The Metric Producer):** Evaluates a skill folder holistically. It reads `evals/evals.json`, tests the prompts against the skill's description, and computes `quality_score`, `accuracy`, `f1`, and `heuristic` scores. 
2.  **`evaluate.py` (The Loop Gate):** Used during active mutation. It calls `eval_runner.py`, compares the output against the `BASELINE` row in `evals/results.tsv`, and either outputs `KEEP` or automatically reverts the skill directory (`DISCARD`) if the F1 score regressed.

For `evaluate.py` to become an enforceable inline gate for all future agent edits, **every skill must have an `evals.json` and a baseline `results.tsv`**. 

## **The Schema Requirement**
An `evals.json` defines binary assertions to test if a skill correctly routes or triggers.
```json
{
  "test_cases": [
    {
      "prompt": "User input that should trigger this specific skill.",
      "should_trigger": true
    },
    {
      "prompt": "User input that sounds similar but belongs to a different skill.",
      "should_trigger": false
    }
  ]
}
```

## **Execution Instructions: The Ubiquity Sweep**
You must autonomously iterate through every skill in the repository and perform the following gap analysis and generation:

1.  **Discovery:** Scan `plugins/*/skills/*/` for all skills.
2.  **Gap Analysis:** Check if `evals/evals.json` exists for each skill.
3.  **Generation (If Missing):**
    * Read the target skill's `SKILL.md` (specifically the description and examples).
    * Create a new `evals/evals.json` file.
    * Write **3 precise positive (`should_trigger: true`)** test cases.
    * Write **3 HARD negative (`should_trigger: false`)** test cases. (Crucial: These should be "adversarial" prompts that share keywords with the skill but logically belong to a different tool, establishing a strict F1 boundary against trigger bloat).
4.  **Baselining:** * Run `python3 <path-to-plugin-scripts>/eval_runner.py --skill <path-to-skill-folder> --json`.
    * Parse the output metrics (`accuracy`, `f1`, `heuristic`, `quality_score`).
5.  **State Initialization:**
    * Create `evals/results.tsv` for the skill.
    * Write the initial baseline row using this exact TSV format:
      `commit\tprimary_value\tprimary_baseline\taccuracy\theuristic\tf1\tstatus\tdesc`
      *(For the first row, `commit` can be `init`, `status` MUST be `BASELINE`, and `desc` should be "Auto-generated baseline sweep".)*

## **Operating Constraints**
* **Do Not Modify Existing Evals:** If a skill already has `evals/evals.json` and `results.tsv`, skip it and do not overwrite its history.
* **Do Not Modify Gate Logic:** Do not edit `eval_runner.py` or `evaluate.py`.
* **Zero Halucination:** Do not create test cases for capabilities the skill does not explicitly claim in its `SKILL.md`.
* **Track Progress:** Maintain a local `temp/ubiquity-sweep-log.md` detailing which skills were skipped (already had evals) and which were newly baselined, including their starting F1 scores.

**BEGIN SWEEP.**
```