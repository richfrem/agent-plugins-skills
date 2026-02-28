# Project Sanctuary: Plan Augmentation

> This file contains project-specific best practices for the plan workflow.
> It is NOT overwritten by `sync_configuration.py` — only `SKILL.md` is auto-synced.

## Leverage Doc Co-Authoring for Plans

The `doc-coauthoring` skill (from Anthropic/Claude) provides a structured 3-stage workflow that improves plan quality. **Use it when writing plan.md content, especially for complex architectures.**

**Cross-reference**: `plugins/doc-coauthoring/skills/doc-coauthoring/SKILL.md`

### When to Use Doc Co-Authoring

Apply the doc-coauthoring workflow when:
- The plan involves architectural decisions with trade-offs
- Multiple implementation approaches need to be evaluated
- The plan requires data model design or API contracts
- The user wants to co-author the technical approach

Skip it when plans are straightforward (single-file changes, dependency updates, documentation fixes).

### How to Integrate

During `/spec-kitty.plan`, apply the doc-coauthoring stages to the plan content:

#### Stage 1: Context Gathering (Before Plan Generation)

Before generating plan.md:
1. **Review the spec**: Read spec.md thoroughly — identify all requirements and constraints
2. **Technical dump**: Ask the user to share any architectural context, existing patterns, tech stack preferences
3. **Clarifying questions**: Focus on implementation-specific unknowns:
   - Which existing patterns should be followed?
   - Are there performance or scaling constraints?
   - What's the testing strategy preference?
   - Are there migration or backward-compatibility concerns?

#### Stage 2: Refinement (During Plan Writing)

After initial plan.md is generated:
1. **Architecture section**: Brainstorm 3-5 architectural approaches, evaluate trade-offs, let user select
2. **Data model section**: If applicable, propose schema options and let user refine
3. **Dependency ordering**: Map WP dependencies, brainstorm groupings, optimize for parallelism
4. **Risk assessment**: Brainstorm 5-10 risks, user curates which to mitigate vs accept

#### Stage 3: Reader Testing (Before Task Generation)

Before moving to `/spec-kitty.tasks`:
1. **Predict implementer questions**: What will the agent executing WP01 need to know?
2. **Test self-sufficiency**: Can each WP be implemented from the plan alone?
3. **Verify spec alignment**: Does every spec requirement map to at least one WP?
4. **Fix gaps**: Ensure no WP has ambiguous deliverables

### Plan Quality Signals

A plan is ready for task generation when:
- Every spec requirement maps to a concrete implementation step
- WP dependencies form a valid DAG (no circular dependencies)
- Each WP has clear, testable deliverables
- Architectural decisions are documented with rationale (not just "we chose X")
- An implementing agent can start coding from the plan without asking "but how?"
