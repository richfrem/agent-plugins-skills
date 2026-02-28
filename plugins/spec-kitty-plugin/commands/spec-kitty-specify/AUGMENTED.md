# Project Sanctuary: Specify Augmentation

> This file contains project-specific best practices for the specify workflow.
> It is NOT overwritten by `sync_configuration.py` — only `SKILL.md` is auto-synced.

## Leverage Doc Co-Authoring for Specifications

The `doc-coauthoring` skill (from Anthropic/Claude) provides a structured 3-stage workflow that significantly improves specification quality. **Use it when writing spec.md content.**

**Cross-reference**: `plugins/doc-coauthoring/skills/doc-coauthoring/SKILL.md`

### When to Use Doc Co-Authoring

Apply the doc-coauthoring workflow when:
- The feature is ambiguous or complex (Track B Discovery)
- Multiple stakeholders need to understand the spec
- The scope needs iterative refinement before planning
- The user has lots of context to dump but it's unorganized

Skip it for Track A (Factory) or Track C (Micro-Tasks) where specs are deterministic.

### How to Integrate

During `/spec-kitty.specify`, apply the doc-coauthoring stages to the spec content:

#### Stage 1: Context Gathering (Before Spec Generation)

Before running the CLI to generate spec.md:
1. **Ask the 5 meta-context questions**: doc type (always "feature spec"), audience, desired impact, template (use spec-kitty template), constraints
2. **Info dump**: Let the user dump all context — technical details, dependencies, stakeholder concerns, timeline pressures
3. **Clarifying questions**: Generate 5-10 targeted questions based on gaps
4. **Exit when**: You can ask about edge cases and trade-offs without needing basics explained

#### Stage 2: Refinement (During Spec Writing)

After initial spec.md is generated:
1. **Section-by-section refinement**: For each spec section (User Scenarios, Acceptance Criteria, Non-Functional Requirements), brainstorm 5-20 options
2. **Curation**: User picks what to keep/remove/combine
3. **Gap check**: Ask what's missing after each section
4. **Iterative editing**: Use surgical edits, never reprint the whole spec

#### Stage 3: Reader Testing (Before Plan Phase)

Before moving to `/spec-kitty.plan`:
1. **Predict questions**: What will the implementing agent ask when reading this spec?
2. **Test clarity**: Can a fresh agent understand the spec without additional context?
3. **Fix gaps**: Loop back to refinement for any sections that confused the reader

### Quality Signals

A spec is ready for planning when:
- An agent with no prior context can understand the feature from the spec alone
- Acceptance criteria are testable and unambiguous
- Edge cases and failure modes are documented
- Dependencies are explicitly listed
