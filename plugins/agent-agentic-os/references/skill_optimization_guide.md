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
