---
concept: agent-skills-best-practices
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/link-checker-agent/references/best-practices.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.107878+00:00
cluster: plugin-code
content_hash: 387a09dbc55929cc
---

# Agent Skills Best Practices

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Agent Skills Best Practices

Source: [agentskills.io](https://agentskills.io/skill-creation/best-practices.md)
Built with [Mintlify](https://mintlify.com)

---

# Best practices for skill creators

How to write skills that are well-scoped and calibrated to the task.

### Match specificity to fragility
**Give the agent freedom** when multiple approaches are valid and the task tolerates variation. For flexible instructions, explaining *why* can be more effective than rigid directives.

**Be prescriptive** when operations are fragile, consistency matters, or a specific sequence must be followed:

````markdown
## Database migration

Run exactly this sequence:
```bash
python scripts/migrate.py --verify --backup
```
Do not modify the command or add additional flags.
````

### Provide defaults, not menus
When multiple tools or approaches could work, pick a default and mention alternatives briefly rather than presenting them as equal options.

### Favor procedures over declarations
A skill should teach the agent *how to approach* a class of problems, not *what to produce* for a specific instance.

### Gotchas sections
The highest-value content in many skills is a list of gotchas — environment-specific facts that defy reasonable assumptions.

### Templates for output format
When you need the agent to produce output in a specific format, provide a template.

### Checklists for multi-step workflows
An explicit checklist helps the agent track progress and avoid skipping steps.

### Validation loops
Instruct the agent to validate its own work before moving on.

### Plan-validate-execute
For batch or destructive operations, have the agent create an intermediate plan in a structured format, validate it against a source of truth, and only then execute.

### Bundling reusable scripts
When iterating on a skill, if you notice the agent independently reinventing the same logic each run, that's a signal to write a tested script once and bundle it in `scripts/`.

---
Built with [Mintlify](https://mintlify.com)


## See Also

- [[agent-triggering-examples-best-practices]]
- [[agent-triggering-examples-best-practices]]
- [[azure-ai-foundry-agents-open-agent-skills]]
- [[strategic-analysis-agent-skills-ecosystem-in-azure]]
- [[agent-skills-documentation-index]]
- [[link-checking-standards-best-practices]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/link-checker-agent/references/best-practices.md`
- **Indexed:** 2026-04-17T06:42:10.107878+00:00
