# Analysis Framework Reference

Deep reference for the 6-phase plugin/skill analysis methodology.

## Phase Details

### Phase 1: Inventory — Detailed Rubric

The inventory phase produces a complete file manifest. The goal is zero surprises — every file accounted for and classified.

**Classification Priority Order:**
1. Exact filename match (e.g., `SKILL.md` → skill, `plugin.json` → manifest)
2. Parent directory context (e.g., files in `commands/` → command, files in `references/` → reference)
3. File extension fallback (e.g., `.py` → script, `.md` → document)
4. Default to "other"

**Metrics to Capture:**
| Metric | Why It Matters |
|--------|----------------|
| Total file count | Plugin complexity indicator |
| Lines per SKILL.md | Progressive disclosure compliance (<500) |
| Script count | Automation maturity indicator |
| Reference file count | Knowledge depth indicator |
| Command count | User-facing surface area |
| Ratio: refs to skills | How much depth per skill |

### Phase 2: Structure Analysis — Evaluation Rubric

Score each dimension on a 3-point scale:

| Dimension | ✅ Exemplary | ⚠️ Adequate | ❌ Needs Work |
|-----------|-------------|-------------|---------------|
| **Progressive Disclosure** | SKILL.md <300 lines, rich `references/` | SKILL.md <500 lines, some refs | SKILL.md >500 lines or no refs |
| **README Quality** | File tree + examples + diagram | File tree + basic description | Missing or minimal |
| **Naming** | All kebab-case, descriptive names | Mostly consistent | Inconsistent or unclear |
| **Component Balance** | Skills + commands + refs + scripts | Skills + some support files | Monolithic SKILL.md only |
| **Connector Design** | `~~category` abstraction for tools | Named tools with fallbacks | Hardcoded tool dependencies |
| **Standalone Capability** | Fully works without MCP tools | Core works, MCP enhances | Requires MCP to function |

### Phase 3: Content Analysis — Quality Signals

**High-quality SKILL.md indicators:**
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
- Deep domain knowledge not duplicated in SKILL.md
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
| 1 | SKILL.md > 500 lines | Warning | Line count |
| 2 | Missing acceptance criteria | Error | No `references/acceptance-criteria.md` |
| 3 | Bash/PowerShell scripts | Error | `.sh` or `.ps1` in `scripts/` |
| 4 | Hardcoded absolute paths | Warning | Grep for `/Users/`, `/home/`, `C:\` |
| 5 | Missing README file tree | Warning | No `├──` / `└──` in README |
| 6 | Unqualified tool names | Warning | MCP tool references without namespace |
| 7 | Silent error handling | Warning | Scripts with bare `except:` or `|| true` |
| 8 | Nested references | Warning | Reference files linking to other references |
| 9 | Monolithic SKILL.md | Warning | >300 lines with no `references/` directory |
| 10 | Description not third person | Info | Starts with "I" or "You" instead of verb |
| 11 | Missing `CONNECTORS.md` | Info | Plugin uses MCP tools but no connector docs |
| 12 | No examples | Info | No `examples/` directory or inline examples |

### Phase 6: Synthesis — Report Structure

> For the full report templates (single plugin and comparative mode), see [output-templates.md](./output-templates.md).
> For the maturity model and scoring weights, see [maturity-model.md](./maturity-model.md).
