# Synthesis of Learnings: Anthropic Skills Repository

**Source**: `https://github.com/anthropics/skills.git`
**Analyzed Skills**: `skill-creator`, `pdf`, `doc-coauthoring`, `mcp-builder`

## 1. Executive Summary
A deep-dive analysis of the official Anthropic skills repository reveals significant advancements in how skills are structured, tested, and optimized. The introduction of rigorous evaluation loops, dynamic context fetching, and multi-agent testing workflows are patterns that should immediately be ported into our `agent-scaffolders` and `agent-scaffolders`.

## 2. Key Pattern Discoveries

### A. The Evaluation & Benchmark Pattern (from `skill-creator`)
**Observation**: The `skill-creator` implements a software-development-like rigor for evaluating agent skills. It uses parallel sub-agents to run test prompts in a clean context, separating a "baseline" run (without the skill) from a "with-skill" run. It captures timing and token data, and it uses a secondary subagent (`grader.md`) to assert pass/fail criteria.
**Target Improvement**: Our `create-skill` scaffolder should scaffold an `evals/evals.json` alongside `references/` and integrate a basic grader or testing structure so that every skill we create is born testable.

### B. The Context-Free Reader Testing Pattern (from `doc-coauthoring`)
**Observation**: For complex generation skills like documentation co-authoring, the skill explicitly spins up a fresh "Reader Claude" subagent that has absolutely no context from the current conversation. This subagent acts as a blind reviewer to catch false assumptions or missing context.
**Target Improvement**: `agent-scaffolders/skills/create-sub-agent` should include an option for a "Tainted Context Cleanser" or "Blind Reviewer" pattern. The `agent-scaffolders` should look for this pattern in skills that generate persistent artifacts.

### C. Trigger Description Optimization (from `skill-creator`)
**Observation**: Output quality is moot if the skill fails to trigger. `skill-creator` uses an automated loop to test the skill's description against 20 "should-trigger" and "should-not-trigger" prompts on a 60/40 train/test split.
**Target Improvement**: The `agent-scaffolders` needs to mandate clear trigger testing. `create-skill` could generate a `trigger-evals.json`.

### D. Dynamic Specification Fetching (from `mcp-builder`)
**Observation**: Instead of bundling massive specifications inside the skill, `mcp-builder` instructs the agent to use `WebFetch` to dynamically pull the latest MCP schema directly from `raw.githubusercontent.com`.
**Target Improvement**: `agent-scaffolders/skills/create-mcp-integration` should automatically inject WebFetch instructions to pull the latest SDK specs instead of relying on stale pre-trained knowledge.

### E. Environment-Aware Degradation (from `skill-creator`)
**Observation**: The skill explicitly changes its workflow depending on where it's running (e.g., Cowork vs. Claude.ai vs. Claude Code), adjusting mechanisms like how it handles parallel sub-agents or local file HTML browser views.
**Target Improvement**: `agent-scaffolders` should define an "Environment Awareness" standard, providing templates for how a skill should degrade gracefully if sub-agents or UI rendering aren't available.

## 3. Next Steps & Recommendations

1. **Update `pattern-catalog.md`**: Add the "Blind Reader Test", "Trigger Optimizer", and "Dynamic Context Fetch" to the catalog.
2. **Update `create-skill` Scaffolder**: Scaffold `evals/evals.json` and a `.gitignore` ignoring benchmark artifacts by default.
3. **Update Specs**: Incorporate these patterns into `ecosystem-authoritative-sources/reference/skills.md`.
