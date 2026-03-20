# The Dual-Mode Meta-Skill (Bootstrap → Iteration)

**Use Case:** Complex domains where the agent needs to generate its own contextual reference files or even scaffold out entirely new skills dynamically.

## The Core Mechanic

A tool that doesn't just execute logic, but *manages the creation of other tools and skills*. It operates in two explicit lifecycle modes declared in its frontmatter: Bootstrap (create from scratch) and Iteration (update existing).

### Implementation Standard

Define the modes explicitly in the skill description:

```yaml
---
name: domain-context-extractor
description: >
  BOOTSTRAP MODE - Triggers: "Create a new domain context skill"
  → Asks key questions, structures directories, and generates the initial SKILL.md
  
  ITERATION MODE - Triggers: "Add context about [new topic]"
  → Loads the existing skill, finds gaps, and appends new reference files without destroying the old structure.
---
```

Instruct the agent inside the skill on how to handle the filesystem operations for both modes, acting as an internal file scaffolding engine.
