---
concept: the-dual-mode-meta-skill-bootstrap-iteration
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/dual-mode-meta-skill.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.007523+00:00
cluster: modes
content_hash: ca407dc29117d32b
---

# The Dual-Mode Meta-Skill (Bootstrap → Iteration)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


## See Also

- [[dual-mode-meta-skill]]
- [[dual-mode-meta-skill]]
- [[dual-mode-meta-skill]]
- [[dual-mode-meta-skill]]
- [[dual-mode-meta-skill]]
- [[dual-mode-meta-skill]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/dual-mode-meta-skill.md`
- **Indexed:** 2026-04-17T06:42:10.007523+00:00
