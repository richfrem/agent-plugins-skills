---
concept: synthesize-learnings
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/synthesize-learnings/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.254592+00:00
cluster: analysis
content_hash: 1ba67e58670b912c
---

# Synthesize Learnings

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: synthesize-learnings
description: >
  Convert raw plugin analysis results into actionable improvement recommendations for agent-scaffolders
  and agent-skill-open-specifications. Trigger with "synthesize learnings", "generate improvement
  recommendations", "what should we improve in our scaffolders", "update our meta-skills based on
  these findings", or after completing a plugin analysis.
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Synthesize Learnings

Take raw analysis output from `analyze-plugin` and transform it into concrete, actionable improvements for our meta-skills ecosystem. This is the "close the loop" skill that turns observations into evolution.

## Improvement Targets

Learnings are mapped to three improvement targets:

### Target 1: `agent-scaffolders`
Improvements to the plugin/skill/hook/sub-agent scaffolding tools.

**What to look for:**
- New component types or patterns that `scaffold.py` should support
- Better default templates based on exemplary plugins
- New scaffolder skills needed (e.g., creating connectors, reference files)
- Improved acceptance criteria templates based on real-world examples

### Target 2: `agent-skill-open-specifications`
Improvements to ecosystem standards and authoritative source documentation.

**What to look for:**
- New best practices discovered from high-quality plugins
- Anti-patterns that should be documented as warnings
- Spec gaps where plugins do things the standards don't address
- New pattern categories to add to ecosystem knowledge

### Target 3: `agent-plugin-analyzer` (Self-Improvement)
Improvements to this analyzer plugin itself.

**What to look for:**
- New patterns discovered that should be added to `pattern-catalog.md`
- Analysis blind spots — things that should have been caught
- Framework gaps — phases that need refinement
- New anti-patterns to add to the detection checklist

### Target 4: Domain Plugins (e.g., `oracle-legacy-system-analysis`)
Improvements to the primary domain plugins in this repository — especially the legacy Oracle Forms/DB analysis plugins.

**What to look for:**
- **Severity/classification frameworks** that could improve how legacy code issues are categorized (e.g., GREEN/YELLOW/RED deviation severity from legal contract-review)
- **Playbook-based review methodology** adaptable to legacy code review playbooks (standard migration positions, acceptable risk levels)
- **Confidence scoring** applicable to legacy code analysis certainty levels
- **Connector abstractions** (`~~category` patterns) for tool-agnostic Oracle analysis workflows
- **Progressive disclosure structures** for organizing deep Oracle Forms/DB reference knowledge
- **Decision tables** for legacy migration pathways (like chart selection guides but for migration strategies)
- **Checklist patterns** for legacy system audit completeness
- **Tiered execution strategies** for handling different legacy code complexity levels
- **Bootstrap/iteration modes** for incremental legacy system analysis
- **Output templates** (HTML artifacts, structured reports) for presenting legacy analysis results

## Synthesis Process

### Step 1: Gather Analysis Results
Collect all analysis reports from the current session or from referenced analysis artifacts.

### Step 2: Categorize Observations

Sort every observation into one of these categories:

| Category | Description | Maps To |
|----------|-------------|---------|
| **Structural Innovation** | Novel directory layouts, component organization | Scaffolders |
| **Content Pattern** | Reusable content structures (tables, frameworks, checklists) | Specs + Catalog + Domain |
| **Execution Pattern** | Workflow designs

*(content truncated)*

## See Also

- [[synthesize-learnings-input-contract]]
- [[acceptance-criteria-synthesize-learnings]]
- [[procedural-fallback-tree-synthesize-learnings]]
- [[acceptance-criteria-synthesize-learnings]]
- [[procedural-fallback-tree-synthesize-learnings]]
- [[acceptance-criteria-synthesize-learnings]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/synthesize-learnings/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.254592+00:00
