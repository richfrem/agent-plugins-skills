# Acceptance Criteria: analyze-plugin

To ensure `analyze-plugin` functions correctly and consistently extracts valuable patterns, it must pass the following criteria when evaluated.

## 1. Inventory Completeness
When operating in Single Plugin Mode, the output analysis must accurately reflect the total number of files in the plugin, matching the output of the deterministic `inventory_plugin.py` script. It must not prematurely summarize or skip directories like `references/` or `scripts/`.

## 2. Methodology Adherence
The final analysis report must clearly show evidence of executing all six phases of the Analysis Framework:
1.  **Inventory**: File counts and types are present.
2.  **Structure Score**: Explicit rating of Progressive Disclosure and architecture.
3.  **Content Analysis**: Evaluates the quality of SKILL.md and supporting files.
4.  **Pattern Extraction**: Explicitly names at least one structural or execution pattern.
5.  **Anti-Pattern Detection**: Accurately flags any simulated or real violations of the Open Standard (e.g., >500 lines).
6.  **Synthesis Ready**: The output matches the formats defined in `output-templates.md`.

## 3. Disambiguation
When operating in Comparative Mode on a collection, the skill must distinctly group patterns that are "Universal" (found everywhere) vs. "Unique Innovations" (found in only one capability). It must not blend specific innovations into general statements.
