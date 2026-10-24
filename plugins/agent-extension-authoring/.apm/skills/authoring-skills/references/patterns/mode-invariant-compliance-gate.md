# Mode-Invariant Compliance Gate

**Status:** Draft
**Pattern Type:** Structural Constraint
**Applicable Domain:** Legal, Compliance, Brand, Security, Health

## Executive Summary
A structurally isolated block of mandatory checks that are declared **immune to all conditional execution logic** in the skill. Unlike every other step in the workflow—which executes only when a tool is connected, a configuration exists, or a specific sub-action is requested—the Mode-Invariant Compliance Gate fires **regardless of execution path, configuration state, or user-provided context**. It forms a structural compliance floor.

## The Abstract Problem
When a skill supports multiple modes of execution (e.g., "Full Audit" vs. "Quick Review", or using brand tools vs. generic evaluation), agents often skip safety or compliance checks if those checks are nested inside a branch that wasn't executed. If minimum compliance is required in *every* branch, repeating the check across all branches causes bloat and maintenance errors. 

## The Target
Any workflow where a "minimum safety floor" exists that the agent must absolutely evaluate on every single invocation without exception.

## The Core Mechanic
The skill implicitly partitions all checks into two sets:
1. **Conditionally-executed checks** — governed by `if/else` logic (e.g., guidelines present / absent)
2. **Invariantly-executed checks** — declared `regardless of` all conditions

The invariant partition forms a **compliance floor**: a minimum safety guarantee that is structurally decoupled from the skill's operational modes. No user configuration, missing tool, or execution path can disable it. The agent is constrained to run this layer in every invocation.

## Distinction from Similar Patterns
- **Anti-Pattern Vaccination**: APV screens the draft for domain-specific quality mistakes. The MICG fires as a mandatory execution layer independent of draft quality review.
- **Conditional Step Inclusion**: CSI gates steps behind tool availability (if/else inclusion). MICG steps are *never gated*. The concept of exclusion does not apply.
- **Graduated Autonomy**: GA maps classified risk levels to an autonomy tier. MICG predates all classification; it is the check that *cannot be turned off* by any configuration of risk or mode.

## Implementation Standard

```markdown
## [Step N]: Invariant Compliance Gate

> **Always executed regardless of execution mode, configuration state, or available tools.**

The following checks run in every invocation of this command. They are not conditional. They do not depend on any prior step. They do not degrade.

| Check | What to Flag | Required Action |
|---|---|---|
| [Compliance Check 1] | [Trigger condition] | [Required output behavior] |
| [Compliance Check 2] | [Trigger condition] | [Required output behavior] |

These findings are surfaced in a dedicated `### Compliance Flags` section, **separate from all other output sections**, regardless of whether other findings exist.
```

**Structural rule:** The invariant gate block must appear in the skill at the same hierarchical level as the conditional execution branches—not nested within them. Its independence must be structurally visible, not just prose-declared.

## Anti-Patterns
1. **The Nested Safety Check:** Putting the compliance check inside the "Full Audit" branch, causing "Quick Review" users to bypass safety rules.
2. **The Implicit Assumption:** Assuming the agent will holistically evaluate safety without an explicit structural block demanding it.
3. **The Silent Pass:** Failing to generate the `### Compliance Flags` section when no issues are found. It MUST generate the block with a "Pass" message to prove it executed the invariant logic.
