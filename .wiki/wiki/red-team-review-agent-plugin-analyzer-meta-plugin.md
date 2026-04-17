---
concept: red-team-review-agent-plugin-analyzer-meta-plugin
source: plugin-code
source_file: agent-plugin-analyzer/references/research/round-1-redteam-review-prompt.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.263490+00:00
cluster: design
content_hash: 0d3be10de0c17fca
---

# Red Team Review: Agent Plugin Analyzer Meta-Plugin

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Red Team Review: Agent Plugin Analyzer Meta-Plugin

## Mission

You are reviewing a newly designed **meta-plugin** called `agent-plugin-analyzer`. This plugin gives AI agents the ability to systematically analyze other plugins and skills — extracting design patterns, detecting anti-patterns, and generating improvement recommendations. It feeds a "virtuous cycle" where analyzing existing work continuously improves the tools used to build future plugins.

**Your job is to critically evaluate this design and find weaknesses, gaps, and improvement opportunities.**

## Context

This plugin exists within an ecosystem of 3 interconnected meta-plugins:
1. **agent-plugin-analyzer** (NEW — the subject of this review)
2. **agent-scaffolders** — generates new plugins, skills, hooks, and sub-agents
3. **agent-skill-open-specifications** — defines the rules and standards everything must follow

The analyzer feeds learnings back into the scaffolders and specs, which produce better plugins, which then get analyzed again (virtuous cycle).

## What to Review

Please evaluate the following dimensions and provide structured feedback:

### 1. Completeness
- Does the 6-phase analysis framework cover everything important?
- Are there file types, component types, or design dimensions we're missing?
- Is the pattern catalog (28 patterns, 7 categories) comprehensive enough?
- Are there known plugin/skill design patterns from other ecosystems we should include?

### 2. HITL (Human-in-the-Loop) Design
- Is the interaction guidance in `hitl-interaction-design.md` thorough enough?
- Are there question types or interaction patterns we're missing?
- Is the output design guidance covering all realistic downstream consumers?
- How should we handle skills that need to adapt their HITL level dynamically?

### 3. Analysis Question Quality
- Review the `analysis-questions-by-type.md` — are the self-prompt questions for each file type sharp enough?
- Are there holistic design considerations we're not asking about?
- Should the questions be weighted or prioritized?

### 4. Architecture Critique
- Is the split between `analyze-plugin` (extraction) and `synthesize-learnings` (recommendation mapping) the right decomposition?
- Should there be additional skills? (e.g., `compare-plugins`, `generate-improvement-pr`, `self-audit`)
- Is the `inventory_plugin.py` script doing enough? Too much?
- Should we have separate scripts for different analysis phases?

### 5. Anti-Pattern Coverage
- Are we catching all the anti-patterns that matter?
- Are there known bad practices in the plugin/skill ecosystem that we should flag?
- Is the severity classification (Error vs Warning vs Info) appropriate?

### 6. Output Design
- Are the output templates in `output-templates.md` sufficient?
- Should we support additional output formats? (JSON, HTML, CSV)
- How should comparative analysis across 10+ plugins be presented?

### 7. Self-Improvement Mechanism
- The analyzer is supposed to improve itself. Is the mechanism for that clear enough?
- How should we track which patterns were discovered when and from where?
- Should the pattern catalog have versioning or a changelog?

### 8. Integration with Scaffolders
- Are the connections between analyzer findings and scaffolder improvements concrete enough?
- Is the `improvement-mapping.md` reference actionable?
- What automated steps could bridge the gap between "finding" and "fixing"?

### 9. Scalability
- How well does this design scale to analyzing 50+ plugins?
- What happens when the pattern catalog grows to 100+ patterns?
- Should we have automated deduplication or clustering of similar patterns?

### 10. What We Missed
- What design dimensions, patterns, or considerations are completely absent from this plugin?
- What would YOU add if you were building this from scratch?
- What would make this the definitive meta-plugin for plugin ecosystem intelligence?

## Response Format

Please structure your response as:

```markdown
## Strengths
- [W

*(content truncated)*

## See Also

- [[round-2-red-team-review-refactored-agent-plugin-analyzer]]
- [[round-3-red-team-review-agent-plugin-analyzer-v3]]
- [[agent-plugin-analyzer-l5-red-team-auditor]]
- [[agent-plugin-analyzer-l5-red-team-auditor]]
- [[red-team-review-loop]]
- [[acceptance-criteria-red-team-review]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-plugin-analyzer/references/research/round-1-redteam-review-prompt.md`
- **Indexed:** 2026-04-17T06:42:09.263490+00:00
