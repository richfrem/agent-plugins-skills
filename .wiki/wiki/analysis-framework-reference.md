---
concept: analysis-framework-reference
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/analyze-plugin/references/analysis-framework.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.713152+00:00
cluster: skill
content_hash: 9457bbfa775d5a9f
---

# Analysis Framework Reference

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Analysis Framework Reference

Deep reference for the 6-phase plugin/skill analysis methodology.

## Phase Details

### Phase 1: Inventory — Detailed Rubric

The inventory phase produces a complete file manifest. The goal is zero surprises — every file accounted for and classified.

**Classification Priority Order:**
1. Exact filename match (e.g., `./SKILL.md` → skill, `.claude-plugin/plugin.json` → manifest)
2. Parent directory context (e.g., files in `commands/` → command, files in `references/` → reference)
3. File extension fallback (e.g., `.py` → script, `.md` → document)
4. Default to "other"

**Metrics to Capture:**
| Metric | Why It Matters |
|--------|----------------|
| Total file count | Plugin complexity indicator |
| Lines per ./SKILL.md | Progressive disclosure compliance (<500) |
| Script count | Automation maturity indicator |
| Reference file count | Knowledge depth indicator |
| Command count | User-facing surface area |
| Ratio: refs to skills | How much depth per skill |

### Phase 2: Structure Analysis — Evaluation Rubric

Score each dimension on a 3-point scale:

| Dimension | ✅ Exemplary | ⚠️ Adequate | ❌ Needs Work |
|-----------|-------------|-------------|---------------|
| **Progressive Disclosure** | ./SKILL.md <300 lines, rich `references/` | ./SKILL.md <500 lines, some refs | ./SKILL.md >500 lines or no refs |
| **README Quality** | File tree + examples + diagram | File tree + basic description | Missing or minimal |
| **Naming** | All kebab-case, descriptive names | Mostly consistent | Inconsistent or unclear |
| **Component Balance** | Skills + commands + refs + scripts | Skills + some support files | Monolithic ./SKILL.md only |
| **Connector Design** | `~~category` abstraction for tools | Named tools with fallbacks | Hardcoded tool dependencies |
| **Standalone Capability** | Fully works without MCP tools | Core works, MCP enhances | Requires MCP to function |

### Phase 3: Content Analysis — Quality Signals

**High-quality ./SKILL.md indicators:**
- Description uses third person and includes trigger phrases
- Clear execution flow with numbered phases/steps
- Decision trees for branching logic
- Tables for structured reference data
- Links to `references/` for deep content
- Output format specifications or templates
- Quality checklists at the end

**High-quality Command indicators:**
- Written as instructions FOR the agent (imperative voice)
- Clear argument specification
- Standalone + supercharged paths documented
- Error handling guidance

**High-quality Reference indicators:**
- Deep domain knowledge not duplicated in ./SKILL.md
- Organized by topic/subdomain
- Tables of contents for files >100 lines
- Cross-references to related references
- Examples and code samples

### Phase 4: Pattern Extraction — What to Look For

**Structural Patterns:**
- How are files organized? Flat skills or nested domain groups?
- Is there a `CONNECTORS.md` for tool abstraction?
- Are there `scripts/` for deterministic operations?
- How are config files handled? (`.mcp.json`, `hooks.json`, settings)

**Content Patterns:**
- Decision tables (rows = options, columns = criteria)
- Severity/priority frameworks (P1-P4, GREEN/YELLOW/RED, Tier 1-3)
- Confidence scoring systems
- Output templates (HTML, markdown, structured formats)
- Checklist patterns (quality, accessibility, compliance)
- ASCII workflow diagrams

**Execution Patterns:**
- Phase-based workflows (Discovery → Planning → Execution → Delivery)
- Bootstrap + Iteration dual-mode designs
- Tiered execution strategies (basic → intermediate → advanced)
- Fallback chains (try tool → try manual → ask user)

**Meta-Patterns:**
- Skills that generate other skills
- Self-referencing improvement loops
- Plugin-within-plugin architectures
- Guided wizard-style interactions

### Phase 5: Anti-Pattern Detection — Full Checklist

| # | Anti-Pattern | Severity | How to Detect |
|---|-------------|----------|---------------|
| 1 | ./SKILL.md > 500 lines | Warning | Lin

*(content truncated)*

## See Also

- [[optimizer-engine-patterns-reference-design]]
- [[project-setup-reference-guide]]
- [[optimizer-engine-patterns-reference-design]]
- [[analysis-questions-by-file-type]]
- [[quantification-enforcement-in-analysis]]
- [[security-analysis-checks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/analyze-plugin/references/analysis-framework.md`
- **Indexed:** 2026-04-17T06:42:09.713152+00:00
