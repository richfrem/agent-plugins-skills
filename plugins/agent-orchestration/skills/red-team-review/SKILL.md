---
name: red-team-review
plugin: agent-orchestration
description: "(Industry standard: Review and Critique Pattern) Primary Use Case: Iterative generation paired with adversarial review, continuing until an 'Approved' verdict is reached. Orchestrated adversarial review loop. Use when: research, designs, architectures, or decisions need to be reviewed by red team agents (human, browser, or CLI). Iterates in rounds of research → bundle → review → feedback until approved."
allowed-tools: Bash, Read, Write
---

# Red Team Review (red-team-review)

Orchestrated adversarial review loop pairing iterative plan/code generation with independent critique personas (Architecture Skeptic, Security Auditor, TDD Contract Reviewer) until an "Approved" verdict is earned.

## Contents
- [Critical Constraints](#critical-constraints)
- [Dependencies](#dependencies)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
1. **Fan-Out Trio Invariant**: Multi-persona reviews must dispatch to all 3 Graph Planning roles: Architecture Skeptic (`architect-review`), Security / Edge-Case Auditor (`security-auditor`), and TDD Contract Reviewer (`tdd-contract-reviewer`).
2. **Directory Isolation**: Save review packets and critique outputs to isolated directories (e.g. `.history/review-iteration-1/`) so baseline artifacts are never destructively overwritten.
3. **Convergence Limit**: If 2-3 rounds pass without approval, stop looping and escalate outstanding disagreements to human/orchestrator tie-breaker.
4. **Non-Interactive Input Redirection**: Always append `< /dev/null` to headless CLI commands to prevent `SIGTTIN` hangs.

## Dependencies
- **`context-bundler`** (dev-utils) — Required for creating review packets in Multi-Persona Fan-Out Mode
- **Adversarial personas**: `architect-review`, `security-auditor`, `tdd-contract-reviewer` in `cli-agents`

## Quick start

```bash
# Bundle context using the context-bundler skill in dev-utils
python3 plugins/dev-utils/scripts/bundle_context.py --manifest manifest.json --out temp/review/
```

## Workflow

1. **Research & Packet Generation**: Draft `red-team-prompt.md`, prepare `manifest.json`, and run `context-bundler` in Multi-Persona Fan-Out Mode to generate persona packets.
2. **Select Backend**: Interactively confirm CLI backend (`agy`, `claude`, `copilot`, `codex`) and model tier with user.
3. **Parallel Dispatch**: Dispatch review bundles in parallel to designated persona reviewers.
4. **Synthesize Feedback**: Capture verdicts. If "More Research Needed", iterate with targeted questions. If consensus is reached, advance.
5. **Handoff**: On approval, terminate review loop and pass approved artifacts back to parent orchestrator.

## Verification

```bash
# Execute project unit tests to verify no regressions were introduced
pytest tests/ -k "not test_health_check_signing_status"
```

## References
- [acceptance-criteria.md](references/acceptance-criteria.md) — Review criteria, persona responsibilities, and approval definitions.
- [fallback-tree.md](references/fallback-tree.md) — Deadlock breaking and escalation protocol when reviewers disagree.
