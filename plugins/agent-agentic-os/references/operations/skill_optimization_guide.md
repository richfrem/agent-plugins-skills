# Skill Optimization Guide (Karpathy Loop)

This guide documents lessons learned from the Supervised Learning Loop to help agents and users achieve a "Perfect 1.0" Routing & Heuristic score.

## 1. Scoped Keyword Extraction
The `eval_runner.py` scopes its keyword extraction to the **frontmatter only**. This mimics how real LLM routers (like Claude Plugin Router) operate.

**Best Practice:**
Place your highest-value trigger words (e.g., "license", "copyright", "legal") inside the `description` or `<example>` blocks within the frontmatter (between the `---` bars). Avoid burying them in the Markdown body.

## 2. Example Diversity
Structural health requires at least two `<example>` blocks. For maximum routing accuracy, use the "Direct vs. Audit" pattern:

- **Direct Trigger**: User asks for the task explicitly (e.g., "Add a header to foo.py").
- **Audit/Implicit Trigger**: User describes a state that requires the task (e.g., "Fix the missing legal boilerplate in the project").

## 3. Heuristic Health (Structural Score)
The trainer rewards:
- **XML Consistency**: Proper `<example>` tags.
- **Substance**: A `description` of at least 200 characters to provide sufficient context for the router.

## 4. Avoiding "Trigger Bloat"
Don't add keywords for things the skill *doesn't* do. Every extra keyword in the frontmatter increase the risk of a "Negative Trigger" failure (triggering when it shouldn't).

**Lesson from `headersys` demo:**
Adding too many generic words like "context" or "folder" to a specific skill's description can cause it to over-trigger on general queries about context management. Keep descriptions targeted.

## 5. The Evaluation Machinery (File Topology)
The autoresearch loop relies on a strict separation of concerns between definition, testing, and ledgering. To optimize a skill, you must understand how these files interact:

1. **The Ground Truth (`SKILL.md`):** This is the mutation target. It defines what the tool claims it can do via its YAML frontmatter.
2. **The Boundaries (`evals/evals.json`):** This defines the strict pass/fail test cases (`should_trigger: true/false`). It is the immovable standard the skill is graded against.
3. **The Engine (`eval_runner.py`):** The stateless scorer. It tests the description in `SKILL.md` against the prompts in `evals.json`.
4. **The Gatekeeper (`evaluate.py`):** The stateful decider. It compares the new scores against the baseline, writes to the ledger, and auto-reverts the skill if the metrics degrade.
5. **The Ledger (`evals/results.tsv`):** The permanent, append-only history of the skill's performance.

## 6. The Scoring Math & The F1 Guardian
The loop does not evaluate raw accuracy; it evaluates precision and structural health to prevent "Goodhart's Law" (keyword stuffing). The metrics recorded in `results.tsv` dictate whether a mutation survives (`KEEP`) or is reverted (`DISCARD`).

### The Final Grade: Quality Score
The `primary_value` used to judge an improvement is a weighted formula:
`Quality Score = (Routing Accuracy * 0.7) + (Heuristic Score * 0.3)`

* **Routing Accuracy:** Did the LLM correctly trigger (or correctly ignore) the test cases in `evals.json` based *only* on the `SKILL.md` description?
* **Heuristic Score:** Does the `SKILL.md` follow formatting rules? (e.g., >200 char description, minimum 2 `<example>` tags, under 500 lines total).

### The Guardian: F1 Score
To achieve a `KEEP` status, a mutation must improve or match the baseline Quality Score **AND** maintain or improve the baseline F1 Score. 

The F1 score is the harmonic mean of Precision and Recall. It is the ultimate defense against Trigger Bloat. If you add generic keywords to pass a positive test case, the skill will start accidentally triggering on negative test cases (`should_trigger: false`). This plummets the Precision metric, which destroys the F1 score, resulting in an automatic `DISCARD`.