---
description: Run a structured retrospective for the current session or feature.
---
# Spec Kitty Retrospective

Starts a structured retrospective session using the standard template. This helps improve the agent/user workflow by capturing what went well and what needs improvement.

## 1. Locate Template
Load the retrospective template from:
`cat .agent/templates/workflow/retrospective-template.md`

## 2. Generate Retrospective
Identify the current active specification folder in `kitty-specs/` (e.g., `kitty-specs/0003-hybrid-pilot/`).
Create or append to `retrospective.md` inside that folder:
`kitty-specs/[Current-Spec-ID]/retrospective.md`

**Note:** If `retrospective.md` already exists, append the new session with a header `## Session [YYYY-MM-DD]`.

## 3. Facilitate
Ask the user the core questions:
1.  **What Went Well?**
2.  **What Didn't Go Well?**
3.  **Action Items?**

have the user ask you these questions:
1.  **What Went Well?**
2.  **What Didn't Go Well?** Are there things that could be quickly fixed now? or are there bigger things that we should add to task backlog?
3.  **Action Items?** should we create tasks in the backlog or quickly update some things


## 4. Save & Commit
Once finalized, save the file and commit it to the repository if appropriate.
