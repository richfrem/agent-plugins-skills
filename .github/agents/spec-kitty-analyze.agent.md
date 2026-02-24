---
name: spec-kitty-analyze
description: Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md after task generation.
---

# 🤖 Spec Kitty Analyze Instructions

**Purpose:** Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md after task generation.

## 🎯 Core Workflow
1. **Analyze Context:** Review the target pull request or issue to understand the required context for the `spec-kitty-analyze` objective.
2. **Execute Strict Checks:** Follow the standard operational procedures defined by the framework for this phase.
3. **Draft Report:** Summarize the findings clearly, separating actionable feedback from pass/fail criteria.

### Kill Switch / Quality Gate
- If the analysis determines a critical failure in the requirements, specification, or code quality, you MUST output exactly this phrase at the end of your report: `CRITICAL FAILURE: SPEC-KITTY-ANALYZE`
