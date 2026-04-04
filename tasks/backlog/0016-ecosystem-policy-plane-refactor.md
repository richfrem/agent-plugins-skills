# Task 0016: Ecosystem Policy Plane Refactor

## Objective
Enable a Claude or Gemini 3.1 Pro agent to autonomously manage, refactor, and improve the AI plugins, skills, and agents repository. The agent must:
- Create a feature branch feature/ecosystem-robustness-refactor.
- Initialize temp/refactor-plan/ with tasks.md and specification.md.
- Synthesize ADRs 001-006 and plugin analysis patterns.
- Enforce zero duplication, strict encapsulation, policy plane separation, and automated portability.
- Use bridge_installer.py, os-eval-runner, and audit scripts for implementation and verification.
- Commit with score deltas, update status, and generate a summary report on completion.

## Acceptance Criteria
- Feature branch created: feature/ecosystem-robustness-refactor
- Management directory and files initialized in temp/refactor-plan/
- ADRs and plugin analysis patterns synthesized into actionable plan
- Policy plane separation and portability mandates addressed
- All changes verified, committed, and tracked in tasks.md
- Summary report generated upon completion

## Notes
Reference prompt: See temp/prompts/prompt-to-improve-repo.md for the full autonomous ecosystem management agent instructions and workflow.
