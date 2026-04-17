---
concept: pattern-catalog
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/synthesize-learnings/pattern-catalog.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.257503+00:00
cluster: confidence
content_hash: 3bfe10b4ae5a4b71
---

# Pattern Catalog

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Pattern Catalog

A living catalog of reusable design patterns extracted from plugin and skill analyses. This catalog grows with every analysis — new patterns are appended by the `synthesize-learnings` skill.

## Governance Model

### Pattern Lifecycle States
| State | Meaning | Criteria to Advance |
|-------|---------|-------------------|
| `proposed` | Observed in a single analysis, not yet validated | Must be found in ≥1 plugin |
| `validated` | Confirmed across ≥2 independent plugins | Quality rated "good" or better in both |
| `canonical` | Recommended best practice, embedded in scaffolders | Adopted into `create-skill` or `create-plugin` templates |
| `deprecated` | Superseded or no longer aligned with ecosystem standards | Marked with replacement pattern reference |

### Required Fields Per Pattern
Every pattern entry MUST include:
- **Category**: Architectural / Execution / Content / Knowledge / Interaction / Integration
- **Lifecycle**: `proposed` / `validated` / `canonical` / `deprecated`
- **Confidence**: High (≥3 plugins) / Medium (2 plugins) / Low (1 plugin)
- **First Seen In**: Plugin name and analysis date
- **Last Validated**: Date of most recent cross-plugin confirmation (YYYY-MM-DD)
- **Frequency**: Count of plugins observed using this pattern
- **Description**: What it is and how it works
- **When to Use**: Conditions where this pattern applies
- **Example**: Concrete implementation reference

> **Ossification trigger**: If a `canonical` pattern has `Last Validated` older than 180 days,
> flag it for re-review before the next catalog update. Patterns not confirmed in a living plugin
> for >1 year should be downgraded to `deprecated` unless actively used in scaffolder templates.

### Deduplication Rules
Before adding a new pattern:
1. Check if an existing pattern covers ≥80% of the same behavior
2. If so, update the existing pattern's frequency and add the new source
3. If the new pattern is a meaningful variant, add it as a sub-entry under the parent
4. Never add near-duplicates as separate top-level patterns

### Provenance Tracking
The changelog at the bottom of this file tracks when patterns were added, promoted, or deprecated.

---

## Architectural Patterns

### Standalone vs Supercharged
- **Category**: Architectural
- **Lifecycle**: `canonical`
- **Confidence**: High
- **Frequency**: 5+ plugins
- **First Seen In**: Anthropic sales, customer-support, engineering plugins
- **Description**: Every command and skill works without any MCP integrations (standalone mode), but becomes dramatically more powerful when tools are connected (supercharged). The README documents both paths in a comparison table.
- **When to Use**: Any plugin that can optionally integrate with external tools
- **Example**: Sales `call-prep` skill works with user-provided context, but auto-pulls CRM data when Salesforce connector is available

### Connector Abstraction (`~~category`)
- **Category**: Architectural
- **Lifecycle**: `canonical`
- **Confidence**: High
- **Frequency**: 5+ plugins
- **First Seen In**: Anthropic sales, customer-support, engineering plugins
- **Description**: Use `~~category` placeholders (e.g., `~~project tracker`, `~~chat`, `~~source control`) instead of hardcoding specific tool names. A `CONNECTORS.md` file maps categories to concrete tool options. Makes plugins tool-agnostic.
- **When to Use**: Any plugin intended for distribution across organizations using different tool stacks
- **Example**: `~~project tracker` could be Linear, Jira, or Asana depending on the user's setup

### Meta-Skills (Skills That Generate Skills)
- **Category**: Architectural / Meta
- **Lifecycle**: `validated`
- **Confidence**: Medium
- **Frequency**: 2 plugins
- **First Seen In**: Anthropic `data-context-extractor`, `create-cowork-plugin`
- **Description**: A skill whose primary output is another skill. Follows a guided interview process to extract domain knowledge, then generates a complete skill directory (SKILL.md + references

*(content truncated)*

## See Also

- [[ai-pattern-catalog]]
- [[ai-pattern-catalog]]
- [[loop-scheduler-and-heartbeat-pattern]]
- [[agent-loops-pattern-guide]]
- [[39-pattern-l4-architectural-decision-matrix]]
- [[pattern-action-forcing-output-with-deadline-attribution]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/synthesize-learnings/pattern-catalog.md`
- **Indexed:** 2026-04-17T06:42:10.257503+00:00
