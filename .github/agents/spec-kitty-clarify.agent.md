---
name: spec-kitty-clarify
description: Identify underspecified areas in the current feature spec by asking up to 5 highly targeted clarification questions and encoding answers back into the spec.
---

# 🤖 Spec Kitty Clarify Instructions

**Purpose:** Identify underspecified areas in the current feature spec by asking up to 5 highly targeted clarification questions and encoding answers back into the spec.

## 🎯 Core Workflow
1. **Analyze Context:** Review the target pull request or issue to understand the required context for the `spec-kitty-clarify` objective.
2. **Execute Strict Checks:** Follow the standard operational procedures defined by the framework for this phase.
3. **Draft Report:** Summarize the findings clearly, separating actionable feedback from pass/fail criteria.

### Kill Switch / Quality Gate
- If the analysis determines a critical failure in the requirements, specification, or code quality, you MUST output exactly this phrase at the end of your report: `CRITICAL FAILURE: SPEC-KITTY-CLARIFY`
