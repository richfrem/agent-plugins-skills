# Synthesis of Learnings: Anthropic 'PDF' Skill

**Source**: `https://github.com/anthropics/skills/tree/main/skills/pdf`
**Analyzed by**: `agent-scaffolders` & `synthesize-learnings`

## 1. Categorized Observations

### A. Interaction Design & Procedural Guidance
- **Explicit Fallback Mechanisms**: For complex, brittle tasks (like filling non-fillable PDF forms), the skill uses a highly procedural fallback sequence documented in a dedicated file (`forms.md`). It explicitly tells the agent to try "Structure-Based Coordinates" first, and if that fails, fall back to "Visual Estimation".
- **Step-by-Step Validation**: The workflow enforces intermediate verification steps (e.g., `check_bounding_boxes.py`) before executing destructive or final actions (`fill_pdf_form_with_annotations.py`). This prevents catastrophic failures at the end of a long chain.

### B. Progressive Disclosure
- **Routing over Instructing**: The main `SKILL.md` is surprisingly concise (315 lines), acting primarily as a quick-reference guide and router. For the most complex task (forms), it explicitly says: *"If you need to fill out a PDF form, read FORMS.md and follow its instructions."*

### C. Script Bundling & Determinism
- **High Script-to-Doc Ratio**: The skill contains 8 Python scripts and only 3 markdown documents. Rather than relying on the LLM to write complex PDF coordinate translation math from scratch every time, it bundles deterministic, battle-tested Python scripts.

## 2. Actionable Recommendations for Meta-Plugins

### Enhancement for `agent-scaffolders/create-skill`
1. **Scaffold Fallback Trees**: When interviewing the user for a new skill, the scaffolder should explicitly ask: *"What are the common failure modes for this task, and what is the fallback sequence?"* It should then scaffold a dedicated markdown file (like `fallbacks.md` or `forms.md`) if the process is highly brittle.
2. **Promote Script Bundling**: Explicitly suggest bundling Python/Bash scripts for complex data transformations or geometric math, rather than relying on on-the-fly code generation.

### Enhancement for `agent-scaffolders`
1. **Detect Fallback Patterns**: Update the analyzer's anti-pattern detection to flag complex skills that *lack* explicit failure/fallback workflows.
2. **Script Density Score**: Analyze the ratio of executable scripts to markdown instructions. Skills with a high script density should trigger specialized security and complexity scoring.
