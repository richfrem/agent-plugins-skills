---
concept: skillcommand-two-tier-knowledge-architecture
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/skill-command-two-tier.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.014965+00:00
cluster: skill
content_hash: 8263fe4d39f85bc8
---

# Skill–Command Two-Tier Knowledge Architecture

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Skill–Command Two-Tier Knowledge Architecture

**Use Case:** Large domains (e.g., UX Design, Legal Compliance, Security Auditing) where complex declarative knowledge (rubrics, principles, laws) needs to be separated from procedural workflow logic (slash commands, input routing).

## The Core Mechanic

Do not conflate "what the agent knows" with "what the agent does." Separate the bundle into two distinct tiers:

1. **Skills**:
   - Hold *declarative domain knowledge* (frameworks, principles, criteria).
   - Have no output formatting, no input routing.
   - Example: `design-critique/SKILL.md` contains the 5-point heuristics framework.
   - Loaded passively via natural language triggers defined in their YAML fontmatter.

2. **Commands**:
   - Hold *procedural workflow logic* (input routing, output templates, connector conditional blocks).
   - Are invoked manually by the user via slash commands (e.g., `/critique`).
   - Do NOT duplicate knowledge; they defer to the Skill.

### Implementation Standard

Inside the procedural Command `.md` file, use explicit cross-referencing to load the declarative Skill:

```markdown
See the **[skill-name]** skill for the evaluation framework, rubrics, and feedback principles. Do not violate those principles when filling out the output template below.
```


## See Also

- [[skill-command-two-tier]]
- [[skill-command-two-tier]]
- [[skill-command-two-tier]]
- [[skill-command-two-tier]]
- [[skill-command-two-tier]]
- [[skill-command-two-tier]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/skill-command-two-tier.md`
- **Indexed:** 2026-04-17T06:42:10.014965+00:00
