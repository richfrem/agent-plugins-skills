# Trigger Description Optimization Loop

**Pattern Name**: Trigger Description Optimization Loop
**Category**: Evaluation & Tuning
**Complexity Level**: L5 (Meta-Pattern)

## Description
Agents struggle with "undertriggering" or matching overly broad namespaces because developers write skill descriptions based on intent rather than actual semantic search dynamics. This pattern embeds a post-creation optimization phase where the agent tests the new skill's description against a battery of positive (should-trigger) and negative (should-not-trigger) prompts, iteratively refining the text until it achieves maximum precision and recall against the agent's semantic router.

## When to Use
- Inside meta-skills that generate other skills or plugins (`create-skill`, `create-plugin`).
- When a skill namespace overlaps heavily with canonical knowledge or adjacent skills.
- As a CI/CD pipeline step during pull requests for skill modifications.

## Implementation Example
```markdown
### Trigger Tuning Phase
After finalizing the `././SKILL.md` body logic:
1. Generate an array of 5 Highly Specific "Should-Trigger" prompts.
2. Generate an array of 5 Ambiguous "Should-Not-Trigger" prompts (near-misses).
3. Execute `python3 scripts/optimize_trigger.py --skill ./my-skill --evals ./trigger_evals.json`.
4. The background script will iteratively rewrite and test the frontmatter `description` field until the trigger accuracy exceeds 90%.
5. Apply the optimized description.
```

## Anti-Patterns
- Writing generic, one-sentence descriptions: "A skill to analyze data."
- Trusting the initially drafted description without running comparative evaluation against the existing tool registry ecosystem.
