---
concept: command-template-spec-kittyspecify-documentation-mission
source: plugin-code
source_file: spec-kitty-plugin/assets/templates/.kittify/missions/documentation/command-templates/specify.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.332422+00:00
cluster: feature
content_hash: 1949084aa6cf85f6
---

# Command Template: /spec-kitty.specify (Documentation Mission)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Create a documentation-focused feature specification with discovery and Divio scoping.
---

# Command Template: /spec-kitty.specify (Documentation Mission)

**Phase**: Discover
**Purpose**: Understand documentation needs, identify iteration mode, select Divio types, detect languages, recommend generators.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Discovery Gate (mandatory)

Before running any scripts or writing to disk, conduct a structured discovery interview tailored to documentation missions.

**Scope proportionality**: For documentation missions, discovery depth depends on project maturity:
- **New project** (initial mode): 3-4 questions about audience, goals, Divio types
- **Existing docs** (gap-filling mode): 2-3 questions about gaps, priorities, maintenance
- **Feature-specific** (documenting new feature): 1-2 questions about feature scope, integration

### Discovery Questions

**Question 1: Iteration Mode** (CRITICAL)

Ask user which documentation scenario applies:

**(A) Initial Documentation** - First-time documentation for a project (no existing docs)
**(B) Gap-Filling** - Improving/extending existing documentation
**(C) Feature-Specific** - Documenting a specific new feature/module

**Why it matters**: Determines whether to run gap analysis, how to structure workflow.

**Store answer in**: `meta.json → documentation_state.iteration_mode`

---

**Question 2A: For Initial Mode - What to Document**

Ask user:
- What is the primary audience? (developers, end users, contributors, operators)
- What are the documentation goals? (onboarding, API reference, troubleshooting, understanding architecture)
- Which Divio types are most important? (tutorial, how-to, reference, explanation)

**Why it matters**: Determines which templates to generate, what content to prioritize.

---

**Question 2B: For Gap-Filling Mode - What's Missing**

Inform user you will audit existing documentation, then ask:
- What problems are users reporting? (can't get started, can't solve specific problems, APIs undocumented, don't understand concepts)
- Which areas need documentation most urgently? (specific features, concepts, tasks)
- What Divio types are you willing to add? (tutorial, how-to, reference, explanation)

**Why it matters**: Focuses gap analysis on user-reported issues, prioritizes work.

---

**Question 2C: For Feature-Specific Mode - Feature Details**

Ask user:
- Which feature/module are you documenting?
- Who will use this feature? (what audience)
- What aspects need documentation? (getting started, common tasks, API details, architecture/design)

**Why it matters**: Scopes documentation to just the feature, determines which Divio types apply.

---

**Question 3: Language Detection & Generators**

Auto-detect project languages:
- Scan for `.js`, `.ts`, `.jsx`, `.tsx` files → Recommend JSDoc/TypeDoc
- Scan for `.py` files → Recommend Sphinx
- Scan for `Cargo.toml`, `.rs` files → Recommend rustdoc

Present to user:
"Detected languages: [list]. Recommend these generators: [list]. Proceed with these?"

Allow user to:
- Confirm all
- Select subset
- Skip generators (manual documentation only)

**Why it matters**: Determines which generators to configure in planning phase.

**Store answer in**: `meta.json → documentation_state.generators_configured`

---

**Question 4: Target Audience (if not already clear)**

If not clear from earlier answers, ask:
"Who is the primary audience for this documentation?"
- Developers integrating your library/API
- End users using your application
- Contributors to your project
- Operators deploying/maintaining your system
- Mix of above (specify)

**Why it matters**: Affects documentation tone, depth, assumed knowledge.

**Store answer in**: `spec.md → ## Documentation Scope → Target Audience`

---

**Question 5: Publish Scope (optional)**

Ask user:
- Is documentation release/publish in scope for this effort?
- If yes, 

*(content truncated)*

## See Also

- [[command-template-spec-kittyimplement-documentation-mission]]
- [[command-template-spec-kittyplan-documentation-mission]]
- [[command-template-spec-kittyreview-documentation-mission]]
- [[command-template-spec-kittytasks-documentation-mission]]
- [[command-template-spec-kittytasks-research-mission]]
- [[command-template-spec-kittytasks-research-mission]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/assets/templates/.kittify/missions/documentation/command-templates/specify.md`
- **Indexed:** 2026-04-17T06:42:10.332422+00:00
